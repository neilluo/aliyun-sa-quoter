"""
SLB (Server Load Balancer) product definition.

ProductCode: slb
ProductType: "slb"
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Dict, List, Optional, Union

from ai_friendly.constants import Region, Category, DiskType
from ai_friendly.types import ParamDef, ModuleSpec


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build SLB pricing module list."""
    spec = params.get("spec", "slb.s3.large")
    internet_charge_type = params.get("internet_charge_type", 1)
    bandwidth = params.get("bandwidth", 0)

    modules = [
        {
            "module_code": "LoadBalancerSpec",
            "config": f"LoadBalancerSpec:{spec}",
            "price_type": "Hour",
        },
        {
            "module_code": "InternetTrafficOut",
            "config": f"InternetTrafficOut:{internet_charge_type}",
            "price_type": "Hour",
        },
        {
            "module_code": "InstanceRent",
            "config": "InstanceRent:1",
            "price_type": "Hour",
        },
    ]

    if int(internet_charge_type) == 0 and bandwidth and int(bandwidth) > 0:
        modules.append({
            "module_code": "Bandwidth",
            "config": f"Bandwidth:{bandwidth}",
            "price_type": "Hour",
        })

    return modules


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    charge_type = params.get("internet_charge_type", 1)
    charge_text = "按流量" if int(charge_type) == 1 else "按带宽"
    summary = {
        "规格": params.get("spec", "slb.s3.large"),
        "计费类型": charge_text,
    }
    if int(charge_type) == 0:
        summary["带宽"] = f"{params.get('bandwidth', 0)} Kbps"
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate SLB parameters."""
    errors = []
    charge_type = params.get("internet_charge_type", 1)
    bandwidth = params.get("bandwidth", 0)
    if int(charge_type) == 0 and (not bandwidth or int(bandwidth) <= 0):
        errors.append("按带宽计费时必须指定 bandwidth (Kbps)")
    return errors


PRODUCT = {
    "code": "slb",
    "name": "SLB",
    "display_name": "SLB 负载均衡",
    "product_type": "slb",
    "category": Category.NETWORK,
    "params": [
        {
            "name": "spec",
            "label": "规格",
            "type": "string",
            "required": False,
            "default": "slb.s3.large",
            "choices": ["slb.s0.share", "slb.s1.small", "slb.s2.small", "slb.s2.medium",
                        "slb.s3.small", "slb.s3.medium", "slb.s3.large"],
            "description": "SLB 规格。slb.s0.share=共享型, slb.s1.small=简约型I, slb.s3.large=超强型I",
            "examples": ["slb.s3.large", "slb.s2.medium"],
        },
        {
            "name": "internet_charge_type",
            "label": "流量计费类型",
            "type": "int",
            "required": False,
            "default": 1,
            "choices": [0, 1],
            "description": "1=按流量计费, 0=按带宽计费",
            "examples": [1],
        },
        {
            "name": "bandwidth",
            "label": "带宽",
            "type": "int",
            "required": False,
            "default": 0,
            "choices": None,
            "description": "带宽 (Kbps)，仅按带宽计费时需要",
            "examples": [1000, 5000],
        },
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
