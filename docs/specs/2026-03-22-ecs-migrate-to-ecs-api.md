# ECS 产品迁移到 ECS DescribePrice API

## 背景

当前 ECS 产品使用 BSS OpenAPI 查询价格，但存在以下问题：
- GPU 实例（如 ecs.gn7i-c32g1.8xlarge）返回的价格是原价的一半（¥3,193.99 vs 官网 ¥6,387.98）
- BSS API 对 GPU 实例的定价模块支持不完整

调研发现 ECS 自身的 `DescribePrice` API 能正确返回所有实例类型的价格，包括 GPU 实例。

## 目标

将 ECS 产品的定价查询从 BSS OpenAPI 迁移到 ECS `DescribePrice` API，确保：
- 所有实例类型（包括 GPU）价格准确
- 返回原价（不包含折扣）
- 保持向后兼容（参数和输出格式不变）

## 技术方案

### 方案 A：完全替换 BSS API

ECS 产品使用 ECS DescribePrice API，其他产品继续使用 BSS API。

**优点：**
- 代码简洁
- 价格准确
- 维护成本低

### 架构变更

```
当前架构：
quoter.py -> bss_client.py -> BSS OpenAPI
                ↑
         products/ecs.py (build_modules)

新架构：
quoter.py -> ecs_client.py -> ECS DescribePrice API (仅 ECS)
         -> bss_client.py -> BSS OpenAPI (其他产品)
```

## 实现计划

### Task 1: 创建 ECS API 客户端模块

**文件:** `skill/scripts/ecs_client.py` (新建)

**功能:**
- 封装 ECS DescribePrice API 调用
- 复用 bss_client.py 的签名逻辑
- 返回统一的价格格式

**关键代码:**
```python
# ECS API 端点
_ENDPOINT = "https://ecs.aliyuncs.com"
_API_VERSION = "2014-05-26"

def get_instance_price(region, instance_type, platform="Linux", 
                       system_disk_category="cloud_essd", 
                       system_disk_size=40, period=1, price_unit="Month"):
    """查询 ECS 实例价格，返回原价"""
    # 调用 ECS DescribePrice API
    # 返回: {"original_price": float, "currency": str, "details": {...}}
```

### Task 2: 修改 ECS 产品定义

**文件:** `skill/scripts/products/ecs.py` (修改)

**变更:**
1. 移除 `build_modules` 函数（不再使用 BSS 模块）
2. 新增 `get_price` 函数，调用 ECS API
3. 更新 PRODUCT 定义

**关键代码:**
```python
from ecs_client import get_instance_price

def get_price(params: Dict[str, Any]) -> Dict[str, Any]:
    """使用 ECS API 查询价格"""
    result = get_instance_price(
        region=params["region"],
        instance_type=params["instance_type"],
        platform=params.get("image_os", "linux"),
        system_disk_category=params.get("system_disk_category", "cloud_essd"),
        system_disk_size=params.get("system_disk_size", 40),
        period=params.get("duration", 1),
        price_unit="Month"
    )
    
    # 根据 include_system_disk 决定是否包含系统盘价格
    if not params.get("include_system_disk", False):
        # 只返回实例价格
        return {
            "original_price": result["details"]["instanceType"],
            "currency": result["currency"]
        }
    return result

PRODUCT = {
    # ... 其他配置不变
    "get_price": get_price,  # 新增
    # 移除 build_modules
}
```

### Task 3: 修改 quoter.py 支持产品自定义价格查询

**文件:** `skill/scripts/quoter.py` (修改)

**变更:**
- 检查产品是否有 `get_price` 函数
- 如果有，优先使用；否则使用 BSS API

**关键代码:**
```python
def query_product_price(product_code, params, region, billing, duration, quantity):
    product = registry.get_product(product_code)
    
    # 优先使用产品的自定义价格查询
    if hasattr(product, "get_price"):
        result = product["get_price"](params)
        return format_price_result(result, product_code, params)
    
    # 回退到 BSS API
    modules = product["build_modules"](params)
    # ... BSS API 调用逻辑
```

### Task 4: 测试

**文件:** `tests/test_products/test_ecs.py` (新建或修改)

**测试用例:**
1. 普通实例价格查询（ecs.g9i.xlarge）
2. GPU 实例价格查询（ecs.gn7i-c32g1.8xlarge）
3. 包含/不包含系统盘价格
4. 不同地域价格查询

**验证:**
- 价格与官网一致
- GPU 实例价格正确（不是半价）

## 接口兼容性

### 输入参数（不变）
- `instance_type`: 实例规格
- `image_os`: 操作系统（linux/windows）
- `include_system_disk`: 是否包含系统盘
- `system_disk_category`: 系统盘类型
- `system_disk_size`: 系统盘大小
- `data_disk_category`: 数据盘类型
- `data_disk_size`: 数据盘大小
- `internet_bandwidth`: 公网带宽

### 输出格式（不变）
```json
{
  "original_amount": 6387.98,
  "discount_amount": 0,
  "trade_amount": 6387.98,
  "currency": "CNY",
  "module_details": [...]
}
```

## 风险与回滚

**风险:**
- ECS API 可能有不同的限流策略
- 需要额外处理 ECS API 的错误码

**回滚方案:**
- 保留 BSS API 代码作为 fallback
- 通过配置开关切换

## 验证清单

- [ ] ecs.g9i.xlarge 价格与官网一致（¥477.2/月）
- [ ] ecs.gn7i-c32g1.8xlarge 价格与官网一致（¥6387.98/月）
- [ ] 包含系统盘时总价正确
- [ ] 不包含系统盘时仅返回实例价格
- [ ] 杭州、北京等不同地域价格正确
- [ ] 其他产品（RDS/SLB等）不受影响
