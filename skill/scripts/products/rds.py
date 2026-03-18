"""RDS (Relational Database Service) product definition - ai_friendly format.

ProductCode: rds
ProductType: "rds" (standard), "bards" (Basic edition), "rords" (read-only)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Callable, Dict, List, Optional, Union

from framework.builders import ModuleBuilder
from framework.validators import ValidationRule, Validator
from ai_friendly.constants import Region, Category, DiskType, ProductType, Engine
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "rds"
NAME: str = "RDS"
DISPLAY_NAME: str = "RDS 云数据库"
CATEGORY: str = Category.DATABASE

# 动态 ProductType：根据系列切换
PRODUCT_TYPE: Optional[Union[str, Callable]] = lambda p: (
    ProductType.RDS_BASIC if p.get("series") == "Basic"
    else ProductType.RDS_READONLY if p.get("series") == "Readonly"
    else ProductType.RDS_STANDARD
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
        "name": "engine",
        "label": "数据库引擎",
        "type": "string",
        "required": True,
        "default": None,
        "choices": [Engine.MYSQL, Engine.POSTGRESQL, Engine.MSSQL, Engine.MARIADB],
        "description": "数据库引擎类型",
        "examples": [Engine.MYSQL, Engine.POSTGRESQL],
    },
    {
        "name": "engine_version",
        "label": "引擎版本",
        "type": "string",
        "required": True,
        "default": None,
        "choices": None,
        "description": "引擎版本号。MySQL: 5.7/8.0; PostgreSQL: 13.0/14.0/15.0; MSSQL: 2019_ent/2019_std",
        "examples": ["8.0", "5.7", "14.0"],
    },
    {
        "name": "series",
        "label": "系列",
        "type": "string",
        "required": False,
        "default": "HighAvailability",
        "choices": ["Basic", "HighAvailability", "AlwaysOn"],
        "description": "Basic (基础版), HighAvailability (高可用版), AlwaysOn (集群版)",
        "examples": ["HighAvailability"],
    },
    {
        "name": "instance_class",
        "label": "实例规格",
        "type": "string",
        "required": True,
        "default": None,
        "choices": None,
        "description": "RDS 实例规格，如 mysql.n2.medium.2c (2C4G)",
        "examples": ["mysql.n2.medium.2c", "mysql.n2.large.2c", "mysql.n4.medium.2c"],
    },
    {
        "name": "storage_type",
        "label": "存储类型",
        "type": "string",
        "required": False,
        "default": DiskType.LOCAL_SSD,
        "choices": [DiskType.LOCAL_SSD, DiskType.ESSD, DiskType.SSD],
        "description": "存储类型。local_ssd 仅支持高可用版",
        "examples": [DiskType.LOCAL_SSD, DiskType.ESSD],
    },
    {
        "name": "storage_size",
        "label": "存储大小",
        "type": "int",
        "required": False,
        "default": 100,
        "choices": None,
        "description": "存储大小 (GB)，必须为 5 的倍数",
        "examples": [100, 200, 500],
    },
    {
        "name": "network_type",
        "label": "网络类型",
        "type": "int",
        "required": False,
        "default": 1,
        "choices": [0, 1],
        "description": "0=经典网络, 1=VPC",
        "examples": [1],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

MODULES: List[ModuleSpec] = [
    {
        "module_code": "Engine",
        "config_template": "Engine:{engine}",
    },
    {
        "module_code": "EngineVersion",
        "config_template": "EngineVersion:{engine_version}",
    },
    {
        "module_code": "Series",
        "config_template": "Series:{series}",
    },
    {
        "module_code": "DBInstanceStorageType",
        "config_template": "DBInstanceStorageType:{storage_type}",
    },
    {
        "module_code": "DBInstanceStorage",
        "config_template": "DBInstanceStorage:{storage_size}",
    },
    {
        "module_code": "DBInstanceClass",
        "config_template": "DBInstanceClass:{instance_class}",
    },
    {
        "module_code": "DBNetworkType",
        "config_template": "DBNetworkType:{network_type}",
    },
]

DEFAULT_PRICE_TYPE: str = "Hour"


# =============================================================================
# VALIDATION SECTION
# =============================================================================

VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule(
        name="storage_size",
        label="存储大小",
        required=True,
        min_val=5,
        max_val=32000,
        custom_validator=lambda v, n, l: None if v % 5 == 0 else f"{l} ({n}) 的值 {v} 不是 5 的倍数",
        error_formatter=lambda r, v, t: (
            "存储大小至少为 5GB" if t == 'min_val'
            else "存储大小不能超过 32000GB" if t == 'max_val'
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
    # 设置默认值
    if "series" not in result:
        result["series"] = "HighAvailability"
    if "storage_type" not in result:
        result["storage_type"] = DiskType.LOCAL_SSD
    if "storage_size" not in result:
        result["storage_size"] = 100
    if "network_type" not in result:
        result["network_type"] = 1
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
    return {
        "产品": "RDS 云数据库",
        "地域": params.get("region", Region.HANGZHOU),
        "数据库引擎": f"{params['engine']} {params['engine_version']}",
        "系列": params.get("series", "HighAvailability"),
        "实例规格": params["instance_class"],
        "存储": f"{params.get('storage_type', DiskType.LOCAL_SSD)} {params.get('storage_size', 100)}GB",
    }


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate parameters."""
    errors = []
    
    # 自动验证 PARAMS 中的 choices 和必填
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
    
    # 自定义跨字段验证
    storage_type = params.get("storage_type", DiskType.LOCAL_SSD)
    series = params.get("series", "HighAvailability")
    engine = params.get("engine", Engine.MYSQL)
    
    # local_ssd only supports HighAvailability
    if storage_type == DiskType.LOCAL_SSD and series != "HighAvailability":
        errors.append("local_ssd 存储类型仅支持 HighAvailability (高可用版) 系列")
    
    # MSSQL does not support Basic series
    if engine == Engine.MSSQL and series == "Basic":
        errors.append("SQL Server 不支持基础版 (Basic) 系列")
    
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
