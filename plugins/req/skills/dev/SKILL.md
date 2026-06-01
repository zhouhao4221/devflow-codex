---
name: dev
description: 需求开发 - 启动或继续开发
---

# 需求开发

启动或继续需求开发，先生成实现方案，确认后逐步实现。

> **Audience:** Engineer
> 存储路径规则见 `_storage.md`

## 命令格式

```
/req:dev [REQ-XXX] [--reset]
```

- 省略编号时自动选择「评审通过」或「开发中」的需求
- `--reset` 强制从头开始

---

## 执行流程

### 1. 选择需求

- 指定编号 → 使用该需求
- 未指定 → 查找可开发需求（状态为评审通过/开发中）
- 多个候选 → 交互式选择（列出编号列表，用户输入编号）

### 2. 前置检查（严格执行）

**根据需求类型区分检查规则**：

#### 正式需求 (REQ-XXX) - 必须通过评审

| 当前状态 | 处理方式 |
|---------|---------|
| 草稿 | 拒绝开发，提示：`需求尚未评审，请先执行 /req:review 提交评审` |
| 待评审 | 拒绝开发，提示：`需求正在评审中，请等待评审通过后再开发` |
| 评审驳回 | 拒绝开发，提示：`需求评审未通过，请先修改后重新提审：/req:edit → /req:review` |
| 评审通过 | 允许开发 |
| 开发中 | 允许继续开发 |
| 测试中 | 允许开发（可能是修复测试问题） |
| 已完成 | **readonly 仓库**：允许开发（需求在主仓库已完成，只读仓库可基于其开发）；**primary 仓库**：警告提示：`需求已完成，如需修改请创建新需求` |

#### 快速修复 (QUICK-XXX) - 跳过评审

| 当前状态 | 处理方式 |
|---------|---------|
| 草稿 | 允许开发（方案确认后直接开发） |
| 方案确认 | 允许开发 |
| 开发中 | 允许继续开发 |
| 已完成 | **readonly 仓库**：允许开发；**primary 仓库**：警告提示：`需求已完成，如需修改请创建新需求` |

**重要**：正式需求 (REQ) 未通过评审**不能**开始开发；快速修复 (QUICK) 跳过评审环节；readonly 仓库允许开发已完成的需求。

### 2.5 分支管理

> 仅 `primary` 仓库执行，`readonly` 仓库跳过此步骤。
> 分支策略配置见 [_branch.md](./_branch.md)。

#### 工作区检查

执行 `git status --porcelain`，若有未提交的改动：
- 列出改动文件，提示用户先 commit 或 stash
- **终止流程**，不得静默跳过

#### 读取分支策略

```python
strategy = read_settings("branchStrategy")

if strategy:
    MAIN_BRANCH = strategy["mainBranch"]
    BRANCH_FROM = strategy["branchFrom"]  # 功能分支的拉取基准
    FEATURE_PREFIX = strategy["featurePrefix"]
    FIX_PREFIX = strategy["fixPrefix"]
else:
    # 未配置策略，使用默认行为
    MAIN_BRANCH = detect_main_branch()  # 自动检测
    BRANCH_FROM = MAIN_BRANCH
    FEATURE_PREFIX = "feat/"
    FIX_PREFIX = "fix/"
```

**自动检测主分支**（未配置策略时的回退逻辑）：
1. `git symbolic-ref refs/remotes/origin/HEAD` → 提取分支名
2. 失败 → `git rev-parse --verify origin/main`，再失败 → `origin/master`
3. 都失败 → 回退 `main`

#### 分支处理

**情况 A：需求文档元信息 `branch` 字段有值（非 `-`）**

1. 读取 `branch` 字段值，按逗号拆分得到分支列表
2. **单个分支**：直接 checkout
   - 本地存在 → `git checkout <branch>`
   - 仅远程存在 → `git checkout -b <branch> origin/<branch>`
   - 都不存在 → `git checkout -b <branch> <BRANCH_FROM>`
3. **多个分支**：展示列表，让用户选择切入哪一个：
   ```
   此需求有多个开发分支，请选择：
   1. feat/REQ-025-backend
   2. feat/REQ-025-frontend
   （输入编号，或输入新分支名新建）
   ```
   选择后按单分支逻辑处理

**情况 B：`branch` 字段为 `-` 或缺失（首次进入）**

1. AI 根据需求标题生成英文 slug（lowercase kebab-case，最多 5 词，仅 ASCII）
2. 拼接分支名（使用策略配置的前缀）：
   - REQ-XXX → `<FEATURE_PREFIX>REQ-XXX-<slug>`（默认 `feat/REQ-XXX-<slug>`）
   - QUICK-XXX → `<FIX_PREFIX>QUICK-XXX-<slug>`（默认 `fix/QUICK-XXX-<slug>`）
