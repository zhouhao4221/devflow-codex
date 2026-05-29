---
name: commit
description: |
  规范提交 - 生成 Conventional Commits 格式的 Git 提交
---

# 规范提交

生成符合 Conventional Commits 规范的 Git 提交，自动关联当前需求编号，便于后续 `/req:changelog` 生成版本说明。

> **Audience:** Engineer
> 此命令**不受仓库角色限制**，readonly 仓库也可执行。
> 不触发缓存同步。

---

## 绝对禁止：在保护分支上执行 git commit

**执行本命令时，第一件事是检查当前分支。如果在保护分支上，绝对不允许执行 git add 或 git commit。必须先切换到功能分支。**

保护分支 = `branchStrategy.mainBranch`（如 main/master）或 `branchStrategy.developBranch`（如 develop）。

未配置 `branchStrategy` 时，不做分支检查。

---

## 命令格式

```
/req:commit [消息]
```

**示例：**
- `/req:commit` — 交互式选择类型并生成提交
- `/req:commit 实现部门渠道关联` — 自动分析变更并生成提交

---

## 执行流程

### 1. 分支检查（在任何 git 操作之前）

读取 `.claude/settings.local.json` 的 `branchStrategy`，未配置时跳过。获取当前分支名，判断是否等于 `mainBranch` 或 `developBranch`：

