---
name: issue
description: Issue 工作流 - 创建/编辑/关闭/列表/查看/评论 issue
---

# Issue 工作流

统一管理 GitHub / Gitea issue 的全生命周期：创建、编辑、关闭、重开、列表、查看、评论。

> 不受仓库角色限制，readonly 也可执行。不触发缓存同步。
>
> **CLI 优先级**：GitHub 走 `gh`；Gitea 按 `_gitea_cli.md` 检测 `tea`，可用即走 `tea`，否则回退 curl。`tea` 不支持的操作（评论列表、标签增删等）始终走 curl。

---

## 子命令路由

| 参数 | 功能 |
|------|------|
| `new` | 创建 issue |
| `edit` | 修改字段 |
| `close` | 关闭（可附留言） |
| `reopen` | 重开 |
| `list` | 列出 |
| `show` | 查看详情和评论 |
| `comment` | 添加或列出评论 |
| 无 / `help` | 打印摘要并终止 |

issue 编号支持 `#42` 和 `42` 两种写法。所有子命令都先执行前置检查。

---

## §1 前置检查

读取 `.claude/settings.local.json` 的 `branchStrategy`：

| repoType | 要求 | 失败时 |
|---------|------|-------|
| `gitea` | `giteaUrl` + `giteaToken` 非空；检测 `tea` 可用性 | 提示执行 `/req:branch init` 后终止 |
| `github` | `gh` CLI 已安装 | 提示安装 gh 后终止 |
| `other` / 未配置 | 无 | 写操作输出手动提示；list/show 报错 |

OWNER/REPO 从 `git remote get-url origin` 解析，支持 SSH 和 HTTPS 格式，见 [_issue.md](./_issue.md#ownerrepo-解析)。

---

## §2 共用行为

### 2.1 关联需求

写操作可自动附需求上下文。`--req=REQ-XXX` 显式指定，未指定时从当前分支名提取（匹配 `REQ-\d+` / `QUICK-\d+`）。命中后读需求文档，提取元信息（标题/类型/模块/状态）和功能清单首段作摘要。

### 2.2 标签匹配

**禁止硬编码中英文对照表**，始终从仓库拉取真实 labels 再匹配。

匹配顺序：完全匹配（忽略大小写）→ 去空格/连字符/下划线后匹配 → 子串包含。

无匹配时询问是否在仓库创建该标签；用户拒绝则跳过，不终止。

### 2.3 指派人解析

从仓库协作者列表匹配，匹配策略同 §2.2。`@me` 自动解析为当前登录用户（GitHub 原生支持，Gitea 需先 `GET /user`）。无匹配时跳过，不终止。

### 2.4 JSON 安全

**禁止字符串拼接构造 JSON**，含引号、换行、反斜杠的文本必须用 `python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'` 或 `jq -Rs` 转义后再传入请求体。

### 2.5 错误处理

| 错误 | 提示 |
|------|------|
| 401 / 403 | 鉴权失败，检查 giteaToken 或 gh auth status |
| 404 | Issue 不存在或仓库路径错误 |
| 422 | 回显 API message 字段，标出不合法字段 |
| 423 locked | Issue 已锁定，无法评论/编辑 |
| curl 非 0 | 请求失败，检查网络后重试 |

### 2.6 `--auto` 模式

检测 `.claude/.req-auto` 且 mtime < 10 分钟时跳过交互确认。`new` 强制预览，不受影响。

---

## §3 new

```
/req:issue new <标题> [--body=] [--labels=a,b] [--assignees=u1,u2] [--req=REQ-XXX]
```

**正文生成**：有 `--body` 直接用；无则 AI 生成含「问题描述/复现步骤/预期行为/实际行为/环境信息」的结构化模板，环境信息从 `git branch --show-current` 和 `git rev-parse --short HEAD` 取值。关联需求时在末尾用 `---` 分隔附加需求上下文。

**防误关闭**：正文含 `closes #N` / `fixes #N` 时警告，确认后再提交。

**强制预览**，不受 `--auto` 影响：

```
Issue 草稿：
  仓库：owner/repo (gitea)
  标题：登录超时后 token 未清除
  标签：bug, authentication
  指派：@haiqing
  关联：REQ-001

  正文（前 10 行）：...

  是否提交？(y/n/e - 编辑某字段)
```

`e` 可选择修改字段，改完回到预览。

成功输出：

```
✅ Issue 已创建
  <url>
  #170 登录超时后 token 未清除

/req:fix --from-issue=#170   创建修复
/req:new --from-issue=#170   创建正式需求
```

---

## §4 edit

```
/req:issue edit #N [--title=] [--body=] [--add-labels=] [--remove-labels=] [--assignees=]
```

无字段参数时展示当前状态并提示可用字段，不修改。

**Gitea 限制**：labels 必须走独立端点（`POST /labels` 新增、`DELETE /labels/{id}` 逐个删除），不能通过 PATCH body 修改。title/body/assignees 走 PATCH。

预览变更后提交，`--auto` 跳过预览。

---

## §5 close

```
/req:issue close #N [--comment=<留言>] [--reason=completed|not_planned]
```

**Gitea 执行顺序**：先发评论再改状态——评论失败不阻止关闭，关闭失败时评论已留痕。

**Gitea 不支持 `--reason`**，首次遇到时静默忽略并提示一次（GitHub 专属字段）。

---

## §6 reopen

```
/req:issue reopen #N
```

无预览，直接执行。

---

## §7 list

```
/req:issue list [--state=open|closed|all] [--labels=] [--assignee=] [--limit=20] [--page=1]
```

**Gitea 注意**：`type=issues` 在部分版本未完全过滤 PR，需客户端二次过滤 `pull_request != null` 的条目。limit 上限 50。

输出格式：

```
Open issues @owner/repo（第 1 页 / 20 条）

  #    状态   标题                          标签       指派      更新
  
  170  open   登录超时后 token 未清除        bug        @haiqing  2h
  165  open   导出 Excel 中文乱码            bug, 紧急  -         1d

/req:issue list --page=2
```

---

## §8 show

```
/req:issue show #N
```

拉取 issue 主体和全部评论，渲染格式：

```
Issue #170 登录超时后 token 未清除
  状态：open  作者：@haiqing（2026-04-15 14:32）
  标签：bug   指派：@haiqing

正文 
...

评论（共 3 条）
[1] @alice（15:01）  我能复现。
[2] @haiqing（16:22）已定位到 src/interceptors/request.ts:45

/req:issue comment 170 <文本>
```

---

## §9 comment

```
/req:issue comment #N <评论文本>
/req:issue comment #N --list
```

`--list` 仅渲染评论列表，不显示 issue 主体。

add 模式：关联需求时评论末尾附需求摘要（用 `---` 分隔）。预览后提交，`--auto` 跳过预览。

---

## 与其他命令的分工

| 场景 | 命令 |
|------|------|
| 从 issue 派生需求 | `/req:new --from-issue=#N` |
| 从 issue 派生修复 | `/req:fix --from-issue=#N` |
| 从 issue 派生任务 | `/req:do --from-issue=#N` |
| 需求完成时关闭 issue | `/req:done` / `/req:fix` 结束时询问 |
| commit 自动关联 | message 末尾加 `closes #N` |

---

## 用户输入

$ARGUMENTS
