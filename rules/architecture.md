---
trigger: always_on
---
# 技术架构

## 产品注册表机制（registry.py）

- 启动时扫描 `skill/scripts/products/*.py`（排除 `__init__.py`、`_base.py`、`_` 开头文件）
- 用 `importlib.import_module` 动态加载，提取模块级 `PRODUCT` 变量
- 注册到全局 `_REGISTRY: dict[str, dict]`，key 为 product_code
- 发现失败打印警告跳过，不阻断其他产品
- 对外接口：`get_product(code)`、`list_products()`、`list_products_by_category(category)`
- **新增产品只需在 products/ 下新增 .py 文件，无需修改任何框架文件**

## 产品文件接口约定（PRODUCT dict）

每个 `products/<name>.py` 必须导出 `PRODUCT = { ... }`，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| code | str | BSS ProductCode，如 "ecs"、"rds"、"redis" |
| name | str | 英文简称，如 "ECS"、"Redis" |
| display_name | str | 中文展示名，如 "ECS 云服务器" |
| product_type | str / None / callable(params)->str | BSS ProductType，None=不需要 |
| category | str | 分类：compute / database / network / storage / cdn_security / middleware |
| params | list[dict] | 参数定义列表 |
| build_modules | callable | fn(params_dict) -> list[{module_code, config, price_type}] |
| format_summary | callable | fn(params_dict) -> dict[str, str] 配置摘要 |
| validate | callable / None | fn(params_dict) -> list[str] 错误列表，空=通过 |

### params 列表中每个参数的结构

| 字段 | 类型 | 说明 |
|------|------|------|
| name | str | JSON key，如 "instance_type" |
| label | str | 中文标签，如 "实例规格" |
| type | str | "string" / "int" / "float" |
| required | bool | 是否必填 |
| default | any | 默认值，None=无默认 |
| choices | list / None | None=自由输入，list=可选值 |
| description | str | 参数描述（给 AI 看） |
| examples | list | 示例值 |

### product_type 动态计算

某些产品的 ProductType 取决于参数组合（如 Redis 标准版="redisa"，集群版="rediscluster"）。
此时 product_type 定义为 callable：`def get_product_type(params): -> str`

## CLI 命令结构（quoter.py）

```
quoter.py check                              # 凭证检查
quoter.py products [--category C]            # 列出产品（按分类）
quoter.py modules <product> [--type T]       # 查询 API 计价模块
quoter.py info <product>                     # 查看产品参数定义
quoter.py price <product> --params '{}'      # 询价
         --region R --billing B --duration D --quantity Q
```

- 产品特定参数通过 `--params` JSON 传入
- 通用参数（region/billing/duration/quantity）保留为 CLI flag
- `info` 命令：AI 不确定参数时先查询，再构造 --params

## cmd_price 通用处理流程

```
1. registry.get_product(code) → 产品定义
2. json.loads(params_json) → 参数 dict
3. 填充默认值
4. 类型转换
5. 必填检查
6. 产品验证（validate）
7. 构建模块（build_modules）
8. 计算 ProductType
9. 调用 BSS API
10. 格式化输出（format_summary）
```

## API 调用层（bss_client.py）

- 纯传输层，不含业务逻辑
- HMAC-SHA1 签名（SignatureVersion 1.0）
- Endpoint: https://business.aliyuncs.com
- API Version: 2017-12-14
- 自动重试限流（429/Throttling，指数退避，最多 3 次）
- ProductType 由调用方从产品定义中计算后传入

## 错误处理框架（errors.py + error_codes.json）

```
QuoterError（基类）
  ├── CredentialError       # 凭证缺失
  ├── ProductNotFoundError  # 产品代码无效
  ├── ValidationError       # 参数验证失败
  ├── BssApiError           # API 错误（含 code + friendly_message）
  └── NetworkError          # 网络问题
```

error_codes.json 存储 API 错误码到友好中文消息的映射。

## 报价结果格式

统一 Markdown 表格输出，必含字段：
- 地域、产品名、规格配置、计费方式
- 各计费项金额明细
- 原价、折扣、应付金额、货币单位
