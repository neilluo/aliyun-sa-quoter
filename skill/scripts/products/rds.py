"""
RDS (Relational Database Service) product definition.

ProductCode: rds
ProductType: "rds" (standard), "bards" (Basic edition), "rords" (read-only)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""


def _get_product_type(params):
    """Determine ProductType based on RDS series.

    - Basic edition uses "bards"
    - Read-only instances use "rords"
    - Standard / HighAvailability / AlwaysOn use "rds"
    """
    series = params.get("series", "HighAvailability")
    if series == "Basic":
        return "bards"
    return "rds"


def build_modules(params):
    """Build RDS pricing module list."""
    engine = params["engine"]
    engine_version = params["engine_version"]
    series = params.get("series", "HighAvailability")
    instance_class = params["instance_class"]
    storage_type = params.get("storage_type", "local_ssd")
    storage_size = params.get("storage_size", 100)
    network_type = params.get("network_type", 1)

    modules = [
        {
            "module_code": "Engine",
            "config": f"Engine:{engine}",
            "price_type": "Hour",
        },
        {
            "module_code": "EngineVersion",
            "config": f"EngineVersion:{engine_version}",
            "price_type": "Hour",
        },
        {
            "module_code": "Series",
            "config": f"Series:{series}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceStorageType",
            "config": f"DBInstanceStorageType:{storage_type}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceStorage",
            "config": f"DBInstanceStorage:{storage_size}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBInstanceClass",
            "config": f"DBInstanceClass:{instance_class}",
            "price_type": "Hour",
        },
        {
            "module_code": "DBNetworkType",
            "config": f"DBNetworkType:{network_type}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params):
    """Build human-readable config summary."""
    return {
        "数据库引擎": f"{params['engine']} {params['engine_version']}",
        "系列": params.get("series", "HighAvailability"),
        "实例规格": params["instance_class"],
        "存储": f"{params.get('storage_type', 'local_ssd')} {params.get('storage_size', 100)}GB",
    }


def validate(params):
    """Validate RDS parameter combinations."""
    errors = []

    storage_type = params.get("storage_type", "local_ssd")
    series = params.get("series", "HighAvailability")

    # local_ssd only supports HighAvailability
    if storage_type == "local_ssd" and series != "HighAvailability":
        errors.append("local_ssd 存储类型仅支持 HighAvailability (高可用版) 系列")

    # storage_size must be multiple of 5
    storage_size = params.get("storage_size", 100)
    if storage_size and int(storage_size) % 5 != 0:
        errors.append("存储大小必须为 5 的倍数")

    # MSSQL does not support Basic series
    engine = params.get("engine", "mysql")
    if engine == "mssql" and series == "Basic":
        errors.append("SQL Server 不支持基础版 (Basic) 系列")

    return errors


PRODUCT = {
    "code": "rds",
    "name": "RDS",
    "display_name": "RDS 云数据库",
    "product_type": _get_product_type,
    "category": "database",
    "params": [
        {
            "name": "engine",
            "label": "数据库引擎",
            "type": "string",
            "required": True,
            "default": None,
            "choices": ["mysql", "postgresql", "mssql", "MariaDB"],
            "description": "数据库引擎类型",
            "examples": ["mysql", "postgresql"],
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
            "default": "local_ssd",
            "choices": ["local_ssd", "cloud_essd", "cloud_ssd"],
            "description": "存储类型。local_ssd 仅支持高可用版",
            "examples": ["local_ssd", "cloud_essd"],
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
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
