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

## 参数

- `project-name`: 项目名称（建议使用 kebab-case，如 `my-saas-product`）
- `--reinit`: 重新初始化模式，为已有项目补充缺失的目录和文件（不覆盖已有内容）
- `--readonly`: 以只读仓库角色初始化——只创建模板文件和 docs/prompt/ 等工具文件，不创建本地需求目录和全局缓存

---

## 执行流程

### 1. 解析参数

```
参数: $ARGUMENTS
项目名称: 从参数中提取（排除 --reinit / --readonly）
重新初始化模式: 参数包含 --reinit 时为 true
仓库角色: 见下方判断逻辑
本地存储路径: docs/requirements
全局缓存路径: ~/.claude-requirements/projects/<project-name>
```

**判断逻辑**：
- 若参数包含 `--reinit`，进入重新初始化模式（只补充缺失内容，不覆盖已有文件）
- **仓库角色**按以下优先级确定：
  1. 参数包含 `--readonly` → `readonly`
  2. `.claude/settings.local.json` 中已有 `requirementRole: "readonly"` → `readonly`（--reinit 时自动继承）
  3. 否则 → `primary`

### 2. 创建本地存储目录

**primary**：在 `docs/requirements/` 下创建 `active/`、`completed/`、`modules/`、`templates/` 四个子目录。

**readonly**：只创建 `docs/requirements/templates/`，跳过 `active/`、`completed/`、`modules/`——readonly 仓库不在本地存储需求文档。

### 3. 复制模板文件到本地

将插件 `templates/` 下的模板文件复制到 `docs/requirements/templates/`（**primary 和 readonly 均执行**；仅当目标文件不存在时复制，`--reinit` 模式保护已有文件）。

复制的文件：`requirement-template.md`、`quick-template.md`、`prd-template.md`、`module-template.md`。

### 4. 生成 PRD 文档（仅 primary）

**readonly 仓库跳过此步骤。**

`docs/requirements/PRD.md` 不存在时，从 prd-template.md 复制并替换 `{{PROJECT_NAME}}`、`{{DATE}}` 变量。

### 4.1 创建「快速修复」模块（仅 primary）

**readonly 仓库跳过此步骤。**

`docs/requirements/modules/quick-fix.md` 不存在时，使用 Write 工具生成模块文档（含概述、核心功能、业务规则、相关需求、变更记录各章节）。

### 5. 创建全局缓存目录（仅 primary）

**readonly 仓库跳过此步骤**——readonly 仓库读取已有缓存，不创建新缓存。

primary：在 `~/.claude-requirements/projects/<project-name>/` 下创建 `active/`、`completed/`、`modules/`、`templates/` 目录，将本地模板、PRD、快速修复模块同步过去。

### 6. 更新全局索引（仅 primary）

**readonly 仓库跳过此步骤。**

primary：更新 `~/.claude-requirements/index.json`：

```json
{
  "projects": {
    "<project-name>": {
      "created": "2026-01-08",
      "primaryRepo": "/path/to/current/repo",
      "repos": ["/path/to/current/repo"]
    }
  }
}
```

### 7. 绑定当前仓库

