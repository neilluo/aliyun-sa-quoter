"""
ECS (Elastic Compute Service) product definition.

ProductCode: ecs
ProductType: None (ECS does not require ProductType)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure scripts directory is importable for ecs_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_friendly.constants import Category, DiskType
from ecs_client import get_instance_price


def _extract_instance_family(instance_type: str) -> str:
    """Extract instance family from instance type, e.g. 'ecs.g7.xlarge' -> 'ecs.g7'."""
    parts = instance_type.split(".")
    if len(parts) >= 2:
        return ".".join(parts[:2])
    return instance_type


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build ECS pricing module list."""
    instance_type = params["instance_type"]
    image_os = params.get("image_os", "linux")
    system_disk_category = params.get("system_disk_category", DiskType.ESSD)
    system_disk_size = params.get("system_disk_size", 40)
    data_disk_category = params.get("data_disk_category")
    data_disk_size = params.get("data_disk_size", 0)
    internet_bandwidth = params.get("internet_bandwidth", 0)

    # Check if we should include system disk (default: False - exclude system disk)
    include_system_disk = params.get("include_system_disk", False)

    family = _extract_instance_family(instance_type)

    modules = [
        {
            "module_code": "InstanceType",
            "config": (
                f"InstanceType:{instance_type},"
                f"IoOptimized:IoOptimized,"
                f"ImageOs:{image_os},"
                f"InstanceTypeFamily:{family}"
            ),
            "price_type": "Hour",
        },
    ]

    # SystemDisk - only include if explicitly requested
    if include_system_disk:
        modules.append({
            "module_code": "SystemDisk",
            "config": (
                f"SystemDisk.Category:{system_disk_category},"
                f"SystemDisk.Size:{system_disk_size}"
            ),
            "price_type": "Hour",
        })

    if data_disk_size and int(data_disk_size) > 0:
        category = data_disk_category or system_disk_category
        modules.append({
            "module_code": "DataDisk",
            "config": (
                f"DataDisk.Category:{category},"
                f"DataDisk.Size:{data_disk_size}"
            ),
            "price_type": "Hour",
        })

    if internet_bandwidth and int(internet_bandwidth) > 0:
        modules.append({
            "module_code": "InternetMaxBandwidthOut",
            "config": (
                f"InternetMaxBandwidthOut:{internet_bandwidth},"
                f"InternetMaxBandwidthOut.IsFlowType:5,"
                f"NetworkType:1"
            ),
            "price_type": "Hour",
        })

    return modules


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    include_system_disk = params.get("include_system_disk", False)
    
    summary = {
        "实例规格": params["instance_type"],
        "操作系统": params.get("image_os", "linux"),
    }
    
    # Only show system disk if explicitly included
    if include_system_disk:
        summary["系统盘"] = f"{params.get('system_disk_category', DiskType.ESSD)} {params.get('system_disk_size', 40)}GB"
    
    data_disk_size = params.get("data_disk_size", 0)
    if data_disk_size and int(data_disk_size) > 0:
        cat = params.get("data_disk_category") or params.get("system_disk_category", DiskType.ESSD)
        summary["数据盘"] = f"{cat} {data_disk_size}GB"
    internet_bandwidth = params.get("internet_bandwidth", 0)
    if internet_bandwidth and int(internet_bandwidth) > 0:
        summary["公网带宽"] = f"{internet_bandwidth} Mbps"
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate ECS parameters."""
    errors = []
    data_disk_size = params.get("data_disk_size", 0)
    if data_disk_size and int(data_disk_size) > 0:
        if not params.get("data_disk_category") and not params.get("system_disk_category"):
            errors.append("添加数据盘时需要指定 data_disk_category 或 system_disk_category")

    system_disk_size = params.get("system_disk_size", 40)
    if system_disk_size and int(system_disk_size) < 20:
        errors.append("系统盘大小不能小于 20GB")

    return errors


def get_price(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query ECS instance price via ECS DescribePrice API.
    
    Returns dict matching BSS API format:
    {
        "original_amount": float,
        "discount_amount": float,
        "trade_amount": float,
        "currency": str,
        "module_details": [...]
    }
    """
    region = params.get("region", "cn-hangzhou")
    instance_type = params["instance_type"]
    image_os = params.get("image_os", "linux")
    system_disk_category = params.get("system_disk_category", DiskType.ESSD)
    system_disk_size = params.get("system_disk_size", 40)
    data_disk_category = params.get("data_disk_category")
    data_disk_size = params.get("data_disk_size", 0)
    internet_bandwidth = params.get("internet_bandwidth", 0)
    include_system_disk = params.get("include_system_disk", False)
    duration = params.get("duration", 1)
    
    # Call ECS API to get price
    result = get_instance_price(
        region=region,
        instance_type=instance_type,
        platform=image_os,
        system_disk_category=system_disk_category,
        system_disk_size=system_disk_size,
        period=duration,
        price_unit="Month",
        data_disk_category=data_disk_category,
        data_disk_size=data_disk_size,
        internet_max_bandwidth_out=internet_bandwidth,
    )
    
    # Build module details
    module_details = []
    
    # Instance type price
    instance_price = result["details"].get("instanceType", 0)
    module_details.append({
        "module_code": "InstanceType",
        "original_cost": instance_price,
        "discount_cost": 0,
        "invest_total_cost": 0,
        "cost_after_discount": instance_price,
    })
    
    # System disk price (if included)
    system_disk_price = 0
    if include_system_disk:
        system_disk_price = result["details"].get("SystemDisk", 0)
        module_details.append({
            "module_code": "SystemDisk",
            "original_cost": system_disk_price,
            "discount_cost": 0,
            "invest_total_cost": 0,
            "cost_after_discount": system_disk_price,
        })
    
    # Data disk price
    data_disk_price = result["details"].get("DataDisk", 0)
    if data_disk_price and int(data_disk_size) > 0:
        module_details.append({
            "module_code": "DataDisk",
            "original_cost": data_disk_price,
            "discount_cost": 0,
            "invest_total_cost": 0,
            "cost_after_discount": data_disk_price,
        })
    
    # Internet bandwidth price
    bandwidth_price = result["details"].get("InternetMaxBandwidthOut", 0)
    if bandwidth_price and int(internet_bandwidth) > 0:
        module_details.append({
            "module_code": "InternetMaxBandwidthOut",
            "original_cost": bandwidth_price,
            "discount_cost": 0,
            "invest_total_cost": 0,
            "cost_after_discount": bandwidth_price,
        })
    
    # Calculate total based on include_system_disk flag
    if include_system_disk:
        total_price = result["original_price"]
    else:
        # Only instance price (ECS API returns total including system disk)
        total_price = instance_price
    
    return {
        "original_amount": total_price,
        "discount_amount": 0,
        "trade_amount": total_price,
        "currency": result["currency"],
        "module_details": module_details,
    }


