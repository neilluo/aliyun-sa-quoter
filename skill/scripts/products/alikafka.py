"""
Kafka (消息队列 Kafka) product definition.

ProductCode: alikafka
ProductType: alikafka_pre (Subscription), alikafka_post (PayAsYouGo)
API docs: https://help.aliyun.com/document_detail/170253.html
"""


def _get_product_type(params):
    """Determine ProductType based on subscription type.

    - Subscription (包年包月) uses "alikafka_pre"
    - PayAsYouGo (按量付费) uses "alikafka_post"
    """
    subscription_type = params.get("subscription_type", "Subscription")
    if subscription_type == "PayAsYouGo":
        return "alikafka_post"
    return "alikafka_pre"


def _get_valid_io_specs(spec_type):
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


def build_modules(params):
    """Build Kafka pricing module list."""
    region = params["region"]
    spec_type = params["spec_type"]
    partition_num = params["partition_num"]
    topic_quota = params["topic_quota"]
    disk_type = params["disk_type"]
    disk_size = params["disk_size"]
    eip_max = params.get("eip_max", 0)
    io_max_spec = params.get("io_max_spec")

    # 如果没有指定 io_max_spec，根据 spec_type 使用默认值
    if not io_max_spec:
        if spec_type == "professionalForHighRead":
            io_max_spec = "alikafka.hr.2xlarge"
        else:
            io_max_spec = "alikafka.hw.2xlarge"

    modules = [
        {
            "module_code": "PartitionNum",
            "config": f"PartitionNum:{partition_num},SpecType:{spec_type},RegionId:{region}",
            "price_type": "Hour",
        },
        {
            "module_code": "TopicQuota",
            "config": f"PartitionNum:{partition_num},TopicQuota:{topic_quota},RegionId:{region}",
            "price_type": "Hour",
        },
        {
            "module_code": "IoMaxSpec",
            "config": f"SpecType:{spec_type},IoMaxSpec:{io_max_spec},RegionId:{region}",
            "price_type": "Hour",
        },
        {
            "module_code": "DiskSize",
            "config": f"DiskType:{disk_type},DiskSize:{disk_size},RegionId:{region}",
            "price_type": "Hour",
        },
    ]

    # 公网流量模块（仅当 eip_max > 0 时添加）
    if eip_max > 0:
        modules.append({
            "module_code": "EipMax",
            "config": f"EipMax:{eip_max},RegionId:{region}",
            "price_type": "Hour",
        })

    return modules


def format_summary(params):
    """Build human-readable config summary."""
    subscription_type = params.get("subscription_type", "Subscription")
    spec_type = params["spec_type"]

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

    summary = {
        "产品": "消息队列 Kafka",
        "付费模式": "包年包月" if subscription_type == "Subscription" else "按量付费",
        "地域": params["region"],
        "规格类型": spec_type_map.get(spec_type, spec_type),
        "分区数": str(params["partition_num"]),
        "Topic配额": str(params["topic_quota"]),
        "磁盘类型": disk_type_map.get(str(params["disk_type"]), params["disk_type"]),
        "磁盘容量": f"{params['disk_size']}GB",
        "流量规格": params.get("io_max_spec", "自动选择"),
    }

    eip_max = params.get("eip_max", 0)
    if eip_max > 0:
        summary["公网流量峰值"] = f"{eip_max}MB/s"

    return summary


def validate(params):
    """Validate Kafka parameter combinations."""
    errors = []

    # 必填参数检查
    required_fields = ["region", "spec_type", "partition_num", "topic_quota", "disk_type", "disk_size"]
    for field in required_fields:
        if field not in params or params[field] is None:
            errors.append(f"缺少必填参数: {field}")

    if errors:
        return errors

    # spec_type 有效性检查
    valid_spec_types = ["normal", "professional", "professionalForHighRead"]
    if params["spec_type"] not in valid_spec_types:
        errors.append(f"无效的 spec_type: {params['spec_type']}，可选值: {', '.join(valid_spec_types)}")

    # partition_num 范围检查
    partition_num = params.get("partition_num", 100)
    if partition_num < 0 or partition_num > 40000:
        errors.append(f"partition_num 必须在 0-40000 之间，当前值: {partition_num}")

    # topic_quota 范围检查
    topic_quota = params.get("topic_quota", 50)
    if topic_quota < 1 or topic_quota > 9999:
        errors.append(f"topic_quota 必须在 1-9999 之间，当前值: {topic_quota}")

    # disk_type 有效性检查
    valid_disk_types = ["0", "1", "5", "6", 0, 1, 5, 6]
    if params["disk_type"] not in valid_disk_types:
        errors.append(f"无效的 disk_type: {params['disk_type']}，可选值: 0(高效云盘), 1(SSD), 5(ESSD_PL0), 6(ESSD_PL1)")

    # disk_size 范围检查
    disk_size = params.get("disk_size", 500)
    if disk_size < 100:
        errors.append(f"disk_size 最小为 100GB，当前值: {disk_size}")
    if disk_size > 99999999999:
        errors.append(f"disk_size 超出最大值限制")

    # eip_max 范围检查
    eip_max = params.get("eip_max", 0)
    if eip_max < 0 or eip_max > 2500:
        errors.append(f"eip_max 必须在 0-2500 之间，当前值: {eip_max}")

    # io_max_spec 有效性检查（如果提供）
    io_max_spec = params.get("io_max_spec")
    if io_max_spec:
        spec_type = params.get("spec_type", "normal")
        valid_io_specs = _get_valid_io_specs(spec_type)
        if io_max_spec not in valid_io_specs:
            errors.append(f"io_max_spec '{io_max_spec}' 与 spec_type '{spec_type}' 不匹配，可选值: {', '.join(valid_io_specs)}")

    return errors


PRODUCT = {
    "code": "alikafka",
    "name": "Kafka",
    "display_name": "消息队列 Kafka",
    "product_type": _get_product_type,
    "category": "middleware",
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
            "default": "Subscription",
            "choices": ["Subscription", "PayAsYouGo"],
            "description": "Subscription(包年包月) 或 PayAsYouGo(按量付费)",
            "examples": ["Subscription", "PayAsYouGo"],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}