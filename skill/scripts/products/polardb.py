"""
PolarDB (云原生关系型数据库) product definition.

ProductCode: polardb
ProductType: "online" (必需)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""


def build_modules(params):
    """Build PolarDB pricing module list."""
    db_type = params.get("db_type", "MySQL")
    db_version = params.get("db_version", "8.0")
    pay_type = params.get("pay_type", "Serverless")

    modules = []

    if pay_type == "Serverless":
        # Serverless 版按实际使用计费
        modules.extend([
            {
                "module_code": "DBType",
                "config": f"DBType:{db_type}",
                "price_type": "Hour",
            },
            {
                "module_code": "DBVersion",
                "config": f"DBVersion:{db_version}",
                "price_type": "Hour",
            },
            {
                "module_code": "PayType",
                "config": "PayType:Serverless",
                "price_type": "Hour",
            },
        ])
    else:
        # 包年包月/按量付费
        db_node_class = params.get("db_node_class", "polar.mysql.xlarge")
        db_node_count = params.get("db_node_count", 2)
        storage_size = params.get("storage_size", 100)

        modules.extend([
            {
                "module_code": "DBType",
                "config": f"DBType:{db_type}",
                "price_type": "Hour",
            },
            {
                "module_code": "DBVersion",
                "config": f"DBVersion:{db_version}",
                "price_type": "Hour",
            },
            {
                "module_code": "DBNodeClass",
                "config": f"DBNodeClass:{db_node_class}",
                "price_type": "Hour",
            },
            {
                "module_code": "DBNodeCount",
                "config": f"DBNodeCount:{db_node_count}",
                "price_type": "Hour",
            },
            {
                "module_code": "Storage",
                "config": f"Storage:{storage_size}",
                "price_type": "Hour",
            },
        ])

    return modules


def format_summary(params):
    """Build human-readable config summary."""
    pay_type = params.get("pay_type", "Serverless")

    pay_type_map = {
        "Serverless": "Serverless 版",
        "PrePaid": "包年包月",
        "PostPaid": "按量付费",
    }

    summary = {
        "数据库": f"{params.get('db_type', 'MySQL')} {params.get('db_version', '8.0')}",
        "计费方式": pay_type_map.get(pay_type, pay_type),
    }

    if pay_type != "Serverless":
        summary["节点规格"] = params.get("db_node_class", "polar.mysql.xlarge")
        summary["节点数量"] = str(params.get("db_node_count", 2))
        summary["存储"] = f"{params.get('storage_size', 100)} GB"

    return summary


def validate(params):
    """Validate PolarDB parameters."""
    errors = []

    db_type = params.get("db_type", "MySQL")
    valid_types = ["MySQL", "PostgreSQL", "Oracle"]
    if db_type not in valid_types:
        errors.append(f"数据库类型必须是: {', '.join(valid_types)}")

    db_version = params.get("db_version", "8.0")
    if db_type == "MySQL":
        valid_versions = ["5.6", "5.7", "8.0"]
        if db_version not in valid_versions:
            errors.append(f"MySQL 版本必须是: {', '.join(valid_versions)}")
    elif db_type == "PostgreSQL":
        valid_versions = ["11", "12", "13", "14", "15"]
        if db_version not in valid_versions:
            errors.append(f"PostgreSQL 版本必须是: {', '.join(valid_versions)}")

    pay_type = params.get("pay_type", "Serverless")
    valid_pay_types = ["Serverless", "PrePaid", "PostPaid"]
    if pay_type not in valid_pay_types:
        errors.append(f"计费方式必须是: {', '.join(valid_pay_types)}")

    if pay_type != "Serverless":
        db_node_count = params.get("db_node_count", 2)
        if db_node_count and int(db_node_count) < 2:
            errors.append("PolarDB 至少需要 2 个节点（1 主 1 只读）")

        storage_size = params.get("storage_size", 100)
        if storage_size and int(storage_size) < 20:
            errors.append("存储大小不能小于 20GB")

    return errors


PRODUCT = {
    "code": "polardb",
    "name": "PolarDB",
    "display_name": "PolarDB 云原生数据库",
    "product_type": "online",
    "category": "database",
    "params": [
        {
            "name": "db_type",
            "label": "数据库类型",
            "type": "string",
            "required": False,
            "default": "MySQL",
            "choices": ["MySQL", "PostgreSQL", "Oracle"],
            "description": "数据库引擎类型",
            "examples": ["MySQL", "PostgreSQL"],
        },
        {
            "name": "db_version",
            "label": "数据库版本",
            "type": "string",
            "required": False,
            "default": "8.0",
            "choices": None,
            "description": "数据库版本。MySQL: 5.6/5.7/8.0; PostgreSQL: 11/12/13/14/15",
            "examples": ["8.0", "5.7", "14"],
        },
        {
            "name": "pay_type",
            "label": "计费方式",
            "type": "string",
            "required": False,
            "default": "Serverless",
            "choices": ["Serverless", "PrePaid", "PostPaid"],
            "description": "Serverless (Serverless版), PrePaid (包年包月), PostPaid (按量付费)",
            "examples": ["Serverless", "PrePaid"],
        },
        {
            "name": "db_node_class",
            "label": "节点规格",
            "type": "string",
            "required": False,
            "default": "polar.mysql.xlarge",
            "choices": None,
            "description": "计算节点规格，如 polar.mysql.xlarge (4C8G)",
            "examples": [
                "polar.mysql.xlarge",
                "polar.mysql.2xlarge",
                "polar.mysql.4xlarge",
            ],
        },
        {
            "name": "db_node_count",
            "label": "节点数量",
            "type": "int",
            "required": False,
            "default": 2,
            "choices": None,
            "description": "计算节点数量（至少 2 个：1 主 1 只读）",
            "examples": [2, 3, 4],
        },
        {
            "name": "storage_size",
            "label": "存储大小",
            "type": "int",
            "required": False,
            "default": 100,
            "choices": None,
            "description": "存储大小 (GB)，最小 20GB",
            "examples": [100, 500, 1000],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
