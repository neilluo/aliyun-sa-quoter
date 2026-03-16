"""
MongoDB (云数据库 MongoDB 版) product definition.

ProductCode: dds
ProductType: "" (empty)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""


def build_modules(params):
    """Build MongoDB pricing module list.
    
    Based on BSS API response, MongoDB has:
    - DBInstanceClass (Configs: ReplicationFactor, ReadonlyReplicas, DBInstanceClass)
    - DBInstanceStorage (Configs: StorageType, ReplicationFactor, ReadonlyReplicas)
    """
    instance_class = params.get("instance_class", "dds.mongo.mid")
    storage_size = params.get("storage_size", 100)
    replication_factor = params.get("replication_factor", 3)
    region = params.get("region", "cn-hangzhou")

    modules = [
        {
            "module_code": "DBInstanceClass",
            "config": f"Region:{region},ReplicationFactor:{replication_factor},ReadonlyReplicas:0,DBInstanceClass:{instance_class}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceStorage",
            "config": f"Region:{region},StorageType:cloud_essd,ReplicationFactor:{replication_factor},ReadonlyReplicas:0",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params):
    """Build human-readable config summary."""
    engine_map = {
        "WiredTiger": "WiredTiger",
        "RocksDB": "RocksDB",
    }

    return {
        "版本": params.get("engine_version", "4.4"),
        "存储引擎": engine_map.get(params.get("storage_engine", "WiredTiger"), "WiredTiger"),
        "规格": params.get("instance_class", "dds.mongo.mid"),
        "存储": f"{params.get('storage_size', 100)} GB",
        "副本集": f"{params.get('replication_factor', 3)} 节点",
    }


def validate(params):
    """Validate MongoDB parameters."""
    errors = []

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


PRODUCT = {
    "code": "dds",
    "name": "MongoDB",
    "display_name": "云数据库 MongoDB 版",
    "product_type": "",
    "category": "database",
    "params": [
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
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
