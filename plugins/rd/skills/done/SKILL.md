---
name: done
description: 完成需求 - 标记完成并归档
---

# 完成需求

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:done` 的档位执行；已作为执行子代理时不再次路由。

标记需求为已完成，归档文档。

> 存储路径和写入规则见 _storage.md（按需读取 [_storage.md](../../shared/_storage.md)）
>
> **CLI 优先级**：GitHub 走 `gh`；Gitea 按 `_gitea_cli.md`（按需读取 [_gitea_cli.md](../../shared/_gitea_cli.md)） 检测 `tea`，可用即走 `tea pulls create` / `tea issues close`，否则回退本文 curl 示例。

## 命令格式

```
/rd:done [REQ-XXX|QUICK-XXX]
```

- 省略编号时自动选择「测试中」的需求
- 多个候选时交互式选择

---

## 执行流程

### 1. 选择需求

- 指定编号 → 使用该需求
- 未指定 → 扫描 `active/` 中状态为「测试中」的需求，唯一则直接使用，多个则列出让用户选

### 2. 前置检查

- 读取需求文档元信息；REQ 检查「测试要点」，QUICK 检查「验证方式」
- 状态必须为「测试中」，否则报错退出
- 裸 `- [ ]` 未勾项要求确认或完成验证；明确标注「待观察：原因」的项可放行并在结果列出，不伪称已通过

### 3. 更新需求文档

更新文档「元信息」表格中的 `| 状态 | ... |` 为 `| 状态 | 已完成 |`；如需记录完成日期，在同一表格增加或更新 `| 完成时间 | YYYY-MM-DD |`（今日），不要另写 YAML 元信息。

勾选生命周期「已完成」对应的复选框。

### 4. 更新 PRD 跟踪

REQ 存在对应 PRD 追踪行时，更新该行状态和完成日期；QUICK 不强加 PRD 条目。PRD 不存在或无对应行时跳过。

### 5. 归档文档

将需求文档从 `active/` 移动到 `completed/`（使用 `git mv` 保留历史）。需求文档直接写入主仓，不执行全局缓存同步。

归档后运行[需求目录守卫](../../scripts/check-requirements.py)的 `--check --root <项目根>`，确认状态、生命周期与目录一致。

### 6. 输出确认

```
<REQ-XXX|QUICK-XXX> <标题> 已完成
   归档至 <requirementsDir>/completed/<编号>-<slug>.md
```

### 7. 分支合并提醒

读取 `.devflow/settings.local.json` / `.devflow/settings.json` 的 `branchStrategy`，同时读取需求文档的 `branch` 字段。无 `branchStrategy` 或 `branch` 为空 → 跳过本步。

已有创建 PR 授权时按 [pr](../pr/SKILL.md) 执行；否则仅提示可用操作。归档请求和平台配置不构成推送或 PR 授权；用户要求不创建 PR 时跳过。

**特殊情况**：
- `giteaToken` 缺失 → 提示手工 compare 链接
- Git Flow + hotfix 分支 → 需合并到 `main` 和 `develop` 两处，创建两个 PR

### 8. 关联 issue 关闭提醒

按 _issue.md 的 Issue 读取优先级（按需读取 [_issue.md](../../shared/_issue.md)） 获取 issue 编号：先查需求文档元信息 `issue` 字段，若为 `-` 或为空则查分支名 `-iN` 后缀。均未找到 → 跳过本步。

否则询问用户：

```
检测到关联 issue: #123
   是否关闭该 issue？(y/n)
```

**用户确认（y）** → 按 `repoType` 关闭 issue，逻辑同 [issue.md §5](../issue/SKILL.md)。

**用户拒绝（n）**：跳过。

---

## 与 `/rd:release` 的区别

`/rd:done` 只做归档，不发版。发版用 `/rd:release`（合并 SQL / 生成 changelog / 打 tag / 创建 Release）。

## 用户输入

$ARGUMENTS
