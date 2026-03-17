# Elasticsearch MVP 产品接入 Spec

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan.

**Goal:** 实现 Elasticsearch 产品的最小可用版本（MVP），支持数据节点规格和存储询价。

**架构:** 遵循现有产品定义模式，创建 `products/elasticsearch.py`，实现核心模块（NodeSpec + Disk），支持包年包月和按量付费。

**Tech Stack:** Python 3.6+, 零第三方依赖，BSS OpenAPI

---

## 调研数据

### 产品信息
| 属性 | 值 |
|------|-----|
| **ProductCode** | `elasticsearch` |
| **包年包月 ProductType** | `elasticsearchpre` |
| **按量付费 ProductType** | `elasticsearch` |
| **模块数** | 17-18 个（MVP 用 2 个） |

### MVP 核心模块

#### 1. NodeSpec (数据节点规格)
| Config 参数 | 说明 |
|-------------|------|
| `NodeSpec` | 实例规格，如 `elasticsearch.g7.xlarge` |
| `Region` | 地域 ID |
| `NodeAmount` | 节点数量 |

**NodeSpec 可选值**:
- `elasticsearch.g7.xlarge` - 4核16G
- `elasticsearch.r7.2xlarge` - 8核64G
- `elasticsearch.c7.8xlarge` - 32核64G

#### 2. Disk (数据单节点存储空间)
| Config 参数 | 说明 |
|-------------|------|
| `DataDiskType` | 磁盘类型 |
| `PerformanceLevel` | 性能级别（PL0/PL1/PL2/PL3） |
| `Region` | 地域 ID |
| `NodeAmount` | 节点数量 |
| `Disk` | 单节点磁盘大小 (GB) |

**DataDiskType 可选值**:
- `cloud_ssd` - SSD云盘
- `cloud_essd` - ESSD云盘
- `cloud_efficiency` - 高效云盘

---

## 任务清单

### Task 1: 创建 elasticsearch.py 产品定义文件

**Files:**
- Create: `skill/scripts/products/elasticsearch.py`
- Test: `tests/test_elasticsearch.py`

**参数设计:**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `region` | string | 是 | `cn-hangzhou` | 地域ID |
| `node_spec` | string | 是 | - | 数据节点规格 |
| `node_amount` | int | 是 | 3 | 数据节点数量 |
| `disk_type` | string | 是 | `cloud_ssd` | 磁盘类型 |
| `disk_size` | int | 是 | 20 | 单节点磁盘大小(GB) |
| `performance_level` | string | 否 | `PL1` | ESSD性能级别 |
| `subscription_type` | string | 否 | `Subscription` | 付费类型 |

**Module 构建逻辑:**

```python
def build_modules(params):
    region = params["region"]
    node_spec = params["node_spec"]
    node_amount = params["node_amount"]
    disk_type = params["disk_type"]
    disk_size = params["disk_size"]
    performance_level = params.get("performance_level", "PL1")
    
    modules = [
        {
            "module_code": "NodeSpec",
            "config": f"NodeSpec:{node_spec},Region:{region},NodeAmount:{node_amount}",
            "price_type": "Hour",
        },
        {
            "module_code": "Disk",
            "config": f"DataDiskType:{disk_type},PerformanceLevel:{performance_level},Region:{region},NodeAmount:{node_amount},Disk:{disk_size}",
            "price_type": "Hour",
        },
    ]
    return modules
```

**ProductType 逻辑:**
```python
def _get_product_type(params):
    subscription_type = params.get("subscription_type", "Subscription")
    if subscription_type == "PayAsYouGo":
        return "elasticsearch"
    return "elasticsearchpre"
```

---

### Task 2: 编写单元测试

**测试用例:**

1. **test_build_modules_subscription** - 测试包年包月模块构建
2. **test_build_modules_payg** - 测试按量付费模块构建
3. **test_product_type** - 测试 ProductType 切换
4. **test_format_summary** - 测试摘要格式化
5. **test_validate_required** - 测试必填参数校验
6. **test_validate_choices** - 测试可选值校验

---

### Task 3: 更新注册表

**Files:**
- Modify: `skill/scripts/registry.py`

确保自动发现机制能识别新文件。

---

### Task 4: 手动测试验证

**测试命令:**

```bash
# 包年包月询价
python skill/scripts/quoter.py price --product elasticsearch \
  --region cn-hangzhou \
  --node-spec elasticsearch.g7.xlarge \
  --node-amount 3 \
  --disk-type cloud_ssd \
  --disk-size 20 \
  --subscription-type Subscription

# 按量付费询价
python skill/scripts/quoter.py price --product elasticsearch \
  --region cn-hangzhou \
  --node-spec elasticsearch.g7.xlarge \
  --node-amount 3 \
  --disk-type cloud_ssd \
  --disk-size 20 \
  --subscription-type PayAsYouGo
```

---

## 代码规范

- 遵循 `_base.py` 定义的接口
- 参考 `rds.py` 的实现模式
- 函数职责单一
- 添加中文注释说明 why
- 错误处理完整

---

**信息来源**: 本地文件操作 + BSS API 调研文档，操作时间 2026-03-17 09:05
