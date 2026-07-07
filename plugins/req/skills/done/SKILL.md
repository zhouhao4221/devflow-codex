---
name: done
description: 完成需求 - 标记完成并归档
---

# 完成需求

标记需求为已完成，归档文档。

> 存储路径和缓存同步规则见 _storage.md（见附录：_storage.md）
>
> **CLI 优先级**：GitHub 走 `gh`；Gitea 按 `_gitea_cli.md`（见附录：_gitea_cli.md） 检测 `tea`，可用即走 `tea pulls create` / `tea issues close`，否则回退本文 curl 示例。

## 命令格式

```
/req:done [REQ-XXX]
```

- 省略编号时自动选择「测试中」的需求
- 多个候选时交互式选择

---

## 执行流程

### 1. 选择需求

- 指定编号 → 使用该需求
- 未指定 → 扫描 `active/` 中状态为「测试中」的需求，唯一则直接使用，多个则列出让用户选

### 2. 前置检查

- 读取需求文档 YAML 元信息 + 「测试要点」章节
- 状态必须为「测试中」，否则报错退出
- 若测试要点中存在未勾选项（`- [ ]`），展示警告并要求用户确认继续

### 3. 更新需求文档

修改 YAML 元信息：
- `status: 已完成`
- `completedAt: YYYY-MM-DD`（今日）

勾选生命周期「已完成」对应的复选框。

### 4. 更新 PRD 索引

定位 `docs/requirements/PRD.md` 的「需求追踪」章节（`grep -n "需求追踪"`），更新对应需求所在行的「状态」和「完成日期」两列。PRD 不存在或无该章节时跳过。

### 5. 归档文档 + 同步缓存

将需求文档从 `active/` 移动到 `completed/`（使用 `git mv` 保留历史）。缓存同步由 PostToolUse Hook 自动处理，无需命令内显式调用。

### 6. 输出确认

```
REQ-XXX <标题> 已完成
   归档至 docs/requirements/completed/REQ-XXX-<slug>.md
```

### 7. 分支合并提醒

读取 `.devflow/settings.local.json` / `.devflow/settings.json` 的 `branchStrategy`，legacy fallback 到 `.claude/settings.local.json.branchStrategy`；同时读取需求文档的 `branch` 字段。无 `branchStrategy` 或 `branch` 为空 → 跳过本步。

按 `repoType` 创建 PR，逻辑同 [pr.md](./pr.md)（push + 创建 PR + 提示 review-pr）。

**特殊情况**：
- `giteaToken` 缺失 → 提示手工 compare 链接
- Git Flow + hotfix 分支 → 需合并到 `main` 和 `develop` 两处，创建两个 PR

### 8. 关联 issue 关闭提醒

按 _issue.md 的 Issue 读取优先级（见附录：_issue.md） 获取 issue 编号：先查需求文档元信息 `issue` 字段，若为 `-` 或为空则查分支名 `-iN` 后缀。均未找到 → 跳过本步。

否则询问用户：

```
检测到关联 issue: #123
   是否关闭该 issue？(y/n)
```

**用户确认（y）** → 按 `repoType` 关闭 issue，逻辑同 [issue.md §5](./issue.md)。

**用户拒绝（n）**：跳过。

---

## 与 `/req:release` 的区别

`/req:done` 只做归档，不发版。发版用 `/req:release`（合并 SQL / 生成 changelog / 打 tag / 创建 Release）。

## 用户输入

$ARGUMENTS

---

# 附录（自动内联的共享约定）

> 以下内容由 command 引用的共享子文件自动内联，供不支持 slash 的客户端离线阅读。请勿手动编辑本文件——改动应在对应 command 进行。

## 附录：_storage.md

# 公共逻辑参考 - 存储与配置

> 此文档定义 settings 文件写入、存储路径、缓存同步、需求编号、元信息等共用规则。
>
> 同伴文档：`_branch.md`（见附录：_branch.md）（分支策略）、`_issue.md`（见附录：_issue.md）（Issue 关联）、`_template.md`（见附录：_template.md）（模板与状态确认）、`_granularity.md`（见附录：_granularity.md）（需求粒度）、`_agents-md.md`（见附录：_agents-md.md）（架构检查）。

## settings 文件写入规范

DevFlow 配置存储在项目根的 `.devflow/` 目录，按是否含密钥分两个文件：

| 字段 | 文件 | 纳入 git | 说明 |
|------|------|----------|------|
| `requirementProject` | `.devflow/settings.json` | ✅ | 团队共享配置 |
| `requirementRole` | `.devflow/settings.json` | ✅ | 团队共享配置 |
| `requirementsDir` | `.devflow/settings.json` | ✅ | 需求文档根目录，省略时默认 `docs/requirements` |
| `branchStrategy`（不含 token） | `.devflow/settings.json` | ✅ | 团队共享配置 |
| `giteaToken` | `.devflow/settings.local.json` | ❌ | 个人密钥，禁止提交 |

