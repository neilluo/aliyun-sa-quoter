# Spec: 迁移 RDS/Redis/MongoDB 到 DescribePrice API

## 背景

当前 aliyun-sa-quoter 使用 BSS OpenAPI (`GetSubscriptionPrice`/`GetPayAsYouGoPrice`) 查询产品价格，但 BSS API 存在以下问题：
1. 数据同步延迟，可能返回已下架规格的价格
2. 不校验地域可用性
3. 价格可能不准确（如 mysql.n2.medium.1 在杭州，BSS 返回 ¥236，实际 ¥256）

阿里云各产品有专属的 DescribePrice API，数据更准确、实时性更好。

## 目标

将以下三个产品从 BSS API 迁移到各自的 DescribePrice API：
1. **RDS** (云数据库 MySQL/PostgreSQL/SQL Server)
2. **Redis/Tair** (云数据库 Redis 版)
3. **MongoDB** (云数据库 MongoDB 版)

## 当前状态

- ✅ **ECS** 已使用 DescribePrice API (`ecs_client.py`)
- ❌ **RDS** 使用 BSS API (`rds.py`)
- ❌ **Redis** 使用 BSS API (`redis.py`)
- ❌ **MongoDB** 使用 BSS API (`mongodb.py`)

## 技术方案

### 架构设计

参考 ECS 的实现模式，为每个产品创建独立的 API 客户端：

```
skill/scripts/
├── ecs_client.py          # 已存在 (参考模板)
├── rds_client.py          # 新建
├── redis_client.py        # 新建
├── mongodb_client.py      # 新建
└── products/
    ├── ecs.py             # 已使用 DescribePrice
    ├── rds.py             # 修改为使用 rds_client
    ├── redis.py           # 修改为使用 redis_client
    └── mongodb.py         # 修改为使用 mongodb_client
```

### API 端点

| 产品 | API 端点 | 版本 |
|------|----------|------|
| ECS | `https://ecs.aliyuncs.com` | 2014-05-26 |
| RDS | `https://rds.aliyuncs.com` | 2014-08-15 |
| Redis | `https://r-kvstore.aliyuncs.com` | 2015-01-01 |
| MongoDB | `https://mongodb.aliyuncs.com` | 2015-12-01 |

### 签名机制

所有 API 使用相同的阿里云 RPC 签名机制（HMAC-SHA1）：
1. 参数按字典序排序
2. RFC 3986 URL 编码
3. HMAC-SHA1 签名，密钥为 `AccessKeySecret + "&"`

### 客户端设计

每个客户端包含以下函数：

#### rds_client.py
```python
def get_rds_price(
    region: str,
    engine: str,
    engine_version: str,
    instance_class: str,
    storage_size: int = 100,
    pay_type: str = "Prepaid",  # Prepaid/Postpaid
    period: int = 1,
    time_type: str = "Month"    # Month/Year
) -> Dict[str, Any]:
    """Query RDS instance price via DescribePrice API."""
```

#### redis_client.py
```python
def get_redis_price(
    region: str,
    instance_class: str,
    architecture: str = "standard",  # standard/cluster
    capacity: int = 1024,            # MB
    pay_type: str = "Prepaid",
    period: int = 1,
    time_type: str = "Month"
) -> Dict[str, Any]:
    """Query Redis/Tair instance price via DescribePrice API."""
```

#### mongodb_client.py
```python
def get_mongodb_price(
    region: str,
    instance_class: str,
    storage_size: int = 100,
    pay_type: str = "Prepaid",
    period: int = 1,
    time_type: str = "Month"
) -> Dict[str, Any]:
    """Query MongoDB instance price via DescribePrice API."""
```

### 返回格式

所有客户端返回统一格式：
```python
{
    "original_price": float,    # 原价
    "discount_price": float,    # 折扣价
    "trade_price": float,       # 成交价
    "currency": str,            # 货币 (CNY)
    "details": Dict[str, float] # 各组件价格明细
}
```

## 产品文件修改

### products/rds.py

修改 `get_price()` 函数，使用 `rds_client.get_rds_price()` 替代 BSS API 调用。

**参数映射**:
- `region` → `RegionId`
- `engine` → `Engine`
- `engine_version` → `EngineVersion`
- `instance_class` → `DBInstanceClass`
- `storage_size` → `DBInstanceStorage`
- `pay_type` → `PayType` (Prepaid/Postpaid)