> 写入规范见 [_storage.md](./_storage.md#settings-文件写入规范)。

读取已有 `.claude/settings.json`，合并以下字段后写回（不覆盖已有的 `branchStrategy` 等字段）：

**primary**：
```json
{
  "requirementProject": "<project-name>",
  "requirementRole": "primary"
}
```

**readonly**：
```json
{
  "requirementProject": "<project-name>",
  "requirementRole": "readonly"
}
```

### 8. 生成项目架构文件

扫描项目现有结构，自动生成 `docs/prompt/architecture.md`，并在 CLAUDE.md 中添加引用。
`/req:dev` 和 `/req:test` 运行时会自动读取该文件，无需手动传入。

#### 8.1 检查是否已有架构文件

```
docs/prompt/architecture.md 已存在 → 跳过，不覆盖
CLAUDE.md 中已包含架构章节       → 跳过，不覆盖
```

#### 8.2 扫描项目结构

按以下优先级检测技术栈：

| 检测文件 | 推断技术栈 |
|---------|----------|
| `go.mod` | Go 后端 |
| `pom.xml` / `build.gradle` | Java 后端 |
| `package.json`（含 `next` / `nuxt` / `vite`） | 前端 |
| `package.json`（含 `express` / `fastify` / `nest`） | Node.js 后端 |
| `requirements.txt` / `pyproject.toml` | Python 后端 |
| `Cargo.toml` | Rust |
| 均未找到 | 通用 |

同时扫描：
- 顶层及二级目录结构（推断分层）
- 测试文件位置（`*_test.go` / `*.test.ts` / `tests/` 等）
- 已有代码风格样例（命名、错误处理模式）

#### 8.3 生成架构文件

基于扫描结果，AI 生成 `docs/prompt/architecture.md`，结构固定为：

```markdown
## 技术栈
<!-- AI 从扫描结果填入，如：Go 1.22 · Gin · GORM · MySQL 8 -->

## 分层架构
<!-- AI 从目录结构推断，按开发顺序排列 -->
| 层 | 目录 | 职责 |
|----|------|------|
| ...扫描到的分层... | | |

## 文件命名
<!-- AI 从现有文件推断 -->

## 开发规范
<!-- AI 从现有代码推断，无代码时留空占位 -->

## 测试规范
<!-- AI 从测试文件位置推断 -->
- 测试目录：...
- 运行命令：...
```

生成后展示内容，请用户确认：

```
已扫描项目结构，生成架构文件草稿：

   技术栈：Go 1.22 · Gin · GORM · MySQL
   分层：Model → Store → Biz → Controller → Router
   测试：*_test.go，运行 go test ./...

   草稿已写入 docs/prompt/architecture.md

   内容是否准确？(y/n，默认 y，n 则打开文件手动修改)
```

#### 8.4 在 CLAUDE.md 中添加引用

在 CLAUDE.md 末尾追加一行引用（文件不存在时创建）：

```markdown
## 项目架构

详见 `docs/prompt/architecture.md`，`/req:dev` 和 `/req:test` 会自动读取。
```

CLAUDE.md 不包含架构内容本身，只持有指针。

#### 8.5 已有架构文件时

```
✅ docs/prompt/architecture.md 已存在，跳过生成
```

#### 8.6 创建 Prompt 库骨架

在 `docs/prompt/` 中创建通用 Prompt 文件骨架，仅当文件不存在时创建（--reinit 同样保护已有文件）：

| 文件 | 用途说明（写入 `>` 行） |
|------|------|
| `code-generation.md` | 根据接口定义生成实现代码 |
| `refactoring.md` | 在不改变行为的前提下重构代码结构 |
| `test-generation.md` | 为代码编写测试用例 |
| `testing.md` | 项目测试细节：运行命令、文件位置、环境启动（`/req:test` 读取此文件） |
| `error-diagnosis.md` | 分析错误根本原因并给出修复方向 |
| `pr-review.md` | PR 初轮 AI 审查 |
| `requirement-structuring.md` | 将模糊需求转为结构化输入 |

每个文件使用统一的 5 节骨架，节内容留空，由用户与 AI 协作填写：

```markdown
# <中文标题>

> <用途说明>

## 什么时候用

<!-- 适用场景 + 不适合的情况 -->

## 必备输入

<!-- 触发前需要准备的具体清单，这是最重要的部分 -->

## 触发方式

<!-- 单次任务模板（如何构造 prompt）+ 写入 CLAUDE.md 的推荐做法 -->

## 优质输出标准

<!-- 好的输出长什么样，用于质量判断 -->

## 常见失败模式

| 问题 | 原因 | 解决方案 |
|------|------|----------|
```

同时创建 `docs/prompt/prompt-craft.md`，说明上述格式规范本身（供团队成员新建 prompt 时参考）。

`architecture.md` 已由步骤 8.3 生成，此处跳过。

#### 8.7 引导生成 release.md

**`docs/prompt/release.md` 已存在时**：

```
✅ docs/prompt/release.md 已存在，跳过生成
```

**不存在时**，扫描项目并生成预填充草稿（非空白骨架）：

**扫描目标：**

| 扫描对象 | 推断内容 |
|---------|---------|
| `package.json` → `version` / `scripts.test` / `scripts.build` / `scripts.lint` | 版本号文件路径 + 前置检查命令 |
| `plugin.json` / `marketplace.json` / `pyproject.toml` / `Cargo.toml` | 版本号文件路径 |
| `go.mod` + git tag 格式 | 版本号来源（Go 模块通常不写入文件，说明来源） |
| `Makefile` → `test` / `build` / `lint` targets | 前置检查命令 |
| `.github/workflows/*.yml` / `Jenkinsfile` | 前置检查是否有 CI 门控 |
| `dist/` / `build/` 目录或 glob 输出 | 额外附件候选 |

**基于扫描生成草稿**（三个可推断章节填入发现值，不可推断则留注释）：

- **版本号文件**：列出扫描到的文件 + 字段名
- **发版前检查**：列出扫描到的 test/build/lint 命令（无则留注释示例）
- **发版后步骤**：始终留空（项目特有，AI 无法推断），注释提示填写通知/部署事项
- **额外附件**：若发现 `dist/` 或构建产物 glob 则填入，否则留注释

展示草稿并请用户确认：

```
已扫描项目，生成 release.md 草稿：

   版本号文件：package.json → version
   发版前检查：npm test, npm run build
   额外附件：未发现构建产物目录

   是否写入 docs/prompt/release.md？(y/n/e，默认 y，e 先预览完整内容)
```

- `y`（默认）→ 直接写入
- `n` → 跳过，提示后续可手动创建（模板位于插件 `templates/release-prompt-template.md`）
- `e` → 输出完整草稿内容供审阅，再次询问 y/n

### 9. 项目 Skills 初始化

创建 `.claude/skills/` 目录（不存在时），并根据项目类型引导创建常用 Skill 文件。

#### 9.1 创建目录

创建 `.claude/skills/` 目录（不存在时）。

#### 9.2 引导创建 Skill 文件

**目录为空时**，根据步骤 8 选择的项目类型展示对应提示：

**后端项目（Go / Java / 其他服务端）**：

```
后端项目通常需要声明 migration SQL 目录路径：

   .claude/skills/migration.md
   /req:dev 生成数据库变更 SQL 时会自动读取

   是否创建？(y/n，默认 y)
```

用户选择 `y` → 创建 `.claude/skills/migration.md`：

```markdown
# Migration Skill

声明项目的 migration SQL 存放目录，供 /req:dev 自动使用。

- **MIGRATIONS_DIR**: `db/migrations`
```

并提示用户修改路径：

```
✅ 已创建 .claude/skills/migration.md
   请将 MIGRATIONS_DIR 修改为项目实际路径，如：
   - db/migrations（GORM 默认）
   - database/migrations（Laravel 默认）
   - src/migrations（自定义）
```

**前端项目**：

```
✅ 已创建 .claude/skills/ 目录

   前端项目通常不需要预置 Skill 文件。
   如有项目特有约定（组件规范、接口路径约定等），
   可在此目录创建 .md 文件，/req:dev 会自动读取。
```

**自定义项目**：

```
✅ 已创建 .claude/skills/ 目录

   将项目特有知识写成 Skill 文件放在此目录，/req:dev 和 /req:test 会自动读取。
   示例：
   - migration.md  — 声明数据库 migration 目录
   - testing.md    — 声明项目特有的测试约定
```

**目录已有文件时**，列出现有 Skill 并跳过引导：

```
✅ .claude/skills/ 已有以下 Skill 文件：
   - migration.md
   跳过 Skills 引导
```

### 10. 输出结果

**primary 初始化成功**：
```
✅ 项目 "<project-name>" 初始化成功！

本地存储（主存储，纳入 git）:
   docs/requirements/
   active/         # 进行中的需求
   completed/      # 已完成的需求
   modules/        # 模块文档
     quick-fix.md  # 快速修复模块（预置）
   templates/      # 模板文件
     requirement-template.md  # 需求模板
     quick-template.md        # 快速修复模板
     prd-template.md          # PRD 模板
   PRD.md          # 产品需求文档

全局缓存（同步副本，跨仓库共享）:
   ~/.claude-requirements/projects/<project-name>/

当前仓库已绑定到此项目（role: primary）

已生成 PRD 文档: docs/requirements/PRD.md
   请填写以下关键内容:
   - 产品愿景和目标用户
   - 核心功能列表（P0/P1/P2 优先级）
   - 技术架构选型
   - 版本规划和里程碑

下一步:
   1. 检查 docs/prompt/architecture.md 内容是否准确
   2. 补充 docs/prompt/release.md 中「发版后步骤」章节（通知渠道、部署触发等）
   3. 确认 .claude/skills/migration.md 中的路径是否正确（如已创建）
   4. 按需补充 docs/prompt/ 中各 Prompt 文件的内容（与 AI 协作填写）
   5. 编辑 PRD.md 完善产品规划
   6. /req:branch init  配置分支策略
   7. /req:new <标题>   创建具体需求
```

**readonly 初始化成功**（使用 `--readonly`）：
```
✅ 项目 "<project-name>" 初始化成功！（只读仓库）

本地工具文件（纳入 git）:
   docs/requirements/templates/   # 模板文件（供 /req:new 使用）
     requirement-template.md
     quick-template-template.md
     prd-template.md
     module-template.md
   docs/prompt/                   # 项目架构和 Prompt 库
   .claude/skills/                # 项目 Skill 扩展

需求文档读取来源（只读）:
   ~/.claude-requirements/projects/<project-name>/
   （由 primary 仓库写入并同步）

当前仓库已绑定到此项目（role: readonly）

提示:
   - /req:new、/req:dev、/req:test 等命令正常可用
   - 需求文档从全局缓存只读，不写入本地 docs/requirements/
   - 如需写入需求文档，请在 primary 仓库操作
```

**primary 重新初始化成功**（使用 `--reinit`，role = primary）：
```
✅ 项目 "<project-name>" 重新初始化完成！

检查并补充缺失内容:
   docs/requirements/active/      目录已存在
   docs/requirements/completed/   目录已存在
   docs/requirements/modules/     目录已存在
   + docs/requirements/templates/   模板目录
   + docs/requirements/templates/requirement-template.md  已复制
   + docs/requirements/templates/quick-template.md        已复制
   + docs/requirements/templates/prd-template.md          已复制
   + docs/requirements/modules/quick-fix.md  已生成（新增）
   + docs/requirements/PRD.md       已生成（新增）
   docs/prompt/architecture.md    已存在（或缺失时触发扫描+生成，见步骤 8）
   docs/prompt/ 通用 Prompt 文件  已检查（7 个骨架 + prompt-craft.md，缺失时补创建）
   docs/prompt/release.md         已存在（或缺失时扫描项目引导生成，见步骤 8.7）
   .claude/skills/                已检查（如为空可按引导创建 Skill 文件）

当前仓库已绑定到此项目（role: primary）

提示: --reinit 模式不会覆盖已有文件，仅补充缺失内容
```

**readonly 重新初始化成功**（使用 `--reinit`，role = readonly）：
```
✅ 项目 "<project-name>" 重新初始化完成！（只读仓库）

检查并补充缺失内容:
   + docs/requirements/templates/              模板目录
   + docs/requirements/templates/requirement-template.md  已复制
   + docs/requirements/templates/quick-template.md        已复制
   + docs/requirements/templates/prd-template.md          已复制
   docs/prompt/architecture.md    已存在（或缺失时触发扫描+生成，见步骤 8）
   docs/prompt/ 通用 Prompt 文件  已检查（缺失时补创建）
   docs/prompt/release.md         已存在（或缺失时扫描项目引导生成，见步骤 8.7）
   .claude/skills/                已检查

当前仓库已绑定到此项目（role: readonly）

提示: readonly 仓库不创建 active/completed/modules/ 和全局缓存
```

**项目已存在时**（未使用 `--reinit`）：
```
⚠️ 项目 "<project-name>" 已存在

项目状态:
   - 活跃需求: X 个
   - 已完成: Y 个
   - 主仓库: /path/to/primary/repo
   - 关联仓库: Z 个

若要为历史项目补充缺失文件，请使用:
   /req:init <project-name> --reinit
```

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 未提供项目名 | 提示：请提供项目名称，如 `/req:init my-project` |
| 项目名包含非法字符 | 提示：项目名只能包含字母、数字、连字符 |
| 本地目录已存在（无 --reinit） | 提示：本地需求目录已存在，可使用 `--reinit` 补充缺失文件 |
| readonly 仓库执行时全局缓存不存在 | 打印提示（非阻塞）：`⚠️ 全局缓存 ~/.claude-requirements/projects/<name>/ 不存在，请先在 primary 仓库执行 /req:init`；继续完成本地工具文件初始化 |
| 权限不足 | 提示：无法创建目录，请检查权限 |

---

## 用户输入

$ARGUMENTS
