---
name: issue-guide
description: Issue 操作引导助手。在执行 /req:issue 命令，或需要创建/查看/关闭 GitHub/Gitea issue 时触发。提供平台检测、标签匹配、JSON 安全处理等关键约束。
---

# Issue 操作引导助手

在执行任何 issue 相关操作时激活，确保平台差异、数据安全和交互一致性。

---

## 一、前置：读取平台配置

所有操作开始前，读取 `.devflow/settings.local.json` / `.devflow/settings.json` 的 `branchStrategy`，legacy fallback 到 `.claude/settings.local.json`：

| 字段 | 用途 |
|------|------|
| `repoType` | `github` / `gitea` / `other` — 决定使用哪套 CLI |
| `giteaUrl` | Gitea 实例地址（**必须从配置读取，禁止从 git remote 猜测**） |
| `giteaToken` | Gitea API Token |

**OWNER/REPO 解析**：从 `git remote get-url origin` 提取，去掉 `.git` 后缀取最后两段路径。支持 SSH（`git@host:owner/repo.git`）和 HTTPS（`https://host/owner/repo.git`）。

**未配置时**：提示执行 `/req:branch init`，终止操作。

---

## 二、CLI 优先级

| 平台 | 优先 | 回退 |
|------|------|------|
| GitHub | `gh` | — |
| Gitea | `tea`（先检测可用性） | `curl + giteaToken` |

`tea` 不支持的操作（评论列表、标签增删）始终走 `curl`。

---

## 三、关键约束

### 3.1 JSON 安全（必须遵守）

**禁止字符串拼接构造 JSON**。含引号、换行、反斜杠的文本必须转义后再传入请求体：

```bash
# 方法 A：python3
python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' <<< "$body"

# 方法 B：jq
echo "$body" | jq -Rs .
```

### 3.2 标签匹配

**禁止硬编码中英文对照表**，始终从仓库拉取真实 labels 再匹配：

1. 完全匹配（忽略大小写）
2. 去空格/连字符/下划线后匹配
3. 子串包含匹配

无匹配时：询问用户是否在仓库创建该标签；拒绝则跳过（不终止操作）。

### 3.3 Gitea labels 限制

Gitea 的 labels **不能**通过 PATCH body 修改，必须走独立端点：
- 新增：`POST /repos/{owner}/{repo}/issues/{index}/labels`
- 删除：`DELETE /repos/{owner}/{repo}/issues/{index}/labels/{id}`（逐个删除）
- title / body / assignees 走 `PATCH /repos/{owner}/{repo}/issues/{index}`

### 3.4 指派人解析

从仓库协作者列表匹配（策略同 §3.2）。`@me` 自动解析为当前登录用户（GitHub 原生支持，Gitea 需先 `GET /user`）。无匹配时跳过，不终止。

### 3.5 Gitea list 过滤

`GET /issues?type=issues` 在部分 Gitea 版本未完全过滤 PR，需客户端二次过滤掉 `pull_request != null` 的条目。limit 上限 50。

---

## 四、关联需求上下文

写操作（new / edit / comment）可附需求摘要：

- `--req=REQ-XXX` 显式指定
- 未指定时从当前分支名提取（匹配 `REQ-\d+` / `QUICK-\d+`）
- 命中后读需求文档，提取标题/类型/模块/状态和功能清单首段

---

## 五、new 操作 — 正文生成

无 `--body` 时 AI 生成结构化模板，包含：

- 问题描述 / 复现步骤 / 预期行为 / 实际行为
- 环境信息：从 `git branch --show-current` 和 `git rev-parse --short HEAD` 取值

**强制预览**（不受 `--auto` 影响）：展示草稿，等待用户 y/n/e 确认。

成功后输出：
```
✅ Issue 已创建
  🔗 <url>

💡 /req:fix --from-issue=#N   创建修复
💡 /req:new --from-issue=#N   创建正式需求
```

---

## 六、close 操作 — Gitea 执行顺序

先发评论 → 再改状态（评论失败不阻止关闭）。`--reason` 是 GitHub 专属字段，Gitea 静默忽略并提示一次。

---

## 七、与其他命令的分工

| 需求 | 命令 |
|------|------|
| 从 issue 派生需求 | `/req:new --from-issue=#N` |
| 从 issue 派生修复 | `/req:fix --from-issue=#N` |
| 需求完成时关闭 issue | `/req:done` 结束时询问 |
| commit 自动关联 | message 末尾加 `closes #N` |
