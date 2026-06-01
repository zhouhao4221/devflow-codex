---
name: review-pr
description: PR 审查与合并 - AI 代码审查、提交评论、合并 PR
---

# PR 审查与合并

对已创建的 PR 进行 AI 代码审查，可将审查意见提交到平台（Gitea/GitHub），审查通过后合并 PR。

> 此命令**不受仓库角色限制**，readonly 仓库也可执行。
> 不触发缓存同步。
>
> **CLI 优先级**：GitHub 走 `gh pr` / `gh api`；Gitea 按 [`_gitea_cli.md`](./_gitea_cli.md) 检测 `tea`：**列表/查看/合并** 走 `tea pulls ls|<N>|merge`，**评论** 走 `tea comment <PR-N>`；但 **PR diff、行内 review 评论、reviews 详情**等 tea 未覆盖的接口仍走本文中的 curl 示例。

## 命令格式

```
/req:review-pr [子命令] [REQ-XXX]
```

## 子命令

| 子命令 | 说明 | 示例 |
|--------|------|------|
| (空) | 查看 PR 状态 | `/req:review-pr` |
| `review` | AI 代码审查 | `/req:review-pr review` |
| `fetch-comments` | 拉取 PR 评论，AI 生成修改清单并应用 | `/req:review-pr fetch-comments` |
| `merge` | 合并 PR | `/req:review-pr merge` |

- 省略编号时从当前分支自动匹配需求
- 未指定子命令时展示 PR 状态概览

---

## 前置条件

本命令依赖 `/req:pr` 已创建的 PR。如果需求没有关联的 PR：

```
❌ 未找到关联的 PR

请先创建 PR：/req:pr [REQ-XXX]
```

---

## 执行流程（查看状态）

### 1. 识别需求和 PR

**指定编号** → 读取该需求文档
**未指定** → 从当前分支名匹配需求编号（`REQ-\d+` 或 `QUICK-\d+`）

### 2. 查询 PR 信息

根据 `repoType` 查询 PR：从需求文档 `branch` 字段取分支名，按平台 API 查询关联的 open PR（Gitea 需指定 `head=OWNER:branch`）。

### 3. 展示状态

```
PR 状态：REQ-001 用户积分规则管理

  PR #42: feat(REQ-001): 用户积分规则管理
  状态：Open
  合并方向：feat/REQ-001-user-points → develop
  可合并：✅ 无冲突 / ❌ 有冲突
  审查：未审查 / ✅ 已通过 / ❌ 需修改

可用操作：
- /req:review-pr review   AI 代码审查
- /req:review-pr merge    合并 PR
```

---

## 执行流程（review - AI 代码审查）

### 1. 获取 PR diff

按平台获取 PR diff（Gitea：`GET /pulls/{N}.diff`；GitHub：`gh pr diff`）。

### 2. 读取审查规范

按优先级读取审查依据：
1. 项目 CLAUDE.md 中的**开发规范**章节（错误处理、日志、API 风格等）
2. 项目 CLAUDE.md 中的**测试规范**章节
3. 需求文档中的**功能清单**和**业务规则**（验证实现是否匹配需求）

### 2.5 对比需求文档与实际实现

读取需求文档并与 diff 实际内容交叉检查，找出**文档与代码不一致**的地方，稍后在报告中以「需求文档同步」章节提醒用户更新。

**检查维度：**

| 检查项 | 如何判断 | 提醒内容 |
|--------|---------|---------|
| 状态字段 | 文档状态是否为「开发中 / 测试中」 | 仍为「待评审/草稿」时提醒先走 `/req:review pass` 再合并 |
| 功能清单 (第二章) | diff 是否覆盖清单中每一项 | 未覆盖的项列出；diff 多出的新功能也列出 |
| 接口需求 (第五章) | diff 中新增/修改的路由、DTO 是否在文档中记录 | 缺失的接口列出，建议补充 |
| 数据模型 (11.1) | diff 中的表/字段变更是否在文档中描述 | 未记录的 Model 变更列出 |
| 文件改动清单 (11.3) | diff 实际修改的文件 vs 清单列出的文件 | 两侧差异双向列出（实际多了哪些 / 清单多了哪些） |
| 实现步骤 (11.4) | 清单步骤是否都能在 diff 中找到对应痕迹 | 未落实的步骤列出 |
| 业务规则 (第三章) | 关键规则是否在代码中体现（如余额校验、权限校验） | 代码里找不到校验痕迹的规则列出 |
| 关联需求 | 文档「关联」字段引用的其他需求 | 列出便于用户判断是否需同步更新关联方 |

