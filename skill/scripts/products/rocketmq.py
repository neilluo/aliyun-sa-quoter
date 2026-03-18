"""RocketMQ 4.0 (消息队列 RocketMQ 4.0) product definition - ai_friendly format.

ProductCode: ons
ProductType: ons (标准版), onspre (企业铂金版)
API docs: https://help.aliyun.com/document_detail/170253.html

Note: BSS API supports RocketMQ 4.0, not 5.0.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from framework.builders import ModuleBuilder
from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Region, Category, BillingType, ProductType, PriceType
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "ons"
NAME: str = "RocketMQ"
DISPLAY_NAME: str = "消息队列 RocketMQ 4.0"
CATEGORY: str = Category.MIDDLEWARE


def _get_product_type(params: Dict[str, Any]) -> Optional[str]:
    """Determine ProductType based on subscription type.

    - Subscription (包年包月) uses "onspre" (企业铂金版)
    - PayAsYouGo (按量付费) uses "ons" (标准版)
    """
    subscription_type = params.get("subscription_type", BillingType.SUBSCRIPTION)
    if subscription_type == BillingType.PAY_AS_YOU_GO:
        return "ons"
    return "onspre"


PRODUCT_TYPE: Optional[Union[str, Callable]] = _get_product_type


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
        "name": "topic_capacity",
        "label": "Topic数上限",
        "type": "int",
        "required": False,
        "default": 25,
        "choices": None,
        "description": "Topic数量上限 (25-3000, 步长5)",
        "examples": [25, 100, 500],
    },
    {
        "name": "tps_max",
        "label": "TPS峰值",
        "type": "int",
        "required": False,
        "default": 5000,
        "choices": [5000, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 190000, 200000, 210000, 220000, 230000, 240000, 250000, 260000, 270000, 280000, 290000, 300000, 310000, 320000, 330000, 340000, 350000, 360000, 370000, 380000, 390000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000],
        "description": "每秒消息处理峰值(条/秒)",
        "examples": [5000, 10000, 50000],
    },
    {
        "name": "message_capacity",
        "label": "消息存储容量",
        "type": "int",
        "required": False,
        "default": 700,
        "choices": [700, 1400, 1500, 2500, 2800, 3000, 5000, 6000, 10000, 15000, 19000],
        "description": "消息存储容量(GB)",
        "examples": [700, 1400, 5000],
    },
    {
        "name": "subscription_type",
        "label": "付费类型",
        "type": "string",
        "required": False,
        "default": BillingType.SUBSCRIPTION,
        "choices": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
        "description": "Subscription(包年包月) 或 PayAsYouGo(按量付费)",
        "examples": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

# RocketMQ 4.0 企业铂金版 modules (from BSS API)
MODULES: List[ModuleSpec] = [
    {
        "module_code": "Topic_capacity",
        "config_template": "Region:{region},Topic_capacity:{topic_capacity}",
    },
    {
        "module_code": "Tps_max",
        "config_template": "Region:{region},Tps_max:{tps_max},Message_capacity:{message_capacity}",
    },
]

DEFAULT_PRICE_TYPE: str = PriceType.MONTH


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="flow_out_bandwidth",
        label="公网带宽",
        min_val=0,
        max_val=600,
    ),
    ValidationRule(
        name="topic_paid",
        label="付费Topic数量",
        min_val=0,
    ),
]


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _get_valid_process_specs(chip_type: str) -> List[str]:
    """根据 chip_type 返回有效的 msg_process_spec 列表."""
    if chip_type == "arm":
        return [
            "rmq.su.2xlarge",
            "rmq.su.4xlarge",
            "rmq.su.6xlarge",
        ]
    else:  # x86
        return [
            "rmq.su.2xlarge",
            "rmq.su.4xlarge",
            "rmq.su.6xlarge",
            "rmq.su.8xlarge",
        ]


def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    
    # Set defaults
    if "region" not in result:
        result["region"] = Region.HANGZHOU
    if "chip_type" not in result:
        result["chip_type"] = "x86"
    if "msg_process_spec" not in result:
        result["msg_process_spec"] = "rmq.su.2xlarge"
    if "msg_store_spec" not in result:
        result["msg_store_spec"] = "rmq.ssu.2xlarge"
    if "series_type" not in result:
        result["series_type"] = "standard"
    if "flow_out_bandwidth" not in result:
        result["flow_out_bandwidth"] = 0
    if "flow_out_type" not in result:
        result["flow_out_type"] = "payByTraffic"
    if "topic_paid" not in result:
        result["topic_paid"] = 0
    if "subscription_type" not in result:
        result["subscription_type"] = BillingType.SUBSCRIPTION
    
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
    subscription_type = params.get("subscription_type", BillingType.SUBSCRIPTION)
    
    summary = {
        "产品": DISPLAY_NAME,
        "付费模式": BillingType.DISPLAY_NAMES.get(subscription_type, subscription_type),
        "地域": params.get("region", Region.HANGZHOU),
        "Topic数上限": str(params.get("topic_capacity", 100)),
        "TPS峰值": str(params.get("tps_max", 1000)),
        "消息存储容量": f"{params.get('message_capacity', 100)}GB",
    }
    
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate RocketMQ parameter combinations."""
    errors = []
    
    # Auto-validate PARAMS choices
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


# =============================================================================
# AI 验证命令（运行此文件时执行自检）
# =============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add project root to path
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
