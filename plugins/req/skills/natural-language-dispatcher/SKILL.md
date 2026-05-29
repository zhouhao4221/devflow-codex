---
name: natural-language-dispatcher
description: |
  自然语言需求调度器。当用户用自然语言描述下列意图时自动触发并映射到对应命令：
  - 需求文档：新增/新建/创建需求、修改/编辑/变更需求（带编号）
  - 修复与开发：修 bug、修复报错、优化/重构/升级/统一代码、快速修复、小功能
  - 状态流转：开发/测试/评审通过/评审驳回/完成/归档需求（必须带编号）
  - 版本 PR：规范提交、创建 PR、审查 PR、合并 PR、拉 PR 评论
  - Issue 操作：提/建/开 issue、评论讨论、关闭/重开/查看/列出 issue
  - URL 识别：识别 issue/PR 链接并映射到对应命令（如 owner/repo/issues/169、
    owner/repo/pulls/158、https://github.com/owner/repo/pull/1）
  - 确认偏好：开启/关闭/查询 git commit 前的原生确认弹框（直接维护 marker + memory，不走命令）
  示例："新增需求 用户积分管理"、"修改025需求"、"修个登录超时的 bug"、
  "优化订单查询性能"、"开始开发025"、"025 评审通过"、"完成 025"、"创建 PR"、"审查 PR"、
  "提个 issue 登录超时"、"给 #42 回复 已修复"、"关闭 issue 42"、
  "修 pipexerp/diciai/issues/169"、"审查 pipexerp/diciai/pulls/158"、
  "开启提交确认"、"不用确认了"。
---

# 自然语言需求调度器

当用户用自然语言描述需求/开发操作时，解析意图并执行对应的命令流程。

> 本技能主要做**意图识别与命令映射**，不自行实现命令逻辑——解析完成后读取 `commands/<command>.md` 按原命令流程执行。唯一例外是 §七「确认偏好开关」，该偏好不对应任何 `/req:*` 命令，由本技能直接执行文件动作并更新 memory。

---

## 编号解析规则

所有意图共用以下编号解析：

| 输入 | 解析结果 |
|------|---------|
| `REQ-025` / `REQ025` | REQ-025 |
| `QUICK-003` / `QUICK003` | QUICK-003 |
| 纯数字 `025` / `25` / `3` | REQ-XXX（默认正式需求，数字补零到 3 位） |
| `#42` 或 `issue 42` | issue 编号 `#42`，映射为 `--from-issue=#42` |

**歧义处理**：纯数字默认识别为 REQ。若当前分支暗示 QUICK（如 `fix/QUICK-XXX-...`），优先用 QUICK。无法确定时询问用户确认。

---

## 一、需求文档操作

### 1.1 新增需求 → `/req:new`

**触发**：消息中包含"新增需求"、"新建需求"、"创建需求"（**不要求**需求编号，编号由系统自动生成）。

**参数提取**：

| 字段 | 示例 |
|------|------|
| 标题 | "新增需求 用户积分管理" → 标题="用户积分管理" |
| 类型 | "新增后端需求" → `--type=后端` |
| 模块 | "用户模块的需求" → `--module=用户模块` |
| issue | "从 #42 创建需求" → `--from-issue=#42` |

**示例**：
- "新增需求 用户积分管理" → `/req:new 用户积分管理`
- "新建一个后端需求，做订单导出" → `/req:new 订单导出 --type=后端`
- "从 #12 创建需求" → `/req:new --from-issue=#12`

### 1.2 修改需求 → `/req:edit`

**触发**（同时满足）：
1. 关键词："修改需求"、"编辑需求"、"变更需求"
2. 需求编号：`REQ-XXX` 或纯数字

仅说"修改需求"但不带编号时**不触发**。

**示例**：
- "修改025需求，增加导出功能" → `/req:edit REQ-025`（编辑意图="增加导出功能"）
- "变更需求 REQ-003，调整业务规则" → `/req:edit REQ-003`（编辑意图="调整业务规则"）