**读取路径**：
- `primary` 仓库：`docs/requirements/active/<REQ-ID>-*.md`
- `readonly` 仓库：`~/.claude-requirements/projects/<project>/active/<REQ-ID>-*.md`

**未找到需求文档时**（如 `/req:fix`、`/req:do` 创建的无文档分支）跳过本步骤，仅做代码审查。

### 3. AI 逐文件审查

对 diff 中每个变更文件进行审查，检查维度：

| 维度 | 检查内容 |
|------|---------|
| 正确性 | 逻辑是否正确，边界条件是否处理 |
| 安全性 | SQL 注入、XSS、敏感信息泄露、权限校验 |
| 错误处理 | 异常是否捕获，错误是否正确返回 |
| 命名规范 | 变量/函数/文件命名是否符合项目规范 |
| 代码风格 | 是否符合项目 CLAUDE.md 中的编码规范 |
| 需求匹配 | 实现是否覆盖需求文档中的功能清单 |
| 测试覆盖 | 关键逻辑是否有测试，测试是否充分 |

### 4. 输出审查报告

问题分三级：

| 级别 | 含义 | 影响 |
|------|------|------|
| 阻塞 | 必须修复才能合并 | 阻止合并 |
| 建议 | 建议修改但不阻止合并 | 不阻止 |
| 信息 | 知识分享、风格偏好 | 不阻止 |

报告结构包含两部分：
1. **代码审查**：//分级的代码问题
2. **需求文档同步**：步骤 2.5 中发现的文档与代码偏差（不阻止合并，但建议用户 `/req:edit` 补齐）

输出格式：

```
AI 代码审查报告：PR #42

  审查文件：8 个
  审查结果：1 个阻塞 | 3 个建议 | 2 个信息
  需求同步：⚠️ 3 项待更新

---

阻塞问题：

  internal/user/biz/points.go:45
  问题：积分扣减未检查余额是否充足，可能导致负数
  建议：添加余额校验 `if user.Points < amount { return ErrInsufficientPoints }`

---

建议：

  internal/user/controller/v1/points.go:23
  问题：缺少请求参数校验
  建议：对 amount 字段添加 min=1 校验

  internal/user/store/points_store.go:67
  问题：批量操作未使用事务
  建议：用 db.Transaction() 包裹

  internal/user/model/points_record.go:12
  问题：CreatedAt 字段缺少 json tag
  建议：添加 `json:"created_at"`

---

信息：

  internal/user/biz/points.go:20
  备注：可以考虑将积分规则抽为配置，方便后续调整

  internal/user/router.go:34
  备注：路由分组命名建议统一为 /api/v1/points（当前为 /api/v1/point）

---

需求文档同步（REQ-001）：

  ⚠️ 文件改动清单未同步
    文档第 11.3 节缺失：
      + internal/user/store/points_record_store.go
      + internal/user/model/points_record.go
    文档第 11.3 节多余（实际未改动）：
      - internal/user/controller/v1/admin_points.go

  ⚠️ 接口未记录
    diff 新增路由 POST /api/v1/points/transfer，文档第五章未记录

  ⚠️ 功能清单覆盖不全
    文档第二章列出但 diff 中未找到实现：
      - "积分过期自动清理"

  建议执行：/req:edit REQ-001，补齐以上内容

---

总结：有 1 个阻塞问题需修复后才能合并；3 项需求文档待同步

可用操作：
- 修复后重新提交：/req:commit
- 修复后重新审查：/req:review-pr review
- 更新需求文档：/req:edit REQ-001
- 无阻塞后合并：/req:review-pr merge
```

