"""ECS 产品定义 - 使用 AI 友好模板的完整示例。

这是一个完整的产品定义示例，展示了如何使用 TEMPLATE.py 定义 ECS 产品。
AI 可以参考此文件学习如何接入其他产品。
"""

from typing import Any, Dict, List

from ..framework.builders import ModuleBuilder
from ..framework.validators import ValidationRule, Validator
from .constants import Region, Category, DiskType
from .types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION - 产品配置
# =============================================================================

CODE: str = "ecs"
NAME: str = "ECS"
DISPLAY_NAME: str = "ECS 云服务器"
CATEGORY: str = Category.COMPUTE
PRODUCT_TYPE = None  # ECS 不需要 ProductType


# =============================================================================
# PARAMS SECTION - 参数定义
# =============================================================================

PARAMS: List[ParamDef] = [
    {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": True,
        "default": Region.HANGZHOU,
        "choices": Region.ALL,
        "description": "阿里云地域ID",
        "examples": [Region.HANGZHOU, Region.BEIJING, Region.SHANGHAI],
    },
    {
        "name": "instance_type",
        "label": "实例规格",
        "type": "string",
        "required": True,
        "description": "ECS 实例规格，如 ecs.g7.xlarge (4C16G)",
        "examples": ["ecs.g7.xlarge", "ecs.c7.large", "ecs.r7.2xlarge"],
    },
    {
        "name": "image_os",
        "label": "操作系统",
        "type": "string",
        "required": False,
        "default": "linux",
        "choices": ["linux", "windows"],
        "description": "操作系统类型",
        "examples": ["linux", "windows"],
    },
    {
        "name": "system_disk_category",
        "label": "系统盘类型",
        "type": "string",
        "required": False,
        "default": DiskType.ESSD,
        "choices": [DiskType.ESSD, DiskType.CLOUD_SSD, DiskType.CLOUD_EFFICIENCY],
        "description": "系统盘类型",
        "examples": [DiskType.ESSD],
    },
    {
        "name": "system_disk_size",
        "label": "系统盘大小",
        "type": "int",
        "required": False,
        "default": 40,
        "description": "系统盘大小 (GB)，最小 20GB",
        "examples": [40, 100],
    },
    {
        "name": "data_disk_size",
        "label": "数据盘大小",
        "type": "int",
        "required": False,
        "default": 0,
        "description": "数据盘大小 (GB)，0 表示不添加",
        "examples": [0, 100, 500],
    },
    {
        "name": "internet_bandwidth",
        "label": "公网带宽",
        "type": "int",
        "required": False,
        "default": 0,
        "description": "公网带宽 (Mbps)，0 表示不添加",
        "examples": [0, 5, 10],
    },
]


# =============================================================================
# MODULES SECTION - BSS 模块定义
# =============================================================================

MODULES: List[ModuleSpec] = [
    {
        "module_code": "InstanceType",
        "config_template": "InstanceType:{instance_type},IoOptimized:IoOptimized,ImageOs:{image_os},InstanceTypeFamily:{family}",
    },
    {
        "module_code": "SystemDisk",
        "config_template": "SystemDisk.Category:{system_disk_category},SystemDisk.Size:{system_disk_size}",
    },
    {
        "module_code": "DataDisk",
        "config_template": "DataDisk.Category:{data_disk_category},DataDisk.Size:{data_disk_size}",
        "condition": lambda p: p.get("data_disk_size", 0) > 0,
    },
    {
        "module_code": "InternetMaxBandwidthOut",
        "config_template": "InternetMaxBandwidthOut:{internet_bandwidth},InternetMaxBandwidthOut.IsFlowType:5,NetworkType:1",
        "condition": lambda p: p.get("internet_bandwidth", 0) > 0,
    },
]

DEFAULT_PRICE_TYPE: str = "Hour"


# =============================================================================
# VALIDATION SECTION - 验证规则
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="system_disk_size",
        label="系统盘大小",
        min_val=20,
    ),
]


# =============================================================================
# IMPLEMENTATION SECTION - 实现（通用 + 特定逻辑）
# =============================================================================

def _get_product_type(params: Dict[str, Any]):
    """ECS 不需要 ProductType。"""
    return None


def _extract_instance_family(instance_type: str) -> str:
    """从实例规格提取实例族，如 'ecs.g7.xlarge' -> 'ecs.g7'。"""
    parts = instance_type.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return instance_type


def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """预处理参数。"""
    result = dict(params)
    
    # 计算 instance family
    instance_type = result.get("instance_type", "")
    result["family"] = _extract_instance_family(instance_type)
    
    # 数据盘类型默认使用系统盘类型
    if not result.get("data_disk_category"):
        result["data_disk_category"] = result.get("system_disk_category", DiskType.ESSD)
    
    return result


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """构建 BSS 模块列表。"""
    p = _prepare_params(params)
    builder = ModuleBuilder(default_price_type=DEFAULT_PRICE_TYPE)
    
    for spec in MODULES:
        condition = spec.get("condition")
        price_type = spec.get("price_type")
        
        if condition is not None:
            builder.add_conditional(
                spec["module_code"],
                spec["config_template"],
                condition,
                price_type,
            )
        else:
            builder.add(
                spec["module_code"],
                spec["config_template"],
                price_type,
            )
    
    return builder.build(p)


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """生成配置摘要。"""
    summary = {
        "产品": DISPLAY_NAME,
        "地域": params.get("region", Region.HANGZHOU),
        "实例规格": params["instance_type"],
        "操作系统": params.get("image_os", "linux"),
        "系统盘": f"{params.get('system_disk_category', DiskType.ESSD)} {params.get('system_disk_size', 40)}GB",
    }
    
    # 数据盘
    data_disk_size = params.get("data_disk_size", 0)
    if data_disk_size > 0:
        cat = params.get("data_disk_category") or params.get("system_disk_category", DiskType.ESSD)
        summary["数据盘"] = f"{cat} {data_disk_size}GB"
    
    # 公网带宽
    internet_bandwidth = params.get("internet_bandwidth", 0)
    if internet_bandwidth > 0:
        summary["公网带宽"] = f"{internet_bandwidth} Mbps"
    
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """验证参数。"""
    errors = []
    
    # 自动验证 PARAMS 中的 choices
    for param in PARAMS:
        name = param["name"]
        value = params.get(name)
        
        if param.get("required") and value is None:
            errors.append(f"缺少必填参数: {param['label']} ({name})")
            continue
        
        if value is None:
            continue
        
        choices = param.get("choices")
        if choices and value not in choices:
            errors.append(
                f"参数 {param['label']} ({name}) 的值 '{value}' 无效，"
                f"可选值: {', '.join(str(c) for c in choices)}"
            )
    
    # 验证规则检查
    if VALIDATION_RULES:
        validator = Validator(VALIDATION_RULES)
        errors.extend(validator.validate(params))
    
    # 自定义