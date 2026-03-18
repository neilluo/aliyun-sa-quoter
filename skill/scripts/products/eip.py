"""
EIP (Elastic IP Address) product definition.

ProductCode: eip
ProductType: "eip"
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
Note: Alibaba Cloud API uses "Bindwidth" spelling (not "Bandwidth")
"""

from typing import Any, Dict, List

from ai_friendly.constants import Category


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build EIP pricing module list."""
    bandwidth = params.get("bandwidth", 5)
    internet_charge_type = params.get("internet_charge_type", "PayByTraffic")

    modules = [
        {
            "module_code": "Bindwidth",
            "config": f"Bindwidth:{bandwidth}",
            "price_type": "Hour",
        },
        {
            "module_code": "InternetChargeType",
            "config": f"InternetChargeType:{internet_charge_type}",
            "price_type": "Hour",
        },
    ]

    return modules


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    charge_type = params.get("internet_charge_type", "PayByTraffic")
    charge_text = "按流量" if charge_type == "PayByTraffic" else "按带宽"
    return {
        "带宽": f"{params.get('bandwidth', 5)} Mbps",
        "计费类型": charge_text,
    }


PRODUCT = {
    "code": "eip",
    "name": "EIP",
    "display_name": "EIP 弹性公网IP",
    "product_type": "eip",
    "category": Category.NETWORK,
    "params": [
        {
            "name": "bandwidth",
            "label": "带宽",
            "type": "int",
            "required": False,
            "default": 5,
            "choices": None,
            "description": "带宽 (Mbps)",
            "examples": [1, 5, 10, 100],
        },
        {
            "name": "internet_charge_type",
            "label": "计费类型",
            "type": "string",
            "required": False,
            "default": "PayByTraffic",
            "choices": ["PayByTraffic", "PayByBandwidth"],
            "description": "PayByTraffic (按流量), PayByBandwidth (按带宽)",
            "examples": ["PayByTraffic", "PayByBandwidth"],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": None,
}