### 5. 提交审查评论到平台

**默认先询问用户是否提交**，除非指定 `--auto`。理由：AI 审查结果是会被 reviewer 看到的公开评论，上传前让用户有机会微调或取消。

**5.0 零问题直通（无需询问）**

当同时满足以下条件时，判定为"完全没有问题"，跳过 5.1 的预览和 5.2 的询问，直接用固定模板提交通过评论：

- 阻塞数 = 0
- 建议数 = 0
- 需求文档同步项 = 0

信息级备注不影响判定（纯知识分享，不算问题）。

**固定通过评论模板**（上传到 PR 的 Markdown 内容）：

```markdown
### AI 审查通过 ✅

本次 PR 未发现阻塞问题、改进建议或需求文档同步项，代码符合项目规范，可以合并。
```

**终端输出**：

```
✅ AI 审查未发现问题，已自动提交通过评论到 PR #42
   ${PR_URL}
```

随后进入步骤 6（无阻塞后续操作）。

有任一 //项时，走下方 5.1/5.2/5.3 的原流程。

**5.1 展示精简版预览**

在询问前，先完整打印将要提交的精简版 Markdown 内容（见下面的"精简规则"和"精简后示例"），让用户看清楚要上传什么：

```
即将提交到 PR #42 的评审评论（预览）：


<精简版 Markdown 内容>


是否提交到 PR？(y/n，或输入修改意见)
```

**5.2 等待确认**

| 用户回复 | 行为 |
|---------|------|
| `y` / `yes` / `是` / 回车 | 执行上传 |
| `n` / `no` / `否` / `取消` | 跳过上传，仅保留本地完整报告 |
| 自由文本（修改意见） | 按用户意见调整精简版内容后重新预览并询问 |

**5.3 `--auto` 跳过确认**

若用户传入 `--auto`（或通过自然语言触发词），跳过 5.2 的询问，直接上传。预览仍然打印，但不等待用户输入。

`--auto` 触发方式：
- 显式参数：`/req:review-pr review --auto`
- 自然语言触发词（由 `natural-language-dispatcher` 识别）：
  - "自动审查"、"一键审查"、"审查并提交"、"审完直接评论"
  - "不用确认"、"别问我"、"跑完再说"
  - 在 Git 平台 URL 场景下："自动审查 owner/repo/pulls/158"

识别到 `--auto` 时，回复须明确说明能力边界：

```
识别：/req:review-pr review --auto

--auto 会自动跳过：
  上传评论前的确认询问
  直接把精简版提交到 PR（本地仍保留完整报告）

无法跳过（Claude Code harness 层）：
  - 首次调用 Bash（curl / gh）的工具权限确认

不会跳过：
  - AI 对代码的实际分析（审查逻辑本身）
  - 无阻塞问题时仍会明确结论"未发现明显问题"，不凑字数

开始执行？
```

用户语气明确（"一切自动"、"完全不用问我"）时省略末尾的"开始执行？"，直接执行。

---

**精简规则**

**上传到 PR 的是精简版，完整报告仅在本地终端展示**。PR 评论是给 reviewer 看的，只保留需要被看到的重点，过程性描述、逐文件列表、低优先级信息留在本地即可。

**精简规则：**

| 保留 | 去除 |
|------|------|
| 阻塞问题（全部） | 信息级备注 |
| 建议中与需求/安全/正确性相关的关键项 | 风格、命名等次要建议 |
| 需求文档同步的关键缺失（接口、数据模型、功能清单覆盖不全） | 文件改动清单的双向差异、关联需求列表 |
| 一行总结：阻塞数、建议数、文档同步项数 | 「审查文件：X 个」「可用操作」等过程信息 |

- 只有"未发现明显问题"结论时，评论就一两句话，不要凑字数。
- 评论总长度控制在 **300 字以内**为佳，超过时进一步压缩建议项。
- 文件路径保留绝对路径和行号，便于 reviewer 跳转。

**精简后示例（上传到 PR 的评论内容）：**

