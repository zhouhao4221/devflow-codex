---
name: branch
description: |
  分支管理 - 配置分支策略、查看分支状态、创建紧急修复
---

# 分支管理

管理项目的 Git 分支策略，与需求流程（dev/commit/done）联动。

> **Audience:** Engineer
> 此命令**不受仓库角色限制**，readonly 仓库也可执行。
> 不触发缓存同步。

## 命令格式

```
/req:branch [子命令] [参数]
```

**子命令：**
- `/req:branch` — 无子命令时等同于 `status`
- `/req:branch init` — 交互式配置分支策略
- `/req:branch status` — 查看当前策略和分支状态
- `/req:branch hotfix [描述]` — 从主分支创建紧急修复分支

---

## 子命令：init

交互式选择分支策略，写入 `.claude/settings.json`（`giteaToken` 除外，写入 `settings.local.json`）。

### 执行流程

#### 1. 选择策略模型

```
选择分支管理策略：

  1. GitHub Flow（推荐）
     所有分支从 main 拉，合回 main
     适合：持续部署、Web 应用、中小团队

  2. Git Flow
     功能分支从 develop 拉，合回 develop
     适合：版本发布制、APP、大型项目

  3. Trunk-Based
     短期分支或直接在 main 开发
     适合：成熟团队、高频发布、完善的 CI/CD

请选择（1/2/3）：
```

#### 2. 确认或自定义配置

根据选择生成默认配置，展示给用户确认：

**GitHub Flow 默认配置（写入 `settings.json`）：**
```json
{
  "branchStrategy": {
    "model": "github-flow",
    "repoType": "github",
    "giteaUrl": null,
    "mainBranch": "main",
    "developBranch": null,
    "featurePrefix": "feat/",
    "fixPrefix": "fix/",
    "hotfixPrefix": "hotfix/",
    "branchFrom": "main",
    "mergeTarget": "main",
    "mergeMethod": "merge",
    "deleteBranchAfterMerge": true,
    "reviewers": []
  }
}
```

**Git Flow 默认配置（写入 `settings.json`）：**
```json
{
  "branchStrategy": {
    "model": "git-flow",
    "repoType": "github",
    "giteaUrl": null,
    "mainBranch": "main",
    "developBranch": "develop",
    "featurePrefix": "feat/",
    "fixPrefix": "fix/",
    "hotfixPrefix": "hotfix/",
    "branchFrom": "develop",
    "mergeTarget": "develop",
    "mergeMethod": "merge",
    "deleteBranchAfterMerge": true,
    "reviewers": []
  }
}
```

**Trunk-Based 默认配置（写入 `settings.json`）：**
```json
{
  "branchStrategy": {
    "model": "trunk-based",
    "repoType": "github",
    "giteaUrl": null,
    "mainBranch": "main",
    "developBranch": null,
    "featurePrefix": "feat/",
    "fixPrefix": "fix/",
    "hotfixPrefix": "hotfix/",
    "branchFrom": "main",
    "mergeTarget": "main",
    "deleteBranchAfterMerge": true,
    "reviewers": []
  }
}
```

#### 3. 自动检测主分支名

初始化时从 `origin/HEAD` 检测实际主分支名，不存在时按序探测 `main` / `master`。检测到的主分支与默认值不同时，自动更新配置：
```
检测到主分支为 master，已自动更新配置
```

#### 4. 选择仓库托管类型

```
仓库托管类型：

  1. GitHub
     使用 gh CLI 创建 PR

  2. Gitea
     使用 Gitea REST API 创建 PR

  3. 其他（GitLab / Bitbucket / 本地）
     仅展示合并命令，不自动创建 PR

请选择（1/2/3，默认 1）：
```

**选择 Gitea 时追加配置：**

```
Gitea 实例地址（如 https://git.example.com）：
```

自动从 git remote URL 解析 owner/repo（SSH/HTTPS 均支持）。

**Gitea Token 说明：**
```
Gitea API Token：
   token 存入 .claude/settings.local.json 的顶层 giteaToken 字段（不提交 git）
   生成方式：Gitea → 设置 → 应用 → 生成令牌（需 repo 权限）
```

#### 5. 配置默认审核人（可选）

