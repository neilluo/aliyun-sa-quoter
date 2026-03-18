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
        "name": "chip_type",
        "label": "架构类型",
        "type": "string",
        "required": True,
        "default": "x86",
        "choices": ["x86", "arm"],
        "description": "芯片架构类型: x86 或 arm",
        "examples": ["x86", "arm"],
    },
    {
        "name": "msg_process_spec",
        "label": "消息收发计算规格",
        "type": "string",
        "required": True,
        "default": "rmq.su.2xlarge",
        "choices": None,
        "description": "消息收发计算规格，如 rmq.su.2xlarge (8核16G)",
        "examples": ["rmq.su.2xlarge", "rmq.su.4xlarge"],
    },
    {
        "name": "msg_store_spec",
        "label": "消息存储规格",
        "type": "string",
        "required": True,
        "default": "rmq.ssu.2xlarge",
        "choices": ["rmq.ssu.2xlarge", "rmq.ssu.4xlarge", "rmq.ssu.6xlarge", "rmq.ssu.8xlarge"],
        "description": "消息存储规格，如 rmq.ssu.2xlarge (8核16G)",
        "examples": ["rmq.ssu.2xlarge", "rmq.ssu.4xlarge"],
    },
    {
        "name": "series_type",
        "label": "系列类型",
        "type": "string",
        "required": True,
        "default": "standard",
        "choices": ["standard", "professional"],
        "description": "系列类型: standard(标准版), professional(专业版)",
        "examples": ["standard", "professional"],
    },
    {
        "name": "flow_out_bandwidth",
        "label": "公网带宽",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "公网带宽(MB/s)，范围 0-600，0表示不开通",
        "examples": [0, 100, 200],
    },
    {
        "name": "flow_out_type",
        "label": "公网计费类型",
        "type": "string",
        "required": False,
        "default": "payByTraffic",
        "choices": ["payByTraffic", "fixedBandwidth"],
        "description": "公网计费类型: payByTraffic(按流量), fixedBandwidth(固定带宽)",
        "examples": ["payByTraffic", "fixedBandwidth"],
    },
    {
        "name": "topic_paid",
        "label": "付费Topic数量",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "付费Topic数量，≥0",
        "examples": [0, 10, 50],
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

MODULES: List[ModuleSpec] = [
    {
        "module_code": "msg_process_spec",
        "config_template": "chip_type:{chip_type},region:{region},msg_process_spec:{msg_process_spec}",
    },
    {
        "module_code": "msg_store_spec",
        "config_template": "msg_store_spec:{msg_store_spec},region:{region}",
    },
    {
        "module_code": "flow_out_bandwidth",
        "config_template": "flow_out_bandwidth:{flow_out_bandwidth},flow_out_type:{flow_out_type},region:{region}",
        "condition": lambda p: p.get("flow_out_bandwidth", 0) > 0,
    },
    {
        "module_code": "topic_paid",
        "config_template": "region:{region},series_type:{series_type}",
        "condition": lambda p: p.get("topic_paid", 0) > 0,
    },
]

DEFAULT_PRICE_TYPE: str = PriceType.HOUR


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
    series_type_map = {
        "standard": "标准版",
        "professional": "专业版",
    }
    
    flow_out_type_map = {
        "payByTraffic": "按流量计费",
        "fixedBandwidth": "固定带宽",
    }
    
    subscription_type = params.get("subscription_type", BillingType.SUBSCRIPTION)
    chip_type = params.get("chip_type", "x86")
    series_type = params.get("series_type", "standard")
    
    summary = {
        "产品": DISPLAY_NAME,
        "付费模式": BillingType.DISPLAY_NAMES.get(subscription_type, subscription_type),
        "地域": params.get("region", Region.HANGZHOU),
        "架构类型": chip_type.upper(),
        "系列类型": series_type_map.get(series_type, series_type),
        "消息收发规格": params.get("msg_process_spec", "rmq.su.2xlarge"),
        "消息存储规格": params.get("msg_store_spec", "rmq.ssu.2xlarge"),
    }
    
    flow_out_bandwidth = params.get("flow_out_bandwidth", 0)
    if flow_out_bandwidth > 0:
        flow_out_type = params.get("flow_out_type", "payByTraffic")
        summary["公网带宽"] = f"{flow_out_bandwidth}MB/s"
        summary["公网计费"] = flow_out_type_map.get(flow_out_type, flow_out_type)
    
    topic_paid = params.get("topic_paid", 0)
    if topic_paid > 0:
        summary["付费Topic数"] = str(topic_paid)
    
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
    
    # Run validation rules
    if VALIDATION_RULES:
        validator = Validator(VALIDATION_RULES)
        errors.extend(validator.validate(params))
    
    # Custom validation for msg_process_spec
    chip_type = params.get("chip_type", "x86")
    msg_process_spec = params.get("msg_process_spec")
    if msg_process_spec:
        valid_process_specs = _get_valid_process_specs(chip_type)
        if msg_process_spec not in valid_process_specs:
            errors.append(
                f"msg_process_spec '{msg_process_spec}' 与 chip_type '{chip_type}' 不匹配，"
                f"可选值: {', '.join(valid_process_specs)}"
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
