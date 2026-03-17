"""
RocketMQ 5.0 (消息队列 RocketMQ 5.0) product definition.

ProductCode: ons
ProductType: ons_rmqsub_public_cn (Subscription), ons_rmqpost_public_cn (PayAsYouGo)
API docs: https://help.aliyun.com/document_detail/170253.html
"""


def _get_product_type(params):
    """Determine ProductType based on subscription type.

    - Subscription (包年包月) uses "ons_rmqsub_public_cn"
    - PayAsYouGo (按量付费) uses "ons_rmqpost_public_cn"
    """
    subscription_type = params.get("subscription_type", "Subscription")
    if subscription_type == "PayAsYouGo":
        return "ons_rmqpost_public_cn"
    return "ons_rmqsub_public_cn"


def _get_valid_process_specs(chip_type):
    """根据 chip_type 返回有效的 msg_process_spec 列表."""
    if chip_type == "arm":
        return [
            "rmq.su.2xlarge",
            "rmq.su.4xlarge",
            "rmq.su.6xlarge",
        ]
    else:  # x86
        return [
            "rmq.su.2xlarge",
            "rmq.su.4xlarge",
            "rmq.su.6xlarge",
            "rmq.su.8xlarge",
        ]


def build_modules(params):
    """Build RocketMQ pricing module list.

    Args:
        params: 用户参数字典

    Returns:
        list: 模块列表，每个模块包含 module_code, config, price_type
    """
    region = params["region"]
    chip_type = params["chip_type"]
    msg_process_spec = params["msg_process_spec"]
    msg_store_spec = params["msg_store_spec"]
    series_type = params["series_type"]
    flow_out_bandwidth = params.get("flow_out_bandwidth", 0)
    topic_paid = params.get("topic_paid", 0)

    modules = [
        {
            "module_code": "msg_process_spec",
            "config": f"chip_type:{chip_type},region:{region},msg_process_spec:{msg_process_spec}",
            "price_type": "Hour",
        },
        {
            "module_code": "msg_store_spec",
            "config": f"msg_store_spec:{msg_store_spec},region:{region}",
            "price_type": "Hour",
        },
    ]

    # 公网带宽模块（仅当 flow_out_bandwidth > 0 时添加）
    if flow_out_bandwidth > 0:
        flow_out_type = params.get("flow_out_type", "payByTraffic")
        modules.append({
            "module_code": "flow_out_bandwidth",
            "config": f"flow_out_bandwidth:{flow_out_bandwidth},flow_out_type:{flow_out_type},region:{region}",
            "price_type": "Hour",
        })

    # 付费Topic模块（仅当 topic_paid > 0 时添加）
    if topic_paid > 0:
        modules.append({
            "module_code": "topic_paid",
            "config": f"region:{region},series_type:{series_type}",
            "price_type": "Hour",
        })

    return modules


def format_summary(params):
    """Build human-readable config summary.

    Args:
        params: 用户参数字典

    Returns:
        dict: 配置摘要
    """
    subscription_type = params.get("subscription_type", "Subscription")
    chip_type = params["chip_type"]
    series_type = params["series_type"]

    # 系列类型中文映射
    series_type_map = {
        "standard": "标准版",
        "professional": "专业版",
    }

    # 公网计费类型中文映射
    flow_out_type_map = {
        "payByTraffic": "按流量计费",
        "fixedBandwidth": "固定带宽",
    }

    summary = {
        "产品": "消息队列 RocketMQ 5.0",
        "付费模式": "包年包月" if subscription_type == "Subscription" else "按量付费",
        "地域": params["region"],
        "架构类型": chip_type.upper(),
        "系列类型": series_type_map.get(series_type, series_type),
        "消息收发规格": params["msg_process_spec"],
        "消息存储规格": params["msg_store_spec"],
    }

    # 公网带宽
    flow_out_bandwidth = params.get("flow_out_bandwidth", 0)
    if flow_out_bandwidth > 0:
        flow_out_type = params.get("flow_out_type", "payByTraffic")
        summary["公网带宽"] = f"{flow_out_bandwidth}MB/s"
        summary["公网计费"] = flow_out_type_map.get(flow_out_type, flow_out_type)

    # 付费Topic
    topic_paid = params.get("topic_paid", 0)
    if topic_paid > 0:
        summary["付费Topic数"] = str(topic_paid)

    return summary


