---
name: init
description: 初始化需求项目 - 创建本地存储和主仓需求目录
---

# 初始化需求项目

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:init` 的档位执行；已作为执行子代理时不再次路由。

初始化需求项目，创建本地存储目录和主仓需求目录，并绑定当前仓库。

> 模板源文件：`plugins/rd/templates/`，写入规范：`_storage.md`（按需读取 [_storage.md](../../shared/_storage.md)），架构片段：[`agent-snippets/`](../../templates/agent-snippets/)，release 模板：[`release-prompt-template.md`](../../templates/release-prompt-template.md)，Prompt 库骨架：[`prompt-snippets/`](../../templates/prompt-snippets/)

## 命令格式

```
/rd:init <project-name> [--reinit] [--readonly]
```

- `project-name`: 项目名称（kebab-case）
- `--reinit`: 补充缺失内容，不覆盖已有文件
- `--readonly`: 只读仓库角色，不创建本地需求目录和主仓需求目录

---

## 执行流程

### 1. 参数解析

仓库角色优先级：`--readonly` 参数 → `.devflow/settings.json` 中已有 `readonly` → 默认 `primary`。

### 2. 创建目录结构

**primary**：`docs/requirements/` 下创建 `active/`、`completed/`、`modules/`、`templates/`

**readonly**：仅 `docs/requirements/templates/`

### 3. 复制模板文件

复制到 `docs/requirements/templates/`（仅当目标不存在时，`--reinit` 保护已有）：
`requirement-template.md`、`quick-template.md`、`prd-template.md`、`module-template.md`

### 4. 生成 PRD（仅 primary）

从 `prd-template.md` 复制，替换 `{{PROJECT_NAME}}`、`{{DATE}}` 变量。

### 5. 创建「快速修复」模块（仅 primary）

`docs/requirements/modules/quick-fix.md` 不存在时，生成含概述、核心功能、业务规则、相关需求、变更记录的模块文档。

### 6. 绑定当前仓库

> 写入规范见 _storage.md（按需读取 [_storage.md](../../shared/_storage.md)）。无主仓需求目录：需求文档只存在于 primary 仓库的 `requirementsDir`。

在 `.devflow/settings.json` 写入 `requirementProject`、`requirementRole`、`requirementsDir`（合并写入，不覆盖 `branchStrategy` 等既有字段）。

- **primary**：`requirementRole: "primary"`，需求存本仓 `requirementsDir`，写入即生效、无同步、无缓存
- **readonly**：`/rd:init --readonly` 仅建本地模板目录、不建需求存储；随后用 `/rd:use <primary-repo-path>` 绑定主项目（写 `requirementSource` 到 `.devflow/settings.local.json`）

### 7. 生成架构文件

`docs/prompt/architecture.md` 已存在则跳过。否则扫描项目结构检测技术栈（go.mod → Go · pom.xml/build.gradle → Java · package.json 按依赖判断前后端 · requirements.txt/pyproject.toml → Python · Cargo.toml → Rust · 否则通用），同时扫描目录分层、测试文件位置、代码风格，生成架构文件草稿，用户确认后写入。在 AGENTS.md 末尾追加仅一行指针引用。

### 8. 创建 Prompt 库骨架（仅当目标文件不存在）

从 `templates/prompt-snippets/` **复制**到 `docs/prompt/`（逐文件检查，已存在则跳过，`--reinit` 保护已有）：
`code-generation.md`、`refactoring.md`、`test-generation.md`、`testing.md`、`error-diagnosis.md`、`pr-review.md`、`requirement-structuring.md`、`prompt-craft.md`。

> 用复制而非现场生成，确保各项目骨架结构一致（统一 5 节：什么时候用 / 必备输入 / 触发方式 / 优质输出标准 / 常见失败模式）。骨架节内容为占位注释，供用户按项目填充；消费命令（`/rd:dev`、`/rd:do`、`/rd:fix`、`/rd:pr` 等）在运行时按需 Read 对应文件，缺失即降级为通用行为。

### 9. 生成 release.md

`docs/prompt/release.md` 已存在则跳过。不存在时扫描项目（版本号文件、test/build/lint 命令、CI 配置、构建产物目录），生成预填充草稿，用户确认后写入。

### 10. Skills 初始化

创建 `.agents/skills/` 目录，根据项目类型引导创建 Skill；仅 Codex 兼容场景同步到 `.agents/skills/`：
- **后端**：引导创建 `migration.md`（声明 migration SQL 目录）
- **前端**：提示无需预置
- **自定义**：提示按需创建

---

## 输出要点

成功时输出：目录结构树、已生成文件列表、下一步操作提示（检查架构文件 → 发版配置 → PRD → 分支策略 → 创建需求）。

`--reinit` 标注「已存在」和「新增/补充」的区别。`--readonly` 说明从主仓需求目录只读。

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 未提供项目名 | 提示 `/rd:init my-project` |
| 项目名含非法字符 | 仅允许字母、数字、连字符 |
| 本地目录已存在（无 --reinit） | 提示用 `--reinit` 补充 |
| readonly 主仓需求目录不可读 | 报告路径和原因，待路径可访问后继续绑定 |
| 权限不足 | 提示检查目录权限 |

---

## 用户输入

$ARGUMENTS
