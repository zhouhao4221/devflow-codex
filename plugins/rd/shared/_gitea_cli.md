# 公共逻辑参考 - Gitea CLI 优先

> 此文档定义在 `repoType=gitea` 场景下，何时使用 [`tea`](https://gitea.com/gitea/tea) CLI、何时回退到 `curl + REST API`。GitHub 侧统一使用 `gh`，不在此讨论。
>

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

`_issue.md` 中所有 `repoType="gitea"` 的 curl 示例都视为 **`USE_TEA=0` 时的回退路径**。命令文件不必在每个 curl 块前重复 `USE_TEA` 判断，但必须在 Gitea 操作总入口处引用本文，让执行代理按矩阵选 CLI。

## 不实现的部分

- **不自动 `tea login add`**：理由见上方原则 3
- **不内置 `tea` 安装**：仅检测，缺失时静默回退到 curl，不打断流程
- **不为每个 curl 例改写成 if/else 模板**：命令文件是给执行代理的指令，执行时按本文矩阵挑选即可