def validate(params):
    """Validate RocketMQ parameter combinations.

    Args:
        params: 用户参数字典

    Returns:
        list: 错误信息列表，空列表表示校验通过
    """
    errors = []

    # 必填参数检查
    required_fields = ["region", "chip_type", "msg_process_spec", "msg_store_spec", "series_type"]
    for field in required_fields:
        if field not in params or params[field] is None:
            errors.append(f"缺少必填参数: {field}")

    if errors:
        return errors

    # chip_type 有效性检查
    valid_chip_types = ["x86", "arm"]
    if params["chip_type"] not in valid_chip_types:
        errors.append(f"无效的 chip_type: {params['chip_type']}，可选值: {', '.join(valid_chip_types)}")

    # series_type 有效性检查
    valid_series_types = ["standard", "professional"]
    if params["series_type"] not in valid_series_types:
        errors.append(f"无效的 series_type: {params['series_type']}，可选值: {', '.join(valid_series_types)}")

    # msg_process_spec 有效性检查（与 chip_type 关联）
    chip_type = params.get("chip_type", "x86")
    msg_process_spec = params["msg_process_spec"]
    valid_process_specs = _get_valid_process_specs(chip_type)
    if msg_process_spec not in valid_process_specs:
        errors.append(f"msg_process_spec '{msg_process_spec}' 与 chip_type '{chip_type}' 不匹配，可选值: {', '.join(valid_process_specs)}")

    # msg_store_spec 有效性检查
    valid_store_specs = [
        "rmq.ssu.2xlarge",
        "rmq.ssu.4xlarge",
        "rmq.ssu.6xlarge",
        "rmq.ssu.8xlarge",
    ]
    if params["msg_store_spec"] not in valid_store_specs:
        errors.append(f"无效的 msg_store_spec: {params['msg_store_spec']}，可选值: {', '.join(valid_store_specs)}")

    # flow_out_bandwidth 范围检查
    flow_out_bandwidth = params.get("flow_out_bandwidth", 0)
    if flow_out_bandwidth < 0 or flow_out_bandwidth > 600:
        errors.append(f"flow_out_bandwidth 必须在 0-600 之间，当前值: {flow_out_bandwidth}")

    # flow_out_type 有效性检查（如果提供了公网带宽）
    if flow_out_bandwidth > 0:
        flow_out_type = params.get("flow_out_type", "payByTraffic")
        valid_flow_types = ["payByTraffic", "fixedBandwidth"]
        if flow_out_type not in valid_flow_types:
            errors.append(f"无效的 flow_out_type: {flow_out_type}，可选值: {', '.join(valid_flow_types)}")

    # topic_paid 范围检查
    topic_paid = params.get("topic_paid", 0)
    if topic_paid < 0:
        errors.append(f"topic_paid 必须为非负数，当前值: {topic_paid}")

    return errors


PRODUCT = {
    "code": "ons",
    "name": "RocketMQ",
    "display_name": "消息队列 RocketMQ 5.0",
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
            "name": "chip_type",
            "label": "架构类型",
            "type": "string",
            "required": True,
            "default": "x86",
            "choices": ["x86", "arm"],
            "description": "芯片架构类型: x86 或 arm",
            "examples": ["x86", "arm"],
        },
        {
            "name": "msg_process_spec",
            "label": "消息收发计算规格",
            "type": "string",
            "required": True,
            "default": "rmq.su.2xlarge",
            "choices": None,
            "description": "消息收发计算规格，如 rmq.su.2xlarge (8核16G)",
            "examples": ["rmq.su.2xlarge", "rmq.su.4xlarge"],
        },
        {
            "name": "msg_store_spec",
            "label": "消息存储规格",
            "type": "string",
            "required": True,
            "default": "rmq.ssu.2xlarge",
            "choices": ["rmq.ssu.2xlarge", "rmq.ssu.4xlarge", "rmq.ssu.6xlarge", "rmq.ssu.8xlarge"],
            "description": "消息存储规格，如 rmq.ssu.2xlarge (8核16G)",
            "examples": ["rmq.ssu.2xlarge", "rmq.ssu.4xlarge"],
        },
        {
            "name": "series_type",
            "label": "系列类型",
            "type": "string",
            "required": True,
            "default": "standard",
            "choices": ["standard", "professional"],
            "description": "系列类型: standard(标准版), professional(专业版)",
            "examples": ["standard", "professional"],
        },
        {
            "name": "flow_out_bandwidth",
            "label": "公网带宽",
            "type": "int",
            "required": False,
            "default": 0,
            "choices": None,
            "description": "公网带宽(MB/s)，范围 0-600，0表示不开通",
            "examples": [0, 100, 200],
        },
        {
            "name": "flow_out_type",
            "label": "公网计费类型",
            "type": "string",
            "required": False,
            "default": "payByTraffic",
            "choices": ["payByTraffic", "fixedBandwidth"],
            "description": "公网计费类型: payByTraffic(按流量), fixedBandwidth(固定带宽)",
            "examples": ["payByTraffic", "fixedBandwidth"],
        },
        {
            "name": "topic_paid",
            "label": "付费Topic数量",
            "type": "int",
            "required": False,
            "default": 0,
            "choices": None,
            "description": "付费Topic数量，≥0",
            "examples": [0, 10, 50],
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