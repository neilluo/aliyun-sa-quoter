"""WAF (Web Application Firewall) product definition - ai_friendly format.

ProductCode: waf
ProductType: waf_v3prepaid_public_cn (subscription) / waf_v2_public_cn (payasyougo)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""

from typing import Any, Callable, Dict, List, Optional, Union

from framework.builders import ModuleBuilder
from ai_friendly.constants import (
    Region, Category, BillingType, ProductType, PriceType
)
from ai_friendly.types import ParamDef, ModuleSpec


# =============================================================================
# CONFIG SECTION
# =============================================================================

CODE: str = "waf"
NAME: str = "WAF"
DISPLAY_NAME: str = "Web应用防火墙"
CATEGORY: str = Category.CDN_SECURITY


def _get_product_type(params: Dict[str, Any]) -> Optional[str]:
    """Determine ProductType based on billing mode.

    BSS API uses "waf" for both subscription and pay-as-you-go.
    """
    return "waf"


PRODUCT_TYPE: Optional[Union[str, Callable]] = _get_product_type


# =============================================================================
# PARAMS SECTION
# =============================================================================

PARAMS: List[ParamDef] = [
    {
        "name": "region",
        "label": "地域",
        "type": "string",
        "required": False,
        "default": Region.HANGZHOU,
        "choices": [
            Region.HANGZHOU, Region.SHANGHAI, Region.BEIJING, Region.SHENZHEN,
            Region.QINGDAO, Region.ZHANGJIAKOU, Region.HONGKONG,
            Region.SINGAPORE, Region.TOKYO, Region.SILICON_VALLEY,
            Region.VIRGINIA,
        ],
        "description": "地域 ID",
        "examples": [Region.HANGZHOU, Region.BEIJING],
    },
    {
        "name": "billing_mode",
        "label": "计费模式",
        "type": "string",
        "required": False,
        "default": BillingType.SUBSCRIPTION,
        "choices": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
        "description": "计费模式: Subscription(包年包月), PayAsYouGo(按量付费)",
        "examples": [BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO],
    },
    # 包年包月参数
    {
        "name": "package_code",
        "label": "版本",
        "type": "string",
        "required": False,
        "default": None,
        "choices": ["version_3", "version_4", "version_5"],
        "description": "版本: version_3(高级版), version_4(企业版), version_5(旗舰版)",
        "examples": ["version_4"],
    },
    {
        "name": "qps_package",
        "label": "QPS扩展包",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "QPS扩展包数量",
        "examples": [10],
    },
    {
        "name": "ext_domain_package",
        "label": "域名扩展包",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "域名扩展包数量",
        "examples": [5],
    },
    {
        "name": "bot_web",
        "label": "Bot Web防护",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": [0, 1],
        "description": "是否启用Bot Web防护: 0=否, 1=是",
        "examples": [1],
    },
    {
        "name": "bot_app",
        "label": "Bot APP防护",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": [0, 1],
        "description": "是否启用Bot APP防护: 0=否, 1=是",
        "examples": [1],
    },
    {
        "name": "apisec",
        "label": "API安全",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": [0, 1],
        "description": "是否启用API安全防护: 0=否, 1=是",
        "examples": [1],
    },
    {
        "name": "domain_vip",
        "label": "独享IP数量",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "独享IP数量",
        "examples": [2],
    },
    {
        "name": "log_storage",
        "label": "日志存储容量",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "日志存储容量(GB)",
        "examples": [100],
    },
    {
        "name": "waf_gslb",
        "label": "智能负载均衡",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": [0, 1],
        "description": "是否启用智能负载均衡: 0=否, 1=是",
        "examples": [1],
    },
    {
        "name": "hybrid_cloud_node",
        "label": "混合云节点数",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "多云/混合云WAF扩展节点数",
        "examples": [2],
    },
    {
        "name": "blue_teaming",
        "label": "重保场景",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": [0, 1],
        "description": "是否启用重保场景: 0=否, 1=是",
        "examples": [1],
    },
    {
        "name": "spike_throttle",
        "label": "洪峰限流",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "洪峰限流配置",
        "examples": [100],
    },
    {
        "name": "elastic_qps",
        "label": "弹性QPS",
        "type": "int",
        "required": False,
        "default": 0,
        "choices": None,
        "description": "弹性后付费QPS",
        "examples": [1000],
    },
    # 按量付费参数
    {
        "name": "secu",
        "label": "SeCU",
        "type": "int",
        "required": False,
        "default": None,
        "choices": None,
        "description": "SeCU(安全能力单元)数量，按量付费模式下必填",
        "examples": [100],
    },
]


# =============================================================================
# MODULES SECTION
# =============================================================================

# 包年包月模块定义 (简化版 - 只保留核心 PackageCode)
_SUBSCRIPTION_MODULES: List[ModuleSpec] = [
    {
        "module_code": "PackageCode",
        "config_template": "Region:{region},PackageCode:{package_code}",
    },
]

# 按量付费模块定义
_PAY_AS_YOU_GO_MODULES: List[ModuleSpec] = [
    {
        "module_code": "SeCU",
        "config_template": "SeCU:{secu},Region:{region}",
    },
]

DEFAULT_PRICE_TYPE: str = PriceType.MONTH

# 模块列表（供验证器检查，实际使用 _SUBSCRIPTION_MODULES 和 _PAY_AS_YOU_GO_MODULES）
MODULES: List[ModuleSpec] = _SUBSCRIPTION_MODULES + _PAY_AS_YOU_GO_MODULES


# =============================================================================
# IMPLEMENTATION SECTION
# =============================================================================

def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess parameters before building modules."""
    result = dict(params)

    # Set defaults
    if "region" not in result:
        result["region"] = Region.HANGZHOU
    if "billing_mode" not in result:
        result["billing_mode"] = BillingType.SUBSCRIPTION

    # Ensure numeric fields are integers
    for key in ["qps_package", "ext_domain_package", "domain_vip", "log_storage",
                "hybrid_cloud_node", "spike_throttle", "elastic_qps", "secu",
                "bot_web", "bot_app", "apisec", "waf_gslb", "blue_teaming"]:
        if key in result and result[key] is not None:
            result[key] = int(result[key])

    return result


