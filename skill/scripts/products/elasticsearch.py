"""
Elasticsearch product definition.

ProductCode: elasticsearch
ProductType: "elasticsearchpre" (Subscription), "elasticsearch" (PayAsYouGo)
API docs: https://help.aliyun.com/document_detail/170253.html

MVP Version: Support core data node and disk modules only.
"""


def _get_product_type(params):
    """Determine ProductType based on subscription type.
    
    - Subscription (包年包月) uses "elasticsearchpre"
    - PayAsYouGo (按量付费) uses "elasticsearch"
    """
    subscription_type = params.get("subscription_type", "Subscription")
    if subscription_type == "PayAsYouGo":
        return "elasticsearch"
    return "elasticsearchpre"


def build_modules(params):
    """Build Elasticsearch pricing module list.
    
    MVP version only includes:
    - NodeSpec: Data node specification
    - Disk: Data node storage
    
    Future extensions:
    - MasterNodeSpec: Dedicated master node
    - KibanaNodeSpec: Kibana node
    - WarmNodeSpec: Warm data node
    - ClientNodeSpec: Client node
    """
    region = params["region"]
    node_spec = params["node_spec"]
    node_amount = params["node_amount"]
    disk_type = params["disk_type"]
    disk_size = params["disk_size"]
    performance_level = params.get("performance_level", "PL1")

    modules = [
        {
            "module_code": "NodeSpec",
            "config": f"NodeSpec:{node_spec},Region:{region},NodeAmount:{node_amount}",
            "price_type": "Hour",
        },
        {
            "module_code": "Disk",
            "config": f"DataDiskType:{disk_type},PerformanceLevel:{performance_level},Region:{region},NodeAmount:{node_amount},Disk:{disk_size}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params):
    """Build human-readable config summary."""
    subscription_type = params.get("subscription_type", "Subscription")
    pricing_mode = "包年包月" if subscription_type == "Subscription" else "按量付费"
    
    return {
        "产品": "Elasticsearch",
        "付费模式": pricing_mode,
        "地域": params["region"],
        "数据节点规格": params["node_spec"],
        "数据节点数量": str(params["node_amount"]),
        "存储类型": params["disk_type"],
        "单节点存储": f"{params['disk_size']}GB",
    }


def validate(params):
    """Validate Elasticsearch parameter combinations."""
    errors = []

    # Validate node_amount range (typically 2-50 for production)
    node_amount = params.get("node_amount", 3)
    if node_amount < 2:
        errors.append("数据节点数量至少为 2 个（建议 3 个以上保证高可用）")
    if node_amount > 50:
        errors.append("数据节点数量不能超过 50 个")

    # Validate disk_size range (20-20480 GB)
    disk_size = params.get("disk_size", 20)
    if disk_size < 20:
        errors.append("单节点存储大小至少为 20GB")
    if disk_size > 20480:
        errors.append("单节点存储大小不能超过 20480GB")

    # ESSD disk requires performance level
    disk_type = params.get("disk_type", "cloud_ssd")
    performance_level = params.get("performance_level", "PL1")
    if disk_type == "cloud_essd" and not performance_level:
        errors.append("ESSD 云盘必须指定性能级别 (PL0/PL1/PL2/PL3)")

    return errors


# Node specification choices (common options)
# Format: elasticsearch.{instance_family}.{instance_size}
# g7 = general purpose, r7 = memory optimized, c7 = compute optimized
NODE_SPEC_CHOICES = [
    # General purpose (g7) - balanced CPU/memory
    "elasticsearch.g7.xlarge",    # 4C16G
    "elasticsearch.g7.2xlarge",   # 8C32G
    "elasticsearch.g7.4xlarge",   # 16C64G
    "elasticsearch.g7.8xlarge",   # 32C128G
    # Memory optimized (r7) - high memory ratio
    "elasticsearch.r7.xlarge",    # 4C32G
    "elasticsearch.r7.2xlarge",   # 8C64G
    "elasticsearch.r7.4xlarge",   # 16C128G
    # Compute optimized (c7) - high CPU ratio
    "elasticsearch.c7.xlarge",    # 4C8G
    "elasticsearch.c7.2xlarge",   # 8C16G
    "elasticsearch.c7.4xlarge",   # 16C32G
]


PRODUCT = {
    "code": "elasticsearch",
    "name": "Elasticsearch",
    "display_name": "Elasticsearch 检索分析服务",
    "product_type": _get_product_type,
    "category": "database",
    "params": [
        {
            "name": "region",
            "label": "地域",
            "type": "string",
            "required": True,
            "default": "cn-hangzhou",
            "choices": None,
            "description": "阿里云地域ID",
            "examples": ["cn-hangzhou", "cn-beijing", "cn-shanghai"],
        },
        {
            "name": "node_spec",
            "label": "数据节点规格",
            "type": "string",
            "required": True,
            "default": None,
            "choices": NODE_SPEC_CHOICES,
            "description": "Elasticsearch 数据节点规格，如 elasticsearch.g7.xlarge (4C16G)",
            "examples": ["elasticsearch.g7.xlarge", "elasticsearch.r7.2xlarge"],
        },
        {
            "name": "node_amount",
            "label": "数据节点数量",
            "type": "int",
            "required": True,
            "default": 3,
            "choices": None,
            "description": "数据节点数量，建议至少3个保证高可用，范围 2-50",
            "examples": [3, 5, 10],
        },
        {
            "name": "disk_type",
            "label": "存储类型",
            "type": "string",
            "required": True,
            "default": "cloud_ssd",
            "choices": ["cloud_ssd", "cloud_essd", "cloud_efficiency"],
            "description": "数据节点存储类型：cloud_ssd (SSD云盘), cloud_essd (ESSD云盘), cloud_efficiency (高效云盘)",
            "examples": ["cloud_ssd", "cloud_essd"],
        },
        {
            "name": "disk_size",
            "label": "单节点存储大小",
            "type": "int",
            "required": True,
            "default": 20,
            "choices": None,
            "description": "每个数据节点的存储大小，单位 GB，范围 20-20480",
            "examples": [20, 100, 500],
        },
        {
            "name": "performance_level",
            "label": "ESSD性能级别",
            "type": "string",
            "required": False,
            "default": "PL1",
            "choices": ["PL0", "PL1", "PL2", "PL3"],
            "description": "ESSD云盘性能级别，仅在使用 cloud_essd 时有效",
            "examples": ["PL1", "PL2"],
        },
        {
            "name": "subscription_type",
            "label": "付费类型",
            "type": "string",
            "required": False,
            "default": "Subscription",
            "choices": ["Subscription", "PayAsYouGo"],
            "description": "Subscription (包年包月) 或 PayAsYouGo (按量付费)",
            "examples": ["Subscription", "PayAsYouGo"],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
