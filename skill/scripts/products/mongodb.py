"""MongoDB (云数据库 MongoDB 版) product definition.

ProductCode: dds
ProductType: "" (empty)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Dict, List, Optional

from framework.builders import ModuleBuilder
from ai_friendly.constants import Category, DiskType, Region
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "dds"
NAME: str = "MongoDB"
DISPLAY_NAME: str = "云数据库 MongoDB 版"
CATEGORY: str = Category.DATABASE
PRODUCT_TYPE: Optional[str] = ""

DEFAULT_PRICE_TYPE: str = "Hour"


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
        "name": "engine_version",
        "label": "引擎版本",
        "type": "string",
        "required": False,
        "default": "4.4",
        "choices": ["4.0", "4.2", "4.4", "5.0", "6.0"],
        "description": "MongoDB 引擎版本",
        "examples": ["4.4", "5.0", "6.0"],
    },
    {
        "name": "storage_engine",
        "label": "存储引擎",
        "type": "string",
        "required": False,
        "default": "WiredTiger",
        "choices": ["WiredTiger", "RocksDB"],
        "description": "存储引擎类型",
        "examples": ["WiredTiger", "RocksDB"],
    },
    {
        "name": "instance_class",
        "label": "实例规格",
        "type": "string",
        "required": False,
        "default": "dds.mongo.mid",
        "choices": None,
        "description": "MongoDB 实例规格，如 dds.mongo.mid (2C4G)",
        "examples": ["dds.mongo.mid", "dds.mongo.large", "dds.mongo.xlarge"],
    },
    {
        "name": "storage_size",
        "label": "存储大小",
        "type": "int",
        "required": False,
        "default": 100,
        "choices": None,
        "description": "存储大小 (GB)，最小 10GB",
        "examples": [100, 500, 1000],
    },
    {
        "name": "replication_factor",
        "label": "副本集节点数",
        "type": "int",
        "required": False,
        "default": 3,
        "choices": [1, 3, 5, 7],
        "description": "副本集节点数量",
        "examples": [1, 3, 5],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

MODULES: List[ModuleSpec] = [
    {
        "module_code": "DBInstanceClass",
        "config_template": "Region:{region},ReplicationFactor:{replication_factor},ReadonlyReplicas:0,DBInstanceClass:{instance_class}",
    },
    {
        "module_code": "DBInstanceStorage",
        "config_template": "Region:{region},StorageType:{storage_type},ReplicationFactor:{replication_factor},ReadonlyReplicas:0",
    },
]


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)
    # Set default values
    result.setdefault("region", Region.HANGZHOU)
    result.setdefault("instance_class", "dds.mongo.mid")
    result.setdefault("storage_size", 100)
    result.setdefault("replication_factor", 3)
    result.setdefault("storage_type", DiskType.ESSD)
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
    engine_map = {
        "WiredTiger": "WiredTiger",
        "RocksDB": "RocksDB",
    }

    return {
        "产品": DISPLAY_NAME,
        "地域": params.get("region", Region.HANGZHOU),
        "版本": params.get("engine_version", "4.4"),
        "存储引擎": engine_map.get(params.get("storage_engine", "WiredTiger"), "WiredTiger"),
        "规格": params.get("instance_class", "dds.mongo.mid"),
        "存储": f"{params.get('storage_size', 100)} GB",
        "副本集": f"{params.get('replication_factor', 3)} 节点",
    }


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate MongoDB parameters."""
    errors = []

    # Validate required fields presence
    for param in PARAMS:
        name = param["name"]
        value = params.get(name)
        if param.get("required") and value is None:
            errors.append(f"缺少必填参数: {param['label']} ({name})")

    engine_version = params.get("engine_version", "4.4")
    valid_versions = ["4.0", "4.2", "4.4", "5.0", "6.0"]
    if engine_version not in valid_versions:
        errors.append(f"引擎版本必须是: {', '.join(valid_versions)}")

    storage_engine = params.get("storage_engine", "WiredTiger")
    valid_engines = ["WiredTiger", "RocksDB"]
    if storage_engine not in valid_engines:
        errors.append(f"存储引擎必须是: {', '.join(valid_engines)}")

    storage_size = params.get("storage_size", 100)
    if storage_size and int(storage_size) < 10:
        errors.append("存储大小不能小于 10GB")

    replication_factor = params.get("replication_factor", 3)
    valid_factors = [1, 3, 5, 7]
    if replication_factor not in valid_factors:
        errors.append(f"副本集节点数必须是: {', '.join(map(str, valid_factors))}")

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
# AI 验证命令
# =============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

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
