# WAF 产品接入实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 aliyun-sa-quoter 接入 WAF 3.0 产品报价功能，支持包年包月和按量付费两种计费模式

**Architecture:** 按照项目现有模式，创建 `products/waf.py` 定义 PRODUCT dict，包含动态 product_type 计算、模块构建、参数校验逻辑。同步创建测试文件和更新文档。

**Tech Stack:** Python 3.6+ (仅标准库), 阿里云 BSS OpenAPI

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `skill/scripts/products/waf.py` | 创建 | WAF 产品定义（PRODUCT dict） |
| `tests/test_products/test_waf.py` | 创建 | 单元测试 + 集成测试 |
| `skill/SKILL.md` | 修改 | 添加 WAF 使用示例 |
| `skill/product-reference.md` | 修改 | 添加 WAF 参数参考 |

---

## Chunk 1: 创建 WAF 产品定义文件

### Task 1: 创建 waf.py 基础结构

**Files:**
- Create: `skill/scripts/products/waf.py`

- [ ] **Step 1: 写入文件头部注释和导入**

```python
"""
WAF (Web Application Firewall) product definition.

ProductCode: waf
ProductType: waf_v3prepaid_public_cn (subscription) / waf_v2_public_cn (payasyougo)
API docs: https://api.aliyun.com/document/BssOpenApi/2017-12-14/GetSubscriptionPrice
"""
```

- [ ] **Step 2: 实现 get_product_type 函数**

```python
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
```

- [ ] **Step 3: 实现 build_modules 函数 - 包年包月逻辑**

```python
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
    if params.get("bot_web", False):
        modules.append({
            "module_code": "botWeb",
            "config": f"botWeb:1,Region:{region},bot_version:1,PackageCode:{package_code}",
            "price_type": "Month",
        })
    
    # Bot APP 防护
    if params.get("bot_app", False):
        modules.append({
            "module_code": "botApp",
            "config": f"botApp:1,Region:{region},bot_version:1",
            "price_type": "Month",
        })
    
    # API 安全
    if params.get("apisec", False):
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
    if params.get("waf_gslb", False):
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
    if params.get("blue_teaming", False):
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
```

- [ ] **Step 4: 实现按量付费模块构建**

```python
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
```

- [ ] **Step 5: 实现 format_summary 函数**

```python
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
            extensions.append(f"QPS扩展({params['qps_package']