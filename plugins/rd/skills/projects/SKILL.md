---
name: projects
description: 查看当前仓库的需求项目配置和可读需求目录
---

# 需求项目

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:projects` 的档位执行；已作为执行子代理时不再次路由。

```
/rd:projects [--detail]
```

按 [_storage.md](../../shared/_storage.md) 合并本仓 `.devflow/settings.json` 和 `.devflow/settings.local.json`，展示 `requirementProject`、角色、配置的需求目录及是否可读。primary 使用本仓 `requirementsDir`，readonly 读取 `requirementSource.path` 指向的主仓及其 `requirementsDir`。缺少绑定时说明 `/rd:init` 或 `/rd:use` 的下一步。

目录可读时，实时统计 `active/` 和 `completed/` 内 REQ 与 QUICK 文件数量；`--detail` 再按状态展开。只展示当前仓及其明确绑定的主仓，不从已废弃的全局索引推测其他项目或关联仓库。纯只读。

## 用户输入

$ARGUMENTS