def build_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build BSS module list."""
    p = _prepare_params(params)
    billing_mode = p.get("billing_mode", BillingType.SUBSCRIPTION)

    if billing_mode == BillingType.SUBSCRIPTION:
        return _build_subscription_modules(p)
    else:
        return _build_pay_as_you_go_modules(p)


def _build_subscription_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build subscription (包年包月) modules."""
    builder = ModuleBuilder(default_price_type=PriceType.MONTH)

    # Add bot_web, bot_app, apisec to params for condition evaluation
    p = dict(params)
    p["bot_web"] = 1 if p.get("bot_web", 0) == 1 else 0
    p["bot_app"] = 1 if p.get("bot_app", 0) == 1 else 0
    p["apisec"] = 1 if p.get("apisec", 0) == 1 else 0

    for spec in _SUBSCRIPTION_MODULES:
        condition = spec.get("condition")
        price_type = spec.get("price_type")

        if condition is not None:
            builder.add_conditional(
                spec["module_code"],
                spec["config_template"],
                condition,
                price_type,
            )
        else:
            builder.add(
                spec["module_code"],
                spec["config_template"],
                price_type,
            )

    return builder.build(p)


def _build_pay_as_you_go_modules(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build pay-as-you-go (按量付费) modules."""
    builder = ModuleBuilder(default_price_type=PriceType.HOUR)

    for spec in _PAY_AS_YOU_GO_MODULES:
        builder.add(
            spec["module_code"],
            spec["config_template"],
            spec.get("price_type"),
        )

    return builder.build(params)


def format_summary(params: Dict[str, Any]) -> Dict[str, str]:
    """Build human-readable config summary."""
    billing_mode = params.get("billing_mode", BillingType.SUBSCRIPTION)
    region = params.get("region", Region.HANGZHOU)

    summary: Dict[str, str] = {
        "产品": DISPLAY_NAME,
        "地域": region,
    }

    if billing_mode == BillingType.SUBSCRIPTION:
        package_code = params.get("package_code", "version_3")
        version_map = {
            "version_3": "高级版",
            "version_4": "企业版",
            "version_5": "旗舰版",
        }
        summary["版本"] = version_map.get(package_code, package_code)
        summary["计费模式"] = "包年包月"

        # 扩展功能
        extensions = []
        if params.get("qps_package", 0) > 0:
            extensions.append(f"QPS扩展({params['qps_package']})")
        if params.get("ext_domain_package", 0) > 0:
            extensions.append(f"域名扩展({params['ext_domain_package']})")
        if params.get("domain_vip", 0) > 0:
            extensions.append(f"独享IP({params['domain_vip']})")
        if params.get("log_storage", 0) > 0:
            extensions.append(f"日志存储({params['log_storage']}GB)")
        if params.get("hybrid_cloud_node", 0) > 0:
            extensions.append(f"混合云节点({params['hybrid_cloud_node']})")
        if params.get("spike_throttle", 0) > 0:
            extensions.append(f"洪峰限流({params['spike_throttle']})")
        if params.get("elastic_qps", 0) > 0:
            extensions.append(f"弹性QPS({params['elastic_qps']})")

        # 安全功能
        security_features = []
        if params.get("bot_web", 0) == 1:
            security_features.append("Bot-Web")
        if params.get("bot_app", 0) == 1:
            security_features.append("Bot-App")
        if params.get("apisec", 0) == 1:
            security_features.append("API安全")
        if params.get("waf_gslb", 0) == 1:
            security_features.append("智能负载均衡")
        if params.get("blue_teaming", 0) == 1:
            security_features.append("重保场景")

        if extensions:
            summary["扩展包"] = ", ".join(extensions)
        if security_features:
            summary["安全功能"] = ", ".join(security_features)
    else:
        summary["计费模式"] = "按量付费"
        summary["SeCU"] = str(params.get("secu", 1))

    return summary


def validate(params: Dict[str, Any]) -> List[str]:
    """Validate WAF parameters."""
    errors = []

    # Validate billing_mode
    billing_mode = params.get("billing_mode")
    if not billing_mode:
        errors.append("billing_mode 是必填参数，可选值: Subscription, PayAsYouGo")
    elif billing_mode not in (BillingType.SUBSCRIPTION, BillingType.PAY_AS_YOU_GO):
        errors.append(f"无效的 billing_mode: {billing_mode}，可选值: Subscription, PayAsYouGo")

    if billing_mode == BillingType.SUBSCRIPTION:
        package_code = params.get("package_code")
        if not package_code:
            errors.append("包年包月模式下 package_code 是必填参数")
        elif package_code not in ("version_3", "version_4", "version_5"):
            errors.append(f"无效的 package_code: {package_code}，可选值: version_3(高级版), version_4(企业版), version_5(旗舰版)")

        # 验证数值参数为非负整数
        for key in ["qps_package", "ext_domain_package", "domain_vip", "log_storage",
                    "hybrid_cloud_node", "spike_throttle", "elastic_qps"]:
            value = params.get(key, 0)
            if value and int(value) < 0:
                errors.append(f"{key} 必须为非负整数")

    elif billing_mode == BillingType.PAY_AS_YOU_GO:
        secu = params.get("secu")
        if not secu:
            errors.append("按量付费模式下 secu 是必填参数")
        elif int(secu) < 1:
            errors.append("secu 必须大于等于 1")

    return errors


# =============================================================================
# EXPORT SECTION
# =============================================================================

PRODUCT = {
    "code": CODE,
    "name": NAME,
    "display_name": DISPLAY_NAME,
    "product_type": PRODUCT_TYPE,
    "category": CATEGORY,
    "params": PARAMS,
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}


# =============================================================================
# AI 验证命令（运行此文件时执行自检）
# =============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from ai_friendly.validate import validate_product_file

    print(f"验证产品定义: {CODE}")
    errors = validate_product_file(__file__)

    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        sys.exit(0)
