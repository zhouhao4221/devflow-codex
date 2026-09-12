---
name: fix
description: 轻量修复 - 无文档的 bug 修复流程，AI 辅助定位问题
---

# 轻量修复

创建修复分支，AI 辅助分析定位 bug，修复后直接提交和 PR。不创建需求文档。

> **Audience:** Engineer
> 此命令**不受仓库角色限制**，readonly 仓库也可执行。
> 不触发缓存同步（无需求文档）。
>
> **CLI 优先级**：GitHub 用 `gh`；Gitea 按 [`_gitea_cli.md`](../../shared/_gitea_cli.md) 检测 `tea`，可用即走 `tea`，否则回退本文 curl 示例。

## 命令格式

```
/req:fix <问题描述> [--from-issue=#编号] [--auto]
```

**`--auto` 非交互模式**：跳过修复方案确认、issue 关闭询问，修复完成后自动串联 `/req:commit` + `/req:pr`。
用于小 bug 一键走完，**代价是放弃方案/提交前的 review 机会**；Codex 的权限审批仍按运行环境执行。

示例：
- `/req:fix 登录超时后 token 未清除`
- `/req:fix 订单列表分页数据重复`
- `/req:fix 导出 Excel 中文文件名乱码`
- `/req:fix --from-issue=#42` - 从 issue 读取问题描述后分析
- `/req:fix 导出 Excel 中文文件名乱码 --auto` - 一键走完修复并创建 PR

---

> 涉及子代理的步骤先按需读取 [_delegate.md](../../shared/_delegate.md)：按运行环境能力和任务独立性决定委派，不可用时主会话完成同一工作。用户已有授权和分支偏好优先，不重复询问已确认方案。

## 执行流程

### 0. （可选）从 issue 读取问题描述

