---
name: projects
description: 列出所有需求项目 - 查看主仓需求目录中的所有项目
---

# 列出所有需求项目

显示主仓需求目录中所有项目的概览。

## 命令格式

```
/req:projects
```

---

## 执行流程

### 1. 检查主仓需求目录

检查 `<requirementSource.path>/<requirementsDir>/` 是否存在且非空。

**如果缓存不存在或为空**：
```
暂无需求项目

使用 /req:init <project-name> 创建第一个项目
```

### 2. 读取全局索引

读取 `（无中心索引，已废弃）` 获取各项目的元信息和关联仓库列表。

### 3. 扫描每个项目

对每个项目收集：
- 活跃需求数量
- 已完成需求数量
- 关联的仓库列表
- 创建时间

### 4. 获取当前仓库绑定

读取当前仓库的 `.devflow/settings.local.json` / `.devflow/settings.json` 中的 `requirementProject`，legacy fallback 到 `.claude/settings.local.json`

### 5. 输出项目列表

```
需求项目列表

| 项目 | 活跃 | 已完成 | 关联仓库 | 创建时间 |
|------|------|--------|---------|---------|
| my-saas-product | 3 | 12 | 2 | 2026-01-01 |
| internal-tools | 1 | 5 | 1 | 2026-01-05 |
| client-portal | 0 | 0 | 0 | 2026-01-08 |

= 当前仓库绑定的项目

缓存路径: <requirementSource.path>/<requirementsDir>/

可用命令:
   - /req:use <project>   切换到指定项目
   - /req:init <project>  创建新项目
```

---

## 详细模式

```
/req:projects --detail
```

显示每个项目的详细信息：

```
需求项目列表


my-saas-product (当前项目)

   创建时间: 2026-01-01
   路径: <requirementSource.path>/<requirementsDir>/

   需求统计:
      - 开发中: 1
      - 待评审: 1
      - 草稿: 1
      - ✅ 已完成: 12

   关联仓库:
      - /Users/xxx/backend
      - /Users/xxx/frontend


internal-tools

   创建时间: 2026-01-05
   路径: <requirementSource.path>/<requirementsDir>/

   需求统计:
      - 开发中: 1
      - ✅ 已完成: 5

   关联仓库:
      - /Users/xxx/tools
```

---

## 用户输入

$ARGUMENTS
