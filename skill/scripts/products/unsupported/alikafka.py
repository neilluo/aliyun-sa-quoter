"""Kafka (消息队列 Kafka) product definition - ai_friendly format.

ProductCode: alikafka
ProductType: alikafka_pre (Subscription), alikafka_post (PayAsYouGo)
API docs: https://help.aliyun.com/document_detail/170253.html
"""

from typing import Any, Callable, Dict, List, Optional, Union

from framework.builders import ModuleBuilder
from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Region, Category, BillingType, ProductType, PriceType
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "alikafka"
NAME: str = "Kafka"
DISPLAY_NAME: str = "消息队列 Kafka"
CATEGORY: str = Category.MIDDLEWARE


def _get_product_type(params: Dict[str, Any]) -> Optional[str]:
    """Determine ProductType based on subscription type.

    - Subscription (包年包月) uses "alikafka_pre"
    - PayAsYouGo (按量付费) uses "alikafka_post"
    """
    subscription_type = params.get("subscription_type", BillingType.SUBSCRIPTION)
    if subscription_type == BillingType.PAY_AS_YOU_GO:
        return ProductType.KAFKA_POST
    return ProductType.KAFKA_PRE


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
        "name": "spec_type",
        "label": "规格类型",
        "type": "string",
        "required": True,
        "default": "normal",
        "choices": ["normal", "professional", "professionalForHighRead"],
        "description": "规格类型: normal(标准版-高写), professional(专业版-高写), professionalForHighRead(专业版-高读)",
        "examples": ["normal", "professional"],
    },
    {
        "name": "partition_num",
        "label": "分区数",
        "type": "int",
        "required": True,
        "default": 100,
        "choices": None,
        "description": "分区数，范围 0-40000",
        "examples": [100, 500, 1000],
    },
    {
        "name": "topic_quota",
        "label": "Topic配额",
        "type": "int",
        "required": True,
        "default": 50,
        "choices": None,
        "description": "Topic配额数量，范围 1-9999",
        "examples": [50, 100, 500],
    },
    {
        "name": "disk_type",
        "label": "磁盘类型",
        "type": "string",
        "required": True,
        "default": "1",
        "choices": ["0", "1", "5", "6"],
        "description": "磁盘类型: 0=高效云盘, 1=SSD, 5=ESSD_PL0, 6=ESSD_PL1",
        "examples": ["1", "6"],
    },
    {
        "name": "disk_size",
        "label": "磁盘容量",
        "type": "int",
        "required": True,
        "default": 500,
        "choices": None,
        "description": "磁盘容量(GB)，最小100，步长100",
        "examples": [500, 1000, 2000],
    },
    {
        "name": "eip_max",
        "label": "公网流量峰值",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "公网流量峰值(MB/s)，范围 0-2500，0表示不开通公网",
        "examples": [0, 100, 500],
    },
    {
        "name": "io_max_spec",
        "label": "流量规格",
        "type": "string",
        "required": False,
        "default": None,
        "choices": None,
        "description": "流量规格，如 alikafka.hw.2xlarge，不指定则自动选择",
        "examples": ["alikafka.hw.2xlarge", "alikafka.hr.3xlarge"],
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
        "module_code": "PartitionNum",
        "config_template": "PartitionNum:{partition_num},SpecType:{spec_type},RegionId:{region}",
    },
    {
        "module_code": "TopicQuota",
        "config_template": "PartitionNum:{partition_num},TopicQuota:{topic_quota},RegionId:{region}",
    },
    {
        "module_code": "IoMaxSpec",
        "config_template": "SpecType:{spec_type},IoMaxSpec:{io_max_spec},RegionId:{region}",
    },
    {
        "module_code": "DiskSize",
        "config_template": "DiskType:{disk_type},DiskSize:{disk_size},RegionId:{region}",
    },
    {
        "module_code": "EipMax",
        "config_template": "EipMax:{eip_max},RegionId:{region}",
        "condition": lambda p: p.get("eip_max", 0) > 0,
    },
]