PRODUCT = {
    "code": "ecs",
    "name": "ECS",
    "display_name": "ECS 云服务器",
    "product_type": None,
    "category": Category.COMPUTE,
    "params": [
        {
            "name": "instance_type",
            "label": "实例规格",
            "type": "string",
            "required": True,
            "default": None,
            "choices": None,
            "description": "ECS 实例规格，如 ecs.g7.xlarge (4C16G), ecs.c7.large (2C4G)",
            "examples": ["ecs.g7.xlarge", "ecs.c7.large", "ecs.r7.2xlarge"],
        },
        {
            "name": "image_os",
            "label": "操作系统",
            "type": "string",
            "required": False,
            "default": "linux",
            "choices": ["linux", "windows"],
            "description": "操作系统类型",
            "examples": ["linux", "windows"],
        },
        {
            "name": "include_system_disk",
            "label": "包含系统盘",
            "type": "bool",
            "required": False,
            "default": False,
            "choices": None,
            "description": "是否将系统盘价格计入总价（默认 false，仅计算实例价格）",
            "examples": [False, True],
        },
        {
            "name": "system_disk_category",
            "label": "系统盘类型",
            "type": "string",
            "required": False,
            "default": DiskType.ESSD,
            "choices": [DiskType.ESSD, DiskType.SSD, DiskType.EFFICIENCY],
            "description": "系统盘类型：cloud_essd (ESSD), cloud_ssd (SSD), cloud_efficiency (高效云盘)。仅在 include_system_disk=true 时生效",
            "examples": [DiskType.ESSD],
        },
        {
            "name": "system_disk_size",
            "label": "系统盘大小",
            "type": "int",
            "required": False,
            "default": 40,
            "choices": None,
            "description": "系统盘大小 (GB)，最小 20GB。仅在 include_system_disk=true 时生效",
            "examples": [40, 100],
        },
        {
            "name": "data_disk_category",
            "label": "数据盘类型",
            "type": "string",
            "required": False,
            "default": None,
            "choices": [DiskType.ESSD, DiskType.SSD, DiskType.EFFICIENCY],
            "description": "数据盘类型，不填则继承系统盘类型",
            "examples": [DiskType.ESSD],
        },
        {
            "name": "data_disk_size",
            "label": "数据盘大小",
            "type": "int",
            "required": False,
            "default": 0,
            "choices": None,
            "description": "数据盘大小 (GB)，0 表示不添加数据盘",
            "examples": [0, 100, 500],
        },
        {
            "name": "internet_bandwidth",
            "label": "公网带宽",
            "type": "int",
            "required": False,
            "default": 0,
            "choices": None,
            "description": "公网带宽 (Mbps)，0 表示不添加公网带宽",
            "examples": [0, 5, 10],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
    "get_price": get_price,
}
