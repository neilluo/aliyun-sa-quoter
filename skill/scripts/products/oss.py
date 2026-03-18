"""
OSS (Object Storage Service) product definition.

ProductCode: oss
ProductType: "oss"
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
Note: OSS module codes should be verified via DescribePricingModule.
"""

from typing import Any, Dict, List, Optional, Union

from ai_friendly.constants import Region, Category, DiskType
from ai_friendly.types import ParamDef, ModuleSpec


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build OSS pricing module list."""
    capacity = params.get("capacity", 100)
    storage_class = params.get("storage_class", "Standard")

    modules = [
        {
            "module_code": "Capacity",
            "config": f"Capacity:{capacity},StorageClass:{storage_class}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    class_map = {
        "Standard": "标准存储",
        "IA": "低频访问",
        "Archive": "归档存储",
    }
    storage_class = params.get("storage_class", "Standard")
    return {
        "存储类型": class_map.get(storage_class, storage_class),
        "容量": f"{params.get('capacity', 100)} GB",
    }


PRODUCT = {
    "code": "oss",
    "name": "OSS",
    "display_name": "OSS 对象存储",
    "product_type": "oss",
    "category": Category.STORAGE,
    "params": [
        {
            "name": "storage_class",
            "label": "存储类型",
            "type": "string",
            "required": False,
            "default": "Standard",
            "choices": ["Standard", "IA", "Archive"],
            "description": "Standard (标准存储), IA (低频访问), Archive (归档存储)",
            "examples": ["Standard"],
        },
        {
            "name": "capacity",
            "label": "容量",
            "type": "int",
            "required": False,
            "default": 100,
            "choices": None,
            "description": "存储容量 (GB)",
            "examples": [100, 500, 1000],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": None,
}