若命令带 `--from-issue=#N`，按 [_issue.md 的 Issue 拉取规范](../../shared/_issue.md#issue-拉取规范) 拉取 issue，把 issue 标题 + 正文拼成用户问题描述传入步骤 1。

本命令不创建需求文档，issue 编号通过**分支名 `-iN` 后缀**持久化（步骤 2.3 创建分支时追加），供 `/req:commit`、步骤 5 关闭 issue 等后续操作识别。参见 [_issue.md 的 Issue 与分支关联](../../shared/_issue.md#issue-与分支提交的关联)。

用户同时提供了描述和 `--from-issue` 时，以用户描述为主，issue 内容作为补充上下文。

### 1. AI 辅助分析 bug

> Read `docs/prompt/architecture.md` 了解分层结构和目录布局；缺失则回退 AGENTS.md 的「项目架构」章节（兼容旧项目），都没有静默继续。
> Read `docs/prompt/error-diagnosis.md`，存在则按其规范（必备输入、根因判定标准、常见失败模式）约束定位；缺失静默跳过。
> **此阶段在当前分支上进行，不创建新分支。**

根据用户描述的问题，AI 进行定位分析：

#### 1.1 问题分析

```
Bug 分析：登录超时后 token 未清除

问题理解：
- 现象：用户登录超时后，本地 token 未被清除，导致后续请求携带过期 token
- 影响范围：认证流程、请求拦截器

可能涉及的代码：
```

#### 1.2 定位相关文件

存在可独立执行的定位任务时，按共享规则委派 `code-scout` 搜索代码库（prompt 给：1.1 的现象与影响范围、报错信息/符号名、已加载的 architecture.md 或 AGENTS.md 分层目录摘要），主会话拿到清单后只精读高/中相关的关键行段，用于 1.4 根因分析；规则见 [`_delegate.md`](../../shared/_delegate.md)。范围小或不可委派时由主会话定位。展示格式：

```
相关文件定位：

| 文件 | 相关度 | 原因 |
|------|-------|------|
| src/utils/auth.ts | 高 | token 存取逻辑 |
| src/interceptors/request.ts | 高 | 请求拦截，超时处理 |
| src/store/user.ts | 中 | 用户状态管理 |
```

#### 1.3 关联需求匹配（自动，低成本）

**目的**：找出可能引入此 bug 的需求，获取业务上下文辅助定位。

**流程**（只读索引 + 按需读正文，控制 token 消耗）：

1. 读 `docs/requirements/INDEX.md`（~500 token）
2. 用 bug 相关文件路径 + 关键词在 INDEX.md 中模糊匹配（标题含关键词 或 模块与 bug 相关 → 命中）
3. 命中时仅读该需求的「十一、实现方案 - 文件改动清单」（~1k token/个，最多 2 个）；未命中静默跳过

**命中时展示**：

```
关联需求：

| 需求 | 标题 | 关联原因 |
|------|------|---------|
| REQ-003 | 登录认证优化 | 修改了 src/interceptors/request.ts |

此 bug 可能由 REQ-003 引入，已读取其文件改动清单辅助定位。
```

**未命中时**：静默跳过，不输出任何内容，不消耗额外 token。

**成本控制**：

| 步骤 | Token 消耗 | 条件 |
|------|-----------|------|
| 读 INDEX.md | ~500 | 始终执行 |
| 匹配关键词 | ~0 | AI 内部处理 |
| 读命中需求节选 | ~1k/个 | 仅命中时，最多 2 个 |
| **总计** | **500 ~ 2500** | 远低于全量读取（~50k） |

#### 1.4 根因分析

AI 综合代码搜索结果和关联需求上下文，给出根因判断：

```
根因分析：

在 src/interceptors/request.ts:45，响应拦截器捕获 401 状态码时
调用了 router.push('/login')，但未调用 removeToken()。
（REQ-003 登录认证优化 新增了 401 拦截逻辑，但遗漏了 token 清除）

建议修复：在跳转登录页前清除 token。
```

#### 1.5 修复建议

```
修复建议：

1. src/interceptors/request.ts
   - 在 401 处理分支中，跳转前调用 removeToken()
   - 验收：<可执行命令 | 可观察行为>

2. 建议同时检查：
   - token 过期的其他入口（如定时刷新失败）

是否按以上方案修复？（可以补充说明或调整方向）
```

每条修复附「验收」行，写法见 [`_verify.md`](../../shared/_verify.md)。

**`--auto` 模式**：跳过"等待用户确认"，直接展示方案后进入步骤 2。

**非 `--auto` 模式**：尚未获得方案授权时等待确认，已有等价授权则继续。用户可以：
- 确认方案 → 进入步骤 2
- 补充信息 / 调整方向 → AI 重新分析
- 放弃 → 结束，不创建分支

---

### 2. 处理修复分支

先遵循用户和项目 AGENTS.md 的分支约定；明确要求直接在主分支工作时跳过创建分支，保护已有改动后进入步骤 3。

> **用户确认修复方案后**才创建分支，避免分析后放弃导致残留空分支。

#### 2.1 工作区检查

有未提交改动时终止，提示先 commit 或 stash。

#### 2.2 读取分支策略

从 `branchStrategy` 读取 `mainBranch`、`branchFrom`（缺省同 mainBranch）、`fixPrefix`（缺省 `fix/`）；未配置时自动检测主分支。

#### 2.3 创建分支

AI 根据问题描述生成英文 slug（lowercase kebab-case，最多 5 词）。

**有 `--from-issue=#N`**：分支名末尾追加 `-i<N>`（参见 [_issue.md 的 Issue 与分支关联](../../shared/_issue.md#issue-与分支提交的关联)）。

```
创建修复分支：fix/login-token-not-cleared-i42
   基于：main（来源：branchStrategy.branchFrom）
```

**无 `--from-issue`**：不加 issue 后缀。

```
创建修复分支：fix/login-token-not-cleared
   基于：main（来源：branchStrategy.branchFrom）
```

fetch `branchFrom`，从远端创建并切换到新分支（有 issue 时分支名末尾追加 `-i<N>`）。

---

### 3. 执行修复

AI 按确认的方案修改代码。

> bug 修复通常范围集中，**默认主会话自己改**。只有当同一处根因要在多个互不依赖的单元里重复同一类改动（如同一个错误用法散落在多个模块）时，才按 [`_delegate.md`](../../shared/_delegate.md) 的「实施准入」并行派 `impl-worker`；每个单元包含实现与对应测试，由主会话复核实际改动和当前验证证据后再继续。

修改完成后按 `_verify.md`（步骤 1.5 已链接）执行验证：编译/lint → 相关测试回归（派 `test-runner`）→ 覆盖判断与必要 UT。失败处理和 `--auto` 验证要求统一按共享规则执行，未解决的必需检查不进入步骤 4。

---

### 4. 修复完成提示

```
✅ 修复完成！

分支：fix/login-token-not-cleared
修改文件：
- src/interceptors/request.ts（+3 -1）

验证结果：
- 编译：✓ | ✗ | 未配置
- lint：✓ | ✗ | 未配置
- 测试：n/m 通过（<命令>） | 未配置
- 无测试覆盖：<文件> | 无
- 手动验证：
  - [ ] <可观察行为>
- 测试改动：<用例与原因> | 无

后续操作：
- /req:commit - 提交修复代码
- /req:pr - 创建 PR
```

「验证结果」段的字段含义与缺项写法见 `_verify.md`，整段不得省略。

若来自 `--from-issue=#N`，在后续操作提示中追加：
```
提交时建议在 commit message 末尾添加 closes #N 以自动关联 issue
```

---

### 4.5 （仅 `--auto` 模式）自动串联 commit + PR

非 `--auto` 模式跳过本步骤，结束命令。

`--auto` 模式下，步骤 4 展示完成提示后**立即继续执行**，不等待用户输入。

#### 4.5.0 传递本次授权

把用户明确指定的 `--auto` 作为本次调用上下文传给 commit/pr。不得创建或依赖 marker 绕过 Codex 权限审批。若用户明确要求不创建 PR，按其要求提交/推送后结束。

#### 4.5.1 调用 `/req:commit` 流程

参见 [commit.md](../commit/SKILL.md)：

- 仅暂存本次任务的变更，保留用户无关改动
- 从当前分支名 `fix/<slug>-iN` 中不含 REQ/QUICK 编号 → commit message 不加 `(REQ-XXX)`
- 若有 `--from-issue=#N`，在 commit message 末尾自动追加 `closes #N`
- 使用 `修复:` 前缀（fix 命令语义固定为修复）
- 示例：`修复: 登录超时后 token 未清除 closes #42`
- 执行 `git commit`，复用当前已获授权；环境要求的权限审批仍生效

#### 4.5.2 调用 `/req:pr` 流程

参见 [pr.md](../pr/SKILL.md)：

- `git push -u origin <branch>`
- 按 `branchStrategy.repoType` 创建 PR：
  - `gitea` → 调用 Gitea API
  - `github` → `gh pr create`
  - `other` → 仅输出合并命令
- PR 标题：`fix: <问题描述>`（无 REQ 编号）
- PR body 包含：问题描述、根因分析（来自步骤 1.4）、修改文件清单；若有 `closes #N` 自动关联 issue

#### 4.5.3 失败处理

任何一步失败（commit/push/PR 创建）→ **立即停止**，展示错误、已完成的外部操作和可继续的位置，不跳过到下一步。

#### 4.5.4 核对结果

核对实际提交、远程分支和 PR 状态，避免失败重试时重复创建。

**成功输出**：
```
✅ 一键修复完成！

  commit abc1234: 修复: 登录超时后 token 未清除 closes #42
  PR: <url>

下一步：/req:review-pr review 审查 PR
```

---

### 5. （可选）关闭 issue

仅当命令带 `--from-issue=#N` **且非 `--auto` 模式**时执行本步骤。

> **`--auto` 模式跳过询问**：commit message 已包含 `closes #N`，PR 合并时 Git 平台会自动关闭 issue，不需要在 PR 未合并前主动关闭。

在步骤 4 展示完成提示后，询问用户：

```
本次修复来自 issue #N
   是否关闭该 issue？(y/n)
```

**用户确认（y）** → 按 `repoType` 关闭 issue，逻辑同 [issue.md §5](../issue/SKILL.md)。

**用户拒绝（n）**：跳过。

> commit message 含 `closes #N` 时，PR 合并时 Git 平台会自动关闭 issue，无需手动操作。

---

## 与其他修复方式的区别

| 方式 | 命令 | 文档 | 分支 | 适用场景 |
|------|------|------|------|---------|
| 轻量修复 | `/req:fix` | 无 | fix/slug | 日常小 bug，改动 < 5 个文件 |
| 有记录的修复 | `/req:new-quick` | QUICK 文档 | fix/QUICK-XXX-slug | 需要记录的修复，方便追溯 |
| 紧急修复 | `/req:branch hotfix` | 无 | hotfix/slug | 线上紧急问题，从主分支拉 |

**选择依据：**
- 改完就忘的小 bug → `/req:fix`
- 需要测试和记录的修复 → `/req:new-quick`
- 线上出问题了 → `/req:branch hotfix`

---

## 用户输入

$ARGUMENTS
