---
name: projects
description: 查看需求项目绑定 - 展示当前 DevFlow 项目配置
---

# 查看需求项目绑定

显示当前仓库的 DevFlow 需求项目配置，以及 readonly 绑定的主仓状态。

## 命令格式

```
/req:projects
```

---

## 执行流程

### 1. 读取 DevFlow 配置

按优先级读取：

- `.devflow/settings.local.json`
- `.devflow/settings.json`
- `.claude/settings.local.json`（legacy fallback）

如果没有绑定项目，提示执行 `/req:init <project-name>`。

### 2. 解析需求根目录

按角色解析：

- `primary`：当前仓库 `requirementsDir`，默认 `docs/requirements`
- `readonly`：`requirementSource.path` + `requirementSource.requirementsDir`
- legacy：仅 `.devflow` 未配置时可回退 `~/.claude-requirements/projects/<project>`

### 3. 扫描当前项目

对解析出的需求根目录收集：
- 活跃需求数量
- 已完成需求数量
- 模块数量
- PRD 是否存在
- 主仓路径（readonly）

### 4. 输出项目状态

```
需求项目状态

项目: devflow-codex
角色: primary
需求目录: docs/requirements
配置: .devflow/settings.json

统计:
   - 活跃需求: X
   - 已完成需求: Y
   - 模块: Z
   - PRD: 已存在 / 未创建

可用命令:
   - /req                 查看需求列表
   - /req:use <主仓路径>   将当前仓绑定到主仓
   - /req:init <项目名>    初始化当前仓为主仓
```

---

## 详细模式

```
/req:projects --detail
```

显示配置来源和 legacy fallback 信息：

```
配置详情

   配置来源:
      - .devflow/settings.local.json: 存在 / 不存在
      - .devflow/settings.json: 存在 / 不存在
      - .claude/settings.local.json: legacy 存在 / 不存在

   requirementSource:
      - type: local
      - path: /Users/xxx/primary-repo
      - requirementsDir: docs/requirements

   需求统计:
      - 开发中: 1
      - ✅ 已完成: 5

   关联仓库:
      - /Users/xxx/tools
```

---

## 用户输入

$ARGUMENTS
