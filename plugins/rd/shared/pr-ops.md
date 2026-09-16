# PR 子命令：状态、审查、评论与合并

由 `rd:pr` 主入口按需读取。

对已创建的 PR 进行 AI 代码审查，可将审查意见提交到平台，审查通过后合并 PR。

> 不受仓库角色限制，readonly 可执行。
>
> CLI 优先级：GitHub → `gh pr`/`gh api`；Gitea → 按 [`_gitea_cli.md`](./_gitea_cli.md) 检测 `tea`。tea 未覆盖的接口走 curl。

## 子命令格式

```
/rd:pr [status|review|comments|merge] [PR-ID|REQ-XXX|QUICK-XXX] [--level=low|medium|high] [--auto]
```

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `status` | 查看 PR 状态 | `/rd:pr status` |
| `review` | AI 代码审查（`--level=` 指定审查深度，省略则按复杂度自动选） | `/rd:pr review` |
| `comments` | 拉取 PR 评论，AI 生成修改清单并应用 | `/rd:pr comments` |
| `merge` | 合并 PR | `/rd:pr merge` |

省略编号时从当前分支查关联 PR；无需求编号的分支也可查询。未指定子命令时由主入口创建 PR。

---

## 通用前置

依赖 `/rd:pr` 已创建 PR。未找到关联 PR 时提示先创建。

GitHub 的 `gh` 仅在已安装且 `gh auth status` 成功时可用。不可用时，只读查询可回退公开 REST API；私有仓库无凭据时报告访问限制。提交审查评论、Approve 和合并不可执行时，输出 PR 链接及手动操作说明。

---

## 查看状态

根据 `repoType` 查询 PR（从需求文档 `branch` 字段取分支名，Gitea 需指定 `head=OWNER:branch`）。展示：PR 编号、标题、状态、合并方向、是否可合并、审查状态、可用操作。

---

## review — AI 代码审查

### 1. 取 diff 并判定规模

按平台获取实际 PR 元数据（GitHub `gh pr view`/`gh api`，Gitea `/pulls/{N}`），读取该 PR 的 base/head 仓库、ref 和 SHA。使用 PR 实际目标分支，不用全局 `mergeTarget` 覆盖；fork PR 从 head 仓库获取。fetch 两端后确认本地对象与记录的 SHA 相符，固定 `BASE_SHA...HEAD_SHA` 为本轮审查范围，不切换或修改用户工作区。

用 `git diff --numstat BASE_SHA...HEAD_SHA` 和 `--name-status` 取得文件数、逐文件增删行数和重命名信息；行数指新增与删除之和。二进制文件记为行数未知并单列；不能当成零行。

| PR 规模 | 判定 | 读取方式 |
|---------|------|----------|
| 小 PR | ≤ 10 个文件且已知增删总数 ≤ 800 行，无未知行数文件 | 主会话读取全量 diff |
| 大 PR | 超过任一阈值或有未知行数文件 | 先按 [_delegate.md](./_delegate.md) 用 diff-digest 取摘要，再执行第 4 步完整审查 |

无法取得精确对象或 merge-base 时说明未覆盖范围，不用工作区 diff 冒充 PR diff。需用户补充访问或对象时保持未完成状态。

### 2. 读取审查依据

按优先级：项目 AGENTS.md 开发规范 → 测试规范 → 需求文档功能清单和业务规则。

另 Read `docs/prompt/pr-review.md`，存在则将其审查维度（必备输入、优质输出标准、常见失败模式）并入第 4 步审查关注点；缺失静默跳过。

### 3. 对比需求文档与实际实现

检查维度：

| 检查项 | 判断依据 |
|--------|---------|
| 状态字段 | 文档状态是否为「开发中/测试中」 |
| 功能清单 (第二章) | diff 是否覆盖清单每一项 |
| 接口需求 (第五章) | diff 中路由/DTO 是否在文档中记录 |
| 数据模型 (11.1) | 表/字段变更是否在文档中描述 |
| 文件改动清单 (11.3) | diff 实际文件 vs 清单列出文件 |
| 实现步骤 (11.4) | 清单步骤是否在 diff 中能找到 |
| 业务规则 (第三章) | 关键规则是否在代码中体现（如校验逻辑） |
| 关联需求 | 文档「关联」字段引用 |