> **`.devflow/` 与 `.claude/` 的分工**：`.devflow/` 只放 DevFlow 业务配置（上表字段）；Claude Code 自身的 hooks、permissions 仍在 `.claude/settings.json`，两者互不迁移。项目级窄知识 skill 优先放在 `.agents/skills/`，旧 Claude Code 项目可 legacy fallback 到 `.claude/skills/`。

**写入规则（强制）**：

1. **禁止独立配置文件**：DevFlow 字段一律合并进 `.devflow/settings.json` 或 `.devflow/settings.local.json`，禁止另建 `devflow.json`、`branchStrategy.json` 等
2. **合并写入**：先读取已有文件内容，合并需要更新的字段后写回，**不得覆盖已有字段**
3. **目录检查**：`.devflow/` 目录不存在时先创建
4. **读取合并顺序**：命令读配置时先读 `.devflow/settings.json`，再用 `.devflow/settings.local.json` 覆盖同名字段（`giteaToken` 以 local 为准）
5. **无写入权限的回退**：当 Write/Edit 工具被拒绝时，**不得**改写到其他文件，而应直接输出可复制执行的 shell 命令：

   ```bash
   # 写入 .devflow/settings.json（团队配置）
   python3 -c "import json,os; p='.devflow/settings.json'; os.makedirs('.devflow',exist_ok=True); d=json.load(open(p)) if os.path.exists(p) else {}; d['requirementProject']='my-project'; d['requirementRole']='primary'; json.dump(d,open(p,'w'),indent=2,ensure_ascii=False)"
   # 写入 .devflow/settings.local.json（本地密钥）
   python3 -c "import json,os; p='.devflow/settings.local.json'; os.makedirs('.devflow',exist_ok=True); d=json.load(open(p)) if os.path.exists(p) else {}; d['giteaToken']='YOUR_TOKEN'; json.dump(d,open(p,'w'),indent=2,ensure_ascii=False)"
   ```

```python
# 写入团队配置（.devflow/settings.json）
import json, os

path = ".devflow/settings.json"
os.makedirs(".devflow", exist_ok=True)
existing = json.load(open(path)) if os.path.exists(path) else {}
existing["requirementProject"] = "..."  # 只更新需要的字段
with open(path, "w") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

# 写入本地密钥（.devflow/settings.local.json）
path = ".devflow/settings.local.json"
existing = json.load(open(path)) if os.path.exists(path) else {}
existing["giteaToken"] = "YOUR_TOKEN"
with open(path, "w") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
```

### 读取惯例

命令读取 `requirementProject` / `requirementRole` / `requirementsDir` / `branchStrategy` 时，统一按以下顺序合并：

```
config = merge(.devflow/settings.json, .devflow/settings.local.json)
# .devflow/settings.local.json 中的同名字段覆盖 settings.json
```

**Legacy Claude 迁移（breaking change）**：v2.x 旧项目的 DevFlow 字段在 `.claude/settings.json(.local)`。**读取只认 `.devflow/`，不再回退 `.claude/`**——升级后未迁移的项目读不到配置。迁移方式（任选其一）：
- 运行 `scripts/migrate-config.sh`（搬运 DevFlow 字段到 `.devflow/`，密钥进 `settings.local.json`）
- 重新运行 `/req:init --reinit` 或 `/req:branch init`

> SessionStart hook 检测到 `.claude/` 存在 DevFlow 字段但 `.devflow/` 缺失时，会打印迁移提示。

---

## 存储路径解析

```
需求存储（唯一源，在 primary 仓库）: <requirementsDir>/   默认 docs/requirements/
modules/      # 模块文档
specs/        # 规范文档（数据类型、接口契约等，跨仓库共享）
active/       # 进行中需求
completed/    # 已完成需求
INDEX.md      # 索引
```

**无全局缓存**：需求文档只存在于 primary 仓库的 `requirementsDir`，是唯一事实源。readonly 仓库不复制、不缓存，直接读 primary 仓库目录。

**解析规则**：
1. 读 `.devflow/settings.json` 的 `requirementRole` / `requirementsDir` / `requirementSource`，再用 `.devflow/settings.local.json` 覆盖同名字段
2. `primary`：需求根目录 = 本仓 `requirementsDir`（省略时默认 `docs/requirements/`；下文 `docs/requirements/` 均指此解析结果）
3. `readonly`：需求根目录 = `requirementSource.path` 指向的主仓根 + 该主仓的 `requirementsDir`；未配置 `requirementSource` 时报错，提示先 `/req:use <primary-repo-path>` 绑定

**仓库角色**（`requirementRole` 字段）：

| 角色 | 值 | 说明 |
|------|------|------|
| 主仓库 | `primary` | 拥有本地 `requirementsDir`，可读写，写入即生效 |
| 只读仓库 | `readonly` | 无本地需求目录，经 `requirementSource.path` 直接读主仓，不可创建/编辑/变更状态 |

