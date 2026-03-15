---
trigger: always_on
---
# 文档一致性维护规则

## 单一信息源原则

每个事实只在一个文件中定义。其他文件如需引用，使用"详见 xxx.md"，不复述内容。

## 文档职责映射

| 文件 | 负责定义的信息 |
|------|---------------|
| AGENTS.md | 项目介绍、技术栈、文件结构树 |
| rules/architecture.md | 注册表机制、PRODUCT 接口、CLI 命令结构、处理流程、API 调用层、错误框架、输出格式 |
| rules/api-constraints.md | 数据源原则、产品接入标准流程、安全约束、限流保护 |
| rules/testing.md | 测试命令、文件命名、测试结构、完成标准 |
| skill/SKILL.md | AI 使用技能的工作流、各产品 CLI 调用示例、参数映射表 |
| skill/product-reference.md | 各产品的 ModuleCode / Config / 参数有效值 |

## 更新触发规则

完成代码改动后，按以下清单检查是否需要同步更新文档：

- **修改框架代码**（quoter.py / registry.py / bss_client.py / errors.py / formatters.py）→ 检查 `architecture.md`
- **变更 CLI 接口**（argparse 参数增删改）→ 检查 `architecture.md` + `skill/SKILL.md`
- **变更 PRODUCT dict 结构**（_base.py 接口约定）→ 检查 `architecture.md`
- **变更 API 调用方式 / 安全策略 / 接入流程** → 检查 `api-constraints.md`
- **变更测试约定**（conftest.py / 测试结构）→ 检查 `testing.md`
- **新增或删除产品** → 检查 `skill/SKILL.md` + `skill/product-reference.md`
- **修改产品参数定义**（products/*.py 的 params）→ 检查 `skill/product-reference.md` + `skill/SKILL.md` 对应示例
- **新增或删除顶层文件 / 目录** → 检查 `AGENTS.md` 的文件结构树
- **技术栈变更**（Python 版本、新增依赖等）→ 检查 `AGENTS.md`
