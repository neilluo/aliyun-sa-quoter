"""NAS (File Storage NAS) product definition - ai_friendly format.

ProductCode: nas
ProductType: "naspost" (fixed)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
Note: NAS primarily supports PayAsYouGo billing mode.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from framework.builders import ModuleBuilder
from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Region, Category, BillingType, ProductType, PriceType
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "nas"
NAME: str = "NAS"
DISPLAY_NAME: str = "文件存储 NAS"
CATEGORY: str = Category.STORAGE

# NAS uses fixed ProductType
PRODUCT_TYPE: Optional[Union[str, Callable]] = "naspost"


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
        "name": "file_system_type",
        "label": "文件系统类型",
        "type": "string",
        "required": True,
        "default": "standard",
        "choices": ["standard", "extreme", "cpfs"],
        "description": "文件系统类型: standard(通用型), extreme(极速型), cpfs(并行文件系统)",
        "examples": ["standard", "extreme"],
    },
    {
        "name": "storage_type",
        "label": "存储类型",
        "type": "string",
        "required": True,
        "default": "Performance",
        "choices": ["Performance", "Capacity"],
        "description": "存储类型: Performance(性能型), Capacity(容量型)",
        "examples": ["Performance", "Capacity"],
    },
    {
        "name": "protocol_type",
        "label": "协议类型",
        "type": "string",
        "required": True,
        "default": "NFS",
        "choices": ["NFS", "SMB"],
        "description": "协议类型: NFS(Linux/Unix), SMB(Windows)",
        "examples": ["NFS", "SMB"],
    },
    {
        "name": "capacity",
        "label": "存储容量",
        "type": "int",
        "required": True,
        "default": 100,
        "choices": None,
        "description": "存储容量(GB)，最小100GB，不同文件系统类型有不同上限",
        "examples": [100, 1000, 10000],
    },
    {
        "name": "data_transfer",
        "label": "数据传出流量",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "数据传出流量(GB)，≥0",
        "examples": [0, 100, 1000],
    },
    {
        "name": "subscription_type",
        "label": "付费类型",
        "type": "string",
        "required": False,
        "default": BillingType.PAY_AS_YOU_GO,
        "choices": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
        "description": "付费类型。注意：NAS主要支持按量付费",
        "examples": [BillingType.PAY_AS_YOU_GO],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

MODULES: List[ModuleSpec] = [
    {
        "module_code": "FileSystem",
        "config_template": "Region:{region},FileSystemType:{file_system_type},StorageType:{storage_type},ProtocolType:{protocol_type}",
    },
    {
        "module_code": "Capacity",
        "config_template": "Region:{region},Capacity:{capacity}",
    },
    {
        "module_code": "DataTransfer",
        "config_template": "Region:{region},DataTransfer:{data_transfer}",
        "condition": lambda p: p.get("data_transfer", 0) > 0,
    },
]

DEFAULT_PRICE_TYPE: str = PriceType.HOUR


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="capacity",
        label="存储容量",
        required=True,
        min_val=100,
        max_val=256 * 1024 * 1024,  # 256TB in GB
    ),
    ValidationRule(
        name="data_transfer",
        label="数据传出流量",
        min_val=0,
    ),
]


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    # Set defaults
    if "file_system_type" not in result:
        result["file_system_type"] = "standard"
    if "storage_type" not in result:
        result["storage_type"] = "Performance"
    if "protocol_type" not in result:
        result["protocol_type"] = "NFS"
    if "capacity" not in result:
        result["capacity"] = 100
    if "data_transfer" not in result:
        result["data_transfer"] = 0
    if "subscription_type" not in result:
        result["subscription_type"] = BillingType.PAY_AS_YOU_GO
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
    file_system_type_map = {
        "standard": "通用型",
        "extreme": "极速型",
        "cpfs": "CPFS",
    }
    storage_type_map = {
        "Performance": "性能型",
        "Capacity": "容量型",
    }
    protocol_type_map = {
        "NFS": "NFS",
        "SMB": "SMB",
    }
    
    subscription_type = params.get("subscription_type", BillingType.PAY_AS_YOU_GO)
    
    summary = {
        "产品": DISPLAY_NAME,
        "付费模式": BillingType.DISPLAY_NAMES.get(subscription_type, subscription_type),
        "地域": params.get("region", Region.HANGZHOU),
        "文件系统类型": file_system_type_map.get(
            params.get("file_system_type", "standard"),
            params.get("file_system_type", "standard")
        ),
        "存储类型": storage_type_map.get(
            params.get("storage_type", "Performance"),
            params.get("storage_type", "Performance")
        ),
        "协议类型": protocol_type_map.get(
            params.get("protocol_type", "NFS"),
            params.get("protocol_type", "NFS")
        ),
        "存储容量": f"{params.get('capacity', 100)}GB",
    }
    
    data_transfer = params.get("data_transfer", 0)
    if data_transfer > 0:
        summary["数据传出流量"] = f"{data_transfer}GB"
    
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate parameters."""
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
    
    # Custom cross-field validation
    capacity = params.get("capacity", 100)
    file_system_type = params.get("file_system_type", "standard")
    
    # Check capacity upper limit based on file system type
    if file_system_type == "extreme" and capacity > 256 * 1024:  # 256TB
        errors.append(f"极速型 NAS 容量不能超过 256TB，当前值: {capacity}GB")
    
    # Check capacity lower limit for CPFS
    if file_system_type == "cpfs" and capacity < 4096:  # 4TB = 4096GB
        errors.append(f"CPFS capacity 最小为 4096GB (4TB)，当前值: {capacity}GB")
    
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