**读取策略**：
- `primary`：读写本仓 `requirementsDir`
- `readonly`：直接读 `requirementSource.path` 下的需求目录（实时，无副本）

## 写入规则（无缓存，主仓唯一源）

**核心原则**：需求文档**只有一份**，位于 primary 仓库的 `requirementsDir`。不存在缓存层，因此没有同步动作。

- **primary**：所有修改需求的命令（new、new-quick、edit、review、dev、test、done、upgrade、modules/specs/prd 编辑）直接写本仓 `requirementsDir`，写完即生效，**无任何后续同步或 cp**。
- **readonly**：禁止一切写操作（创建、编辑、状态更新）。仅读取 `requirementSource.path`。

> **历史说明（v2.x → v3 breaking change）**：v2.x 曾用 `~/.claude-requirements/` 全局缓存 + PostToolUse `sync-cache.sh` 单向同步，readonly 从缓存读。v3 起**移除缓存**：readonly 改为经 `requirementSource.path` 直读主仓，`sync-cache.sh` 不再注册。命令内**不应再有任何缓存读写、cp 到缓存、或全局索引（`~/.claude-requirements/index.json`）操作**。

## 需求编号生成

扫描 active/ 和 completed/ 目录，找最大编号 +1，格式 `REQ-XXX`

## 元信息字段

| 字段 | 说明 |
|------|------|
| 编号 | REQ-XXX |
| 类型 | 后端/前端/全栈 |
| 状态 | 当前状态 |
| 模块 | 所属模块 |
| 关联需求 | 前后端对应需求 |
| branch | 开发分支名（/req:dev 首次进入时生成） |
| issue | 关联的 Git 平台 issue 编号（如 `#123`），无关联为 `-`。`/req:new --from-issue` 自动填充，`/req:done` 读取后可选关闭 |

## 附录：_gitea_cli.md

# 公共逻辑参考 - Gitea CLI 优先

