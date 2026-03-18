"""
ECS (Elastic Compute Service) product definition.

ProductCode: ecs
ProductType: None (ECS does not require ProductType)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Dict, List, Optional, Union

from ai_friendly.constants import Region, Category, DiskType
from ai_friendly.types import ParamDef, ModuleSpec


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
        {
            "module_code": "SystemDisk",
            "config": (
                f"SystemDisk.Category:{system_disk_category},"
                f"SystemDisk.Size:{system_disk_size}"
            ),
            "price_type": "Hour",
        },
    ]

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
    summary = {
        "实例规格": params["instance_type"],
        "操作系统": params.get("image_os", "linux"),
        "系统盘": f"{params.get('system_disk_category', DiskType.ESSD)} {params.get('system_disk_size', 40)}GB",
    }
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
            "name": "system_disk_category",
            "label": "系统盘类型",
            "type": "string",
            "required": False,
            "default": DiskType.ESSD,
            "choices": [DiskType.ESSD, DiskType.SSD, DiskType.EFFICIENCY],
            "description": "系统盘类型：cloud_essd (ESSD), cloud_ssd (SSD), cloud_efficiency (高效云盘)",
            "examples": [DiskType.ESSD],
        },
        {
            "name": "system_disk_size",
            "label": "系统盘大小",
            "type": "int",
            "required": False,
            "default": 40,
            "choices": None,
            "description": "系统盘大小 (GB)，最小 20GB",
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
}