- **否（feat/*、fix/*、hotfix/* 等）** → 当前分支是安全的，直接跳到步骤 2 正常提交。
- **是** → 当前在保护分支，**禁止提交**，执行以下操作：

**保护分支处理流程：**

按优先级推断当前改动关联的需求：

**第 1 步：从当前改动的文件推断需求**

获取当前已修改的文件列表，与活跃需求（状态为「开发中」或「测试中」）的「文件改动清单」（第十一章 11.3）进行匹配。如果某个需求的改动清单覆盖了当前修改的文件 → 命中该需求。

**第 2 步：从当前对话上下文推断**

如果第 1 步未命中，检查当前对话中是否提及过具体的需求编号（如用户说过"继续做 REQ-001"）。

**第 3 步：兜底扫描活跃需求**

如果前两步都未命中，才扫描所有活跃需求。

---

**推断结果处理：**

**命中 1 个需求** → 自动切换/创建分支：

```
当前在保护分支 <CURRENT>，不允许直接提交。
根据当前改动关联到 <REQ-ID>，自动切换分支...
```

- 需求有 branch 字段 → `git stash` → `git checkout <branch>` → `git stash pop`
- 需求无 branch 字段 → `git stash` → `git checkout -b <新分支> <branchFrom>` → `git stash pop` → 更新需求文档 branch 字段

**命中多个需求** → 列出让用户选择（**没有跳过选项**）：

```
当前在保护分支 <CURRENT>，不允许直接提交。请选择需求：

  1. REQ-001 用户积分规则管理
  2. REQ-002 订单状态流转

请选择：
```

选择后同上切换/创建分支。

**未命中任何需求** → **根据 `branchStrategy` 自动生成分支名并切换**：

1. 根据 `git diff --cached --stat` / `git diff --name-only` 的改动文件与内容，推断：
   - **变更性质**：
     - 有明确修复语义（修复 bug、错误处理、异常分支等） → 使用 `fixPrefix`（默认 `fix/`）
     - 其他（新功能、重构、优化等） → 使用 `featurePrefix`（默认 `feat/`）
   - **英文 slug**：基于改动主题生成 lowercase kebab-case，≤5 词（如 `order-export-approval`、`dept-channel-filter`）

2. 组装分支名：`<prefix><slug>`，若同名分支已存在则追加短 hash 后缀。

3. 展示给用户确认，然后执行：

```
当前在保护分支 <CURRENT>，未关联到活跃需求。
根据当前改动自动生成分支：<新分支名>（基于 <branchFrom>）

确认使用该分支名？（回车确认 / 输入自定义分支名）
```

用户确认后：`git stash` → `git checkout -b <新分支> <branchFrom>` → `git stash pop` → 继续步骤 2。

**注意**：未命中需求时不写入需求文档的 branch 字段（因无需求可写）。需求关联的分支命名仍遵循 `<featurePrefix>REQ-XXX-<english-slug>` / `<fixPrefix>QUICK-XXX-<english-slug>` 规则（见「命中 1 个需求」分支）。

### 2. 检查工作区状态

检查工作区是否有变更及暂存情况。**无变更时：**
```
❌ 没有可提交的变更

请先暂存文件：
- git add <file>       暂存指定文件
- git add -A           暂存所有变更
```

**有未暂存变更时：**
自动将所有变更暂存（`git add -A`），展示暂存结果：

```
已暂存所有变更：
  M  internal/sys/biz/dept_channel.go
  A  internal/sys/model/sys_dept_channel_model.go
  M  internal/sys/controller/v1/sys_dept.go
  M  internal/sys/router.go
```

### 3. Code Review 提醒

提交前展示代码审查提醒（信息展示，不等待回复）：

```
⚠️ 提交前请确认已完成 Code Review
   检查要点：逻辑正确性、安全隐患、错误处理、代码规范、调试代码清理
```

### 4. 检测当前需求

优先从分支名提取 `REQ-XXX` / `QUICK-XXX` 编号；未匹配时回退扫描活跃需求（按 `requirementRole` 决定读本地还是缓存）：命中 1 个自动关联，命中多个列出让用户选，未命中则不关联。

### 5. 分析变更内容

读取 `git diff --cached` 的内容，分析暂存的代码变更：

- 变更性质（新增功能、修复问题、重构等）
- 变更描述（从代码差异中提炼）

### 6. 生成提交信息

#### 6.1 选择提交类型

**auto 模式**：若项目内存在 `.claude/.req-auto` 且 mtime 在 10 分钟内（由上游 `/req:fix --auto` 等命令创建），**跳过交互式选择**，AI 根据 `git diff --cached` 的变更内容自动推断类型（如上游是 `/req:fix` 则固定为"修复"）。

非 auto 模式下，如果用户未提供消息，交互式选择：

```
选择提交类型：

  1. 新功能     新增功能
  2. 修复       问题修复
  3. 重构       代码重构
  4. 优化       性能优化
  5. 文档       文档更新
  6. 测试       测试相关
  7. 构建       构建/工具/依赖
  8. 样式       代码格式（不影响逻辑）
```

如果用户已提供消息，根据变更内容和消息自动推断类型。

#### 6.2 组装提交消息

**格式：**
```
前缀: 描述 (REQ-XXX)
```

**规则：**
- `前缀`：必填，中文类型前缀
- 描述：简洁的中文描述
- `(REQ-XXX)`：自动追加当前需求编号（如有）

**前缀映射：**

| 前缀 | 含义 | Changelog 分类 |
|------|------|---------------|
| `新功能` | 新增功能 | 新功能 (Features) |
| `修复` | 问题修复 | 问题修复 (Bug Fixes) |
| `重构` | 代码重构 | 重构优化 (Refactoring) |
| `优化` | 性能优化 | 性能优化 (Performance) |
| `文档` | 文档更新 | 文档更新 (Documentation) |
| `测试` | 测试相关 | 测试 (Tests) |
| `构建` | 构建/工具/依赖 | 其他变更 (Others) |
| `样式` | 代码格式 | 其他变更 (Others) |

**Issue 关联：** 按 [_issue.md 的 Issue 读取优先级](./_issue.md#issue-编号的读取优先级) 获取 issue 编号：先查需求文档 `issue` 字段，再查分支名 `-iN` 后缀。检测到 issue 编号时，在 commit message 末尾追加 `closes #N`。

**示例：**
```
新功能: 实现部门渠道关联 (REQ-001)
修复: 订单渠道过滤逻辑错误 (REQ-001)
重构: 部门服务层代码 (QUICK-003)
新功能: 实现用户积分规则 (REQ-001) closes #12
优化: 订单查询添加索引 closes #42
文档: 更新 API 文档
构建: 升级依赖版本
```

### 7. 确认并提交

展示完整提交预览：

```
提交预览：

  类型：新功能
  描述：实现部门渠道关联
  关联：REQ-001

  完整消息：
  新功能: 实现部门渠道关联 (REQ-001)

  变更文件（4）：
  A  internal/sys/model/sys_dept_channel_model.go
  A  internal/sys/store/sys_dept_channel_store.go
  A  internal/sys/biz/dept_channel.go
  M  internal/sys/router.go

```

展示预览后直接执行提交（默认直通；仅当项目内存在 `.claude/.req-confirm-commit` marker 时，Hook 才会弹出原生确认对话框——该 marker 由 Claude 按用户自然语言意图维护）。

### 8. 提交结果

```
✅ 提交成功！

  commit abc1234
  新功能: 实现部门渠道关联 (REQ-001)

  4 files changed, 156 insertions(+), 3 deletions(-)

是否创建 PR？
- /req:pr           创建 PR
- 继续开发          稍后再说
```

---

## Breaking Change 支持

如果变更包含破坏性改动，在前缀后添加 `!` 标记：

```
新功能!: 重构部门 API 返回结构 (REQ-005)
```

交互式流程中增加确认：

```
如果变更涉及 API 返回结构变更、数据库 schema 变更等，自动标记为 Breaking Change。
```

---

## 多行提交消息

对于需要详细说明的提交，支持添加 body：

```
新功能: 实现部门渠道关联 (REQ-001)

- 新增 sys_dept_channel 表及 Model/Store 层
- 实现渠道范围校验逻辑
- 添加获取可选渠道接口
```

当变更涉及多个文件或逻辑复杂时，自动添加 body 说明。

---

## 与 Changelog 的对应关系

本命令生成的提交消息使用中文前缀，`/req:changelog` 可直接解析：

| 提交格式 | Changelog 分类 |
|---------|---------------|
| `新功能: 描述 (REQ-XXX)` | 新功能 (Features) |
| `修复: 描述 (REQ-XXX)` | 问题修复 (Bug Fixes) |
| `重构: 描述` | 重构优化 (Refactoring) |
| `优化: 描述` | 性能优化 (Performance) |
| `文档: 描述` | 文档更新 (Documentation) |
| `测试: 描述` | 测试 (Tests) |
| `构建/样式: 描述` | 其他变更 (Others) |

**需求编号关联**：commit message 中的 `(REQ-XXX)` / `(QUICK-XXX)` 会被 changelog 自动提取并归入「关联需求」章节。

## 用户输入

$ARGUMENTS
