"""
Redis (云数据库 Redis 版) product definition.

ProductCode: redisa
ProductType: "" (empty)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Dict, List, Optional, Union

from ai_friendly.constants import Region, Category, DiskType, Architecture, Edition
from ai_friendly.types import ParamDef, ModuleSpec


def _get_product_type(params: Dict[str, Any]) -> str:
    """Redis uses empty ProductType.

    Args:
        params: 用户参数字典

    Returns:
        str: 空字符串（Redis 不需要 ProductType）
    """
    return ""


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build Redis pricing module list.

    Based on BSS API response, Redis only has InstanceClass module.
    The Config format should include Region and InstanceClass.

    Args:
        params: 用户参数字典，包含 instance_class, region 等参数

    Returns:
        list: 模块列表，每个模块包含 module_code, config, price_type
    """
    instance_class = params.get("instance_class", "redis.master.small.default")
    region = params.get("region", Region.HANGZHOU)

    modules = [
        {
            "module_code": "InstanceClass",
            "config": f"Region:{region},InstanceClass:{instance_class}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary.

    Args:
        params: 用户参数字典

    Returns:
        dict: 配置摘要字典，包含版本、架构、规格等信息
    """
    edition = params.get("edition", Edition.COMMUNITY)
    architecture = params.get("architecture", Architecture.STANDARD)

    edition_map = {
        Edition.COMMUNITY: "社区版",
        Edition.ENTERPRISE: "企业版 (Tair)",
    }

    arch_map = {
        Architecture.STANDARD: "标准架构",
        Architecture.CLUSTER: "集群架构",
        Architecture.RWSPLIT: "读写分离架构",
    }

    summary = {
        "版本": edition_map.get(edition, edition),
        "架构": arch_map.get(architecture, architecture),
        "规格": params.get("instance_class", "redis.master.small.default"),
    }

    if architecture == Architecture.CLUSTER:
        summary["分片数"] = str(params.get("shard_count", 1))

    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate Redis parameters.

    Args:
        params: 用户参数字典

    Returns:
        list: 错误信息列表（空列表表示验证通过）
    """
    errors = []

    edition = params.get("edition", Edition.COMMUNITY)
    valid_editions = Edition.ALL
    if edition not in valid_editions:
        errors.append(f"版本必须是: {', '.join(valid_editions)}")

    architecture = params.get("architecture", Architecture.STANDARD)
    valid_archs = Architecture.ALL
    if architecture not in valid_archs:
        errors.append(f"架构必须是: {', '.join(valid_archs)}")

    # 集群架构需要分片数
    if architecture == Architecture.CLUSTER:
        shard_count = params.get("shard_count", 1)
        if shard_count and int(shard_count) < 2:
            errors.append("集群架构至少需要 2 个分片")

    return errors


PRODUCT = {
    "code": "redisa",
    "name": "Redis",
    "display_name": "云数据库 Redis 版",
    "product_type": _get_product_type,
    "category": Category.DATABASE,
    "params": [
        {
            "name": "edition",
            "label": "版本",
            "type": "string",
            "required": False,
            "default": Edition.COMMUNITY,
            "choices": Edition.ALL,
            "description": "community (社区版), enterprise (企业版 Tair)",
            "examples": [Edition.COMMUNITY, Edition.ENTERPRISE],
        },
        {
            "name": "architecture",
            "label": "架构",
            "type": "string",
            "required": False,
            "default": Architecture.STANDARD,
            "choices": Architecture.ALL,
            "description": "standard (标准架构), cluster (集群架构), rwsplit (读写分离)",
            "examples": [Architecture.STANDARD, Architecture.CLUSTER],
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
