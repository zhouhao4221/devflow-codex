---
name: use
description: 绑定主项目 - 将当前仓库设为只读，直读主项目需求
---

# 绑定主项目

执行模型：按[命令模型路由](../../shared/_command-models.md)中 `req:use` 的档位执行；已作为执行子代理时不再次路由。

将当前仓库设为 `readonly`，绑定到一个 primary 仓库，运行时**直接读取**其需求文档（无主仓需求目录、无副本）。

## 命令格式

```
/req:use <primary-repo-path>
```

## 参数

- `primary-repo-path`: primary 仓库根目录的**绝对路径**（拥有需求文档的项目）

---

## 执行流程

### 1. 解析参数

```
目标主项目: $ARGUMENTS   # 绝对路径
```

### 2. 校验主项目

- 路径不存在 -> 报错，要求提供有效的 primary 仓库绝对路径
- 读取目标路径下 `.devflow/settings.json` 的 `requirementsDir`（缺省 `docs/requirements`）
- 检查 `<path>/<requirementsDir>/` 是否存在；不存在 -> 报错，提示先在主项目执行 `/req:init`

### 3. 写入绑定

> 写入规范见 _storage.md（按需读取 [_storage.md](../../shared/_storage.md)）。

- `.devflow/settings.json`（合并写入，不覆盖既有 `branchStrategy` 等）：
  ```json
  { "requirementRole": "readonly", "requirementProject": "<主项目名>" }
  ```
- `.devflow/settings.local.json`（合并写入，本机路径不入 git）：
  ```json
  { "requirementSource": { "path": "<绝对路径>", "project": "<主项目名>" } }
  ```

> `requirementProject` 仅作标签（取主项目 `.devflow/settings.json` 的同名字段）；真正定位需求靠 `requirementSource.path`。

### 4. 项目配置检查

#### 4.1 AGENTS.md 架构检查

检查 AGENTS.md 是否含：`分层架构`、`目录结构`、`技术栈`、`项目架构`、`Architecture`、`Tech Stack`、`Project Structure` 之一。缺失时引导（与 `/req:init` 架构检查一致），选择项目类型后从 `<plugin-path>/templates/agent-snippets/` 追加片段。

#### 4.2 分支策略检查

读取 `.devflow/settings.json` 的 `branchStrategy`，未配置时提示（不阻断）执行 `/req:branch init`。

### 5. 输出结果

```
已绑定主项目（readonly）

主项目: <绝对路径>
需求目录: <path>/<requirementsDir>/
角色: readonly（直读，无副本）

需求概览:
   - 活跃: X 个   已完成: Y 个

使用 /req 查看完整列表
```

---

## 无参数模式

不带参数执行 `/req:use` 时显示当前绑定：

```
当前角色: <primary | readonly>
# readonly 额外显示：
主项目: <requirementSource.path>
需求目录: <主项目 requirementsDir>

可用命令:
   - /req:use <primary-repo-path>  绑定/切换主项目
   - /req:projects                 查看绑定状态
```

---

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 路径不存在 | 报错，要求有效的 primary 仓库绝对路径 |
| 主项目无需求目录 | 提示先在主项目执行 `/req:init` |
| 当前仓库本身是 primary | 提示 primary 仓库无需绑定；如确需改为只读，先确认 |

---

## 用户输入

$ARGUMENTS