> 按 [_storage.md](./_storage.md) 解析需求根目录后读取 `active/`；readonly 使用主仓自身配置的 `requirementsDir`。未找到需求文档时说明并跳过此步。
>
> 大 PR 用第 1 步 `diff-digest` 返回的文件清单与结构性改动（路由、DTO、表/字段）做比对，不拉 diff 原文。

### 4. 代码质量审查

小 PR 主会话审查全量 diff；大 PR 按下面的深度与范围执行。摘要只用于导航和需求比对，不能替代实际代码质量审查。不要假定存在 Claude 的 `/code-review`，也不要修改会话模型配置。

**4.1 深度选择**：`--level=low|medium|high` 显式指定优先；无效值说明后要求修正。否则按下表选深度并输出 `深度：<level>（命中：<信号>）`。这些是工作量启发式，不是漏洞判定或覆盖率证明。

| 分值 | 信号 | 判定依据 |
|------|------|---------|
| +1 | 规模大 | 超过 30 个文件或 2000 行 |
| +1 | 契约变更 | 摘要确认接口签名、DTO/表字段、错误码、配置项或依赖变化 |
| +1 | 敏感路径 | 涉及迁移、鉴权、权限、支付或删除路径；以实际路径及语义确认 |
| +1 | 测试变化少 | 源码有改动，测试改动行数不足源码的 10%；仍须查看已有覆盖 |
| +1 | 跨模块 | 涉及至少 3 个实际模块，按项目架构识别 |
| −1 | 轻量需求 | QUICK 需求或 hotfix 分支 |
| −1 | 非代码为主 | 至少 80% 已知改动行属于文档、配置、lock 或生成文件 |

总分 ≤ −1 → low；0 或 1 → medium；≥ 2 → high。未知行数不用于比例计算，说明统计局限。发现新风险时补查相关范围，不因最初选了 low 就忽略。

- **low**：覆盖全部变更，核对直接调用方、明显行为回归和相应测试。
- **medium**：增加跨文件调用链、接口兼容、错误处理与测试覆盖核对。
- **high**：在 medium 基础上，针对实际涉及的权限、数据迁移、并发、删除及故障路径追踪端到端行为；必要时运行聚焦验证。

**4.2 大 PR 执行**：按以下优先级选择完整审查后端，只做本地只读审查，不隐式发布评论：

1. 当前运行时若暴露可调用的 Codex 专用 review 工具，并能固定实际 base/head 范围，则按真实接口传入 `BASE_SHA`、`HEAD_SHA`、项目约束和所选深度。仅能打开 review 面板、或只能依赖当前工作区状态的 UI 操作不算可调用后端。
2. 本地环境若可执行 `codex exec review --help`，调用本 skill 自带的 [Codex review 适配器](../skills/pr/scripts/run-codex-review.sh)。从标准输入传入一段自包含的 custom review instructions，至少包含：只审本 PR 引入的问题、所选深度对应的关注点、需求功能与业务规则、项目特有审查规范，以及输出文件行号和触发后果。适配器会校验 base ref 仍指向 `BASE_SHA`，在 `HEAD_SHA` 的临时 detached worktree 中运行 `codex exec review --ephemeral --base <BASE_REF> -`，不切换用户工作区。
3. 原生后端不存在，或首次调用因版本、认证、配置、范围或运行错误失败时，记录失败原因并按 [_delegate.md](./_delegate.md) 派发独立审查子任务；不要修改用户 Codex 配置或用同一参数反复重试。子任务按行为或模块划分并保留调用关系，不机械地每文件派一个。每个任务自行读取其范围的原始 diff 和必要上下文，返回问题证据及已覆盖清单；主会话审查跨模块契约并汇总核实。

调用适配器前使用第 1 步已经核实的本地仓库路径、`BASE_REF`、`BASE_SHA` 和 `HEAD_SHA`。先将 `adapter_path` 解析为本 skill 内脚本的实际路径，并将自包含说明保存在 `review_prompt`，再调用：

```bash
printf '%s\n' "$review_prompt" | "$adapter_path" \
  --repo "$repo_root" \
  --base-ref "$base_ref" \
  --base-sha "$base_sha" \
  --head-sha "$head_sha"
```

不得把凭据、完整环境变量或无关文档放入 prompt。无需新增固定的 file-reviewer agent。

不可委派时由主会话按模块依次读取原始 diff 审查，注明执行方式。跟踪已审/未审文件；二进制、生成产物或访问受限部分说明验证手段和局限，不能默认为已通过。

