# Alibaba Cloud Quoter (aliyun-quoter)

通过阿里云 BSS OpenAPI 查询全量云产品实时价格的 Qoder Skill。
用户用自然语言描述需求，AI 自动映射为产品参数并返回精准报价。

## 技术栈

- Python 3.6+，零第三方依赖（仅标准库）
- 阿里云 BSS OpenAPI（HMAC-SHA1 签名，RPC 风格）
- 凭证：通过环境变量配置（详见 api-constraints.md 安全节）

## 项目结构

```
skill/scripts/quoter.py              # CLI 入口（5 个子命令: check/products/modules/info/price）
skill/scripts/bss_client.py          # BSS API 客户端（签名、重试、错误处理）
skill/scripts/errors.py              # 统一错误处理框架
skill/scripts/formatters.py          # Markdown 输出格式化
skill/scripts/registry.py            # 【已删除】合并到 framework/registry.py
skill/scripts/product_params.py      # 【已删除】旧版模块构建器
skill/scripts/framework/             # 核心框架（ builders/validators/base/registry ）
skill/scripts/products/              # 每个产品一个文件（自包含 PRODUCT dict）
skill/scripts/products/_base.py      # 【已删除】合并到 framework/base.py
skill/scripts/ai_friendly/           # AI 友好开发框架（常量、类型、模板、验证）
skill/SKILL.md                       # AI 技能入口文档
skill/product-reference.md           # 全产品参数速查
rules/                               # 开发规范（通过 .qoder/rules/ 符号链接自动加载）
tests/                               # 单元测试 + 集成测试
```

## 规则文件

详细开发规范在 `rules/` 下（通过 `.qoder/rules/` 符号链接自动加载）：

- `architecture.md` — 技术架构、CLI 命令结构、处理流程
- `api-constraints.md` — 数据源原则、产品接入流程、安全约束
- `testing.md` — 测试规范与完成标准
- `doc-maintenance.md` — 文档一致性维护规则
