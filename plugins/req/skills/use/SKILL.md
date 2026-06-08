---
name: use
description: 绑定需求主仓 - 将 readonly 仓库指向主仓文档
---

# 绑定需求主仓

将当前仓库绑定到一个 primary 主仓，使 readonly 仓库直接读取主仓的 `docs/requirements/` 文档。

## 命令格式

```
/req:use <primary-repo-path>
```

## 参数

- `primary-repo-path`: 需求主仓的本地绝对路径或相对路径

---

## 执行流程

### 1. 解析参数

```
主仓路径: $ARGUMENTS
```

将路径规范化为绝对路径。

### 2. 检查主仓是否有效

检查主仓是否存在以下文件或目录：

- `.devflow/settings.json`
- `docs/requirements/`

读取主仓 `.devflow/settings.json`：

```json
{
  "requirementProject": "<project-name>",
  "requirementRole": "primary",
  "requirementsDir": "docs/requirements"
}
```

**如果主仓无效**：
- 提示在主仓执行 `/req:init <project-name>`
- 不写入当前仓库配置

### 3. 读取当前绑定

读取当前仓库 `.devflow/settings.json` 和 `.devflow/settings.local.json`，识别旧的 `requirementSource`。

### 4. 更新仓库绑定

读取已有 `.devflow/settings.json`，合并以下字段后写回，不覆盖已有的 `branchStrategy` 等字段：

```json
{
  "requirementProject": "<project-name>",
  "requirementRole": "readonly",
  "requirementSource": {
    "type": "local",
    "path": "<primary-repo-absolute-path>",
    "requirementsDir": "docs/requirements"
  }
}
```

`/req:use` 绑定的仓库默认为 `readonly` 角色，仅从主仓读取需求。如需升级为主仓库，在当前仓库执行 `/req:init <project-name> --reinit`。

### 5. Legacy Claude 兼容

仅当存在 `.claude/settings.local.json` 或用户明确要求 Claude Code 兼容时，同步写入 `requirementProject` 和 `requirementRole`。不要再更新 `~/.claude-requirements/index.json`，该全局缓存已是 legacy fallback。

### 6. 项目配置检查

绑定完成后检查当前仓库的配置完整性。

#### 6.1 AGENTS.md 架构检查

检查 `AGENTS.md` 是否包含以下关键词之一：`分层架构`、`目录结构`、`技术栈`、`项目架构`、`Architecture`、`Tech Stack`、`Project Structure`。

**缺失时引导**（与 `/req:init` 步骤 8 相同）：

```
⚠️ AGENTS.md 中未检测到项目架构描述

   /req:dev 需要架构信息来生成实现方案

   选择项目类型，生成 AGENTS.md 建议片段：

   1. Go 后端（Gin + GORM 分层架构）
   2. Java 后端（Spring Boot 分层架构）
   3. 前端项目（React/Vue + TypeScript）
   4. 自定义（生成空白模板，手动填写）
   5. 跳过（稍后手动添加）

请选择（1-5）：
```

选择后读取 `<plugin-path>/templates/agent-snippets/` 对应模板，追加到 `AGENTS.md`。

#### 6.2 分支策略检查

读取 `.devflow/settings.json` 中的 `branchStrategy` 字段。

**未配置时提示**（不阻断）：

```
未配置分支策略，/req:dev 将使用默认行为
   建议执行 /req:branch init 配置分支策略
```

### 7. 输出结果

```
✅ 已绑定需求主仓

项目状态:
   - 项目: <project-name>
   - 主仓: <primary-repo-path>
   - 活跃需求: X 个
   - 已完成: Y 个

活跃需求列表:
   | 编号 | 标题 | 状态 |
   |------|------|------|
   | REQ-001 | ... | 开发中 |
   | REQ-002 | ... | 待评审 |

使用 /req 查看完整列表
```

---

## 无参数模式

当不带参数执行 `/req:use` 时：

### 显示当前绑定

```
当前项目: <project-name>
角色: readonly
主仓: <primary-repo-path>
需求目录: <primary-repo-path>/docs/requirements/

可用命令:
   - /req:use <primary-repo-path>  重新绑定主仓
   - /req:projects                 查看当前绑定
```

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 主仓路径不存在 | 提示提供有效路径 |
| 主仓未初始化 | 提示在主仓执行 `/req:init <project-name>` |

---

## 用户输入

$ARGUMENTS