```
默认审核人（创建 PR 时自动设置，无需每次确认）：
   多个用逗号分隔，留空则不设置（如：alice,bob）：
```

输入格式：
- 单人：`alice`
- 多人：`alice,bob,carol`
- 留空回车 → `reviewers: []`，PR 创建时不附带审核人

写入 `branchStrategy.reviewers`（数组）。用户名按平台规范：
- GitHub：账号 username
- Gitea：实例内 username

> 不在此校验用户是否存在；`/req:pr` 创建 PR 时调用平台 API，单个无效用户会输出 ⚠️ 但不阻塞 PR。

#### 6. Git Flow 额外步骤

如果选择 Git Flow，检查 develop 分支是否存在于远端：存在 → 使用；
- 不存在 → 提示创建：
  ```
  develop 分支不存在，是否从 main 创建？
  ```

#### 7. 写入配置

> 写入规范见 [_storage.md](./_storage.md#settings-文件写入规范)。

**`branchStrategy`（不含 token）写入 `.claude/settings.json`**：读取已有内容，合并 `branchStrategy` 字段后写回。

**`giteaToken` 单独写入 `.claude/settings.local.json`**（顶层字段，非嵌套在 `branchStrategy` 内）：
```json
{ "giteaToken": "<用户输入的 token>" }
```
非 Gitea 仓库时跳过此步骤（无需写入）。

⚠️ **禁止**创建独立的 `branchStrategy.json` 或其他文件。

```
✅ 分支策略已配置！

策略：GitHub Flow
仓库类型：Gitea（https://git.example.com）
主分支：main
功能分支：feat/REQ-XXX-slug（从 main 拉）
修复分支：fix/QUICK-XXX-slug（从 main 拉）
紧急修复：hotfix/xxx（从 main 拉）
合并目标：main
合并后删除分支：是
默认审核人：@alice, @bob   ← reviewers 非空时输出，空数组不输出此行

后续使用：
- /req:dev 创建分支时会自动遵循此策略
- /req:commit 会检查分支合规性
- /req:done 会根据仓库类型自动创建 PR 或提示合并命令
```

---

## 子命令：status

查看当前分支策略和各需求分支的状态。

### 执行流程

#### 1. 读取策略配置

从 `.claude/settings.json` 读取 `branchStrategy`；若需要 `giteaToken`，再从 `.claude/settings.local.json` 读取顶层 `giteaToken` 字段。

**未配置时：**
```
⚠️ 未配置分支策略，使用默认行为

建议执行 /req:branch init 配置分支策略
```

#### 2. 展示策略信息

```
分支策略：GitHub Flow

| 配置项 | 值 |
|-------|-----|
| 模型 | github-flow |
| 仓库类型 | gitea（https://git.example.com）|
| 主分支 | main |
| 功能分支前缀 | feat/ |
| 修复分支前缀 | fix/ |
| 紧急修复前缀 | hotfix/ |
| 拉取基准 | main |
| 合并目标 | main |
| 合并后删除 | 是 |
| 默认审核人 | @alice, @bob（空数组显示 -） |
```

#### 3. 展示当前分支状态

获取当前分支名并展示：
```
当前分支：feat/REQ-001-user-points
```

#### 4. 展示活跃需求的分支信息

扫描活跃需求文档，提取 branch 字段：

```
需求分支状态：

| 需求 | 分支 | 状态 | 是否当前 |
|------|------|------|---------|
| REQ-001 用户积分 | feat/REQ-001-user-points | 开发中 | ← 当前 |
| QUICK-002 修复过滤 | fix/QUICK-002-order-filter | 开发中 | |
| REQ-003 订单管理 | - (未创建) | 评审通过 | |
```

#### 5. 检查分支健康状况

```
✅ 分支健康检查：
- 当前在需求分支，关联 REQ-001 
- 需求分支与主分支无冲突 
```

或：

```
⚠️ 分支注意事项：
- 当前在 main 分支，有 2 个活跃需求分支
- feat/REQ-001-user-points 落后 main 3 个提交，建议 rebase
```

---

## 子命令：hotfix

从主分支创建紧急修复分支，用于线上紧急问题。

### 执行流程

#### 1. 工作区检查

有未提交改动时终止，提示先 commit 或 stash。

#### 2. 收集信息

如果未提供描述，询问用户：
- 问题描述（必填）

#### 3. 生成分支名

```
hotfix/<slug>
```

- slug：问题描述的英文翻译，lowercase kebab-case，最多 5 词

#### 4. 创建分支

**关键**：hotfix 始终从**主分支**拉取，无论当前使用什么策略。

fetch 并基于 `branchStrategy.mainBranch`（默认 main）创建 `hotfix/<slug>` 分支。

```
紧急修复分支已创建

分支：hotfix/fix-order-total-calc
基于：main (最新)
完成后合并到：main

后续步骤：
1. 修复问题
2. /req:commit 修复订单金额计算错误
3. 合并到 main：git checkout main && git merge hotfix/fix-order-total-calc
4. 删除分支：git branch -d hotfix/fix-order-total-calc
```

#### 5. Git Flow 额外提醒

如果使用 Git Flow 策略，hotfix 完成后需要合并到**两个分支**：

```
完成后需合并到：
1. main（生产环境）
2. develop（开发分支同步）

合并命令：
git checkout main && git merge hotfix/fix-order-total-calc
git checkout develop && git merge hotfix/fix-order-total-calc
git branch -d hotfix/fix-order-total-calc
```

---

## 策略对各命令的影响

### /req:dev 分支创建

| 配置项 | 影响 |
|-------|------|
| `branchFrom` | `git checkout -b <branch> <branchFrom>` 的基准分支 |
| `featurePrefix` | REQ-XXX 分支前缀（替代硬编码的 `feat/`） |
| `fixPrefix` | QUICK-XXX 分支前缀（替代硬编码的 `fix/`） |

### /req:commit 分支检查

| 场景 | 行为 |
|------|------|
| 在 mainBranch 上，有活跃需求 | ⚠️ 警告并建议切换到需求分支 |
| 在 mainBranch 上，无活跃需求 | 正常提交 |
| 在 developBranch 上（Git Flow） | ⚠️ 警告，功能开发应在功能分支 |
| 在需求分支上 | 正常提交，自动关联对应需求 |
| 在 hotfix 分支上 | 正常提交，类型建议选「修复」 |

### /req:pr 审核人自动设置

| 配置项 | 影响 |
|-------|------|
| `reviewers` | 非空时创建 PR 后自动请求审核（GitHub: `gh pr create --reviewer ...`；Gitea: `POST /pulls/<N>/requested_reviewers`），不再询问用户 |

### /req:done 合并方式

根据 `repoType` 决定合并方式：

| 仓库类型 | 行为 |
|---------|------|
| `gitea` | 自动推送分支 + 调用 Gitea API 创建 PR |
| `github` | 提示使用 `gh pr create` 命令 |
| `other` | 仅展示 `git merge` 合并命令 |

合并目标根据策略决定：

| 策略 | 合并目标 |
|------|---------|
| GitHub Flow | `main` |
| Git Flow | `develop`（hotfix 额外合并到 main） |
| Trunk-Based | `main` |

---

## 配置兼容性

### 未配置策略时的行为

所有命令保持当前默认行为，不会报错：
- `/req:dev`：使用硬编码的 `feat/` 和 `fix/` 前缀，自动检测主分支
- `/req:commit`：不做分支检查
- `/req:done`：通用合并提醒

### 配置存储

```jsonc
// .claude/settings.json（纳入 git，团队共享）
{
  "requirementProject": "my-saas",
  "requirementRole": "primary",
  "branchStrategy": {
    "model": "github-flow",
    "repoType": "gitea",
    "giteaUrl": "https://git.example.com",
    "mainBranch": "main",
    "developBranch": null,
    "featurePrefix": "feat/",
    "fixPrefix": "fix/",
    "hotfixPrefix": "hotfix/",
    "branchFrom": "main",
    "mergeTarget": "main",
    "mergeMethod": "merge",
    "deleteBranchAfterMerge": true,
    "reviewers": ["alice", "bob"]
  }
}
```

```jsonc
// .claude/settings.local.json（本地，加入 .gitignore，不提交）
{
  "giteaToken": "YOUR_TOKEN_HERE"
}
```

---

## 用户输入

$ARGUMENTS
