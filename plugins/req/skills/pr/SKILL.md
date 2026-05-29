---
name: pr
description: |
  创建 PR - 根据仓库类型自动创建 Pull Request
---

# 创建 Pull Request

根据分支策略中的仓库类型，自动推送分支并创建 PR。

> **Audience:** Engineer
> 不受仓库角色限制，readonly 也可执行。不触发缓存同步。
>
> **CLI 优先级**：GitHub 走 `gh pr create`；Gitea 按 [`_gitea_cli.md`](./_gitea_cli.md) 检测，可用 `tea` 时走 `tea pulls create --base <target> --head <branch> --title ... --description ...`，否则回退本文 curl 示例。

## 命令格式

```
/req:pr [REQ-XXX] [--title=自定义标题] [--base=目标分支]
```

- 省略编号时根据当前分支名匹配需求
- `--title`、`--base` 覆盖自动值

---

## 执行流程

### 1. 识别需求和分支

- 指定编号 → 读取该需求的 `branch` 字段，按逗号拆分得到分支列表
- 未指定 → `git branch --show-current`，从分支名提取 `REQ-XXX` / `QUICK-XXX`
- 两者都失败 → 提示 `请指定需求编号：/req:pr REQ-XXX` 退出

**多分支处理**：`branch` 字段含多个分支时，为**每个分支各创建一个 PR**，依次执行步骤 2–8：

```
此需求有 2 个开发分支，将分别创建 PR：
  [1/2] feat/REQ-025-backend  → main
  [2/2] feat/REQ-025-frontend → main
```

若只需对当前分支创建 PR，直接运行（不传编号），命令自动匹配当前分支。

### 2. 前置检查

`git status --porcelain` 有未提交改动时，自动串联执行 `/req:commit` 流程（分支检查 + 生成提交信息 + 提交），成功后继续。

### 3. 读取策略配置 + 推导合并目标

读取 `.claude/settings.local.json.branchStrategy`：
- `model`（`git-flow` / `github-flow` / `trunk-based`，缺省 `github-flow`）
- `mainBranch`（缺省 `main`）
- `developBranch`（缺省 `develop`，git-flow 专用）
- `mergeTarget`（兜底值，缺省 `main`）
- `repoType`（缺省 `other`）
- `giteaUrl`、`giteaToken`（仅 gitea 需要）
- `deleteBranchAfterMerge`（缺省 `true`）
- `reviewers`（数组，缺省 `[]`；非空则自动设置审核人，无需确认）

无 `branchStrategy` → 按 `other` 处理，`reviewers` 视为空。

**合并目标推导**（`--base` 可覆盖最终结果）：

```
branch = 当前分支名

if model == "git-flow":
    if branch 以 "hotfix/" 开头:
        targets = [mainBranch, developBranch]   # 步骤 7 双 PR
    elif branch 以 "release/" 或 "chore/release-" 开头:
        targets = [mainBranch]                  # release 合入主线
    else:                                       # feat/ fix/ 等功能分支
        targets = [developBranch]               # 功能合入 develop
elif model in ("github-flow", "trunk-based"):
    targets = [mainBranch]
else:
    targets = [mergeTarget]                     # 兜底
```

`--base` 存在时直接覆盖 `targets = [args.base]`，跳过上述推导。

### 4. 生成 PR 标题和 Body

**标题**（`--title` 覆盖）：
- REQ-XXX → `feat(REQ-XXX): <标题>`
- QUICK-XXX → `fix(QUICK-XXX): <标题>`
- hotfix 分支 → `hotfix: <描述>`

**Body**（Markdown）：
```
## 需求
- 编号 / 标题 / 状态（从需求文档 YAML 元信息读取）

## 功能清单
（从需求文档「二、功能清单」提取）

## 变更文件
（从「十一、实现方案.文件改动清单」提取；无则跳过）
```

### 5. 推送分支

推送当前分支到 origin 并设置上游追踪。

### 6. 按 repoType 创建 PR

#### gitea

1. 解析 `git remote get-url origin` 得到 `OWNER/REPO`（SSH/HTTPS 均支持）
2. `giteaToken` 缺失 → 提示配置方式，给出手动 compare 链接退出
3. 先查 `GET /api/v1/repos/{OWNER}/{REPO}/pulls?state=open&head={OWNER}:{branch}&base={target}` 是否已有 PR；有 → 输出现有 PR 链接，跳到步骤 8
4. 无 → `POST /api/v1/repos/{OWNER}/{REPO}/pulls`，参数 `title/body/head/base`
5. **设置审核人**（`reviewers` 非空时，**不询问**直接执行）：
   - `POST /api/v1/repos/{OWNER}/{REPO}/pulls/{N}/requested_reviewers`，body `{"reviewers": [...]}`
   - tea CLI 无对应子命令，统一走 curl
   - 单个失败（用户名不存在 / 权限不足）不阻塞主流程，输出 ⚠️ 提示后继续

成功输出：
```
✅ PR 已创建
   <url>
已请求审核：@user1, @user2     ← reviewers 非空时输出
/req:review-pr review / merge，或 /req:done 归档
```

#### github

检查 `command -v gh`。可用 → `gh pr create --title "..." --body "..." --base <target>`，`reviewers` 非空时追加 `--reviewer <逗号分隔列表>`（**不询问**直接执行）。不可用 → 提示命令 + 浏览器 compare 链接。

#### other

不创建 PR，输出：
```
分支已推送：<branch> → <target>
合并命令：git checkout <target> && git merge <branch>
```

### 7. 多目标处理

`targets` 包含多个分支时（当前仅 git-flow hotfix 场景），对每个 target 各执行一次步骤 6，输出对应 PR 链接 / 命令。

### 8. 分支清理提示

**auto 模式跳过**：若项目内存在 `.claude/.req-auto` 且 mtime 在 10 分钟内（由 `/req:fix --auto` 等上游命令创建），直接跳过本步骤，不询问也不切分支——PR 刚创建还没合并，此时删本地分支不合理，合并后用 `/req:review-pr merge` 自然处理。

非 auto 模式下，`deleteBranchAfterMerge != false` 时询问：
```
是否切回 <target> 并删除本地分支 <branch>？
```
确认 → 切回 target 并删除本地分支（用 `-d` 而非 `-D`，未合并时会被 git 拒绝）。当前已在目标分支则跳过切换。远程分支不删。

---

## 用户输入

$ARGUMENTS
