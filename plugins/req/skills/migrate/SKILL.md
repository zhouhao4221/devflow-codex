---
name: migrate
description: 迁移需求 - 将本地需求迁移到全局缓存
---

# 迁移需求

将本地 `docs/requirements/` 中的需求迁移到全局缓存。

## 命令格式

```
/req:migrate <project-name> [--keep]
```

## 参数

- `project-name`: 目标项目名称（必填）
- `--keep`: 保留本地文件（可选，默认删除）

---

## 执行流程

### 1. 前置检查

`docs/requirements/active` 和 `completed` 均不存在时报错退出，提示使用 `/req:init`。统计本地活跃/已完成需求数量。

### 2. 检查目标项目

目标路径 `~/.claude-requirements/projects/<project-name>/`。项目不存在时自动创建；已存在且有需求文档时，询问合并策略：合并（编号冲突时重新编号）、覆盖、取消。

### 3. 显示迁移预览

```
需求迁移预览

源目录: docs/requirements/
目标项目: <project-name>
目标路径: ~/.claude-requirements/projects/<project-name>/

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

将 active/、completed/、templates/（如存在）分别复制到目标项目对应目录。

### 5. 处理编号冲突（合并模式）

如果目标项目已有需求，检查编号冲突：

```
⚠️ 检测到编号冲突

冲突列表:
- REQ-001 (本地: 部门渠道关联 vs 远程: 用户管理)
- REQ-002 (本地: 用户积分系统 vs 远程: 权限配置)

处理方式:
- REQ-001 → 保留远程，本地重命名为 REQ-004
- REQ-002 → 保留远程，本地重命名为 REQ-005
```

### 6. 绑定当前仓库

> 写入规范见 `_storage.md`。

读取已有 `.claude/settings.local.json`，合并以下字段后写回（不覆盖已有的 `branchStrategy` 等字段）：

```json
{
  "requirementProject": "<project-name>"
}
```

### 7. 清理本地文件（默认行为）

无 `--keep` 时删除本地 active/、completed/、templates/ 目录。指定 `--keep` 时保留并提示手动清理命令。

### 8. 输出结果

```
✅ 迁移完成！

迁移统计:
- 迁移活跃需求: X 个
- 迁移已完成需求: Y 个
- 重新编号: Z 个

新位置: ~/.claude-requirements/projects/<project-name>/

当前仓库已绑定到项目 "<project-name>"

下一步:
- 查看需求列表: /req
- 在其他仓库绑定: /req:use <project-name>
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
