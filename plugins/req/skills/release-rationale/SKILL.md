---
name: release-rationale
description: |
  release-rationale
---

# /req:release 设计原理与边界情况

> 本文档是 `release.md` 的伴随文档。记录复杂决策的"为什么"和完整的边界情况查询表。
>
> **正常发版流程不需要读本文档**。AI 在以下情况按需查阅：
> - 用户追问"为什么这样设计"
> - 出错时根据 §6 边界情况速查表定位处理方式
> - 修改 release 命令前需要理解决策依据

---

## 1. 为什么 draft 是默认模式

从 v2 开始 `/req:release` 默认创建 Gitea / GitHub draft release——对外不可见、CI/CD 不触发，需手工在平台点 Publish 才正式发版。

**设计原因**：
- 发布的大部分步骤不可逆（commit、push、tag、平台 Release），人工 gate 让用户最后有机会检查 release notes / 资产文件 / 版本范围
- 与 git-flow cross-branch 流程天然配合——一次 PR gate（merge 到主分支）+ 一次 draft gate（平台 publish），两道闸门都过了才真正对外发版

不想 draft 就加 `--no-draft`。老的 `--draft` 作为冗余别名接受但无效果（向前兼容）。

---

## 2. 为什么不静默降级 `repoType=other` 的 draft

旧版本会在 `repoType=other` 时静默把 `is_draft` 改成 false。这会让用户在"以为创建了 draft，实际已经 push 了 tag 并创建了正式 release"的状态下惊讶。

v3.0.0+ 改为强制交互确认，把"我要放弃 draft 闸门"这个决定变成明确的用户动作，避免发版事故。

---

## 3. 流程模式（cross-branch vs release-branch）选择

| 维度 | cross-branch | release-branch |
|------|-------------|---------------|
| 起步分支 | `developBranch` | `release/<version>` 或 `chore/release-*` |
| PR 数量 | 1（develop → main） | 2（release → main，release → develop 回流） |
| 适用场景 | develop 到 main 的 delta 就是本次要发的全部内容 | develop 上已积累未准备发布的 feature，需要隔离发布内容 |
| tag 落点 | 主分支 HEAD | 主分支 HEAD（PR1 合并后） |

**判断方法**：如果 develop 到 main 的 delta 没有未准备发布的 feature 堆积，cross-branch 更简单；否则必须用 release-branch 隔离要发的部分，否则 tag 会带上未准备发布的代码。

---

## 4. 为什么 git-flow 的主分支不允许 direct 模式

git-flow 的 `mainBranch` 通常设有保护规则。step 8.8 的 `chore(release): prepare` 提交会被直接 push 拒绝，用户被迫手动 reset → 切 develop → cherry-pick → 新 PR → 等合并 → 回主分支 → tag，绕一大圈。

步骤 1（策略合规检查）的守门会把这种"误起步"在最早环节挡下，给出 cross-branch / release-branch 两种推荐路径。

---

## 5. draft 模式行为矩阵详解

| `is_draft` | 最终行为 | 典型触发 | 不可逆程度 |
|----|----|----|----|
| `false` | 本地创建 annotated tag → push tag → 平台正式 Release（对外可见） | `--no-draft` | **最强**，tag + 外部 release 双重不可逆 |
| `true` | 平台 **draft** Release（作者可见，需手工 publish）；Gitea 需先 push tag，GitHub 懒创建 tag | **默认行为** | Gitea 中（需清理 tag + draft）/ GitHub 低（仅删 draft） |

### 5.1 draft 模式下的 tag 行为按 `repoType` 分叉

- **gitea**：Release API 要求 tag 必须先存在（否则返回 `Release is has no Tag`），所以 **draft 模式也会先 push annotated tag**。放弃 draft 时需一并清理 tag：`git push --delete origin <tag> && git tag -d <tag>`
- **github**：`gh release create --draft --target <SHA>` 懒创建 tag（publish 时平台创建 lightweight tag），本地 + 远程都没有 tag，放弃仅需删 draft
- **other**：draft 模式在 step 1.5 已降级为 `--no-draft`，不进入该分叉

