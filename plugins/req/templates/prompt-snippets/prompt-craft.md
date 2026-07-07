# Prompt 文件规范

> 本文件说明 `docs/prompt/` 下各 Prompt 文件的用途与统一结构，供团队维护参考。由 `/req:init` 生成。

## 什么是 Prompt 文件

Prompt 文件是**项目特有的知识库**，供 req 插件的命令在运行时自动读取，让 AI 理解本项目的独特约定。每个文件描述一个方面的规范，命令按需注入对应文件；文件缺失时命令降级为通用行为（不报错）。

## 文件清单与消费命令

| 文件 | 内容 | 主要消费命令 |
|------|------|-------------|
| `architecture.md` | 项目架构（分层、技术栈、目录、命名）| `/req:dev`、`/req:test`（自动生成）|
| `code-generation.md` | 代码生成规范 | `/req:dev` |
| `refactoring.md` | 重构规范（不改变行为）| `/req:do` |
| `test-generation.md` | 测试用例生成规范 | `/req:test-new` |
| `testing.md` | 测试运行规范 | `/req:test`、`/req:test-regression` |
| `error-diagnosis.md` | 错误根因分析规范 | `/req:fix` |
| `pr-review.md` | PR 评审规范 | `/req:review-pr` |
| `requirement-structuring.md` | 模糊需求结构化规范 | `/req:new`、`/req:edit` |
| `release.md` | 发版规则 | `/req:release` |

## 统一 5 节结构

除 `architecture.md`/`release.md` 外，每个 Prompt 文件遵循固定 5 节骨架：

| 节 | 作用 |
|----|------|
| **什么时候用** | 适用场景与不适用情况 |
| **必备输入** | 触发前必须准备的清单（最关键的一节，缺则质量差）|
| **触发方式** | 如何触发，或写入 AGENTS.md 持续生效 |
| **优质输出标准** | 好的输出长什么样，用于自评 |
| **常见失败模式** | 表格：问题 / 原因 / 解决方案 |

## 维护建议

- **纳入 git**：所有 Prompt 文件随项目版本管理。
- **简明举例**：用代码示例和真实案例，而非抽象描述。
- **指向权威**：引用 AGENTS.md、README、`architecture.md` 等，避免重复。
- **新成员**：加入项目时通读全部 Prompt 文件了解约定。

---

> 本规范由 `/req:init` 自动生成。新增自定义 Prompt 文件时沿用同一 5 节结构。