> 此文档定义在 `repoType=gitea` 场景下，何时使用 [`tea`](https://gitea.com/gitea/tea) CLI、何时回退到 `curl + REST API`。GitHub 侧统一使用 `gh`，不在此讨论。
>
> 同伴文档：`_issue.md`（见附录：_issue.md）、`_branch.md`（见附录：_branch.md）。

## 总体原则

1. **优先 `tea`**：当本机存在 `tea` 且已为目标 Gitea 实例配置 login 时，凡是 `tea` 能覆盖的操作一律走 `tea`。
2. **回退 `curl`**：以下任一条件不满足即回退到 `curl + giteaToken`：
   - `command -v tea` 不存在
   - `tea login list` 中没有匹配 `branchStrategy.giteaUrl` 的条目
   - 操作不在 `tea` 覆盖范围（见下方矩阵）
3. **绝不自动 `tea login add`**：`tea login add` 会把 token 写入 `~/.config/tea/config.yml`，属用户可见的全局副作用，必须由用户主动配置。命令检测到 tea 未登录时，**只回退 curl**，最多在首次提示一次："已检测到 `tea` 但未配置当前 Gitea 实例，可手动 `tea login add --name <name> --url ${giteaUrl} --token <token>` 启用 tea CLI 工作流"。

## 检测脚本

各命令在执行 Gitea 调用前先跑一次：

```bash
USE_TEA=0
if command -v tea &>/dev/null; then
  if tea login list 2>/dev/null | awk 'NR>1 {print $3}' | grep -qx "${GITEA_URL%/}"; then
    USE_TEA=1
    # 取匹配的 login name 备用（多 login 场景需要 --login <name>）
    TEA_LOGIN=$(tea login list 2>/dev/null | awk -v u="${GITEA_URL%/}" 'NR>1 && $3==u {print $2; exit}')
  fi
fi
```

- `tea login list` 输出列：`Name | URL | SSHHost | User`，第 3 列是 URL
- 多 login 场景务必显式 `--login "${TEA_LOGIN}"`，避免选错实例
- 检测结果在同一命令会话内复用，不重复探测

## 操作覆盖矩阵

| 操作 | tea 命令 | tea 是否够用 | 不够用时回退原因 |
|------|---------|------------|----------------|
| 查看 issue 详情 | `tea issues <N>` | ✅ | — |
| 列出 issues | `tea issues ls --state ... --labels ...` | ✅ | — |
| 创建 issue | `tea issues create --title --body --labels --assignees` | ✅ | — |
| 编辑 issue 标题/正文 | `tea issues edit <N> --title --description` | ⚠️ 部分 | tea 无 `--add-labels` / `--remove-labels`，标签增删仍用 curl |
| 关闭 / 重开 issue | `tea issues close <N>` / `tea issues reopen <N>` | ✅ | tea 不支持 `--reason`（GitHub 专属），保持原静默降级提示 |
| 评论 issue | `tea comment <N> <body>` | ✅ | — |
| 列出 issue 评论 | — | ❌ | tea 无对应子命令，使用 `curl /issues/{n}/comments` |
| 创建 PR | `tea pulls create --title --description --base --head` | ✅ | — |
| 列出 PR | `tea pulls ls --state ... --base ...` | ✅ | — |
| 查看 PR 详情 | `tea pulls <N>` | ✅ | — |
| 拉取 PR diff | — | ❌ | tea 无 `pulls diff`，用 `curl ${url}/pulls/${N}.diff` |
| PR 评论（讨论级） | `tea comment <PR-N> <body>` | ✅ | — |
| PR Review（行内评论 / approve） | — | ❌ | tea 无 reviews API，全部走 curl |
| 合并 PR | `tea pulls merge <N> --style merge|rebase|squash` | ✅ | — |
| 创建 Release | `tea releases create --tag --title --note` | ⚠️ 部分 | 上传附件不便（无 `--asset` 一致语义），SQL 资产仍用 curl |
| 列出 / 查看 Release | `tea releases ls` / `tea releases <tag>` | ✅ | — |
| 标签 CRUD（仓库级 labels） | `tea labels ls` / `tea labels create` | ⚠️ 部分 | 删除/批量场景用 curl |

> 不在表中的 Gitea 接口（如 `collaborators`、`/user`、PR review threads 等）默认走 curl。

## 命令执行约定

**有 tea 的分支**：

```bash
# 示例：关闭 issue
if [[ $USE_TEA -eq 1 ]]; then
  tea issues close --login "${TEA_LOGIN}" "${N}"
else
  curl -s -X PATCH "${GITEA_URL}/api/v1/repos/${OWNER}/${REPO}/issues/${N}" \
    -H "Authorization: token ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"state":"closed"}'
fi
```

**输出解析差异**：
- `tea` 默认输出人类可读表格，要 JSON 用 `--output json`（部分子命令支持）
- 解析需求复杂时，依旧用 curl + jq，保持稳定
- 状态码 / 错误处理：`tea` 失败时 exit code 非 0 + stderr 文字，不要试图按 HTTP code 判断

## 与 `_issue.md` 的关系

`_issue.md` 中所有 `repoType="gitea"` 的 curl 示例都视为 **`USE_TEA=0` 时的回退路径**。命令文件不必在每个 curl 块前重复 `USE_TEA` 判断，但必须在 Gitea 操作总入口处引用本文，让 Claude 在执行时按矩阵选 CLI。

## 不实现的部分

- **不自动 `tea login add`**：理由见上方原则 3
- **不内置 `tea` 安装**：仅检测，缺失时静默回退到 curl，不打断流程
- **不为每个 curl 例改写成 if/else 模板**：命令文件是给 Claude 的指令，Claude 按本文矩阵在运行时挑选即可

## 附录：_issue.md

# 公共逻辑参考 - Issue 关联

> 此文档定义 `--from-issue` 拉取规范、OWNER/REPO 解析、Issue 与分支/提交的关联规则、Issue 编号读取优先级、关闭策略。
>
> 同伴文档：`_storage.md`（见附录：_storage.md）、`_branch.md`（见附录：_branch.md）、`_template.md`（见附录：_template.md）、`_granularity.md`（见附录：_granularity.md）、`_agents-md.md`（见附录：_agents-md.md）、`_gitea_cli.md`（见附录：_gitea_cli.md）。
>
> **CLI 优先级**：所有 Gitea 调用先按 `_gitea_cli.md`（见附录：_gitea_cli.md） 检测 `tea`，可用即走 `tea`；本文中的 `curl` 示例视为 `USE_TEA=0` 时的回退路径。

## Issue 拉取规范

`--from-issue=#N` 参数用于从 Git 平台拉取 issue 信息。各命令统一使用以下逻辑：

### 变量来源

| 变量 | 来源 | 说明 |
|------|------|------|
| `GITEA_URL` | `branchStrategy.giteaUrl` | Gitea 实例地址，**必须从配置读取，禁止从 git remote 猜测** |
| `TOKEN` | `branchStrategy.giteaToken` | Gitea API Token |
| `OWNER/REPO` | `git remote get-url origin` 解析 | 从 remote URL 提取，支持 SSH 和 HTTPS 格式 |
| `repoType` | `branchStrategy.repoType` | 决定使用 Gitea API 还是 gh CLI |

### OWNER/REPO 解析

从 `git remote get-url origin` 的结果中提取：
```
ssh://git@gitea.example.com:10022/owner/repo.git  →  owner/repo
git@github.com:owner/repo.git                     →  owner/repo
https://github.com/owner/repo.git                 →  owner/repo
```

去掉 `.git` 后缀，取最后两段路径作为 `OWNER/REPO`。

### 拉取逻辑

**repoType = "gitea"**：
```bash
# tea 可用 + 已 login（详见 _gitea_cli.md）
tea issues --login "${TEA_LOGIN}" "${N}" --output json

# 回退：curl
curl -s "${GITEA_URL}/api/v1/repos/${OWNER}/${REPO}/issues/${N}" \
  -H "Authorization: token ${TOKEN}"
```
- `GITEA_URL` 和 `TOKEN` 未配置时提示：`❌ Gitea 未配置 giteaUrl 或 giteaToken，请先执行 /req:branch init`

**repoType = "github"**：
```bash
gh issue view ${N} --json title,body,number,url,labels
```

**repoType = "other" 或未配置**：
```
❌ 未配置支持的 Git 平台（需 repoType=github 或 gitea）
请先执行 /req:branch init 配置
```

## Issue 与分支/提交的关联

### Issue 编号在分支名中的传递

当需求或任务来自 `--from-issue=#N`，分支名末尾追加 `-iN` 后缀，使 issue 编号可从分支名推断：

```
feat/REQ-001-user-points-i12       ← /req:dev，需求文档 issue=#12
fix/QUICK-003-fix-login-i5         ← /req:dev，快速修复 issue=#5
fix/optimize-order-query-i42       ← /req:do --from-issue=#42
fix/login-token-not-cleared-i42    ← /req:fix --from-issue=#42
feat/REQ-001-user-points           ← 无 issue 关联，不加后缀
```

**规则**：
- `-iN` 仅当 issue 编号存在时追加（需求文档 `issue` 字段非 `-`，或 `/req:do`、`/req:fix` 的 `--from-issue` 参数）
- `N` 为纯数字，不带 `#`
- 位于分支名最末尾，不影响 REQ-XXX / QUICK-XXX 的提取

### Issue 编号的读取优先级

各命令需要获取当前 issue 编号时，按以下顺序查找：

| 优先级 | 来源 | 适用场景 |
|-------|------|---------|
| 1 | 需求文档元信息 `issue` 字段 | `/req:done`、`/req:commit`（有需求文档时） |
| 2 | 当前分支名的 `-iN` 后缀 | `/req:commit`、`/req:do`、`/req:fix` 完成时（无需求文档时） |

**解析正则**：`-i(\d+)$` 匹配分支名末尾的 issue 编号。

### Issue 在 commit message 中的关联

当检测到 issue 编号时，`/req:commit` 在 commit message 末尾追加 `closes #N`：

```
优化: 订单查询添加索引 closes #42
新功能: 实现用户积分规则 (REQ-001) closes #12
```

Git 平台（GitHub / Gitea）会自动将该 commit 关联到 issue，并在合并时关闭 issue。

### Issue 关闭策略

| 场景 | issue 来源 | 关闭方式 | 关闭时机 |
|------|-----------|---------|---------|
| `/req:new --from-issue` | 需求文档 `issue` 字段 | `/req:done` 询问 + API 关闭 | 需求完成时 |
| `/req:new-quick --from-issue` | 需求文档 `issue` 字段 | `/req:done` 询问 + API 关闭 | 需求完成时 |
| `/req:do --from-issue` | 分支名 `-iN` | `/req:do` 完成时询问 + API 关闭 | 任务完成时 |
| `/req:fix --from-issue` | 分支名 `-iN` | `/req:fix` 完成时询问 + API 关闭 | 修复完成时 |
| 以上所有 | commit message `closes #N` | Git 平台自动关闭 | PR 合并时 |

## 附录：_branch.md

# 公共逻辑参考 - 分支策略

> 此文档定义分支策略配置（`branchStrategy`）的结构、预设和读取规则。
>
> 同伴文档：`_storage.md`（见附录：_storage.md）、`_issue.md`（见附录：_issue.md）、`_template.md`（见附录：_template.md）、`_granularity.md`（见附录：_granularity.md）、`_agents-md.md`（见附录：_agents-md.md）。

## 分支策略配置

分支策略存储在 `.devflow/settings.json` 的 `branchStrategy` 字段中，通过 `/req:branch init` 初始化。`giteaToken` 敏感字段单独存入 `.devflow/settings.local.json`（不纳入 git）。

### 配置结构

`settings.json`（团队共享，纳入 git）：
```jsonc
{
  "branchStrategy": {
    "model": "github-flow",       // github-flow | git-flow | trunk-based
    "repoType": "github",         // github | gitea | other（仓库托管类型）
    "giteaUrl": null,             // Gitea 实例地址（repoType=gitea 时必填，如 https://git.example.com）
    "mainBranch": "main",         // 生产分支
    "developBranch": null,        // git-flow 模式下的开发分支
    "featurePrefix": "feat/",     // REQ-XXX 分支前缀
    "fixPrefix": "fix/",          // QUICK-XXX 分支前缀
    "hotfixPrefix": "hotfix/",    // 紧急修复前缀
    "branchFrom": "main",         // 功能/修复分支的拉取基准
    "mergeTarget": "main",        // 默认合并目标
    "mergeMethod": "merge",       // 合并方式：merge | squash | rebase
    "deleteBranchAfterMerge": true
  }
}
```

`settings.local.json`（本地私有，禁止提交）：
```jsonc
{
  "giteaToken": null             // Gitea API Token（tea 未配置时的 curl 回退凭据）
}
```

### 三种策略预设

| 配置项 | GitHub Flow | Git Flow | Trunk-Based |
|--------|------------|----------|-------------|
| branchFrom | main | develop | main |
| mergeTarget | main | develop | main |
| developBranch | null | develop | null |
| hotfix 合并目标 | main | main + develop | main |

### 读取规则

1. 先读 `.devflow/settings.json` 的 `branchStrategy`，再用 `.devflow/settings.local.json` 中同名字段覆盖（`giteaToken` 以 local 为准）
2. **有配置** → 使用配置值
3. **无配置** → 使用默认行为（`feat/`、`fix/` 前缀，自动检测主分支）

### 各命令的策略消费

| 命令 | 读取的配置 | 用途 |
|------|-----------|------|
| `/req:dev` | `branchFrom`、`featurePrefix`、`fixPrefix` | 创建分支时的基准和前缀 |
| `/req:commit` | `mainBranch`、`developBranch` | 检查当前分支是否合规 |
| `/req:done` | `mergeTarget`、`deleteBranchAfterMerge`、`repoType`、`giteaUrl` | 合并提醒、PR 创建（Gitea）|
| `/req:branch hotfix` | `mainBranch`、`hotfixPrefix` | 从主分支创建紧急修复 |
| `/req:branch status` | `repoType` | 显示仓库托管类型 |

## 附录：_template.md

# 公共逻辑参考 - 模板格式与状态确认

> 此文档定义状态更新确认机制、确认操作规范、状态流转、Memory 隔离规则、模板格式约束等共用规则。
>
> 同伴文档：`_storage.md`（见附录：_storage.md）（存储与配置）、`_branch.md`（见附录：_branch.md）、`_issue.md`（见附录：_issue.md）、`_granularity.md`（见附录：_granularity.md）、`_agents-md.md`（见附录：_agents-md.md）。

## 状态更新确认机制

不同命令对状态更新的确认要求：

| 命令 | 状态变更 | 确认机制 |
|-----|---------|---------|
| `/req:review pass/reject` | 待评审 → 评审通过/驳回 | 显式参数即为确认 |
| `/req:dev` | 评审通过 → 开发中 | 首次进入时自动更新 |
| `/req:test` | 开发中 → 测试中 | 测试完成后自动更新 |
| `/req:done` | 测试中 → 已完成 | **必须明确确认（y/n）** |

## 确认操作规范

默认**不弹任何原生确认对话框**——命令已通过多轮讨论 / 显式参数 / y/n 完成意图确认，Claude Code 本身也足够稳定，无需再叠加一层打断。用户可按需通过自然语言开启 Bash 侧拦截，**无需手动编辑任何配置文件**。

### 开启/关闭拦截（记忆 + marker 文件）

开关由项目内 `.claude/.req-confirm-commit` 标记文件承载。Claude 根据用户自然语言意图维护该文件并在 memory 中落 feedback：

| 用户说 | Claude 动作 |
|-------|-------------|
| "以后 git commit 前帮我确认" / "开启提交确认" / "commit 前弹一下" | `mkdir -p .claude && touch .claude/.req-confirm-commit`，保存/更新 feedback memory 记录偏好 |
| "不用确认了" / "关闭提交确认" / "别再弹框了" | `rm -f .claude/.req-confirm-commit`，更新 memory |

标记文件已加入 `.gitignore`（每台机器独立）。Claude 在新会话首次感知到偏好与 marker 状态不一致时，可按 memory 中的 feedback 自动补 `touch`，用户无需重复交代。

### Hook 原生确认（仅在 marker 存在时生效）

| 操作 | Hook 脚本 | 触发条件 |
|------|----------|---------|
| git commit | confirm-before-commit.sh | Bash 命令包含 git commit |
| 移动需求文件 | confirm-before-commit.sh | Bash 命令包含 mv ... REQ-/QUICK- |
| 删除需求文件 | confirm-before-commit.sh | Bash 命令包含 rm ... REQ-/QUICK- |

> `--auto` 模式标记（`.claude/.req-auto`）仍由 `/req:fix --auto` 等流程负责建立/清理；在 marker 启用拦截时它负责让 Hook 放行自动化流水线。

### 执行规则

1. **展示预览后直接执行** — 不输出"回车继续"等文本确认提示
2. **默认直通** — 任何 Write/Edit/Bash 都不走 Hook 原生对话框
3. **需要用户输入的场景仍需等待** — 选择章节编号、选择目标需求、描述修改意图等由命令层负责
4. **`/req:done` 等显式 y/n 场景** — 由命令层提示，不依赖 Hook

## 状态流转

```
草稿 → 待评审 → ✅ 评审通过 → 开发中 → 测试中 → 已完成
```

## Memory 隔离规则（强制）

涉及模板的命令和 skill **禁止受 auto-memory 影响**。模板化输出必须完全由模板结构和用户当前输入决定，不得因 memory 中的偏好、历史记录或反馈而改变文档结构、章节内容或格式。

**适用范围**：
- 命令：`/req:new`、`/req:new-quick`、`/req:edit`、`/req:upgrade`、`/req:prd-edit`
- skill：`requirement-analyzer`、`prd-analyzer`

**具体禁止行为**：
1. 不得根据 memory 中的偏好跳过或合并模板章节
2. 不得根据 memory 中的历史需求自动填充当前需求内容
3. 不得根据 memory 中的反馈调整模板格式（如章节顺序、表格列数）
4. 不得读取 `~/.claude/projects/*/memory/` 目录下的文件来辅助文档生成

**允许的行为**：memory 可影响**交互风格**（如提问的详略程度），但不得影响**文档产出物**。

---

## 模板格式约束（强制）

创建和编辑需求文档时，**必须严格遵循模板格式**：

### 模板读取优先级

| 需求类型 | 优先读取 | 回退读取 |
|---------|---------|---------|
| REQ-XXX | `docs/requirements/templates/requirement-template.md` | `<plugin-path>/templates/requirement-template.md` |
| QUICK-XXX | `docs/requirements/templates/quick-template.md` | `<plugin-path>/templates/quick-template.md` |
| PRD | `docs/requirements/templates/prd-template.md` | `<plugin-path>/templates/prd-template.md` |

**模板不存在时终止**：两个路径都不存在时，**必须终止操作**，提示用户执行 `/req:update-template` 恢复模板。不得在无模板的情况下创建或编辑文档。

### 格式规则

1. **章节结构不可变**：不得新增、删除、合并或重命名模板中的章节
2. **层级标题不可变**：章节标题、编号（一、二、三...）必须与模板完全一致
3. **表格格式不可变**：表格的列名、列数必须与模板一致
4. **保留空章节**：未涉及的章节保留模板占位文本，不得删除
5. **仅填充内容**：在模板对应章节的占位文本处填充实际内容

### 适用命令

- `/req:new` - 创建时严格按模板生成
- `/req:new-quick` - 创建时严格按快速模板生成
- `/req:edit` - 编辑时保持模板结构不变
- `/req:upgrade` - 转换时按目标模板结构生成

### 验证机制

`scripts/validate-requirement.sh` 在 Write/Edit 后自动验证：
- REQ-XXX：检查所有章节（元信息、生命周期、一~十）
- QUICK-XXX：检查简化模板的所有章节（元信息、生命周期、问题描述、实现方案、验证方式、开发记录）

## 附录：_granularity.md

# 公共逻辑参考 - 需求粒度

> 此文档定义需求粒度规则、REQ 与 QUICK 的选择、前后端拆分规则。
>
> 同伴文档：`_storage.md`（见附录：_storage.md）、`_branch.md`（见附录：_branch.md）、`_issue.md`（见附录：_issue.md）、`_template.md`（见附录：_template.md）、`_agents-md.md`（见附录：_agents-md.md）。

## 需求粒度规则

### 基本原则

一个 REQ **对应一个可独立交付的业务功能**，不按技术层拆分，不按开发步骤拆分。

判断标准：**这个需求完成后，用户能感知到一个完整的功能变化吗？** 如果能，粒度合适；如果不能，说明拆得太细。

### 粒度参考

| 粒度 | 是否合适 | 说明 |
|------|---------|------|
| 「用户积分系统」含积分规则+积分查询+积分兑换+积分排行 | 太大 | 拆为多个 REQ |
| 「用户积分-积分规则管理」含 CRUD + 规则校验 | 合适 | 一个完整功能 |
| 「用户积分-积分规则-新增接口」仅一个 API | 太小 | 合并到功能级 REQ |
| 「用户积分-新增 model 层」按技术层拆分 | 错误 | 按功能拆，不按层拆 |

### 拆分建议

**应该拆分的情况：**
- 功能可独立上线、独立使用（如：积分规则管理 vs 积分兑换）
- 不同功能由不同人负责
- 功能之间无强时序依赖（可并行开发）
- 单个需求涉及文件超过 15 个

**不应该拆分的情况：**
- CRUD 属于同一业务实体（增删改查放一个 REQ）
- 功能之间强耦合，必须同时上线
- 拆开后单个 REQ 无法独立验证

### 已有需求的功能扩展

当 REQ 已存在，需要新增功能点时，按以下规则判断是修改原 REQ 还是新建：

**核心问题：去掉这个功能点，原需求还能独立交付吗？**
- **能** → 新建 REQ，通过关联字段链接
- **不能** → 修改原 REQ（`/req:edit`），在功能清单中补充

| 场景 | 建议 | 原因 |
|------|------|------|
| 新功能是原需求的自然延伸，缺少则不完整 | 修改原 REQ | 属于同一个可交付单元 |
| 新功能可独立上线，不依赖原 REQ | 新建 REQ | 独立交付，独立测试 |
| 原 REQ 已 `已完成` | 必须新建 REQ | 已归档需求不应回退状态 |
| 原 REQ 在 `开发中`/`测试中`，新功能会影响已写代码 | 新建 REQ | 避免范围蔓延，保持进度可控 |

**修改原 REQ 时**：使用 `/req:edit`，在变更记录章节说明新增内容。
**新建 REQ 时**：使用 `/req:new`，在关联信息中填写原 REQ 编号。

### 前后端拆分

前后端按类型字段区分，不按 REQ 编号拆分同一端的功能：

```
正确：
  REQ-001 用户积分规则管理-后端    （含 CRUD 全部接口）
  REQ-002 用户积分规则管理-前端    （含 CRUD 全部页面）

错误：
  REQ-001 用户积分规则-新增接口
  REQ-002 用户积分规则-查询接口
  REQ-003 用户积分规则-修改接口
```

### REQ 与 QUICK 的选择

| 场景 | 使用 | 理由 |
|------|------|------|
| 新业务功能（CRUD、新页面） | REQ | 需完整设计和评审 |
| 已有功能的小调整（加字段、改逻辑） | QUICK | 改动范围小、风险低 |
| Bug 修复 | QUICK | 除非修复涉及重构 |
| 重构/优化（不改变功能） | QUICK 或 REQ | 按改动范围判断，超过 5 个文件用 REQ |

### 创建时的 AI 辅助判断

`/req:new` 创建需求时，AI 应根据以上规则辅助判断粒度是否合适：
- 标题过于宽泛（如「XX系统」「XX模块」） → 建议拆分，列出子功能
- 标题过于具体（如「新增XX接口」「修改XX字段」） → 建议合并或改用 QUICK
- 不确定时询问用户业务目标，再给出建议

## 附录：_agents-md.md

# 公共逻辑参考 - AGENTS.md 架构检查

> 此文档定义命令对项目 AGENTS.md「项目架构」章节的依赖检查规则。
>
> 同伴文档：`_storage.md`（见附录：_storage.md）、`_branch.md`（见附录：_branch.md）、`_issue.md`（见附录：_issue.md）、`_template.md`（见附录：_template.md）、`_granularity.md`（见附录：_granularity.md）。

## AGENTS.md 架构检查

### 为什么需要

插件不硬编码任何项目架构细节（如分层顺序、目录结构、命名规范）。这些信息由项目自己的 AGENTS.md 提供。dev-guide、test-guide 等 skill 读取 AGENTS.md 后适配引导。

### 检查时机

以下命令执行前检查 AGENTS.md 是否包含架构信息：

| 命令 | 依赖的架构信息 | 缺失时影响 |
|------|--------------|-----------|
| `/req:dev` | 分层架构、目录结构 | 无法生成准确的实现方案和文件清单 |
| `/req:test`、`/req:test-new` | 测试规范、测试目录 | 无法定位测试文件和生成测试代码 |
| `/req:new`（后端/全栈类型） | API 风格 | 无法生成准确的接口需求章节 |

### 检查规则

```python
claude_md_path = "AGENTS.md"  # 项目根目录
architecture_keywords = [
    "分层架构", "目录结构", "技术栈", "项目架构",
    "Architecture", "Tech Stack", "Project Structure"
]

if os.path.exists(claude_md_path):
    content = read_file(claude_md_path)
    has_architecture = any(kw in content for kw in architecture_keywords)
else:
    has_architecture = False
```

### 缺失时的提醒（非阻断，仅警告）

```
⚠️ AGENTS.md 中未检测到项目架构描述

   /req:dev 需要架构信息来生成实现方案（分层顺序、目录结构、开发规范）
   /req:test 需要测试规范来定位测试文件和生成测试代码

   添加方式：
   - /req:init <project> --reinit  交互式生成架构片段
   - 手动在 AGENTS.md 中添加「项目架构」章节

   继续执行，但生成的方案可能不够准确。
```

### 架构片段模板

插件提供预置模板供用户选择（存放在 `templates/agent-snippets/`）：

| 模板 | 文件 | 适用场景 |
|------|------|---------|
| Go 后端 | `go-backend.md` | Gin + GORM 分层架构 |
| Java 后端 | `java-backend.md` | Spring Boot 分层架构 |
| 前端 React | `frontend-react.md` | React/Next.js + TypeScript |
| 通用 | `generic.md` | 空白模板，手动填写 |
