---
name: init
description: 初始化需求项目 - 创建本地存储和全局缓存
---

# 初始化需求项目

初始化需求项目，创建本地存储目录和全局缓存，并绑定当前仓库。

## 命令格式

```
/req:init <project-name> [--reinit] [--readonly]
```

- `project-name`: 项目名称（kebab-case）
- `--reinit`: 补充缺失内容，不覆盖已有文件
- `--readonly`: 只读仓库角色，不创建本地需求目录和全局缓存

---

## 执行流程

### 1. 参数解析

仓库角色优先级：`--readonly` 参数 → `.claude/settings.local.json` 中已有 `readonly` → 默认 `primary`。

### 2. 创建目录结构

**primary**：`docs/requirements/` 下创建 `active/`、`completed/`、`modules/`、`templates/`

**readonly**：仅 `docs/requirements/templates/`

### 3. 复制模板文件

> 模板源文件位于 `plugins/req/templates/`

将以下模板复制到 `docs/requirements/templates/`（仅当目标不存在时，`--reinit` 保护已有）：

- `requirement-template.md` — 需求文档模板
- `quick-template.md` — 快速修复模板
- `prd-template.md` — PRD 模板
- `module-template.md` — 模块文档模板

### 4. 生成 PRD（仅 primary）

从 `plugins/req/templates/prd-template.md` 复制，替换 `{{PROJECT_NAME}}`、`{{DATE}}` 变量。

### 5. 创建「快速修复」模块（仅 primary）

`docs/requirements/modules/quick-fix.md` 不存在时，生成包含概述、核心功能、业务规则、相关需求、变更记录的模块文档。

### 6. 创建全局缓存（仅 primary）

在 `~/.claude-requirements/projects/<project-name>/` 下创建与本地结构对应的缓存目录，同步模板、PRD、快速修复模块。

### 7. 更新全局索引（仅 primary）

> 索引格式见 `plugins/req/templates/index-template.md`

更新 `~/.claude-requirements/index.json`，记录项目名、创建时间、主仓库路径、关联仓库列表。

### 8. 绑定当前仓库

> 写入规范：读取已有 `.claude/settings.json`，合并字段后写回，不覆盖已有字段。

在 `.claude/settings.local.json` 写入 `requirementProject` 和 `requirementRole`，不覆盖已有字段（如 `branchStrategy`）。

### 9. 生成架构文件

> 架构文件格式和 CLAUDE.md 片段见 `plugins/req/templates/claude-md-snippets/`

**9.1** `docs/prompt/architecture.md` 已存在则跳过

**9.2** 扫描项目结构检测技术栈：
- `go.mod` → Go 后端 · `pom.xml`/`build.gradle` → Java · `package.json`(next/nuxt/vite) → 前端 · `package.json`(express/fastify/nest) → Node.js · `requirements.txt`/`pyproject.toml` → Python · `Cargo.toml` → Rust · 否则通用

**9.3** 同时扫描目录分层、测试文件位置、代码风格，生成架构文件草稿，用户确认后写入

**9.4** 在 CLAUDE.md 末尾追加架构文件引用（仅一行指针，不含内容）

### 10. 创建 Prompt 库骨架（仅当文件不存在）

在 `docs/prompt/` 下创建 7 个通用 Prompt 骨架 + `prompt-craft.md`（格式规范说明）：

| 文件 | 用途 |
|------|------|
| `code-generation.md` | 根据接口定义生成实现代码 |
| `refactoring.md` | 不改变行为重构代码 |
| `test-generation.md` | 为代码编写测试用例 |
| `testing.md` | 项目测试细节（`/req:test` 读取） |
| `error-diagnosis.md` | 分析错误根因 |
| `pr-review.md` | PR AI 审查 |
| `requirement-structuring.md` | 模糊需求结构化 |

每个文件使用统一的 5 节骨架（适用场景、必备输入、触发方式、输出标准、失败模式），节内容留空供用户填写。

### 11. 生成 release.md

> 模板见 `plugins/req/templates/release-prompt-template.md`

`docs/prompt/release.md` 已存在则跳过。不存在时扫描项目（版本号文件、test/build/lint 命令、CI 配置、构建产物目录），生成预填充草稿，用户确认后写入。

### 12. Skills 初始化

创建 `.claude/skills/` 目录，根据项目类型引导创建 Skill：
- **后端**：引导创建 `migration.md`（声明 migration SQL 目录）
- **前端**：提示无需预置 Skill
- **自定义**：提示可按需创建

---

## 输出要点

成功时输出：
- 目录结构树（本地存储 + 全局缓存路径）
- 已生成的文件列表
- 下一步操作提示（检查架构文件 → 发版配置 → PRD → 分支策略 → 创建需求）

`--reinit` 模式额外标注「已存在」和「新增/补充」的区别。

`--readonly` 模式说明需求文档从全局缓存只读。

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 未提供项目名 | 提示提供 `/req:init my-project` |
| 项目名含非法字符 | 仅允许字母、数字、连字符 |
| 本地目录已存在（无 --reinit） | 提示用 `--reinit` 补充缺失文件 |
| readonly 本地缓存缺失 | 警告但不阻塞，继续初始化 |
| 权限不足 | 提示检查目录权限 |

---

## 用户输入

$ARGUMENTS
