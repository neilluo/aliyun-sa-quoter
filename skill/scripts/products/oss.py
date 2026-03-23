"""
OSS (Object Storage Service) product definition.

ProductCode: oss
ProductType: "oss"
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
Note: OSS module codes should be verified via DescribePricingModule.
"""

from typing import Any, Dict, List, Optional

from ai_friendly.constants import Category

# 存储类型和冗余类型映射到 BSS 模块
MODULE_MAP = {
    ("Standard", "LRS"): "Storage",  # 标准-本地冗余
    ("Standard", "ZRS"): "StorageZRSXC",  # 标准-同城冗余
    ("IA", "LRS"): "IaOrAchieveChargedStorage",  # 低频-本地冗余
    ("IA", "ZRS"): "ChargedDatasizeZRS",  # 低频-同城冗余
    ("Archive", "LRS"): "IaOrAchieveChargedStorage",  # 归档-本地冗余
    ("Archive", "ZRS"): "ChargedDataSizeArcZRS",  # 归档-同城冗余
}

# 存储类型映射
STORAGE_TYPE_MAP = {
    "Standard": "StandardStorage",  # 标准型存储容量
    "IA": "IAStorage",  # 低频访问型存储容量
    "Archive": "ArchiveStorage",  # 归档型存储容量
}

# 资源包价格表（中国内地）
# 价格单位: 元
RESOURCE_PACKAGES = {
    "standard_lrs": {  # 标准-本地冗余
        "40GB": {"month": 4.98, "half_year": None, "year": 9},
        "100GB": {"month": 11, "half_year": 54.78, "year": 99},
        "500GB": {"month": 54, "half_year": 268.92, "year": 486},
        "1TB": {"month": 111, "half_year": 552.78, "year": 999},
    },
    "standard_zrs": {  # 标准-同城冗余
        "100GB": {"month": 14, "half_year": 69.72, "year": 126},
        "500GB": {"month": 68, "half_year": 338.64, "year": 612},
    },
}


def _get_package_key(storage_class: str, redundancy_type: str) -> Optional[str]:
    """获取资源包键名。"""
    key_map = {
        ("Standard", "LRS"): "standard_lrs",
        ("Standard", "ZRS"): "standard_zrs",
    }
    return key_map.get((storage_class, redundancy_type))


def _get_package_size(capacity: int) -> str:
    """根据容量获取资源包规格。"""
    if capacity <= 40:
        return "40GB"
    elif capacity <= 100:
        return "100GB"
    elif capacity <= 500:
        return "500GB"
    else:
        return "1TB"