**4.3 结果核对**：只将本 PR 引入且有依据的缺陷列为阻塞或建议。每条附触发条件、后果、文件行号和证据。原有问题归为信息并标注；风格偏好不自动阻塞。原生 review 的优先级不能机械替代 DevFlow 分级：P0/P1 默认阻塞，P2/P3 仍按实际后果判断；会导致错误行为、安全、数据或兼容性问题的缺陷即使优先级较低也应阻塞。缺少文件行号、触发条件或范围证据的 finding 先定点核实，不能直接发布。子任务结果按 [统一证据契约](./_evidence.md) 核对实际覆盖清单和审查范围，再由主会话去重、核实关键判断，并与需求文档同步项合并。

**4.4 完整性**：部分结果或失败的子任务继续补齐，无法补齐时报告未审范围；在完整性不足时不能输出「审查通过」。发布评论或合并前重新核对 head SHA，PR 已变化则补审增量后再操作。

### 5. 输出审查报告

问题分三级：**阻塞**（阻止合并）、**建议**（不阻止）、**信息**（知识分享）。

报告分两部分：代码审查 + 需求文档同步（文档与代码偏差，不阻止合并但建议 `/rd:edit` 补齐）。

### 6. 提交审查评论

默认只展示审查结果并结束。只有用户明确授权「审查并提交评论」、明确使用 `review --auto` 或已有等价授权时才发布；`--auto` 仅涵盖本次审查评论，不授权 Approved 或合并。用户要求发布但目标或范围仍不清时，先展示具体内容再澄清；纯审查请求不追加发布确认，零问题同样适用。`repoType=other` 只在本地展示。

> 精简规则：保留阻塞（全部）、关键建议、文档同步关键缺失；去除信息级备注、风格命名建议、过程信息。控制在 300 字以内。
>
> Gitea：PR 评论用 `/issues/{N}/comments`（不是 `/pulls/`）。`repoType = "other"` 仅本地展示。

### 7. 无阻塞时的后续操作

阻塞=0 且 PR 为 Open 时，只继续用户已授权的后续动作。明确要求提交 Approved 才调用 Gitea `POST /pulls/{N}/reviews`（`{"event":"APPROVED"}`）或 GitHub `gh pr review --approve`；明确要求合并才进入 merge 流程。审核人配置不构成授权，纯审查在报告后结束。

---

## comments — 拉取评论并修改代码

### 1. 拉取评论

同时拉取 Issue Comments（整体讨论）和 Review Comments（行内评论，含 `path` 和 `line` 字段）。
Gitea：整体评论 `/issues/{N}/comments`，行内评论先 `GET /pulls/{N}/reviews` 再逐条 `/reviews/{ID}/comments`。

### 2. 过滤评论

排除：当前 git 用户自己的评论、已 resolved/outdated 的行评论、AI 自提交的审查报告（body 以 `AI 代码审查报告` 开头）。

### 3. 展示 & 分析

分组展示评论清单，逐条读取引用源码上下文，判断可执行/需讨论，生成具体修改方案。用户已要求处理反馈时在其范围内实施并验证；只要求查看评论时交付分析，额外范围或关键选择再澄清。

---

## merge — 合并 PR

### 前置检查

PR 存在 → PR 为 Open → 无合并冲突。逐项失败时提示处理方式。

### 执行合并

读取 `branchStrategy.mergeMethod`（默认 `merge`），按平台执行（GitHub `gh pr merge --<mergeMethod>`，Gitea merge method 通过 `Do` 字段传递）。`repoType = "other"` 展示手动合并命令。

### 合并后

重新查询平台确认 `merged=true` 后输出合并信息，提示 `/rd:done` 归档。读取 `branchStrategy.deleteBranchAfterMerge`（默认 `true`），按用户授权处理已合并分支。

---

## Git Flow 双 PR 场景

hotfix 分支可能存在两个 PR（→ main + → develop），分别展示，按先 main 后 develop 顺序操作。

---

## 与 `/rd:release` 的关系

`/rd:pr merge` 是单需求里程碑，不是发版：
- migration SQL 在 merge 时不会被归档，等 `/rd:release` 统一处理
- 合并到 developBranch ≠ 发布
- 不要手工 tag 或建 Release，应由 `/rd:release` 原子化完成
