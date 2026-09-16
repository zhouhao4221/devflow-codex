---
name: req
description: 需求工作流管理 - 实时列出 REQ 和 QUICK 的状态与进度
---

# 需求工作流管理

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:req` 的档位执行；已作为执行子代理时不再次路由。

## 命令格式

```
/rd:req [--module=模块名] [--type=REQ|QUICK]
```

其他子命令使用 `/rd:new`、`/rd:dev`、`/rd:test`、`/rd:done` 等独立入口。

## 列表流程

1. 按 [_storage.md](../../shared/_storage.md) 合并 `.devflow/settings.json` 与 `.devflow/settings.local.json`，确定 primary 本仓或 readonly 主仓的需求根目录。缺少必须的 `requirementSource.path` 时报告并停止。
2. 实时扫描需求根目录 `active/` 和 `completed/`，仅将 `REQ-XXX-*.md` 与 `QUICK-XXX-*.md` 作为需求文档。`INDEX.md` 不是事实源，不读取也不重写。
3. 解析每份文档的编号、标题、类型、模块、状态、更新时间、功能或验证进度及关联。状态与目录冲突时显式标注异常；不默默修正。
4. 按 `--module`、`--type` 过滤，按状态分组展示活跃和已完成需求。头部显示插件版本、项目角色和分支策略；只显示实际可读到的数据。
5. 根据各需求的类型与状态提示下一步：REQ 草稿可评审；QUICK 草稿可开发；开发中可测试；测试中可完成。多个候选只列出，不擅自改变状态。

## 用户输入

$ARGUMENTS