def _get_package_price(storage_class: str, redundancy_type: str, capacity: int, duration: int) -> Optional[float]:
    """获取资源包价格。
    
    Args:
        storage_class: 存储类型
        redundancy_type: 冗余类型
        capacity: 容量 (GB)
        duration: 时长 (月)
    
    Returns:
        价格 (元), 如果找不到价格返回 None
    """
    package_key = _get_package_key(storage_class, redundancy_type)
    if not package_key:
        return None
    
    packages = RESOURCE_PACKAGES.get(package_key)
    if not packages:
        return None
    
    # 找到合适的规格
    package_size = _get_package_size(capacity)
    package = packages.get(package_size)
    if not package:
        return None
    
    # 根据时长选择价格
    if duration <= 1:
        return package["month"]
    elif duration == 6:
        # 6个月，使用半年价格
        return package.get("half_year") or package["month"] * 6
    elif duration == 12:
        # 1年，使用年价格（买9送3）
        return package.get("year") or package["month"] * 12
    elif duration < 6:
        # 2-5个月，按包月价格计算
        return package["month"] * duration
    elif duration < 12:
        # 7-11个月，半年价格 + 剩余月份包月价格
        half_year_price = package.get("half_year") or package["month"] * 6
        return half_year_price + package["month"] * (duration - 6)
    else:
        # 1年以上，年价格 + 剩余月份
        year_price = package.get("year") or package["month"] * 12
        return year_price * (duration // 12) + package["month"] * (duration % 12)


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build OSS pricing module list."""
    billing = params.get("billing", "payAsYouGo")

    # 如果是包年包月，使用本地价格表
    if billing == "subscription":
        # 返回特殊标记，表示使用本地计算
        return [{"module_code": "__LOCAL_CALCULATION__"}]

    capacity = params.get("capacity", 100)
    storage_class = params.get("storage_class", "Standard")
    redundancy_type = params.get("redundancy_type", "LRS")

    # 根据存储类型和冗余类型选择模块
    module_code = MODULE_MAP.get((storage_class, redundancy_type), "Storage")
    
    # 获取存储类型值
    storage_type = STORAGE_TYPE_MAP.get(storage_class, "StandardStorage")

    # StorageZRSXC 模块的配置格式与其他模块不同
    if module_code == "StorageZRSXC":
        config = f"StorageZRSXC:{capacity},StorageType:{storage_type}"
    else:
        config = f"Storage:{capacity},StorageType:{storage_type}"

    modules = [
        {
            "module_code": module_code,
            "config": config,
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
    redundancy_map = {
        "LRS": "本地冗余",
        "ZRS": "同城冗余",
    }
    storage_class = params.get("storage_class", "Standard")
    redundancy_type = params.get("redundancy_type", "LRS")
    billing = params.get("billing", "payAsYouGo")
    
    summary = {
        "存储类型": class_map.get(storage_class, storage_class),
        "冗余类型": redundancy_map.get(redundancy_type, redundancy_type),
        "容量": f"{params.get('capacity', 100)} GB",
        "计费方式": "包年包月" if billing == "subscription" else "按量付费",
    }
    
    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate OSS parameters."""
    errors = []
    
    storage_class = params.get("storage_class", "Standard")
    redundancy_type = params.get("redundancy_type", "LRS")
    
    if storage_class not in ["Standard", "IA", "Archive"]:
        errors.append(f"无效的存储类型: {storage_class}，可选: Standard, IA, Archive")
    
    if redundancy_type not in ["LRS", "ZRS"]:
        errors.append(f"无效的冗余类型: {redundancy_type}，可选: LRS, ZRS")
    
    # 检查是否有支持的资源包
    billing = params.get("billing", "payAsYouGo")
    if billing == "subscription":
        package_key = _get_package_key(storage_class, redundancy_type)
        if not package_key:
            errors.append(f"当前存储类型和冗余类型组合暂不支持资源包: {storage_class}-{redundancy_type}")
    
    return errors


def calculate_price(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate OSS resource package price locally.
    
    Args:
        params: OSS parameters including storage_class, redundancy_type, capacity, duration
    
    Returns:
        Dict with price calculation result
    """
    storage_class = params.get("storage_class", "Standard")
    redundancy_type = params.get("redundancy_type", "LRS")
    capacity = params.get("capacity", 100)
    duration = params.get("duration", 1)
    
    price = _get_package_price(storage_class, redundancy_type, capacity, duration)
    
    if price is None:
        raise ValueError(f"无法找到 {storage_class}-{redundancy_type} {capacity}GB 的资源包价格")
    
    return {
        "original_amount": price,
        "discount_amount": 0,
        "trade_amount": price,
        "currency": "CNY",
        "storage_class": storage_class,
        "redundancy_type": redundancy_type,
        "capacity": capacity,
        "duration": duration,
        "module_details": [
            {
                "module_code": "StoragePackage",
                "module_name": "存储资源包",
                "original_cost": price,
                "discount_cost": 0,
                "invest_total_cost": 0,
                "cost_after_discount": price,
            }
        ],
    }


PRODUCT = {
    "code": "oss",
    "name": "OSS",
    "display_name": "OSS 对象存储",
    "product_type": "",
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
            "name": "redundancy_type",
            "label": "冗余类型",
            "type": "string",
            "required": False,
            "default": "ZRS",
            "choices": ["LRS", "ZRS"],
            "description": "LRS (本地冗余) / ZRS (同城冗余)",
            "examples": ["LRS", "ZRS"],
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
    "validate": validate,
}
