---
name: update-template
description: 更新项目需求模板并保留差异预览
---

# 更新模板

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `rd:update-template` 的档位执行；已作为执行子代理时不再次路由。

```
/rd:update-template [requirement|quick|module|prd|release-prompt|all] [--force]
```

从当前已安装的 `rd` 插件目录读取 `templates/`，按 [_storage.md](../../shared/_storage.md) 解析本仓 `requirementsDir`。仅 primary 可更新，readonly 提示到主仓执行；需求目录不存在时先 `/rd:init`。模板名称省略时列出可选项。

| 名称 | 源 | 目标 |
|------|----|------|
| requirement | `templates/requirement-template.md` | `<requirementsDir>/templates/requirement-template.md` |
| quick | `templates/quick-template.md` | `<requirementsDir>/templates/quick-template.md` |
| module | `templates/module-template.md` | `<requirementsDir>/templates/module-template.md` |
| prd | `templates/prd-template.md` | `<requirementsDir>/templates/prd-template.md` |
| release-prompt | `templates/release-prompt-template.md` | `docs/prompt/release.md` |

逐项核对源文件存在；目标相同时跳过。目标不同则展示章节、表格与本地自定义内容的差异，用户已要求覆盖或传入 `--force` 时写入；未给覆盖授权且会丢失本地自定义内容时，展示具体差异后询问。写入只发生在本仓，需求文档和 PRD 正文不会被覆盖，也不向缓存或其他仓库复制。

输出各模板的目标路径和更新、跳过或失败状态。

## 用户输入

$ARGUMENTS