**计费方式映射**:
- `subscription` → `Prepaid`
- `payAsYouGo` → `Postpaid`

### products/redis.py

修改 `get_price()` 函数，使用 `redis_client.get_redis_price()`。

**参数映射**:
- `region` → `RegionId`
- `instance_class` → `InstanceClass`
- `capacity` → `Capacity` (MB)
- `architecture` → 影响 `InstanceClass` 选择

### products/mongodb.py

修改 `get_price()` 函数，使用 `mongodb_client.get_mongodb_price()`。

**参数映射**:
- `region` → `RegionId`
- `instance_class` → `DBInstanceClass`
- `storage_size` → `DBInstanceStorage`

## 实现步骤

### Task 1: 创建 rds_client.py
- 复制 ecs_client.py 的签名逻辑
- 修改端点和版本
- 实现 `get_rds_price()` 函数
- 测试 RDS MySQL 价格查询

### Task 2: 修改 products/rds.py
- 导入 rds_client
- 修改 `get_price()` 使用新客户端
- 保持接口兼容（参数和返回格式不变）
- 测试验证

### Task 3: 创建 redis_client.py
- 复制 ecs_client.py 的签名逻辑
- 修改端点和版本
- 实现 `get_redis_price()` 函数
- 测试 Redis 价格查询

### Task 4: 修改 products/redis.py
- 导入 redis_client
- 修改 `get_price()` 使用新客户端
- 测试验证

### Task 5: 创建 mongodb_client.py
- 复制 ecs_client.py 的签名逻辑
- 修改端点和版本
- 实现 `get_mongodb_price()` 函数
- 测试 MongoDB 价格查询

### Task 6: 修改 products/mongodb.py
- 导入 mongodb_client
- 修改 `get_price()` 使用新客户端
- 测试验证

### Task 7: 回归测试
- 测试所有三个产品的价格查询
- 对比 BSS API 和 DescribePrice API 的结果差异
- 验证边界情况（错误参数、网络异常等）

## 测试用例

### RDS 测试
```bash
# MySQL 杭州
python3 quoter.py price rds --params '{"engine":"mysql","engine_version":"8.0","instance_class":"mysql.x2.large.2","storage_size":100}' --region cn-hangzhou

# PostgreSQL 北京
python3 quoter.py price rds --params '{"engine":"postgresql","engine_version":"14.0","instance_class":"pg.n2.medium.2c","storage_size":100}' --region cn-beijing
```

### Redis 测试
```bash
# Redis 杭州
python3 quoter.py price redis --params '{"region":"cn-hangzhou","instance_class":"redis.master.small.default","capacity":1024}'
```

### MongoDB 测试
```bash
# MongoDB 杭州
python3 quoter.py price mongodb --params '{"region":"cn-hangzhou","instance_class":"mdb.shard.2x.large.d","storage_size":100}'
```

## 风险与注意事项

1. **API 限流**: DescribePrice API 可能有调用频率限制，已实现指数退避重试
2. **参数差异**: 不同产品的 API 参数命名和格式不同，需仔细对照文档
3. **地域差异**: 某些规格可能只在特定地域可用，API 会返回错误
4. **向后兼容**: 保持 `products/*.py` 的接口不变，只修改内部实现

## 参考文档

- [RDS DescribePrice API](https://help.aliyun.com/zh/rds/developer-reference/api-rds-2014-08-15-describeprice)
- [Redis DescribePrice API](https://help.aliyun.com/zh/redis/developer-reference/api-r-kvstore-2015-01-01-describeprice-redis)
- [MongoDB DescribePrice API](https://help.aliyun.com/zh/mongodb/developer-reference/api-dds-2015-12-01-describeprice)
- 现有实现: `skill/scripts/ecs_client.py`

## 验收标准

- [ ] rds_client.py 创建完成，可正确查询 RDS 价格
- [ ] products/rds.py 修改完成，使用 DescribePrice API
- [ ] redis_client.py 创建完成，可正确查询 Redis 价格
- [ ] products/redis.py 修改完成，使用 DescribePrice API
- [ ] mongodb_client.py 创建完成，可正确查询 MongoDB 价格
- [ ] products/mongodb.py 修改完成，使用 DescribePrice API
- [ ] 所有测试用例通过
- [ ] 代码风格与 ecs_client.py 保持一致