DEFAULT_PRICE_TYPE: str = PriceType.HOUR


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="partition_num",
        label="分区数",
        required=True,
        min_val=0,
        max_val=40000,
    ),
    ValidationRule(
        name="topic_quota",
        label="Topic配额",
        required=True,
        min_val=1,
        max_val=9999,
    ),
    ValidationRule(
        name="disk_size",
        label="磁盘容量",
        required=True,
        min_val=100,
        max_val=99999999999,
    ),
    ValidationRule(
        name="eip_max",
        label="公网流量峰值",
        min_val=0,
        max_val=2500,
    ),
]


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _get_valid_io_specs(spec_type: str) -> List[str]:
    """根据 spec_type 返回有效的 io_max_spec 列表."""
    if spec_type == "professionalForHighRead":
        return [
            "alikafka.hr.2xlarge",
            "alikafka.hr.3xlarge",
            "alikafka.hr.6xlarge",
            "alikafka.hr.9xlarge",
            "alikafka.hr.12xlarge",
        ]
    else:
        return [
            "alikafka.hw.2xlarge",
            "alikafka.hw.3xlarge",
            "alikafka.hw.6xlarge",
            "alikafka.hw.9xlarge",
            "alikafka.hw.12xlarge",
        ]


def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    
    # Set defaults
    if "region" not in result:
        result["region"] = Region.HANGZHOU
    if "spec_type" not in result:
        result["spec_type"] = "normal"
    if "partition_num" not in result:
        result["partition_num"] = 100
    if "topic_quota" not in result:
        result["topic_quota"] = 50
    if "disk_type" not in result:
        result["disk_type"] = "1"
    if "disk_size" not in result:
        result["disk_size"] = 500
    if "eip_max" not in result:
        result["eip_max"] = 0
    if "subscription_type" not in result:
        result["subscription_type"] = BillingType.SUBSCRIPTION
    
    # Set default io_max_spec based on spec_type
    if not result.get("io_max_spec"):
        if result["spec_type"] == "professionalForHighRead":
            result["io_max_spec"] = "alikafka.hr.2xlarge"
        else:
            result["io_max_spec"] = "alikafka.hw.2xlarge"
    
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
    spec_type_map = {
        "normal": "标准版(高写)",
        "professional": "专业版(高写)",
        "professionalForHighRead": "专业版(高读)",
    }
    
    disk_type_map = {
        "0": "高效云盘",
        "1": "SSD",
        "5": "ESSD_PL0",
        "6": "ESSD_PL1",
    }
    
    subscription_type = params.get("subscription_type", BillingType.SUBSCRIPTION)
    spec_type = params.get("spec_type", "normal")
    
    summary = {
        "产品": DISPLAY_NAME,
        "付费模式": BillingType.DISPLAY_NAMES.get(subscription_type, subscription_type),
        "地域": params.get("region", Region.HANGZHOU),
        "规格类型": spec_type_map.get(spec_type, spec_type),
        "分区数": str(params.get("partition_num", 100)),
        "Topic配额": str(params.get("topic_quota", 50)),
        "磁盘类型": disk_type_map.get(str(params.get("disk_type", "1")), params.get("disk_type", "1")),
        "磁盘容量": f"{params.get('disk_size', 500)}GB",
        "流量规格": params.get("io_max_spec", "自动选择"),
    }
    
    eip_max = params.get("eip_max", 0)
    if eip_max > 0:
        summary["公网流量峰值"] = f"{eip_max}MB/s"
    
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate Kafka parameter combinations."""
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
    
    # Custom validation for io_max_spec
    io_max_spec = params.get("io_max_spec")
    if io_max_spec:
        spec_type = params.get("spec_type", "normal")
        valid_io_specs = _get_valid_io_specs(spec_type)
        if io_max_spec not in valid_io_specs:
            errors.append(
                f"io_max_spec '{io_max_spec}' 与 spec_type '{spec_type}' 不匹配，"
                f"可选值: {', '.join(valid_io_specs)}"
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