---

## 二、修复与开发意图（无文档）

### 2.1 修 bug → `/req:fix`

**触发**（同时满足）：
1. 动词："修"、"修复"、"修一下"、"修个"
2. 问题词："bug"、"问题"、"报错"、"异常"、"错误"
3. **有具体问题描述**（不是单纯讨论）

**示例**：
- "修个登录超时的 bug" → `/req:fix 登录超时`
- "修复订单分页数据重复" → `/req:fix 订单分页数据重复`
- "修一下 Excel 导出中文乱码" → `/req:fix Excel 导出中文乱码`
- "修 #42 这个 bug" / "修复 issue #42" → `/req:fix --from-issue=#42`

**`--auto` 非交互模式触发词**（用户希望一键跑完，跳过方案确认并自动提交 + 发 PR）：

- "一键修"、"一键修复"、"直接修"、"自动修"、"自动修复"
- "修完直接发 PR"、"改完自动提交"、"修好就发 PR"
- "不用确认"、"别问我"、"自动来"、"跑完再说"
- 显式带 "--auto"

**示例**：
- "一键修复登录超时" → `/req:fix 登录超时 --auto`
- "直接修 Excel 导出乱码并发 PR" → `/req:fix Excel 导出乱码 --auto`
- "自动修 #42" → `/req:fix --from-issue=#42 --auto`
- "修下登录超时，不用确认" → `/req:fix 登录超时 --auto`

**识别到 `--auto` 意图时，回复必须明确说明能力边界**（让用户知道还会有什么弹框）：

```
🧠 识别：/req:fix <问题> --auto

⚙️ --auto 会自动跳过：
  ✓ 修复方案确认
  ✓ git commit 前的原生确认弹框（默认就不存在；若已开启提交确认，通过 .claude/.req-auto marker 放行）
  ✓ /req:commit 的类型交互式选择（AI 推断为"修复"）
  ✓ --from-issue 时的关闭 issue 询问
  ✓ /req:pr 创建后的分支清理询问
  ✓ 手工串联 commit → push → PR

🔒 无法跳过（Claude Code harness 层，需你本地设置）：
  - 首次调用 Bash/Write/Edit 的工具权限确认
  - Plan Mode approval（若你开了 Plan Mode）

🛑 不会跳过（安全红线）：
  - 保护分支（main/master/develop）上的提交 —— 必须切分支
  - AI 对代码的实际分析与修改（核心执行，非确认）

开始执行？
```

若用户话里明确说了"完全不用问我"、"一切自动"这类**强确认**语气，可以省略最后那句"开始执行？"，直接开干。

**不触发**：
- "这个 bug 怎么修"（提问）
- "这个 bug 得修"（讨论，无具体描述）

### 2.2 优化/重构/升级/规范 → `/req:do`

**触发**（同时满足）：
1. 动词：**"优化"、"重构"、"升级"、"统一"、"整理"、"抽取"、"迁移"**（祈使语气）
2. 动词后带**具体对象**（名词短语）

**示例**：
- "优化订单查询性能" → `/req:do 优化订单查询性能`
- "重构用户服务层" → `/req:do 重构用户服务层`
- "升级 Go 到 1.23" → `/req:do 升级 Go 到 1.23`
- "统一错误码格式" → `/req:do 统一错误码格式`
- "做一下 #42" / "处理 issue #42" → `/req:do --from-issue=#42`

**不触发**：
- "这段代码可以优化"（讨论性）
- "是不是该重构了"（问句）
- "优化一下"（无对象）

### 2.3 快速修复/小功能（需文档）→ `/req:new-quick`

**触发**：
- "快速修复"、"快速改一下"、"快速改"、"小改动"、"小功能"、"快速需求"

与 `/req:fix` 的区别：`/req:fix` 无文档，`/req:new-quick` 会创建 QUICK 文档。用户语气偏向"要有记录"时选此项。

