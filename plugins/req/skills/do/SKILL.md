---
name: do
description: 智能开发 - AI 分析意图，自动选择流程，生成方案并执行
---

# 智能开发

描述你要做的事，AI 自动分析意图、选择合适的流程、生成方案并执行。无需关心该用哪个命令。

> **Audience:** Engineer
> 此命令**不受仓库角色限制**，readonly 仓库也可执行。
> 不触发缓存同步（无需求文档）。
>
> **CLI 优先级**：GitHub 用 `gh`；Gitea 按 `_gitea_cli.md` 检测 `tea`，可用即走 `tea`，否则回退本文 curl 示例。

## 命令格式

```
/req:do <描述> [--from-issue=#编号]
```

示例：
- `/req:do 优化订单查询性能，加索引和分页缓存`
- `/req:do 重构用户服务层，拆分过大的方法`
- `/req:do 升级 Go 到 1.23`
- `/req:do 统一错误码格式`
- `/req:do 给商品列表加个搜索功能`
- `/req:do --from-issue=#42` - 从 issue 读取描述后分析

---

## 执行流程

### 0. （可选）从 issue 读取描述

若命令带 `--from-issue=#N`，按 [_issue.md 的 Issue 拉取规范](./_issue.md#issue-拉取规范) 拉取 issue，把 issue 标题 + 正文拼成用户描述传入步骤 1。

本命令不创建需求文档，issue 编号通过**分支名 `-iN` 后缀**持久化（步骤 3 创建分支时追加），供 `/req:commit`、步骤 5 关闭 issue 等后续操作识别。参见 [_issue.md 的 Issue 与分支关联](./_issue.md#issue-与分支提交的关联)。

### 1. AI 分析意图

根据用户描述，AI 判断任务类型和规模：

```
分析：<用户描述>

  类型：<优化 | 重构 | 升级 | 规范 | 小功能 | 修复>
  规模：<轻量（无需文档）| 中等（建议创建 QUICK）| 正式（建议创建 REQ）>
  影响范围：<涉及的模块/文件数估算>
```

**类型判断依据：**

| 类型 | 关键词/特征 | 分支前缀 | 提交前缀 |
|------|-----------|---------|---------|
| 优化 | 性能、缓存、索引、查询慢、加速 | `improve/` | `优化` |
| 重构 | 重构、拆分、抽取、整理、解耦 | `improve/` | `重构` |
| 升级 | 升级、更新、迁移、版本 | `improve/` | `构建` |
| 规范 | 统一、规范、格式、命名、lint | `improve/` | `样式` |
| 小功能 | 增加、新增、添加、支持 | `feat/` | `新功能` |
| 修复 | 修复、bug、报错、异常、失败 | `fix/` | `修复` |

**规模判断依据：**

| 规模 | 条件 | 建议流程 |
|------|------|---------|
| 轻量 | 改动 < 5 个文件，无新 API/表结构 | 直接执行（本命令） |
| 中等 | 改动 5~15 个文件，或有新 API | 建议 `/req:new-quick` |
| 正式 | 改动 > 15 个文件，涉及多模块/新业务 | 建议 `/req:new` |

**规模为中等或正式时**：
```
此任务规模较大，建议使用正式流程以便追踪：

  /req:new-quick <标题>    有文档记录的轻量任务
  /req:new <标题>          正式需求（含评审、测试）

继续用轻量模式执行，还是切换到上述命令？
```

等待用户选择。用户选择继续 → 进入步骤 2。

### 2. 分析代码，生成方案

> 读取项目 AGENTS.md 的「项目架构」章节，了解分层结构和目录布局。

AI 搜索代码库，定位相关文件：

```
代码分析：

涉及文件：

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| internal/order/store/order_store.go | 修改 | 添加查询索引 |
| internal/order/biz/order_list.go | 修改 | 增加分页缓存逻辑 |
| internal/order/model/order_model.go | 修改 | 补充索引注解 |

修改方案：

1. order_model.go
   - Order 表 `status` + `created_at` 添加复合索引

2. order_store.go
   - ListOrders 查询增加 hint 走索引
   - 添加 count cache（5 分钟 TTL）

3. order_list.go
   - 首页查询结果缓存（Redis，按筛选条件 key）

是否按以上方案执行？（可以补充说明或调整方向）
```

**等待用户确认**。用户可以：
- 确认方案 → 进入步骤 3
- 补充/调整 → AI 重新分析
- 放弃 → 结束

### 3. 执行方案

**无 `--from-issue`**：直接在当前分支上开发，不创建新分支。

**有 `--from-issue=#N`**：在步骤 2 方案确认后、开始编码前，根据分支策略创建分支：
1. 读取 `branchStrategy`（未配置则使用默认前缀）
2. 分支前缀由步骤 1 的类型判断决定（见类型判断依据表的「分支前缀」列）
3. AI 根据 issue 标题生成英文 slug
4. 分支名末尾追加 `-i<N>`（参见 [_issue.md 的 Issue 与分支关联](./_issue.md#issue-与分支提交的关联)）
5. 示例：`fix/optimize-order-query-i42`、`feat/add-search-feature-i12`

AI 按确认的方案修改代码。

### 4. 完成提示

```
✅ 完成！

修改文件：
- internal/order/store/order_store.go（+25 -3）
- internal/order/biz/order_list.go（+40 -5）
- internal/order/model/order_model.go（+2 -0）

后续操作：
- /req:commit       提交代码
- /req:pr           创建 PR
```

若来自 `--from-issue=#N`，在后续操作提示中追加：
```
提交时建议在 commit message 末尾添加 closes #N 以自动关联 issue
```

### 5. （可选）关闭 issue

仅当命令带 `--from-issue=#N` 时执行本步骤。

在步骤 4 展示完成提示后，询问用户：

```
本次任务来自 issue #N
   是否关闭该 issue？(y/n)
```

**用户确认（y）** → 按 `repoType` 关闭 issue，逻辑同 [issue.md §5](./issue.md)。

**用户拒绝（n）**：跳过。

---

## 与其他命令的区别

| 命令 | 文档 | 分支 | AI 分析 | 适用场景 |
|------|------|------|--------|---------|
| `/req:do` | 无 | 自动选前缀 | 分析意图+方案 | 优化、重构、升级、小调整 |
| `/req:fix` | 无 | `fix/` | 定位 bug | 明确的 bug 修复 |
| `/req:new-quick` | QUICK 文档 | `fix/` | 无 | 需要记录的小任务 |
| `/req:new` | REQ 文档 | `feat/` | 需求分析 | 正式业务需求 |

**选择依据：**
- 知道是 bug → `/req:fix`
- 优化/重构/升级/规范化 → `/req:do`
- 需要文档记录 → `/req:new-quick`
- 正式业务功能 → `/req:new`
- 不确定用哪个 → `/req:do`（AI 帮你判断）

---

## 用户输入

$ARGUMENTS
