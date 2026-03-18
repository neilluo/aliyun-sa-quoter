"""Elasticsearch product definition - ai_friendly format.

ProductCode: elasticsearch
ProductType: "elasticsearchpre" (Subscription), "elasticsearch" (PayAsYouGo)
API docs: https://help.aliyun.com/document_detail/170253.html

MVP Version: Support core data node and disk modules only.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from framework.builders import ModuleBuilder
from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Region, Category, DiskType, BillingType
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "elasticsearch"
NAME: str = "Elasticsearch"
DISPLAY_NAME: str = "Elasticsearch 检索分析服务"
CATEGORY: str = Category.DATABASE

# 动态 ProductType：根据订阅类型切换
PRODUCT_TYPE: Optional[Union[str, Callable]] = lambda p: (
    "elasticsearchpre" if p.get("subscription_type") == BillingType.SUBSCRIPTION else "elasticsearch"
)


# =============================================================================
# PARAMS SECTION
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
        "name": "node_spec",
        "label": "数据节点规格",
        "type": "string",
        "required": True,
        "default": None,
        "choices": [
            "elasticsearch.g7.xlarge",
            "elasticsearch.g7.2xlarge",
            "elasticsearch.g7.4xlarge",
            "elasticsearch.g7.8xlarge",
            "elasticsearch.r7.xlarge",
            "elasticsearch.r7.2xlarge",
            "elasticsearch.r7.4xlarge",
            "elasticsearch.c7.xlarge",
            "elasticsearch.c7.2xlarge",
            "elasticsearch.c7.4xlarge",
        ],
        "description": "Elasticsearch 数据节点规格，如 elasticsearch.g7.xlarge (4C16G)",
        "examples": ["elasticsearch.g7.xlarge", "elasticsearch.r7.2xlarge"],
    },
    {
        "name": "node_amount",
        "label": "数据节点数量",
        "type": "int",
        "required": True,
        "default": 3,
        "choices": None,
        "description": "数据节点数量，建议至少3个保证高可用，范围 2-50",
        "examples": [3, 5, 10],
    },
    {
        "name": "disk_type",
        "label": "存储类型",
        "type": "string",
        "required": True,
        "default": DiskType.SSD,
        "choices": [DiskType.SSD, DiskType.ESSD, DiskType.EFFICIENCY],
        "description": "数据节点存储类型",
        "examples": [DiskType.SSD, DiskType.ESSD],
    },
    {
        "name": "disk_size",
        "label": "单节点存储大小",
        "type": "int",
        "required": True,
        "default": 20,
        "choices": None,
        "description": "每个数据节点的存储大小，单位 GB，范围 20-20480",
        "examples": [20, 100, 500],
    },
    {
        "name": "performance_level",
        "label": "ESSD性能级别",
        "type": "string",
        "required": False,
        "default": "PL1",
        "choices": ["PL0", "PL1", "PL2", "PL3"],
        "description": "ESSD云盘性能级别，仅在使用 cloud_essd 时有效",
        "examples": ["PL1", "PL2"],
    },
    {
        "name": "subscription_type",
        "label": "付费类型",
        "type": "string",
        "required": False,
        "default": BillingType.SUBSCRIPTION,
        "choices": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
        "description": "Subscription (包年包月) 或 PayAsYouGo (按量付费)",
        "examples": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

MODULES: List[ModuleSpec] = [
    {
        "module_code": "NodeSpec",
        "config_template": "NodeSpec:{node_spec},Region:{region},NodeAmount:{node_amount}",
    },
    {
        "module_code": "Disk",
        "config_template": "DataDiskType:{disk_type},PerformanceLevel:{performance_level},Region:{region},NodeAmount:{node_amount},Disk:{disk_size}",
    },
]

DEFAULT_PRICE_TYPE: str = "Hour"


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="node_amount",
        label="数据节点数量",
        required=True,
        min_val=2,
        max_val=50,
        error_formatter=lambda r, v, t: (
            "数据节点数量至少为 2 个（建议 3 个以上保证高可用）" if t == 'min_val'
            else "数据节点数量不能超过 50 个" if t == 'max_val'
            else f"参数 {r.label} ({r.name}) 验证失败"
        ),
    ),
    ValidationRule(
        name="disk_size",
        label="单节点存储大小",
        required=True,
        min_val=20,
        max_val=20480,
        error_formatter=lambda r, v, t: (
            "单节点存储大小至少为 20GB" if t == 'min_val'
            else "单节点存储大小不能超过 20480GB" if t == 'max_val'
            else f"参数 {r.label} ({r.name}) 验证失败"
        ),
    ),
]


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    return result


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build BSS module list."""
    p = _prepare_params(params)
    builder = ModuleBuilder(default_price_type=DEFAULT_PRICE_TYPE)
    
    for spec in MODULES:
        builder.add(spec["module_code"], spec["config_template"])
    
    return builder.build(p)


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    subscription_type = params.get("subscription_type", BillingType.SUBSCRIPTION)
    pricing_mode = "包年包月" if subscription_type == BillingType.SUBSCRIPTION else "按量付费"
    
    return {
        "产品": "Elasticsearch",
        "付费模式": pricing_mode,
        "地域": params.get("region", Region.HANGZHOU),
        "数据节点规格": params.get("node_spec"),
        "数据节点数量": str(params.get("node_amount", 3)),
        "存储类型": params.get("disk_type", DiskType.SSD),
        "单节点存储": f"{params.get('disk_size', 20)}GB",
    }


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate parameters."""
    errors = []
    
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
    
    if VALIDATION_RULES:
        validator = Validator(VALIDATION_RULES)
        errors.extend(validator.validate(params))
    
    # ESSD disk requires performance level
    disk_type = params.get("disk_type", DiskType.SSD)
    performance_level = params.get("performance_level", "PL1")
    if disk_type == DiskType.ESSD and not performance_level:
        errors.append("ESSD 云盘必须指定性能级别 (PL0/PL1/PL2/PL3)")
    
    return errors


# =============================================================================
# EXPORT SECTION
# =============================================================================

PRODUCT = {
    "code": CODE,
    "name": NAME,
    "display_name": DISPLAY_NAME,
    "product_type": PRODUCT_TYPE,
    "category": CATEGORY,
    "params": PARAMS,
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from ai_friendly.validate import validate_product_file
    
    print(f"验证产品定义: {CODE}")
    errors = validate_product_file(__file__)
    
    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        sys.exit(0)
