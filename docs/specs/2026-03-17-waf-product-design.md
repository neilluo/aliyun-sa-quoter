# WAF (Web应用防火墙) 产品接入设计文档

> **日期**: 2026-03-17  
> **版本**: v1.0  
> **状态**: 已确认，待实现

---

## 1. 执行摘要

为 aliyun-sa-quoter 项目接入 WAF 3.0 产品报价功能，支持包年包月和按量付费两种计费模式。

---

## 2. 产品信息

| 属性 | 值 |
|------|-----|
| **产品名称** | Web应用防火墙 (WAF) |
| **ProductCode** | `waf` |
| **包年包月 ProductType** | `waf_v3prepaid_public_cn` |
| **按量付费 ProductType** | `waf_v2_public_cn` |
| **产品分类** | `cdn_security` |

---

## 3. 计费模式与模块

### 3.1 包年包月 (Subscription)

**ProductType**: `waf_v3prepaid_public_cn`

| ModuleCode | ModuleName | Config 参数 | 说明 |
|------------|------------|-------------|------|
| `PackageCode` | 版本 | `Region`, `PackageCode` | 基础版本，必填 |
| `QPSPackage` | QPS扩展 | `botWeb`, `apisec`, `botApp`, `Region`, `QPSPackage` | QPS 扩展包 |
| `ExtDomainPackage` | 域名扩展 | `ExtDomainPackage`, `Region`, `PackageCode` | 域名扩展包 |
| `botWeb` | Bot管理-Web防护 | `botWeb`, `Region`, `bot_version`, `PackageCode` | Bot Web 防护 |
| `botApp` | Bot管理-APP防护 | `botApp`, `Region`, `bot_version` | Bot APP 防护 |
| `apisec` | API安全 | `apisec`, `Region`, `PackageCode` | API 安全防护 |
| `domainVip` | 独享IP | `Region`, `domainVip` | 独享 IP |
| `LogStorage` | 日志存储容量 | `Region`, `LogStorage` | 日志存储 |
| `WafGslb` | 智能负载均衡 | `Region`, `WafGslb` | 智能负载均衡 |
| `HybridCloudNode` | 多云/混合云WAF扩展节点 | `Region`, `PackageCode`, `HybridCloudNode` | 混合云节点 |
| `BlueTeaming` | 重保场景 | `BlueTeaming`, `Region`, `PackageCode` | 重保场景 |
| `spikeThrottle` | 洪峰限流 | `Region`, `spikeThrottle` | 洪峰限流 |
| `ElasticQps` | 弹性后付费 | `botWeb`, `apisec`, `botApp`, `Region`, `ElasticQps` | 弹性 QPS |

### 3.2 按量付费 (PayAsYouGo)

**ProductType**: `waf_v2_public_cn`

| ModuleCode | ModuleName | Config 参数 | 说明 |
|------------|------------|-------------|------|
| `SeCU` | SeCU | `SeCU`, `Region` | 安全能力单元 |

---

## 4. 参数定义

### 4.1 核心参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `region` | string | 是 | `cn-hangzhou` | 地域 ID |
| `billing_mode` | string | 是 | - | 计费模式：`subscription` 或 `payasyougo` |

### 4.2 包年包月专用参数

| 参数名 | 类型 | 必填 | 默认值 | 可选值 | 说明 |
|--------|------|------|--------|--------|------|
| `package_code` | string | 是 | - | `version_3`, `version_4`, `version_5` | 版本：高级版/企业版/旗舰版 |
| `qps_package` | int | 否 | 0 | ≥0 | QPS 扩展包数量 |
| `ext_domain_package` | int | 否 | 0 | ≥0 | 域名扩展包数量 |
| `bot_web` | bool | 否 | false | true/false | 启用 Bot Web 防护 |
| `bot_app` | bool | 否 | false | true/false | 启用 Bot APP 防护 |
| `apisec` | bool | 否 | false | true/false | 启用 API 安全 |
| `domain_vip` | int | 否 | 0 | ≥0 | 独享 IP 数量 |
| `log_storage` | int | 否 | 0 | ≥0 | 日志存储容量 (GB) |
| `waf_gslb` | bool | 否 | false | true/false | 启用智能负载均衡 |
| `hybrid_cloud_node` | int | 否 | 0 | ≥0 | 混合云扩展节点数 |
| `blue_teaming` | bool | 否 | false | true/false | 启用重保场景 |
| `spike_throttle` | int | 否 | 0 | ≥0 | 洪峰限流配置 |
| `elastic_qps` | int | 否 | 0 | ≥0 | 弹性 QPS |

### 4.3 按量付费专用参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `secu` | int | 是 | - | SeCU 数量，≥1 |

---

## 5. 地域支持

WAF 支持的地域（参考现有 regions.json）：
- `cn-hangzhou` - 华东1（杭州）
- `cn-shanghai` - 华东2（上海）
- `cn-beijing` - 华北2（北京）
- `cn-shenzhen` - 华南1（深圳）
- `cn-qingdao` - 华北1（青岛）
- `cn-zhangjiakou` - 华北3（张家口）
- `cn-hongkong` - 香港
- `ap-southeast-1` - 新加坡
- `ap-northeast-1` - 日本
- `us-west-1` - 美国（硅谷）
- `us-east-1` - 美国（弗吉尼亚）

