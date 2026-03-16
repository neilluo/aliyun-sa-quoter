# 百炼大模型报价功能 Spec

**日期**: 2026-03-16  
**作者**: Holly  
**状态**: 待实现  
**价格数据最后更新**: 2026-03-11（来源：阿里云官方文档）

---

## 1. 需求概述

为 aliyun-sa-quoter 项目添加百炼大模型（Bailian）报价功能，支持查询通义千问系列模型的调用价格。

### 1.1 背景

- 百炼大模型是阿里云的大模型服务平台
- 按 Token 计费（输入 + 输出分开计费）
- 支持阶梯定价（输入 Token 数越大，单价越高）
- 多地域价格不同
- 支持特殊折扣（Batch 调用 50% 折扣）

### 1.2 目标

- 支持 6 个核心模型：qwen3-max, qwen-max, qwen3.5-plus, qwen-plus, qwen3.5-flash, qwen-flash
- 支持 4 个地域：中国内地(cn-beijing)、全球、国际、美国
- 支持阶梯计价计算
- 支持 Batch 调用折扣

---

## 2. 技术方案

### 2.1 方案选择：静态定价表（方案 A）

**理由**:
- 百炼价格变动频率低（季度或半年调整）
- 实现简单，无外部依赖
- 计算速度快（纯本地）
- 代码即文档，可审计

**价格更新机制**:
- 定价表硬编码在 `products/bailian.py` 中
- 代码中标注价格最后更新日期
- 价格变动时手动更新代码

### 2.2 产品定义结构

遵循现有产品定义接口（PRODUCT dict），新增 `products/bailian.py`：

```python
PRODUCT = {
    "code": "bailian",
    "name": "Bailian",
    "display_name": "百炼大模型",
    "product_type": None,  # 不走 BSS API
    "category": "ai",
    "params": [...],  # 模型、地域、输入/输出 Token 数等参数
    "build_modules": build_modules,  # 本地计算价格
    "format_summary": format_summary,
    "validate": validate,
}
```

### 2.3 定价表结构

```python
# 价格数据最后更新日期：2026-03-11
# 来源：https://help.aliyun.com/zh/model-studio/model-pricing

PRICING_TABLE = {
    "cn-beijing": {  # 中国内地
        "qwen3-max": {
            "input_tiers": [
                {"max_tokens": 32000, "price_per_million": 2.5},
                {"max_tokens": 128000, "price_per_million": 4.0},
                {"max_tokens": 252000, "price_per_million": 7.0},
            ],
            "output_price_per_million": 10.0,  # 非思考模式
            "thinking_output_price_per_million": 10.0,  # 思考模式
            "supports_batch": True,
            "supports_context_cache": True,
        },
        # ... 其他模型
    },
    "global": {...},  # 全球
    "international": {...},  # 国际
    "us": {...},  # 美国
}
```

---

## 3. 功能规格

### 3.1 支持的模型

| 模型 | 输入阶梯 | 输出价格(非思考) | 输出价格(思考) | Batch | 上下文缓存 |
|------|---------|----------------|---------------|-------|-----------|
| qwen3-max | 3级 | 10元/百万 | 10元/百万 | ✓ | ✓ |
| qwen-max | 无阶梯 | 9.6元/百万 | - | ✓ | ✗ |
| qwen3.5-plus | 3级 | 4.8元/百万 | 4.8元/百万 | ✓ | ✗ |
| qwen-plus | 3级 | 2元/百万 | 8元/百万 | ✓ | ✓ |
| qwen3.5-flash | 3级 | 2元/百万 | - | ✓ | ✓ |
| qwen-flash | 3级 | 1.5元/百万 | - | ✓ | ✓ |

### 3.2 支持的参数

```json
{
  "model": "qwen3-max",           // 模型名称（必填）
  "region": "cn-beijing",         // 地域（默认：cn-beijing）
  "input_tokens": 100000,         // 输入 Token 数（必填）
  "output_tokens": 50000,         // 输出 Token 数（必填）
  "thinking": false,              // 是否思考模式（默认：false）
  "batch": false,                 // 是否 Batch 调用（默认：false）
  "context_cache": false          // 是否上下文缓存（默认：false）
}
```