**示例**：
- "快速改一下分页默认值" → `/req:new-quick 分页默认值`
- "小功能：导出按钮加权限控制" → `/req:new-quick 导出按钮加权限控制`
- "快速修复，从 #42" → `/req:new-quick --from-issue=#42`

---

## 三、需求状态流转（必须带编号）

**共同触发条件**：动作关键词 **+** 需求编号（REQ-XXX / QUICK-XXX / 纯数字），缺编号不触发。

### 3.1 开发 → `/req:dev`

**触发**："开发"、"开始开发"、"进入开发" + 编号

**示例**：
- "开始开发025" → `/req:dev REQ-025`
- "开发 QUICK-003" → `/req:dev QUICK-003`

### 3.2 测试 → `/req:test`

**触发**："测试"、"开始测试"、"进入测试"、"做测试" + 编号

**示例**：
- "025 开始测试" → `/req:test REQ-025`
- "测试 REQ-003" → `/req:test REQ-003`

### 3.3 评审 → `/req:review`

**触发**："评审通过"、"通过评审"、"评审驳回"、"驳回评审" + 编号

| 自然语言 | 映射 |
|---------|------|
| "025 评审通过" / "通过评审 025" | `/req:review pass` |
| "025 评审驳回" / "驳回 025" | `/req:review reject` |

### 3.4 完成归档 → `/req:done`

**触发**："完成"、"归档"、"做完了"、"搞完了" + 编号

**示例**：
- "完成025" → `/req:done REQ-025`
- "025 做完了" → `/req:done REQ-025`
- "归档 QUICK-003" → `/req:done QUICK-003`

> `/req:done` 本身要求 y/n 确认，由原命令保证。

---

## 四、版本与 PR 操作

### 4.1 规范提交 → `/req:commit`

**触发**：
- "规范提交"、"提交代码"、"提 commit"、"写 commit"
- 或"提交" + 修饰语（"这次修改"、"本次改动"）

**示例**：
- "规范提交" → `/req:commit`
- "提交这次改动" → `/req:commit`

**不触发**：
- 孤立的"提交"字眼（如"提交到仓库"可能指 push）

### 4.2 创建 PR → `/req:pr`

**触发**："创建 PR"、"提 PR"、"发 PR"、"开 PR"

**示例**：
- "创建 PR" → `/req:pr`
- "提 PR 025" → `/req:pr REQ-025`

### 4.3 审查/合并 PR → `/req:review-pr`

| 自然语言 | 映射 |
|---------|------|
| "审 PR"、"审查 PR"、"review PR"、"代码审查 PR" | `/req:review-pr review` |
| "合并 PR"、"merge PR"、"PR 合并了" | `/req:review-pr merge` |
| "拉 PR 评论"、"应用 PR 评论"、"处理 PR 反馈" | `/req:review-pr fetch-comments` |

**`--auto` 非交互模式触发词**（`review` 子命令专用，跳过上传评论前的确认）：

- "自动审查"、"一键审查"、"审查并提交"、"审完直接评论"、"审完自动提评论"
- "不用确认"、"别问我"、"跑完再说"
- 显式带 "--auto"

**示例**：
- "一键审查 PR" → `/req:review-pr review --auto`
- "自动审查 owner/repo/pulls/158" → `/req:review-pr review --auto`（先切分支）
- "审 PR，别问我" → `/req:review-pr review --auto`

识别到 `--auto` 时回复须说明能力边界（详见 `commands/review-pr.md` 步骤 5.3）。

> `/req:review-pr merge` 和 `/req:review-pr fetch-comments` 自身的交互点不走 `--auto`：
> - `merge` 合并后的分支清理询问由 `branchStrategy.deleteBranchAfterMerge` 配置控制
> - `fetch-comments` 的"是否应用修改"询问保留，避免 AI 误改代码

---

## 五、Issue 操作

**目的**：用户用自然语言创建 / 编辑 / 关闭 / 评论 issue 时，自动映射到 `/req:issue` 子命令。

### 编号解析

issue 编号支持 `#42` / `42` / `issue 42` / `issue #42` 四种写法，都归一为 `42`。