---

## 6. 实现细节

### 6.1 ProductType 动态计算

```python
def get_product_type(params):
    """根据计费模式返回 ProductType."""
    billing_mode = params.get("billing_mode", "subscription")
    if billing_mode == "subscription":
        return "waf_v3prepaid_public_cn"
    else:
        return "waf_v2_public_cn"
```

### 6.2 模块构建逻辑

**包年包月模式**：
1. 必须包含 `PackageCode` 模块（基础版本）
2. 根据可选参数动态添加其他模块：
   - `qps_package` > 0 → 添加 `QPSPackage`
   - `ext_domain_package` > 0 → 添加 `ExtDomainPackage`
   - `bot_web` = True → 添加 `botWeb`
   - `bot_app` = True → 添加 `botApp`
   - `apisec` = True → 添加 `apisec`
   - `domain_vip` > 0 → 添加 `domainVip`
   - `log_storage` > 0 → 添加 `LogStorage`
   - `waf_gslb` = True → 添加 `WafGslb`
   - `hybrid_cloud_node` > 0 → 添加 `HybridCloudNode`
   - `blue_teaming` = True → 添加 `BlueTeaming`
   - `spike_throttle` > 0 → 添加 `spikeThrottle`
   - `elastic_qps` > 0 → 添加 `ElasticQps`

**按量付费模式**：
- 仅包含 `SeCU` 模块

### 6.3 Config 字符串格式

**包年包月**:
```
PackageCode:Region:{region},PackageCode:{package_code}
QPSPackage:botWeb:{0/1},apisec:{0/1},botApp:{0/1},Region:{region},QPSPackage:{qps_package}
ExtDomainPackage:ExtDomainPackage:{ext_domain_package},Region:{region},PackageCode:{package_code}
botWeb:botWeb:1,Region:{region},bot_version:1,PackageCode:{package_code}
botApp:botApp:1,Region:{region},bot_version:1
apisec:apisec:1,Region:{region},PackageCode:{package_code}
```

**按量付费**:
```
SeCU:SeCU:{secu},Region:{region}
```

---

## 7. CLI 使用示例

### 7.1 包年包月 - 基础版本

```bash
python3 scripts/quoter.py price waf \
  --params '{"billing_mode":"subscription","package_code":"version_4","region":"cn-hangzhou"}' \
  --billing subscription \
  --duration 1
```

### 7.2 包年包月 - 带扩展功能

```bash
python3 scripts/quoter.py price waf \
  --params '{"billing_mode":"subscription","package_code":"version_4","region":"cn-hangzhou","qps_package":10,"bot_web":true,"apisec":true}' \
  --billing subscription \
  --duration 1
```

### 7.3 按量付费

```bash
python3 scripts/quoter.py price waf \
  --params '{"billing_mode":"payasyougo","secu":100,"region":"cn-hangzhou"}' \
  --billing payAsYouGo
```

---

## 8. 测试计划

### 8.1 单元测试

| 测试项 | 描述 |
|--------|------|
| `test_product_definition` | 验证 PRODUCT dict 结构完整 |
| `test_build_modules_subscription` | 验证包年包月模块构建 |
| `test_build_modules_payasyougo` | 验证按量付费模块构建 |
| `test_validate_billing_mode` | 验证计费模式必填校验 |
| `test_validate_package_code` | 验证版本参数校验 |
| `test_validate_secU` | 验证 SeCU 参数校验 |

### 8.2 集成测试

| 测试项 | 描述 |
|--------|------|
| `test_subscription_price_basic` | 包年包月基础版本询价 |
| `test_subscription_price_with_extensions` | 包年包月带扩展功能询价 |
| `test_payasyougo_price` | 按量付费询价 |

---

## 9. 文档更新清单

- [ ] `skill/scripts/products/waf.py` - 新建产品定义文件
- [ ] `tests/test_products/test_waf.py` - 新建测试文件
- [ ] `skill/SKILL.md` - 添加 WAF 使用示例
- [ ] `skill/product-reference.md` - 添加 WAF 参数参考

---

## 10. 验收标准

- [ ] `python3 scripts/quoter.py modules waf --type Subscription` 能正确返回模块列表
- [ ] `python3 scripts/quoter.py modules waf --type PayAsYouGo` 能正确返回模块列表
- [ ] `python3 scripts/quoter.py price waf` 包年包月询价返回正确价格
- [ ] `python3 scripts/quoter.py price waf` 按量付费询价返回正确价格
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过（需凭证）
- [ ] 文档已同步更新

---

## 11. 参考信息

- **调研报告**: `research/BSS_PRODUCTS_COMPLETE_RESEARCH_GUIDE.md`
- **模块数据**: `research/high_priority_products_modules.json`
- **现有产品示例**: `skill/scripts/products/slb.py`
- **项目规范**: `rules/architecture.md`, `rules/api-constraints.md`, `rules/testing.md`

---

**信息来源**: 本地文件操作，操作时间 2026-03-17 09:42，基于 research/high_priority_products_modules.json 和 rules/*.md