```markdown
### AI 审查：1 阻塞 / 1 建议 / 2 项文档待同步

**阻塞**
- `internal/user/biz/points.go:45` 积分扣减未检查余额，可能为负 → 加 `if user.Points < amount` 校验

**关键建议**
- `internal/user/store/points_store.go:67` 批量操作未使用事务

**需求文档同步（REQ-001）**
- 新增路由 `POST /api/v1/points/transfer` 未记录（第五章）
- 文件改动清单（11.3）与实际 diff 不一致

> 完整报告见本地终端输出。
```

按平台提交评论。**Gitea 注意**：PR 评论使用 `/issues/{N}/comments` 端点（不是 `/pulls/`）。

**repoType = "other"**：仅本地展示，不提交评论，不触发确认询问。

**上传成功**：
```
✅ 审查报告已提交到 PR #42（精简版）
   ${PR_URL}
   完整报告见上方本地输出
```

**用户拒绝上传**（仅在交互模式下可能）：
```
已跳过上传，完整审查报告保留在本地终端输出
如需重新上传：/req:review-pr review --auto
```

### 6. 无阻塞时的后续操作

**触发条件**（同时满足）：
- 阻塞数 = 0（可以有 /问题）
- PR 当前为 Open 状态（审核中）

不满足时（有阻塞问题 / PR 已合并或关闭）：跳过本步骤，结束。

**6.0 检查是否有审核人**

```python
# 来源 1：PR 上已分配的 reviewers（从 PR 详情读取）
pr_reviewers = [r["login"] for r in pr_info.get("reviewers", [])]

# 来源 2：branchStrategy.reviewers 配置（/req:pr 时自动设置的默认审核人）
config_reviewers = settings.get("branchStrategy", {}).get("reviewers", [])

has_reviewer = bool(pr_reviewers or config_reviewers)
```

**有审核人**（`has_reviewer = True`）→ 展示「审核通过」选项（见 6.1）。

**无审核人**（`has_reviewer = False`）→ 跳到 6.2，仅展示合并选项。

**6.1 有审核人时——提示是否提交审核通过状态**

```
✅ 审查完成，PR #42 无阻塞问题

审核人：@alice, @bob

是否在平台提交「审核通过」状态？
  [y] 提交审核通过  — 在 GitHub/Gitea 将你的 Review 状态更新为 Approved
  [n] 暂不处理     — 保留当前审核状态不变

请输入（y/n，回车默认不处理）：
```

**6.2 无审核人时——仅展示当前结果**

```
✅ 审查完成，PR #42 无阻塞问题（无分配审核人）

如需合并：/req:review-pr merge
```

**y — 审核通过**（仅 `has_reviewer = True` 时出现）

按平台提交「Approved」评审。**Gitea**：`POST /pulls/{N}/reviews`，body 为 `{"event": "APPROVED"}`。GitHub：`gh pr review --approve`。

**repoType = "other"**：跳过，告知用户在平台手动操作。

成功后输出：
```
✅ PR #42 审核状态已更新为「已通过（Approved）」
   ${PR_URL}
   （审核通过 ≠ 合并，PR 仍处于 Open 状态）

如需合并：/req:review-pr merge
```

失败时输出：
```
❌ 审核状态提交失败

可能原因：
- Token 权限不足（需要 repo 写入权限）
- 当前用户不在 PR 审核人列表
- 网络问题

请在平台手动操作：${PR_URL}
```

**n / 回车 — 暂不处理**（`has_reviewer = True`）

```
已跳过，PR #42 保持当前状态

后续可执行：
- /req:review-pr merge    合并 PR
```

---

## 执行流程（fetch-comments - 拉取评论并修改代码）

> 用途：PR 已被人工或 AI 审查并留下评论，开发者用此子命令拉取评论、让 AI 分析并应用修改。

### 1. 识别需求和 PR

与「查看状态」流程相同（支持从当前分支名反查）。

### 2. 拉取 PR 评论

同时拉取两类评论：
- **Issue Comments（整体讨论评论）**：针对 PR 整体的讨论
- **Review Comments（行内评论）**：针对 diff 具体行的评论，含 `path` 和 `position`/`line` 字段

