# PR 子命令流程（status / comments / merge）

> 由 `/rd:pr <子命令>` 按需读取，不是独立命令。创建 PR 在 `pr` skill，AI 代码审查和按评论改代码在 `/rd:review`。
>
> 不受仓库角色限制，`readonly` 可执行。GitHub 优先用已登录的 `gh`；Gitea 按 [_gitea_cli.md](./_gitea_cli.md) 检测 `tea`，未覆盖的接口用 curl。

## 通用前置

- 依赖已创建的 PR；未找到时提示先执行 `/rd:pr` 创建。
- 参数给 PR ID 时直接使用；给需求编号时取需求文档 `branch`；都省略时从当前分支匹配。
- `gh` 只在已安装且 `gh auth status` 通过时可用。不可用时，只读查询可回退公开 REST API；私有仓库无凭据时提示登录并结束。合并等写操作不可用时只输出 PR 链接与手动指引。

## status — 查看 PR 状态

根据 `repoType` 查询 PR，展示编号、标题、状态、合并方向、是否可合并、审查状态和可用操作。

## comments — 只读查看评论

1. 同时拉取整体讨论与行内评论，行内评论保留 `path` 和 `line`。Gitea 整体评论用 `/issues/{N}/comments`，行内评论先取 `/pulls/{N}/reviews`，再逐条取 `/reviews/{ID}/comments`。
2. 排除当前 git 用户自己的评论、已 resolved/outdated 的行评论、以 `AI 代码审查报告` 开头的 AI 自提交报告。
3. 按「整体评论 / 行内评论（按文件）」分组展示作者、时间和正文，行内评论附 `path:line`。
4. 不读源码、不生成修改方案、不改文件。末尾提示：`/rd:review comments` 可按评论改代码。

## merge — 合并 PR

### 前置检查

确认 PR 存在、状态为 Open、无合并冲突。任一失败时停止并提示处理方式。

### 执行合并

读取 `branchStrategy.mergeMethod`（默认 `merge`），按平台执行：GitHub 使用 `gh pr merge --<mergeMethod>`，Gitea 通过 `Do` 字段传递。`repoType=other` 只展示手动合并命令。

GitHub 的 `gh` 不可用时不尝试合并；输出 PR 链接和与 `mergeMethod` 对应的网页按钮。用户回复已合并后，仍需查 API 确认 `merged=true` 才进入合并后流程。

### 合并后

重新查询平台确认 `merged=true` 后，输出合并信息并提示 `/rd:done`。读取 `branchStrategy.deleteBranchAfterMerge`（默认 `true`），按用户授权处理已合并分支。

hotfix 可能有分别指向 main 和 develop 的两个 PR，按先 main 后 develop 分别展示和操作。`/rd:pr merge` 是单需求里程碑，不是发版；migration SQL、tag 和 Release 仍由 `/rd:release` 处理。