### 5.1 创建 issue → `/req:issue new`

**触发**（同时满足）：
1. 动词："提"、"建"、"开"、"新建"、"创建"、"报"
2. 对象：**"issue"** 或 **"bug"**（带"报"字时）

**示例**：
- "提个 issue: 登录超时" → `/req:issue new 登录超时`
- "新建 issue 导出 Excel 乱码" → `/req:issue new 导出 Excel 乱码`
- "开 issue 积分排行榜排序异常" → `/req:issue new 积分排行榜排序异常`
- "报个 bug：订单分页数据重复" → `/req:issue new 订单分页数据重复`
- "给 REQ-001 建 issue 讨论实现方案" → `/req:issue new 讨论实现方案 --req=REQ-001`

**不触发**：
- "这个 bug 提给谁？"（提问）
- "怎么提 issue"（询问用法，走 `/req:help`）

### 5.2 评论 / 讨论 → `/req:issue comment`

**触发**（同时满足）：
1. 动词："评论"、"回复"、"回帖"、"留言"、"追评"、"补一句"
2. issue 编号

**示例**：
- "给 #42 回复 已修复" → `/req:issue comment 42 已修复`
- "在 issue 170 评论：已定位到 auth.ts" → `/req:issue comment 170 已定位到 auth.ts`
- "#42 追评：测试环境验证通过" → `/req:issue comment 42 测试环境验证通过`
- "看下 #42 的讨论" / "列出 #42 的评论" → `/req:issue comment 42 --list`

### 5.3 关闭 → `/req:issue close`

**触发**：
- "关闭 issue 42" / "close #42" / "把 issue 42 关了"
- "关闭 issue 42 并留言 xxx" → `/req:issue close 42 --comment=xxx`

**不触发**：
- "关闭需求 REQ-042"（走 `/req:done`，不是 issue）

### 5.4 重开 → `/req:issue reopen`

**触发**："重开 issue 42" / "reopen #42" / "把 issue 42 打开"

### 5.5 查看详情 → `/req:issue show`

**触发**：
- "看下 issue 42" / "issue 42 详情" / "展示 #42"
- "issue 42 有哪些评论" → `/req:issue show 42`（show 会包含评论列表）

### 5.6 列表 → `/req:issue list`

**触发**：
- "列出 issue" / "列表 issue" / "open 的 issue" → `/req:issue list --state=open`
- "已关闭 issue" → `/req:issue list --state=closed`
- "我的 issue" / "分给我的 issue" → `/req:issue list --assignee=@me`
- "紧急 issue" / "bug issue" → `/req:issue list --labels=<匹配词>`

### 5.7 编辑 → `/req:issue edit`

**触发**：
- "给 issue 42 加标签 bug" → `/req:issue edit 42 --add-labels=bug`
- "改 issue 42 标题为 xxx" → `/req:issue edit 42 --title=xxx`
- "把 issue 42 指派给 @haiqing" → `/req:issue edit 42 --assignees=haiqing`

---

## 六、Git 平台 URL 识别

**目的**：用户直接粘贴 issue / PR 链接时，自动识别类型并映射到对应命令。

### 6.1 识别模式

统一正则（支持带协议头和纯路径两种形式）：

```
(?:https?://[^/\s]+/)?([^/\s]+)/([^/\s]+)/(issues|pull|pulls)/(\d+)
```

**捕获分组**：域名（可选）、`owner`、`repo`、类型（`issues` / `pull` / `pulls`）、编号 `N`。

**支持的 URL 形式**：

| 形式 | 示例 |
|------|------|
| 完整 URL | `https://github.com/pipexerp/diciai/pull/158` |
| 完整 URL（Gitea） | `https://git.example.com/pipexerp/diciai/pulls/158` |
| 纯路径 | `pipexerp/diciai/issues/169` |
| 纯路径 | `pipexerp/diciai/pulls/158` |

`pull` 和 `pulls` 都识别为 PR（GitHub 用单数，Gitea 用复数）。

