---
name: branch
description: 分支管理 - 配置分支策略、查看分支状态、创建紧急修复
---

# 分支管理

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `req:branch` 的档位执行；已作为执行子代理时不再次路由。

管理项目的 Git 分支策略，与需求流程（dev/commit/done）联动。

> 不受仓库角色限制，readonly 可执行。不触发缓存同步。写入规范见 `_storage.md`（按需读取 [_storage.md](../../shared/_storage.md)）。

## 命令格式

```
/req:branch [子命令] [参数]
```

| 子命令 | 说明 |
|--------|------|
| (空) | 等同于 `status` |
| `init` | 交互式配置分支策略 |
| `status` | 查看当前策略和分支状态 |
| `hotfix [描述]` | 从主分支创建紧急修复分支 |

---

## init

交互式选择分支策略。`branchStrategy` 写入 `.devflow/settings.json`，`giteaToken` 写入 `.devflow/settings.local.json`。

### 流程

1. **选择策略模型**：GitHub Flow（推荐）/ Git Flow / Trunk-Based。三种策略的默认配置差异见 `model`、`mainBranch`、`developBranch`、`branchFrom`、`mergeTarget` 等字段。
2. **确认或自定义**：生成默认配置展示，可调整各项参数。
3. **自动检测主分支**：从 `origin/HEAD` 检测，不存在时按序探测 `main`/`master`。与默认值不同时自动更新。
4. **选择仓库类型**：GitHub (`gh` CLI) / Gitea (REST API) / 其他（仅展示命令）。Gitea 需额外输入实例 URL 和 API Token。
5. **配置默认审核人**：逗号分隔的用户名，写入 `reviewers` 数组。留空不设置。`/req:pr` 创建时自动请求审核。
6. **Git Flow 额外步骤**：检查 develop 分支，不存在从 main 创建。
7. **写入配置**：输出策略摘要（模型、仓库类型、分支前缀、合并目标、审核人等）。禁止创建独立的 `branchStrategy.json`。

---

## status

1. 读取配置（未配置时提示执行 `init`）
2. 展示策略信息表
3. 展示当前分支
4. 扫描活跃需求文档，展示分支状态和是否当前
5. 检查分支健康（是否在需求分支、与主分支冲突、是否需 rebase）

---

## hotfix

从主分支创建紧急修复分支。

### 流程

1. 工作区检查（未提交改动则终止）
2. 收集问题描述（必填）
3. 生成分支名 `hotfix/<slug>`（英文翻译，kebab-case，最多 5 词）
4. 基于 `branchStrategy.mainBranch` 创建分支（fetch 后从 main 拉）
5. **Git Flow 额外提醒**：hotfix 完成后需合并到 main 和 develop

---

## 策略对各命令的影响

### `/req:dev` 分支创建
`branchFrom` 决定基准分支，`featurePrefix`/`fixPrefix` 决定分支前缀。

### `/req:commit` 分支检查

| 场景 | 行为 |
|------|------|
| 在 mainBranch 上，有活跃需求 | 警告建议切换 |
| 在 developBranch 上（Git Flow） | 警告应在功能分支 |
| 在需求/hotfix 分支上 | 正常提交 |

### `/req:pr` 审核人
`reviewers` 非空时创建 PR 后自动请求审核（GitHub `gh pr create --reviewer ...`，Gitea `POST /pulls/<N>/requested_reviewers`），不询问用户。

### `/req:done` 合并方式

| 仓库类型 | 行为 |
|---------|------|
| `gitea` | 推送 + API 创建 PR |
| `github` | 提示 `gh pr create` |
| `other` | 展示 `git merge` 命令 |

合并目标：GitHub Flow → `main`，Git Flow → `develop`（hotfix 额外 → main）。

---

## 配置兼容性

未配置策略时保持默认行为（`feat/`/`fix/` 前缀，不做分支检查，通用合并提醒），不会报错。

配置文件：`branchStrategy` 写入 `.devflow/settings.json`（团队共享），`giteaToken` 写入 `.devflow/settings.local.json`（不提交）。

---

## 用户输入

$ARGUMENTS
