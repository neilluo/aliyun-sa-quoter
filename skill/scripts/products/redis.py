"""
Redis (云数据库 Redis 版) product definition.

ProductCode: redisa
ProductType: "" (empty)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""


def _get_product_type(params):
    """Redis uses empty ProductType."""
    return ""


def build_modules(params):
    """Build Redis pricing module list.
    
    Based on BSS API response, Redis only has InstanceClass module.
    The Config format should include Region and InstanceClass.
    """
    instance_class = params.get("instance_class", "redis.master.small.default")
    region = params.get("region", "cn-hangzhou")

    modules = [
        {
            "module_code": "InstanceClass",
            "config": f"Region:{region},InstanceClass:{instance_class}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params):
    """Build human-readable config summary."""
    edition = params.get("edition", "community")
    architecture = params.get("architecture", "standard")

    edition_map = {
        "community": "社区版",
        "enterprise": "企业版 (Tair)",
    }

    arch_map = {
        "standard": "标准架构",
        "cluster": "集群架构",
        "rwsplit": "读写分离架构",
    }

    summary = {
        "版本": edition_map.get(edition, edition),
        "架构": arch_map.get(architecture, architecture),
        "规格": params.get("instance_class", "redis.master.small.default"),
    }

    if architecture == "cluster":
        summary["分片数"] = str(params.get("shard_count", 1))

    return summary


def validate(params):
    """Validate Redis parameters."""
    errors = []

    edition = params.get("edition", "community")
    valid_editions = ["community", "enterprise"]
    if edition not in valid_editions:
        errors.append(f"版本必须是: {', '.join(valid_editions)}")

    architecture = params.get("architecture", "standard")
    valid_archs = ["standard", "cluster", "rwsplit"]
    if architecture not in valid_archs:
        errors.append(f"架构必须是: {', '.join(valid_archs)}")

    # 集群架构需要分片数
    if architecture == "cluster":
        shard_count = params.get("shard_count", 1)
        if shard_count and int(shard_count) < 2:
            errors.append("集群架构至少需要 2 个分片")

    return errors


PRODUCT = {
    "code": "redisa",
    "name": "Redis",
    "display_name": "云数据库 Redis 版",
    "product_type": "",
    "category": "database",
    "params": [
        {
            "name": "edition",
            "label": "版本",
            "type": "string",
            "required": False,
            "default": "community",
            "choices": ["community", "enterprise"],
            "description": "community (社区版), enterprise (企业版 Tair)",
            "examples": ["community", "enterprise"],
        },
        {
            "name": "architecture",
            "label": "架构",
            "type": "string",
            "required": False,
            "default": "standard",
            "choices": ["standard", "cluster", "rwsplit"],
            "description": "standard (标准架构), cluster (集群架构), rwsplit (读写分离)",
            "examples": ["standard", "cluster"],
        },
        {
            "name": "instance_class",
            "label": "实例规格",
            "type": "string",
            "required": False,
            "default": "redis.master.small.default",
            "choices": None,
            "description": "Redis 实例规格，如 redis.master.small.default (1GB)",
            "examples": [
                "redis.master.small.default",
                "redis.master.mid.default",
                "redis.master.large.default",
                "redis.master.2xlarge.default",
            ],
        },
        {
            "name": "shard_count",
            "label": "分片数",
            "type": "int",
            "required": False,
            "default": 1,
            "choices": None,
            "description": "集群架构分片数量（仅集群架构需要）",
            "examples": [2, 4, 8],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