### 6.2 仓库匹配检查

解析出 `owner/repo` 后，与当前仓库对比：

```bash
git remote get-url origin
```

从 remote URL 提取 `owner/repo`，与 URL 中的 `owner/repo` 比较：
- **匹配**：继续按意图映射
- **不匹配**：提示并退出，不自动跨仓库执行：
  ```
  ⚠️ URL 指向的仓库 pipexerp/diciai 与当前仓库 xxx/yyy 不同
  💡 请切换到对应仓库目录后再执行
  ```

### 6.3 Issue URL → 创建/修复/查看类命令

**URL 形式**：`.../issues/<N>`

#### 单独粘贴 URL（无动词）

展示选项让用户选择：

```
🔗 识别到 issue #169（pipexerp/diciai）
   请选择操作：
   1. 修 bug          → /req:fix --from-issue=#169
   2. 创建正式需求    → /req:new --from-issue=#169
   3. 创建快速修复    → /req:new-quick --from-issue=#169
   4. 智能开发        → /req:do --from-issue=#169
   5. 查看 issue 详情 → /req:issue show 169
   6. 评论该 issue    → /req:issue comment 169 <文本>
   7. 关闭该 issue    → /req:issue close 169
```

#### URL + 动词（直接映射）

| 用户消息 | 映射 |
|---------|------|
| "修复 .../issues/169" / "修 .../issues/169 的 bug" | `/req:fix --from-issue=#169` |
| "创建需求 .../issues/169" / "从 .../issues/169 新建需求" | `/req:new --from-issue=#169` |
| "快速修复 .../issues/169" | `/req:new-quick --from-issue=#169` |
| "处理 .../issues/169" / "做一下 .../issues/169" | `/req:do --from-issue=#169` |
| "看下 .../issues/169" / "展示 .../issues/169" | `/req:issue show 169` |
| "评论 .../issues/169 xxx" / "回复 .../issues/169 xxx" | `/req:issue comment 169 xxx` |
| "关闭 .../issues/169" / "close .../issues/169" | `/req:issue close 169` |
| "重开 .../issues/169" / "reopen .../issues/169" | `/req:issue reopen 169` |

### 6.4 PR URL → 审查/合并类命令

**URL 形式**：`.../pull/<N>` 或 `.../pulls/<N>`

#### 分支匹配检查（必须先做）

`/req:review-pr` 通过**当前分支**匹配关联的 PR。识别到 PR URL 后，先验证：

```bash
# 获取当前分支对应的 PR 编号
gh pr view --json number 2>/dev/null  # GitHub
# 或通过 Gitea API 按 head branch 查询（参考 _issue.md 的 Issue 拉取规范）
```

- **当前分支的 PR 编号 = URL 中的编号** → 可直接执行对应子命令
- **不匹配** → 提示切换分支：
  ```
  ⚠️ PR #158 对应的分支不是当前分支
     当前分支：main
     PR 分支：feat/REQ-001-user-points
  💡 请先切换：git checkout feat/REQ-001-user-points
  ```

#### 单独粘贴 PR URL（无动词）

分支匹配后展示选项：

```
🔗 识别到 PR #158（pipexerp/diciai）
   请选择操作：
   1. 查看状态        → /req:review-pr
   2. AI 审查代码     → /req:review-pr review
   3. 拉评论应用到代码 → /req:review-pr fetch-comments
   4. 合并 PR         → /req:review-pr merge
```

#### PR URL + 动词（直接映射）

| 用户消息 | 映射 |
|---------|------|
| "看下 .../pulls/158"、"状态 .../pulls/158" | `/req:review-pr` |
| "审查 .../pulls/158"、"review .../pulls/158"、"审 .../pulls/158" | `/req:review-pr review` |
| "拉评论 .../pulls/158"、"应用评论 .../pulls/158" | `/req:review-pr fetch-comments` |
| "合并 .../pulls/158"、"merge .../pulls/158" | `/req:review-pr merge` |

### 6.5 处理优先级

同一条消息中**多种信号共存**时的优先级：

