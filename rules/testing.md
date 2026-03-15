---
trigger: always_on
---
# 测试规范

## 命令

```bash
python3 -m pytest tests/ -v                           # 全部测试（含集成测试，需凭证）
python3 -m pytest tests/ -v -k "not API"              # 仅单元测试（无需凭证）
python3 -m pytest tests/test_products/test_xxx.py -v  # 单产品测试
```

## 文件命名

每个产品必须有对应测试文件：`tests/test_products/test_<product_code>.py`

## 测试结构

每个产品测试文件包含两个测试类：

### 单元测试类（不需要凭证）

- `test_product_definition` — 验证 PRODUCT dict 结构完整（必需字段齐全）
- `test_build_modules` — 验证模块构建输出格式正确（每个 module 含 module_code/config/price_type）
- `test_validate_rules` — 测试合法 / 非法参数组合

### 集成测试类（需要 AK/SK 凭证）

类名包含 `API`，用 `@skip_without_credentials` 装饰器标记：
- `test_subscription_price` — 用已知合法参数调用包年包月询价 API，验证 trade_amount > 0
- `test_payasyougo_price` — 用已知合法参数调用按量付费询价 API，验证 trade_amount > 0

## conftest.py

提供公共 fixtures：
- `HAS_CREDENTIALS` — bool，检查环境变量是否配置
- `skip_without_credentials` — 装饰器，无凭证时跳过集成测试
- `create_test_client()` — 创建 bss_client 实例

## 产品接入完成标准

测试全部通过后，该产品才算接入完成。未通过测试的产品不得合入。
