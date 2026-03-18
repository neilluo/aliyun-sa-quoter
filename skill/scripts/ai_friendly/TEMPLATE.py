"""产品定义模板 - AI 接入新产品的唯一入口。

【AI 开发指南】
1. 复制此文件到 products/<product_code>.py
2. 填写 "CONFIG SECTION" 中的常量
3. 在 PARAMS 中定义参数
4. 在 MODULES 中定义 BSS 模块
5. 在 VALIDATION_RULES 中定义验证规则（可选）
6. 运行验证: python -m ai_friendly.validate <product_code>

【约定】
- 所有大写常量必须填写
- 所有列表必须至少有一个元素
- product_type 为 None 表示不需要 ProductType
- product_type 为函数表示动态计算

【示例】
见 TEMPLATE_EXAMPLE.py
"""

from typing import Any, Callable, Dict, List, Optional, Union

# =============================================================================
# AI 提示: 从 framework 导入，不要修改这些导入
# =============================================================================
from ..framework.builders import ModuleBuilder
from ..framework.validators import ValidationRule, Validator
from .constants import Region, Category, BillingType
from .types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION - AI 填写区域开始
# =============================================================================

# 产品基础信息（必填）
CODE: str = "example"                           # 产品代码，如 "ecs", "rds"
NAME: str = "Example"                           # 英文名称
DISPLAY_NAME: str = "示例产品"                   # 中文显示名称
CATEGORY: str = Category.COMPUTE                # 分类常量

# ProductType 配置（三选一）
# 选项 1: None - 不需要 ProductType
# 选项 2: str - 固定 ProductType，如 "alikafka_pre"
# 选项 3: Callable - 动态计算，如 lambda p: "alikafka_pre" if p.get("billing") == "subscription" else "alikafka_post"
PRODUCT_TYPE: Optional[Union[str, Callable]] = None


# =============================================================================
# PARAMS SECTION - 参数定义
# =============================================================================
# AI 提示: 每个参数是一个 ParamDef 字典
# 必填字段: name, label, type, required
# 可选字段: default, choices, description, examples

PARAMS: List[ParamDef] = [
    {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": True,
        "default": Region.HANGZHOU,
        "choices": Region.ALL,
        "description": "阿里云地域ID",
        "examples": [Region.HANGZHOU, Region.BEIJING],
    },
    {
        "name": "instance_type",
        "label": "实例规格",
        "type": "string",
        "required": True,
        "description": "实例规格代码",
        "examples": ["ecs.g7.xlarge"],
    },
]


# =============================================================================
# MODULES SECTION - BSS 模块定义
# =============================================================================
# AI 提示: 每个模块是一个 ModuleSpec 字典
# 必填字段: module_code, config_template
# 可选字段: condition（条件函数）, price_type（覆盖默认值）

MODULES: List[ModuleSpec] = [
    {
        "module_code": "Instance",
        "config_template": "Region:{region},InstanceType:{instance_type}",
    },
    # 条件模块示例:
    # {
    #     "module_code": "Disk",
    #     "config_template": "DiskSize:{disk_size}",
    #     "condition": lambda p: p.get("disk_size", 0) > 0,
    # },
]

# 默认价格类型（可选，默认 "Hour"）
DEFAULT_PRICE_TYPE: str = "Hour"


# =============================================================================
# VALIDATION SECTION - 验证规则（可选）
# =============================================================================
# AI 提示: 如果 PARAMS 中的 choices/min/max 足够，这里可以为空
# 复杂的跨字段验证在此定义

VALIDATION_RULES: List[ValidationRule] = [
    # 示例:
    # ValidationRule(
    #     name="disk_size",
    #     label="磁盘大小",
    #     min_val=20,
    #     max_val=32768,
    # ),
]


# =============================================================================
# IMPLEMENTATION SECTION - 实现区域（通常无需修改）
# =============================================================================
# AI 提示: 以下代码是通用的，除非有特殊需求，否则不要修改

def _get_product_type(params: Dict[str, Any]) -> Optional[str]:
    """Resolve ProductType."""
    if callable(PRODUCT_TYPE):
        return PRODUCT_TYPE(params)
    return PRODUCT_TYPE


def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    # AI: 如果需要参数预处理，在此添加
    return result


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build BSS module list."""
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
    """Build human-readable config summary."""
    summary = {
        "产品": DISPLAY_NAME,
        "地域": params.get("region", Region.HANGZHOU),
    }
    # AI: 添加其他摘要字段
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate parameters."""
    # 自动验证 PARAMS 中的 choices 和范围
    errors = []
    
    for param in PARAMS:
        name = param["name"]
        value = params.get(name)
        
        # 必填检查
        if param.get("required") and value is None:
            errors.append(f"缺少必填参数: {param['label']} ({name})")
            continue
        
        if value is None:
            continue
        
        # choices 检查
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
    
    # AI: 添加自定义验证逻辑
    return errors


# =============================================================================
# EXPORT SECTION - 导出 PRODUCT dict（不要修改）
# =============================================================================

PRODUCT = {
    "code": CODE,
    "name": NAME,
    "display_name": DISPLAY_NAME,
    "product_type": _get_product_type,
    "category": CATEGORY,
    "params": PARAMS,
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}


# =============================================================================
# AI 验证命令（运行此文件时执行自检）
# =============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加项目根目录到路径
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