按平台拉取。**Gitea 注意**：整体评论用 `/issues/{N}/comments`；行内评论需两级拉取——先 `GET /pulls/{N}/reviews`，再对每条 review 拉 `/reviews/{ID}/comments`。GitHub：`gh api` 直接支持两个独立端点。

**repoType = "other"**：提示不支持，结束。

### 3. 过滤评论

排除以下评论，避免无效循环：
- 作者为当前 git 用户（`git config user.name` / `git config user.email`）的评论
- 已 resolved / outdated 状态的行评论（Gitea 字段 `resolved`，GitHub 字段无需过滤，按时间戳排序）
- AI 自动提交的审查报告（body 以 `AI 代码审查报告` 开头）

可用「上次 fetch-comments 执行时间」作为增量标记（存储在需求文档「开发记录」或 `.claude/settings.local.json` 的 `reviewPrLastFetch` 字段）。**首次执行时拉取全部**。

### 4. 展示评论清单

分组展示，带编号供后续引用：

```
PR #42 评论（7 条，已过滤 2 条 AI 自提交）

整体讨论：

  [1] @reviewer-a (2026-04-15 10:21)
      整体逻辑 OK，但 user_points 表建议加软删除字段，方便回滚。

行内评论：

  [2] @reviewer-b (2026-04-15 10:30)
      internal/user/biz/points.go:45
      余额检查应该放在事务开头，现在位置会有并发问题。

  [3] @reviewer-b (2026-04-15 10:32)
      internal/user/controller/v1/points.go:23
      这里返回 500 不合适，参数错误应该返回 400。
```

### 5. AI 分析并生成修改清单

对每条评论：
1. 读取评论引用的源码位置（使用 Read，范围为评论行的 ±20 行上下文）
2. 判断评论是否**可执行**（改代码）或**需讨论**（需要人判断）
3. 生成修改方案

输出格式：

```
修改方案

[1] ✅ 可执行 — 加软删除字段
   internal/user/model/points_record.go
   在 PointsRecord 结构体追加 `DeletedAt gorm.DeletedAt` 字段，并在 migration SQL 增补列。

[2] ✅ 可执行 — 调整余额校验位置
   internal/user/biz/points.go:42-50
   把余额检查从方法末尾移到事务 `tx.Begin()` 之后、`UPDATE` 之前。

[3] ⚠️ 需确认 — 错误码调整
   internal/user/controller/v1/points.go:23
   原代码统一返回 500，建议改为 400。**但项目 CLAUDE.md 约定由中间件统一处理 400 错误**，需确认是手工返回还是调中间件。

是否按以上方案执行？（回复序号跳过某项，如 "跳过 3"；或直接回复 y 全部执行）
```

### 6. 执行修改

用户确认后：
1. 按方案修改代码（Edit 工具）
2. 对跳过项不做改动
3. 对「需确认」项，等用户进一步说明

### 7. 完成提示

```
✅ 已应用 2 项修改（跳过 1 项待确认）

修改文件：
- internal/user/model/points_record.go（+2 -0）
- internal/user/biz/points.go（+5 -3）

下一步：
- /req:commit        提交修改（建议在 commit message 中引用 PR #42 review）
- /req:review-pr review   可选：再次 AI 自审查
```

提交建议的 commit message 格式：
```
review: 处理 PR #42 的审查评论

- 加软删除字段 (reviewer-a)
- 调整余额校验位置到事务开头 (reviewer-b)
```

---

## 执行流程（merge - 合并 PR）

### 1. 前置检查

依次检查以下条件：

| 检查项 | 失败时行为 |
|--------|-----------|
| PR 是否存在 | ❌ 提示先创建 PR |
| PR 是否 Open 状态 | ❌ 提示 PR 已关闭/已合并 |
| 是否有合并冲突 | ❌ 提示解决冲突后重试 |

```
❌ PR #42 存在合并冲突

解决方式：
  git checkout <branch>
  git merge <merge_target>
  # 解决冲突后
  git add . && git commit
  git push
```

