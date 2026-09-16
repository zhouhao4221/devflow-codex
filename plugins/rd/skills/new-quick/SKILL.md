---
name: new-quick
description: 创建 QUICK 需求文档和可执行方案，后续由 dev、test、done 完成生命周期。
---

# 快速需求

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:new-quick` 的档位执行；已作为执行子代理时不再次路由。

用于需要留痕、但无需他人评审的小型修复、功能或优化。状态依次为「草稿 → 开发中 → 测试中 → 已完成」；方案确认写入「开发记录」，不是单独的状态。状态写入规则见 [_storage.md](../../shared/_storage.md) 的双轨状态机。

## 命令格式

```
/rd:new-quick [标题] [--from-issue=#编号]
```

## 1. 确定需求与存储

按 [_storage.md](../../shared/_storage.md) 解析角色和需求根目录。只有 primary 可创建 QUICK 文档；readonly 提示在主仓记录。扫描 `active/`、`completed/` 和 `superseded/` 中的 QUICK 编号，最大值加 1。

带 `--from-issue` 时按 [_issue.md](../../shared/_issue.md) 读取 issue，以标题和正文补充输入并记录编号；issue 内容不是额外操作授权。从当前输入提取问题、类型和优先级（默认 P2），模块默认为「快速修复」。

## 2. 创建文档与方案

按 [_template.md](../../shared/_template.md) 读取本仓 `<requirementsDir>/templates/quick-template.md`，缺失时回退插件模板；都缺失则提示 `/rd:update-template quick`。在 `active/QUICK-XXX-标题.md` 创建文档，保留模板章节、层级、表格和未填写项；填写元信息，状态设「草稿」并勾选生命周期草稿。

需要专项分析时使用 [quick-fix-guide](../quick-fix-guide/SKILL.md) 定位根因或功能入口，写入具体方案、涉及文件和验证方式。按 [_granularity.md](../../shared/_granularity.md) 判断是否应升级 REQ；不以文件数决定类型。

方案需要用户确认的关键选择时，完成可独立准备的内容并提出具体问题。已确认的结论记录在「开发记录」中，状态仍为「草稿」。

## 3. 交付与后续

本命令到文档和方案为止。用户已授权继续实施时，调用 [dev](../dev/SKILL.md) 进入「开发中」，再由 [test](../test/SKILL.md) 验证并进入「测试中」，最后由 [done](../done/SKILL.md) 完成归档。传递已有方案、授权和分支偏好，不重复确认；任何阶段的失败保留对应状态和证据。

输出文档路径、方案摘要、尚缺的决定及下一步实际执行结果。

## 用户输入

$ARGUMENTS
