---
name: migrate
description: 迁移需求 - 调整需求目录位置或从旧布局迁移到 .devflow
---

# 迁移需求

支持两类迁移：
1. **配置迁移**：从 v2.x 旧布局（`.claude/` 配置 + `~/.claude-requirements/` 全局缓存）迁到 v3（`.devflow/` + 无缓存）
2. **目录迁移**：调整需求文档存放目录（`requirementsDir`）

## 命令格式

```
/req:migrate [--to=<new-requirementsDir>]
```

- 无参数：执行配置迁移（旧布局 -> `.devflow/`）
- `--to=<dir>`：把需求目录迁移到新位置并更新 `requirementsDir`

---

## 执行流程

### 1. 识别当前布局

读 `.devflow/settings.json`（新）或 `.claude/settings.json(.local)`（旧）。检测是否存在旧全局缓存 `~/.claude-requirements/projects/<project>/`。

### 2A. 配置迁移（检测到 `.claude/` 旧 DevFlow 配置）

> 等价于运行 [`scripts/migrate-config.sh`](../scripts/migrate-config.sh)。

- 把 `.claude/settings.json(.local)` 中的 DevFlow 字段搬到 `.devflow/`：
  - `requirementProject` / `requirementRole` / `requirementsDir` / `branchStrategy` -> `.devflow/settings.json`
  - `giteaToken` -> `.devflow/settings.local.json`
- **不搬** Claude Code 自身的 hooks/permissions（留在 `.claude/settings.json`）
- readonly 仓库：提示改用 `/req:use <primary-repo-path>` 重新绑定（旧缓存寻址已废弃）

> **旧全局缓存的数据**：primary 仓库的需求文档本就在本地 `docs/requirements/`，缓存只是副本。迁移确认本地完整后，可手动删除 `~/.claude-requirements/projects/<project>/`。若出现本地缺失、仅缓存有的异常，先从缓存 `mv` 回本地需求目录再删缓存。

### 2B. 目录迁移（提供 `--to`）

- 将当前 `requirementsDir` 下全部内容 `mv` 到 `--to` 指定的新目录
- 更新 `.devflow/settings.json` 的 `requirementsDir` 为新值

### 3. 输出结果

显示迁移类型、搬运的字段/文件、新配置位置与后续提示（如 readonly 重绑定、删除旧缓存）。

---

## 用户输入

$ARGUMENTS
