"""
NAS (File Storage NAS) product definition.

ProductCode: nas
ProductType: naspost
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
Note: NAS primarily supports PayAsYouGo billing mode.
"""


def _get_product_type(params):
    """Get ProductType for NAS based on subscription type.

    Args:
        params: User parameter dict containing subscription_type

    Returns:
        str: ProductType string for NAS API calls
    """
    return "naspost"


def build_modules(params):
    """Build NAS pricing module list.

    Args:
        params: User parameter dict

    Returns:
        list: Module list, each containing module_code, config, price_type
    """
    region = params["region"]
    file_system_type = params["file_system_type"]
    storage_type = params["storage_type"]
    protocol_type = params["protocol_type"]
    capacity = params["capacity"]
    data_transfer = params.get("data_transfer", 0)

    modules = [
        {
            "module_code": "FileSystem",
            "config": f"Region:{region},FileSystemType:{file_system_type},StorageType:{storage_type},ProtocolType:{protocol_type}",
            "price_type": "Hour",
        },
        {
            "module_code": "Capacity",
            "config": f"Region:{region},Capacity:{capacity}",
            "price_type": "Hour",
        },
    ]

    # Add DataTransfer module only when data_transfer > 0
    if data_transfer > 0:
        modules.append({
            "module_code": "DataTransfer",
            "config": f"Region:{region},DataTransfer:{data_transfer}",
            "price_type": "Hour",
        })

    return modules


def format_summary(params):
    """Build human-readable config summary.

    Args:
        params: User parameter dict

    Returns:
        dict: Configuration summary
    """
    subscription_type = params.get("subscription_type", "PayAsYouGo")
    file_system_type = params["file_system_type"]
    storage_type = params["storage_type"]
    protocol_type = params["protocol_type"]

    # File system type Chinese mapping
    file_system_type_map = {
        "standard": "通用型",
        "extreme": "极速型",
        "cpfs": "CPFS",
    }

    # Storage type Chinese mapping
    storage_type_map = {
        "Performance": "性能型",
        "Capacity": "容量型",
    }

    # Protocol type Chinese mapping
    protocol_type_map = {
        "NFS": "NFS",
        "SMB": "SMB",
    }

    summary = {
        "产品": "文件存储 NAS",
        "付费模式": "包年包月" if subscription_type == "Subscription" else "按量付费",
        "地域": params["region"],
        "文件系统类型": file_system_type_map.get(file_system_type, file_system_type),
        "存储类型": storage_type_map.get(storage_type, storage_type),
        "协议类型": protocol_type_map.get(protocol_type, protocol_type),
        "存储容量": f"{params['capacity']}GB",
    }

    data_transfer = params.get("data_transfer", 0)
    if data_transfer > 0:
        summary["数据传出流量"] = f"{data_transfer}GB"

    return summary


def validate(params):
    """Validate NAS parameter combinations.

    Args:
        params: User parameter dict

    Returns:
        list: Error message list, empty list means validation passed
    """
    errors = []

    # Required fields check
    required_fields = ["region", "file_system_type", "storage_type", "protocol_type", "capacity"]
    for field in required_fields:
        if field not in params or params[field] is None:
            errors.append(f"缺少必填参数: {field}")

    if errors:
        return errors

    # file_system_type validity check
    valid_file_system_types = ["standard", "extreme", "cpfs"]
    if params["file_system_type"] not in valid_file_system_types:
        errors.append(f"无效的 file_system_type: {params['file_system_type']}，可选值: {', '.join(valid_file_system_types)}")

    # storage_type validity check
    valid_storage_types = ["Performance", "Capacity"]
    if params["storage_type"] not in valid_storage_types:
        errors.append(f"无效的 storage_type: {params['storage_type']}，可选值: {', '.join(valid_storage_types)}")

    # protocol_type validity check
    valid_protocol_types = ["NFS", "SMB"]
    if params["protocol_type"] not in valid_protocol_types:
        errors.append(f"无效的 protocol_type: {params['protocol_type']}，可选值: {', '.join(valid_protocol_types)}")

    # capacity range check
    capacity = params.get("capacity", 100)
    file_system_type = params.get("file_system_type", "standard")

    if capacity < 100:
        errors.append(f"capacity 最小为 100GB，当前值: {capacity}")

    # Check capacity upper limit based on file system type
    if file_system_type == "extreme" and capacity > 256 * 1024:  # 256TB
        errors.append(f"极速型 NAS 容量不能超过 256TB，当前值: {capacity}GB")

    # Check capacity lower limit for CPFS
    if file_system_type == "cpfs" and capacity < 4096:  # 4TB = 4096GB
        errors.append(f"CPFS capacity 最小为 4096GB (4TB)，当前值: {capacity}GB")

    # data_transfer range check
    data_transfer = params.get("data_transfer", 0)
    if data_transfer < 0:
        errors.append(f"data_transfer 必须为非负数，当前值: {data_transfer}")

    return errors


PRODUCT = {
    "code": "nas",
    "name": "NAS",
    "display_name": "文件存储 NAS",
    "product_type": _get_product_type,
    "category": "storage",
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
            "name": "file_system_type",
            "label": "文件系统类型",
            "type": "string",
            "required": True,
            "default": "standard",
            "choices": ["standard", "extreme", "cpfs"],
            "description": "文件系统类型: standard(通用型), extreme(极速型), cpfs(并行文件系统)",
            "examples": ["standard", "extreme"],
        },
        {
            "name": "storage_type",
            "label": "存储类型",
            "type": "string",
            "required": True,
            "default": "Performance",
            "choices": ["Performance", "Capacity"],
            "description": "存储类型: Performance(性能型), Capacity(容量型)",
            "examples": ["Performance", "Capacity"],
        },
        {
            "name": "protocol_type",
            "label": "协议类型",
            "type": "string",
            "required": True,
            "default": "NFS",
            "choices": ["NFS", "SMB"],
            "description": "协议类型: NFS(Linux/Unix), SMB(Windows)",
            "examples": ["NFS", "SMB"],
        },
        {
            "name": "capacity",
            "label": "存储容量",
            "type": "int",
            "required": True,
            "default": 100,
            "choices": None,
            "description": "存储容量(GB)，最小100GB，不同文件系统类型有不同上限",
            "examples": [100, 1000, 10000],
        },
        {
            "name": "data_transfer",
            "label": "数据传出流量",
            "type": "int",
            "required": False,
            "default": 0,
            "choices": None,
            "description": "数据传出流量(GB)，≥0",
            "examples": [0, 100, 1000],
        },
        {
            "name": "subscription_type",
            "label": "付费类型",
            "type": "string",
            "required": False,
            "default": "PayAsYouGo",
            "choices": ["Subscription", "PayAsYouGo"],
            "description": "Subscription(包年包月) 或 PayAsYouGo(按量付费)。注意：NAS主要支持按量付费",
            "examples": ["PayAsYouGo"],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