### 5.2 危险组合：`is_draft=false` 在 developBranch / release 分支

意味着你正在跳过 draft 闸门直接走 cross-branch / release-branch 发布。是合法但少见的组合，step 1.6 末尾的额外 y/n 就是为它准备的闸门。

常见误操作：原本只是想 dry-check 发版流程却覆盖了 draft 默认。

---

## 6. `push_tag_first` 决策矩阵的四个为什么

矩阵本身见 release.md §9。这里解释每个分支的设计依据。

### 6.1 为什么非 draft + github 要先 push tag

GitHub Release API 在 tag 不存在时会用 `target_commitish` 现场创建 tag。如果 `target_commitish` 缺省为默认分支（可能是 develop），tag 就被打错。先推已存在的 annotated tag，API 直接引用，不再创建。

### 6.2 为什么非 draft + gitea 不 push tag

Gitea Release API 在 `draft=false` 时会从 `target_commitish` 现场生成 lightweight tag，而步骤 12（创建平台 Release）显式把 `target_commitish` 设为 `tag_target`（主分支名），不会打错分支。

本地再 push annotated tag 是**冗余**——会出现"本地 annotated、远程 lightweight"两种类型 tag 同名冲突（或者被 push 覆盖）。省掉这一步既简化流程、又与用户直觉一致（tag 在创建 Release 时一并出现）。

### 6.3 为什么 Gitea 的 draft 模式反而要先 push tag

Gitea Release API 在 `draft=true` 时不会为你创建 tag——必须先存在，否则返回 `422 Release is has no Tag`。

步骤 11（创建 Git Tag）的本地 `git push origin <tag>` 如果失败或未执行，就会触发此错误。排查：`git ls-remote --tags origin | grep <version>` 确认远程是否有 tag；检查 Gitea 对 tag 是否配了保护规则。

这是 Gitea 与 GitHub 的关键差异（GitHub 的 draft release 可以引用未来的 tag，Gitea 不可以）。因此 Gitea 上的 draft 闸门价值比 GitHub 弱一些：放弃 draft 需同时清理 tag。

### 6.4 为什么 GitHub 的 draft 模式不 push tag

1. GitHub Release API / `gh --draft` 允许 tag 在 publish 时才创建——这是 draft 的核心价值
2. draft 的 `target_commitish` 传主分支名（`tag_target`），publish 时 tag 打在该分支最新 HEAD 上。比 SHA 更直观方便，适合 draft 创建后很快 publish 的场景
3. 本地如果先 `git tag -a` 会和平台最终创建的 lightweight tag 类型冲突，push 时还会被拦或产生 divergent 状态——干脆完全不碰本地 tag

---

## 7. 跨分支 / 发布分支流程的设计要点

### 7.1 cross-branch：提交顺序的关键性

必须先完成"提交产物到 develop 并 push"，再创建/复用 PR。这样 PR 的 head 就包含 changelog，合并后主分支就有 changelog，不会出现 step 8.5 步骤 4 的 "changelog 不存在" 错误。

### 7.2 release-branch：为什么 PR1 在前，PR2 在后

先合 PR1 保证 tag 落在干净的 main HEAD 上（只含本次发布内容）；PR2 把 changelog/SQL/回滚脚本回流到 develop，让下次 release 不重复产出这些文件。

顺序颠倒会导致 tag 被 develop 上未准备发布的 feature 污染。

### 7.3 PR 复用的状态过滤

查询 PR 必须过滤 `state=open` 才能复用。`merged`/`closed` 状态的 PR 编号 **绝不能复用**——会出现"复用了已合并 PR 编号但 head 指向旧 commit"的情况，导致主分支拉下来缺 changelog。

