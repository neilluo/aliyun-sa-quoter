"""
WAF (Web Application Firewall) product definition.

ProductCode: waf
ProductType: waf_v3prepaid_public_cn (subscription) / waf_v2_public_cn (payasyougo)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""


def get_product_type(params):
    """根据计费模式返回 ProductType.

    Args:
        params: 用户参数字典

    Returns:
        str: ProductType 字符串
    """
    billing_mode = params.get("billing_mode", "subscription")
    if billing_mode == "subscription":
        return "waf_v3prepaid_public_cn"
    else:
        return "waf_v2_public_cn"


def build_modules(params):
    """Build WAF pricing module list.

    Args:
        params: 用户参数字典

    Returns:
        list: 模块列表，每个模块包含 module_code, config, price_type
    """
    region = params.get("region", "cn-hangzhou")
    billing_mode = params.get("billing_mode", "subscription")

    if billing_mode == "subscription":
        return _build_subscription_modules(params, region)
    else:
        return _build_payasyougo_modules(params, region)


def _build_subscription_modules(params, region):
    """构建包年包月模块列表."""
    package_code = params.get("package_code", "version_3")

    modules = [
        {
            "module_code": "PackageCode",
            "config": f"Region:{region},PackageCode:{package_code}",
            "price_type": "Month",
        },
    ]

    # QPS 扩展包
    qps_package = params.get("qps_package", 0)
    if qps_package and int(qps_package) > 0:
        bot_web = 1 if params.get("bot_web", False) else 0
        bot_app = 1 if params.get("bot_app", False) else 0
        apisec = 1 if params.get("apisec", False) else 0
        modules.append({
            "module_code": "QPSPackage",
            "config": f"botWeb:{bot_web},apisec:{apisec},botApp:{bot_app},Region:{region},QPSPackage:{qps_package}",
            "price_type": "Month",
        })

    # 域名扩展包
    ext_domain_package = params.get("ext_domain_package", 0)
    if ext_domain_package and int(ext_domain_package) > 0:
        modules.append({
            "module_code": "ExtDomainPackage",
            "config": f"ExtDomainPackage:{ext_domain_package},Region:{region},PackageCode:{package_code}",
            "price_type": "Month",
        })

    # Bot Web 防护
    if params.get("bot_web", 0) == 1:
        modules.append({
            "module_code": "botWeb",
            "config": f"botWeb:1,Region:{region},bot_version:1,PackageCode:{package_code}",
            "price_type": "Month",
        })
    
    # Bot APP 防护
    if params.get("bot_app", 0) == 1:
        modules.append({
            "module_code": "botApp",
            "config": f"botApp:1,Region:{region},bot_version:1",
            "price_type": "Month",
        })
    
    # API 安全
    if params.get("apisec", 0) == 1:
        modules.append({
            "module_code": "apisec",
            "config": f"apisec:1,Region:{region},PackageCode:{package_code}",
            "price_type": "Month",
        })

    # 独享 IP
    domain_vip = params.get("domain_vip", 0)
    if domain_vip and int(domain_vip) > 0:
        modules.append({
            "module_code": "domainVip",
            "config": f"Region:{region},domainVip:{domain_vip}",
            "price_type": "Month",
        })

    # 日志存储
    log_storage = params.get("log_storage", 0)
    if log_storage and int(log_storage) > 0:
        modules.append({
            "module_code": "LogStorage",
            "config": f"Region:{region},LogStorage:{log_storage}",
            "price_type": "Month",
        })

    # 智能负载均衡
    if params.get("waf_gslb", 0) == 1:
        modules.append({
            "module_code": "WafGslb",
            "config": f"Region:{region},WafGslb:1",
            "price_type": "Month",
        })

    # 混合云扩展节点
    hybrid_cloud_node = params.get("hybrid_cloud_node", 0)
    if hybrid_cloud_node and int(hybrid_cloud_node) > 0:
        modules.append({
            "module_code": "HybridCloudNode",
            "config": f"Region:{region},PackageCode:{package_code},HybridCloudNode:{hybrid_cloud_node}",
            "price_type": "Month",
        })

    # 重保场景
    if params.get("blue_teaming", 0) == 1:
        modules.append({
            "module_code": "BlueTeaming",
            "config": f"BlueTeaming:1,Region:{region},PackageCode:{package_code}",
            "price_type": "Month",
        })

    # 洪峰限流
    spike_throttle = params.get("spike_throttle", 0)
    if spike_throttle and int(spike_throttle) > 0:
        modules.append({
            "module_code": "spikeThrottle",
            "config": f"Region:{region},spikeThrottle:{spike_throttle}",
            "price_type": "Month",
        })

    # 弹性 QPS
    elastic_qps = params.get("elastic_qps", 0)
    if elastic_qps and int(elastic_qps) > 0:
        bot_web = 1 if params.get("bot_web", False) else 0
        bot_app = 1 if params.get("bot_app", False) else 0
        apisec = 1 if params.get("apisec", False) else 0
        modules.append({
            "module_code": "ElasticQps",
            "config": f"botWeb:{bot_web},apisec:{apisec},botApp:{bot_app},Region:{region},ElasticQps:{elastic_qps}",
            "price_type": "Month",
        })

    return modules


def _build_payasyougo_modules(params, region):
    """构建按量付费模块列表."""
    secu = params.get("secu", 1)

    return [
        {
            "module_code": "SeCU",
            "config": f"SeCU:{secu},Region:{region}",
            "price_type": "Hour",
        },
    ]


def format_summary(params):
    """Build human-readable config summary.

    Args:
        params: 用户参数字典

    Returns:
        dict: 配置摘要
    """
    billing_mode = params.get("billing_mode", "subscription")
    region = params.get("region", "cn-hangzhou")

    summary = {
        "产品": "WAF",
        "地域": region,
    }

    if billing_mode == "subscription":
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
        summary["SeCU"] = params.get("secu", 1)

    return summary


def validate(params):
    """Validate WAF parameters.

    Args:
        params: 用户参数字典

    Returns:
        list: 错误信息列表
    """
    errors = []

    billing_mode = params.get("billing_mode")
    if not billing_mode:
        errors.append("billing_mode 是必填参数，可选值: subscription, payasyougo")
    elif billing_mode not in ("subscription", "payasyougo"):
        errors.append(f"无效的 billing_mode: {billing_mode}，可选值: subscription, payasyougo")

    if billing_mode == "subscription":
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

    elif billing_mode == "payasyougo":
        secu = params.get("secu")
        if not secu:
            errors.append("按量付费模式下 secu 是必填参数")
        elif int(secu) < 1:
            errors.append("secu 必须大于等于 1")

    return errors


PRODUCT = {
    "code": "waf",
    "name": "WAF",
    "display_name": "Web应用防火墙",
    "product_type": get_product_type,
    "category": "security",
    "params": [
        {
            "name": "region",
            "label": "地域",
            "type": "string",
            "required": False,
            "default": "cn-hangzhou",
            "choices": ["cn-hangzhou", "cn-shanghai", "cn-beijing", "cn-shenzhen",
                        "cn-qingdao", "cn-zhangjiakou", "cn-hongkong",
                        "ap-southeast-1", "ap-northeast-1", "us-west-1", "us-east-1"],
            "description": "地域 ID",
            "examples": ["cn-hangzhou", "cn-beijing"],
        },
        {
            "name": "billing_mode",
            "label": "计费模式",
            "type": "string",
            "required": True,
            "default": None,
            "choices": ["subscription", "payasyougo"],
            "description": "计费模式: subscription(包年包月), payasyougo(按量付费)",
            "examples": ["subscription", "payasyougo"],
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
    ],
    "build_modules": build_modules,
    "format_summary": format_summary,
    "validate": validate,
}