### 3.3 计价逻辑

```
输入价格 = 输入 Token 数 × 对应阶梯单价 / 1,000,000
输出价格 = 输出 Token 数 × 输出单价 / 1,000,000

如果 batch=True:
    输入价格 = 输入价格 × 0.5
    输出价格 = 输出价格 × 0.5

如果 context_cache=True:
    输入价格 = 输入价格 × 0.5  # 仅输入享有折扣

总价格 = 输入价格 + 输出价格
```

---

## 4. 接口设计

### 4.1 CLI 使用示例

```bash
# 基本查询
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":1000000,"output_tokens":500000}'

# 指定地域
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","region":"global","input_tokens":1000000,"output_tokens":500000}'

# Batch 调用
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":1000000,"output_tokens":500000,"batch":true}'

# 思考模式
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3.5-plus","input_tokens":1000000,"output_tokens":500000,"thinking":true}'
```

### 4.2 输出格式

```markdown
# 百炼大模型报价

## 配置摘要
- 模型: qwen3-max
- 地域: 中国内地(cn-beijing)
- 输入 Token: 1,000,000
- 输出 Token: 500,000
- 思考模式: 否
- Batch 调用: 否

## 价格明细
| 项目 | Token 数 | 单价(元/百万) | 小计(元) |
|------|---------|--------------|---------|
| 输入 | 1,000,000 | 2.5 | 2.50 |
| 输出 | 500,000 | 10.0 | 5.00 |

## 总价
**7.50 元**

---
价格数据最后更新: 2026-03-11
```

---

## 5. 文件变更

### 5.1 新增文件

- `skill/scripts/products/bailian.py` - 百炼产品定义和定价表

### 5.2 修改文件

- `skill/SKILL.md` - 添加百炼使用文档
- `skill/product-reference.md` - 添加百炼参数参考

---

## 6. 测试用例

### 6.1 基础测试

```bash
# 测试 qwen3-max 基础价格
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":32000,"output_tokens":10000}'
# 期望: 输入 0.08元 + 输出 0.1元 = 0.18元

# 测试阶梯计价（32K-128K 区间）
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":100000,"output_tokens":10000}'
# 期望: 输入 0.4元 + 输出 0.1元 = 0.5元
```

### 6.2 折扣测试

```bash
# 测试 Batch 折扣
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","input_tokens":32000,"output_tokens":10000,"batch":true}'
# 期望: (0.08 + 0.1) × 0.5 = 0.09元
```

### 6.3 边界测试

```bash
# 测试无效模型
python3 scripts/quoter.py price bailian \
  --params '{"model":"invalid-model","input_tokens":1000,"output_tokens":500}'
# 期望: 错误提示，列出支持的模型

# 测试无效地域
python3 scripts/quoter.py price bailian \
  --params '{"model":"qwen3-max","region":"invalid","input_tokens":1000,"output_tokens":500}'
# 期望: 错误提示，列出支持的地域
```

---

## 7. 实现注意事项

### 7.1 代码规范

- 变量/函数命名清晰有意义
- 函数职责单一（不超过一个抽象层级）
- 关键逻辑有注释（解释 why，不是 what）
- 价格表顶部必须标注最后更新日期

### 7.2 错误处理

- 模型不存在 → 列出支持的模型列表
- 地域不存在 → 列出支持的地域列表
- Token 数为负数 → 参数校验错误
- 超出最大 Token 限制 → 明确提示最大支持数量

### 7.3 扩展性考虑

- 定价表结构易于添加新模型
- 地域扩展预留接口
- 折扣规则可配置

---

## 8. 验收标准

- [ ] `quoter.py price bailian` 命令可正常执行
- [ ] 支持 6 个核心模型的价格计算
- [ ] 支持 4 个地域的价格计算
- [ ] 阶梯计价逻辑正确
- [ ] Batch 折扣计算正确
- [ ] 思考模式价格正确
- [ ] 错误提示清晰友好
- [ ] 输出格式符合规范
- [ ] 代码通过 Code Review
- [ ] SKILL.md 文档已更新

---

**信息来源**: 阿里云官方文档 https://help.aliyun.com/zh/model-studio/model-pricing，价格数据最后更新 2026-03-11