1. **动词 + URL**（最明确）→ 直接按动词映射（§6.3 / §6.4 的第二子节）
2. **仅 URL**（需用户选择）→ 展示选项列表
3. **动词 + 需求编号**（无 URL）→ 走 §一~§五 的原有规则

例："修 pipexerp/diciai/issues/169" → 动词"修" + Issue URL → `/req:fix --from-issue=#169`，不再询问其它选项。

---

## 七、确认偏好开关（直接动作，非命令映射）

用户可用自然语言开/关 Bash 原生确认弹框（git commit / mv / rm 需求文件）。本项由 Claude 直接执行文件动作并写入 memory，不走 `/req:*` 命令。

**触发词**：

| 意图 | 关键词 |
|------|-------|
| 开启 | "开启提交确认"、"commit 前帮我确认"、"以后 commit 要弹框"、"提交前问我一下" |
| 关闭 | "关闭提交确认"、"不用确认了"、"别再弹框"、"不要提交确认" |
| 查询 | "现在弹确认吗"、"提交确认开着吗"、"查看确认状态" |

**执行动作**：

- 开启 → `mkdir -p .claude && touch .claude/.req-confirm-commit`；在 auto-memory 中写入/更新一条 feedback 记录"该用户偏好 git commit 拦截已开启"。
- 关闭 → `rm -f .claude/.req-confirm-commit`；在 memory 中把对应偏好改为"关闭"或删除该条。
- 查询 → 直接检查 `.claude/.req-confirm-commit` 是否存在，告知当前状态，不修改任何文件。

**边界**：

- 只影响 Bash 侧 Hook，不拦截 Write/Edit
- 仅当 req 插件已安装时有效；downstream 项目的 `req` hook 会读取该 marker
- marker 已加入 `.gitignore`，每台机器独立

---

## 不触发的情况（反例合集）

以下情况**不应触发**本技能，避免误匹配：

### 查询/展示类（走 `/req:show`、`/req:status`，本技能不处理）
- "看一下025需求"
- "025 什么状态"
- "展示025详情"

### 讨论/提问性语句
- "这段代码可以优化"
- "是不是该重构了"
- "这个 bug 怎么修"
- "这个需求太大了"
- "怎么新增需求"（询问用法）

### 关键词缺失必要信息
- "修改需求"但无编号
- "优化一下"但无具体对象
- "完成"但无编号
- "开发中"（形容状态，非动作）

### 插件/工具本身的维护
- "修改需求模板"
- "优化这个技能" / "调整 dispatcher"
- 涉及 `templates/`、`skills/`、`commands/` 文件的修改

### URL 相关的反例
- 链接指向其他仓库（与 `git remote` 不匹配）→ 提示后退出，不自动执行
- 链接指向 `/commits/`、`/blob/`、`/tree/`、`/compare/`、`/releases/` 等非 issue/PR 路径 → 不处理
- 纯域名或仓库首页（如 `github.com/owner/repo`）→ 不处理
- 讨论 URL 本身（如"这条链接怎么打开"）→ 不处理

### 已明确用斜杠命令
- 用户消息以 `/req:`、`/pm:`、`/api:` 开头时，不介入，由原命令系统处理

---

## 执行流程

解析完成后：

1. **确认意图**（一行说明即可，不长篇展开）：
   ```
   🧠 识别：/req:fix 登录超时后 token 未清除
   ```

2. **读取对应命令定义**：读取 `commands/<command>.md`，按原命令流程执行

3. **传入解析出的参数**：标题、编号、类型、模块、issue、编辑意图等

4. **后续流程与原 `/req:<command>` 完全一致**：包括命令自身的确认机制、Hook 拦截、状态更新规则

**特殊规则**：
- 同一条消息包含**多个意图**时：按对话顺序逐个询问，不并行执行
- 解析结果**有歧义**时：先向用户展示推断，确认后再执行
- 命令本身需要用户输入（如章节选择、方案确认）时：进入对应命令后按其原有交互继续
