---
name: migrate
description: Legacy 迁移 - 将旧版缓存需求迁回主仓文档
---

# Legacy 迁移

将旧版 `~/.claude-requirements` 全局缓存中的需求迁移回主仓 `docs/requirements/`。

> 新版 DevFlow 不再默认使用全局缓存。primary 仓库直接维护 `docs/requirements/`，readonly 仓库通过 `.devflow/settings.json` 的 `requirementSource.path` 读取主仓。

## 命令格式

```
/req:migrate <project-name> [--keep-cache]
```

## 参数

- `project-name`: legacy 缓存中的项目名称（必填）
- `--keep-cache`: 保留 legacy 缓存文件（可选，默认不删除，除非用户确认清理）

---

## 执行流程

### 1. 前置检查

检查 `~/.claude-requirements/projects/<project-name>/` 是否存在。当前仓库如果没有 `.devflow/settings.json`，先提示执行 `/req:init <project-name>` 初始化主仓配置。

### 2. 检查目标路径

源路径为 `~/.claude-requirements/projects/<project-name>/`。目标路径为当前仓库 `.devflow` 配置中的 `requirementsDir`，默认 `docs/requirements/`。目标已存在且有需求文档时，询问合并策略：合并（编号冲突时重新编号）、覆盖、取消。

### 3. 显示迁移预览

```
需求迁移预览

源目录: ~/.claude-requirements/projects/<project-name>/
目标项目: <project-name>
目标路径: docs/requirements/

迁移内容:
- 活跃需求: X 个
- 已完成需求: Y 个
- 模板文件: 1 个

文件列表:
活跃需求:
REQ-001-部门渠道关联.md
REQ-002-用户积分系统.md
REQ-003-订单导出优化.md

已完成:
REQ-000-初始化项目.md
```

### 4. 执行迁移

将 active/、completed/、modules/、templates/、PRD.md（如存在）分别复制到主仓需求目录。

### 5. 处理编号冲突（合并模式）

如果目标目录已有需求，检查编号冲突：

```
⚠️ 检测到编号冲突

冲突列表:
- REQ-001 (本地: 部门渠道关联 vs 远程: 用户管理)
- REQ-002 (本地: 用户积分系统 vs 远程: 权限配置)

处理方式:
- REQ-001 → 保留远程，本地重命名为 REQ-004
- REQ-002 → 保留远程，本地重命名为 REQ-005
```

### 6. 更新 DevFlow 配置

读取已有 `.devflow/settings.json`，合并以下字段后写回（不覆盖已有的 `branchStrategy` 等字段）：

```json
{
  "requirementProject": "<project-name>",
  "requirementRole": "primary",
  "requirementsDir": "docs/requirements"
}
```

### 7. 清理 legacy 缓存（可选）

默认保留 legacy 缓存。只有用户明确确认时，才手动删除 `~/.claude-requirements/projects/<project-name>/`。

### 8. 输出结果

```
✅ 迁移完成！

迁移统计:
- 迁移活跃需求: X 个
- 迁移已完成需求: Y 个
- 重新编号: Z 个

新位置: docs/requirements/

当前仓库已初始化为 primary 项目 "<project-name>"

下一步:
- 查看需求列表: /req
- 在 readonly 仓绑定此主仓: /req:use <primary-repo-path>
```

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 本地无需求 | 提示使用 `/req:init` |
| 目标项目有冲突 | 提供合并策略选择 |
| 权限不足 | 提示检查目录权限 |
| 迁移中断 | 回滚已迁移文件 |

---

## 用户输入

$ARGUMENTS
