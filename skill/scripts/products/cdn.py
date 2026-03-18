"""
CDN (Content Delivery Network) product definition.

ProductCode: cdn
ProductType: "cdn"
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
Note: CDN module codes should be verified via DescribePricingModule.
"""

from typing import Any, Dict, List, Optional, Union

from ai_friendly.constants import Region, Category, DiskType
from ai_friendly.types import ParamDef, ModuleSpec


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build CDN pricing module list."""
    traffic_package = params.get("traffic_package", 100)

    modules = [
        {
            "module_code": "TrafficPackage",
            "config": f"TrafficPackage:{traffic_package}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    return {
        "流量包": f"{params.get('traffic_package', 100)} GB",
    }


PRODUCT = {
    "code": "cdn",
    "name": "CDN",
    "display_name": "CDN 内容分发",
    "product_type": "cdn",
    "category": Category.CDN_SECURITY,
    "params": [
        {
            "name": "traffic_package",
            "label": "流量包",
            "type": "int",
            "required": False,
            "default": 100,
            "choices": None,
            "description": "CDN 流量包大小 (GB)",
            "examples": [100, 500, 1000],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": None,
}