### 7.4 PR 合并后主分支验证

`git pull --ff-only` 之后必须验证 `test -f docs/changelogs/<version>.md`。若文件不存在说明 PR 未真正合并或合并的是旧版本。此时：

- **不得**尝试 `git checkout develop -- docs/changelogs/<version>.md` 这种补丁式操作
- **不得**直接 push 主分支
- 警告用户 PR 状态异常，回到创建 PR 步骤重新创建新 PR

---

## 8. 版本号自动推导背景

v3.0.0 前版本号必须由用户手写，容易出错——尤其 minor vs patch 的判断、格式 `v` 前缀一致性。step 2.5 基于最近一个 git tag + 范围内 conventional commits 自动推导下一个 semver，同时保留 `<version>` / `--bump` 两级覆盖路径。

### 8.1 v 前缀规范化规则

- 基线 `v3.0.0` + 用户输入 `3.1.0` → 自动补齐为 `v3.1.0`
- 基线 `3.0.0` + 用户输入 `v3.1.0` → 自动去除为 `3.1.0`
- 首发场景（`base_tag is None`，默认 `has_v_prefix=True`）→ 按 v 前缀规范化

同一仓库不混用两种格式。

### 8.2 仅识别严格 X.Y.Z core semver

不识别 prerelease 后缀（如 `v1.2.0-rc.1`）。带 prerelease 后缀的基线 tag 会被拒绝，需要显式指定版本号或先打一个规范 tag 作为基线。

### 8.3 chore-only 范围拒绝自动发版

若 `base_tag..to_ref` 范围内 commits 只包含 chore/docs/style/test/ci 类型，拒绝自动发版以避免无意义的版本号累积。用户可显式指定 `<version>` 或 `--bump=patch` 强制发版。

---

## 9. 步骤 6 产物预览的存在意义

发布的大部分动作都不可逆（提交、push、tag、平台 Release）。用户必须在实际执行前看清所有将要发生的事——尤其是在 `--no-draft`、`cross-branch` 这些会改变最终行为的条件下，用户的心智模型和命令默认行为常常不一致。明确的预览消除"以为会 X，实际做了 Y"的事故。

预览**必须完整渲染**，但不等待用户 y/n 确认——自动继续执行 step 6+。用户如需中止请按 Ctrl+C。如需覆盖版本号请在命令中显式传参（`/req:release v1.4.0` 或 `--bump=minor`）。

---

## 10. SQL 文件删除的设计

step 6.5 在合并 SQL 后立即 `git rm` 源文件。设计原因：

- 已合并的 SQL 不应保留在 `docs/migrations/` 顶层，否则下次 release 会重复扫描到
- 用 `git rm` 而非 `rm` 是为了把删除放进暂存区，让步骤 10 各分支流程（direct/cross-branch/release-branch）一次性 commit 干净
- 仅删除**被选中并成功合并**的文件，未选中需求的 SQL 保留——给用户"分批发版"的灵活性
- 若 `released/<version>.sql` 写入失败则不得执行，避免源文件丢失

---

## 11. Gitea Release API 的 emoji 处理

body 必须用 `jq --rawfile body <path>` 从文件构造 JSON，**不要手工拼接 JSON 字符串**，否则 emoji（、、等 4 字节 UTF-8）会在 shell 双引号转义过程中退化成 `�` replacement char。

curl 用 `--data-binary @file` 上传，按二进制流，不做换行/编码转换。Header 显式声明 `Content-Type: application/json; charset=utf-8`。

---

## 12. 边界情况速查表