3. 若需求文档元信息 `issue` 字段非 `-` 且非空（如 `#12`），在分支名末尾追加 `-i<N>`（如 `-i12`），参见 [_issue.md 的 Issue 与分支关联](./_issue.md#issue-与分支提交的关联)
4. 展示分支名供用户确认（可修改）：
   ```
   将创建开发分支：feat/REQ-001-user-points-i12
   基于分支：main（来源：branchStrategy.branchFrom）
   ```
4. 用户确认后：
   - `git checkout -b <branch> <BRANCH_FROM>`
   - 将分支名写入需求文档元信息的 `branch` 字段

### 3. 加载上下文

读取需求文档的需求定义章节：需求描述、功能清单、业务规则、使用场景、接口需求、测试要点

### 4. 生成实现方案（Plan Mode）

> **前置**：读取项目 CLAUDE.md 的「项目架构」章节，获取分层架构、目录结构、开发规范。
> 缺少时发出警告（见 [_claude-md.md](./_claude-md.md)）。

进入 Plan Mode，基于需求文档和 CLAUDE.md 架构信息生成实现方案，填充「十一、实现方案」章节：

- **11.1 数据模型**：新增/修改的表、字段说明、实体关系
- **11.2 API 设计**：基于第五章接口需求 + 项目代码 + CLAUDE.md API 风格，生成具体接口方案（路径、方法、请求/响应字段、错误码）
- **11.3 文件改动清单**：按 CLAUDE.md 分层架构表的顺序列出需要新增/修改的文件
- **11.4 实现步骤**：按 CLAUDE.md 分层架构的顺序拆解开发步骤

如果需求文档「十一、实现方案」已有完整内容（非占位文本），直接展示并请用户确认。

### 5. 更新状态和实现方案

> 仅 `primary` 仓库执行，`readonly` 仓库跳过此步骤（不修改需求文档）。

1. 首次进入 → 状态改为「开发中」
2. 将实现方案写回需求文档的「十一、实现方案」章节（11.1 数据模型、11.2 API 设计、11.3 文件改动清单、11.4 实现步骤）

### 6. 显示开发概览

```
REQ-001 部门渠道关联

进度：2/6 功能点已完成
功能清单：
- [x] Model/Store 层
- [x] 渠道范围校验
- [ ] 获取可选渠道接口 ← 当前
- [ ] 订单数据过滤
...
```

### 7. 生成任务

根据实现步骤生成 TodoWrite 任务列表

### 8. 逐步实现

按 CLAUDE.md 分层架构表定义的顺序逐层开发。

实时检查（根据 CLAUDE.md「开发规范」章节）：
- 文件命名规范
- CLAUDE.md 中定义的其他规范项

### 9. 开发中修改需求文档

> 仅 `primary` 仓库执行，`readonly` 仓库跳过此步骤（不修改需求文档）。

开发过程中用户可能需要修改需求文档，支持两种方式：

**方式一：用户主动提出**

用户在开发过程中说"更新一下功能清单"、"业务规则要加一条"、"接口需求有变化"等，直接修改对应章节。

**方式二：AI 发现偏差时主动提示**

开发过程中 AI 发现实际情况与需求文档不一致时，主动提示用户：

| 发现场景 | 提示内容 |
|---------|---------|
| 代码中发现需求未描述的业务规则 | `发现新的业务规则：xxx，是否补充到第三章？` |
| 实现方案需要新增功能点 | `实现中需要额外功能点：xxx，是否补充到第二章？` |
| 接口设计与需求描述不符 | `接口需求有调整：xxx，是否更新第五章？` |
| 实现步骤需要调整 | 直接更新第十一章，无需确认 |

**修改规则**：
- **一~六章（需求定义）**：修改后提示用户确认，并在第八章变更记录中追加一条
- **十章（实现方案）**：开发过程中可直接更新，不需要变更记录
- **格式约束不变**：修改仍须遵循模板结构，不得增删章节

### 10. 进度更新

每完成一步：更新任务状态（TodoWrite）。`primary` 仓库同时更新需求文档 checkbox，`readonly` 仓库仅更新任务状态，不修改需求文档。

### 11. 开发完成

```
开发完成！
- 功能点：6/6
- 新增/修改文件统计

下一步：
- /req:pr REQ-001 - 创建 PR（根据仓库类型自动创建或提示命令）
- /req:test REQ-001 - 进入测试
- /req:commit - 提交代码
```

> 如果配置了 `branchStrategy.repoType`（gitea/github），会提示可以创建 PR。
> 未配置时不显示 PR 相关提示。

---

## 用户输入

$ARGUMENTS