### 2. 执行合并

读取 `branchStrategy.mergeMethod` 配置（默认 `merge`）：

| 值 | 说明 | 适用场景 |
|------|------|---------|
| `merge` | 保留完整提交历史 | 默认，适合大多数团队 |
| `squash` | 压缩为一个提交 | 希望主分支历史简洁 |
| `rebase` | 变基到目标分支 | 追求线性历史 |

按平台合并。**Gitea 注意**：merge method 通过 `Do` 字段传递（不是 `method`），值为 `"merge"` / `"squash"` / `"rebase"`。GitHub：`gh pr merge --<mergeMethod>`。

**repoType = "other"**：
```
请手动合并 PR

  合并命令：
  git checkout <merge_target>
  git merge <branch>
  git push
```

### 3. 合并成功

```
✅ PR #42 已合并！

  ${PR_URL}
  feat/REQ-001-user-points → develop
  合并方式：merge

后续操作：
- /req:done REQ-001   归档需求
```

### 4. 分支清理

合并成功后，读取 `branchStrategy.deleteBranchAfterMerge` 配置（默认 `true`）。

**配置为 true 或未配置时**：

```
是否删除已合并的分支？

  将执行：
  git checkout <merge_target>
  git pull
  git branch -d <branch>
```

等待用户确认：
- 确认 → 执行切换、拉取最新、删除本地分支
- 拒绝 → 保留分支

**配置为 false 时**：不提示，跳过清理。

---

## Git Flow 双 PR 场景

当策略为 `git-flow` 且分支是 hotfix 时，可能存在两个 PR（→ main + → develop）。

此时分别展示/审查/合并两个 PR：

```
Hotfix 关联 2 个 PR：

  1. PR #42: hotfix/fix-order-calc → main     状态：Open
  2. PR #43: hotfix/fix-order-calc → develop   状态：Open

请选择操作的 PR（或输入 all 全部处理）：
```

合并时按顺序：先合并 → main，再合并 → develop。

---

## 与其他命令的衔接

```
/req:dev        开发完成后
    ↓
/req:commit     提交代码
    ↓
/req:pr         创建 PR
    ↓
/req:review-pr review          AI 审查代码 + 提交评论
    ↓
（他人/AI 留下评论）
    ↓
/req:review-pr fetch-comments  拉取评论 + AI 应用修改
    ↓
/req:commit                    提交修改
    ↓
/req:review-pr merge           合并 PR + 清理分支
    ↓
/req:done       归档需求
```

---

## 与 `/req:release` 的关系

**`/req:review-pr merge` 只是完成单个需求的里程碑，不是发版**。具体边界：

1. **migration SQL 在 merge 时不会被归档**
   合并 PR 后，`docs/migrations/` 下该需求的 SQL 文件仍然保留在原目录，不会被搬到 `released/`。这些 SQL 会等到下一次 `/req:release` 被命令合并到 `docs/migrations/released/<version>.sql`，并 `git rm` 原文件。
2. **合并到 `developBranch` ≠ 发布**
   在 git-flow 下，merge 通常是把 feat 分支合到 `developBranch`。发版仍需要跑 `/req:release`，由它走 cross-branch 流程打开 develop → main 的 release PR。
3. **不要为"发版"手工 tag 或手工建 Release**
   发版的所有动作（合并 SQL、生成回滚、changelog、tag、平台 Release）都应该由 `/req:release` 原子化完成。v3.0.0+ 默认 draft 模式，命令完成后你在 Gitea/GitHub 手工 publish 才真正发版——这是"双闸门"的核心。

**典型发版流水线**：

```
REQ-1 /req:review-pr merge     ← 单需求合并（不发版）
REQ-2 /req:review-pr merge     ← 单需求合并（不发版）
REQ-3 /req:review-pr merge     ← 单需求合并（不发版）
                ↓
        /req:release            ← 真正发版，自动推导版本号 + draft
                ↓
        在 Gitea/GitHub 点 Publish
```

---

## 用户输入

$ARGUMENTS
