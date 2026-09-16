---
name: migrate
description: 迁移需求 - 调整需求文档目录并更新配置
---

# 迁移需求目录

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:migrate` 的档位执行；已作为执行子代理时不再次路由。

## 命令格式

```
/rd:migrate --to=<new-requirementsDir>
```

无参数或缺少 `--to` 时显示用法，停止执行，不扫描其他配置位置。

## 执行流程

1. 按[存储与配置规则](../../shared/_storage.md)合并 `.devflow/settings.json` 和 `.devflow/settings.local.json`。仅 `primary` 仓库可迁移；其他角色报告原因并停止。
2. 确定当前 `requirementsDir`（省略时为 `docs/requirements`）和目标目录。目标必须是仓库内相对路径，不能与源目录相同、互相包含，也不能已含文件。源目录不存在时报错。
3. 将源目录全部内容移动到目标目录，更新 `.devflow/settings.json` 中的 `requirementsDir`，保留其他配置字段。移动或写入失败时报告已完成的步骤和当前路径，避免误报成功。
4. 显示原目录、目标目录和更新后的配置位置。

---

## 用户输入

$ARGUMENTS