| 场景 | 处理方式 |
|------|---------|
| 当前在 feat/* / fix/* / hotfix/* 等 | **硬阻止**，提示切换到 `mainBranch` / `release/*` / `chore/release-*` / `developBranch` |
| 在 `release/*` / `chore/release-*` | 走 release-branch 流程，双 PR：release→main 先合+打 tag，release→develop 后合回流 |
| 在 `developBranch` | 走 cross-branch 流程，单 PR：develop→main，合并后在主分支打 tag |
| 跨分支流程中 PR 未合并用户中止 | 保留已生成的 SQL/changelog/PR，不打 tag |
| 跨分支流程中主分支 pull 后找不到合并提交 | 警告后重新等待用户确认 |
| release-branch 流程 PR1 未合并用户中止 | 保留已生成的 SQL/changelog/PR1，不打 tag，PR2 也不发 |
| release-branch 流程 PR2 用户选"跳过" | tag 和 Release 已完成，命令直接进入最终报告；PR2 保留等用户手动合并，报告中标记 待合并 |
| 没有 git tag | 从首次提交开始，显示警告 |
| 范围内无 commit | 终止操作 |
| 范围内无候选需求 | 提示后自动继续（仅打 tag + 纯 commit changelog） |
| git 范围内只有未完成需求 | 询问一次是否纳入；全部跳过则继续纯 commit changelog 流程 |
| 选中需求都无 SQL | 跳过 SQL 步骤，仅执行 changelog/tag/release |
| `docs/migrations/released/<version>.sql` 已存在 | Hook 弹确认 |
| `docs/changelogs/<version>.md` 已存在 | Hook 弹确认 |
| git tag 已存在 | 提示已存在，询问是否跳过 tag 步骤继续 |
| Gitea token 缺失 | 跳过 Release，保留 tag |
| gh CLI 缺失 | 输出命令让用户手动执行 |
| `repoType` 未配置 | 仅输出手动命令 |
| 默认 draft 模式 + `repoType == other` | 步骤 1（参数校验）强制交互确认降级为 `--no-draft`（不再静默降级），用户取消则中止 |
| draft 模式 draft 创建成功但 release notes 错误 | 在平台编辑 draft，或删除 draft 后重跑命令（gitea 场景需同时删 tag：`git push --delete origin <version> && git tag -d <version>`；github 场景 draft 一删即清） |
| draft 模式下 draft 创建后用户迟迟未 publish | 命令已终止，责任在用户。建议记在团队 checklist 里，或用 cron 巡检未 publish 的 draft |
| Gitea Release API 返回 `Release is has no Tag`（422） | 仅发生在 **draft + gitea** 场景（此时 `PUSH_TAG_FIRST=true`）。步骤 11（创建 Git Tag）的本地 `git push origin <tag>` 失败或未执行。排查：`git ls-remote --tags origin \| grep <version>` 确认远程是否有 tag；检查 Gitea 对 tag 是否配了保护规则拦截了 push。非 draft + gitea 不会触发此错（API 从 target_commitish 自己生成 tag） |
| `--no-draft` 在受保护主分支 + cross-branch/release-branch 流程 | **按 repoType 分叉**：<br>• **github**：步骤 11 会本地 `git tag -a` + `git push origin <tag>`；若 GitHub 对 tag 配了保护规则，push 会失败。改默认 draft 模式同样 push（draft+github 是 `PUSH_TAG_FIRST=false`，不 push）——**推荐回到默认 draft 以绕开 tag 保护**<br>• **gitea**：步骤 11 **不** push tag（`PUSH_TAG_FIRST=false`），API 在服务器侧创建 lightweight tag。若 Gitea 对 tag 有保护规则，API 会返回权限错误。改回默认 draft 模式**无效**（draft+gitea 反而要 push tag），需先解除 tag 保护或用其他路径<br>• **other**：步骤 11 本地 + push，同 github 处理 |
| 用户传 `--draft`（老语法） | 接受但不报错，冗余别名；`args.draft` 变量不参与逻辑，`is_draft` 只看 `args.no_draft` |
| 未指定 `--tag` | 仅跳过步骤 11（annotated tag），Release（步骤 12）照常创建；最终报告走 §16b（draft）或 §16a（--no-draft） |
