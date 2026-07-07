---
name: version-bumper
description: 版本号管理助手。仅在执行 /req:release 命令时触发。 自动检测各插件变更范围，按 semver 规则推导并更新插件版本号和整体版本号。
---

# 版本号管理助手

仅在 `/req:release` 命令执行时触发，负责在发版前更新 devflow 各插件版本号。

## 触发条件

仅在 `/req:release` 执行时触发，在 release 流程的步骤 2（确定版本号）之后、步骤 9（生成 changelog）之前执行。

## 版本文件

| 文件 | 字段 | 当前含义 |
|------|------|---------|
| `.agents/plugins/marketplace.json` | `plugins[]` | 整体 marketplace 清单；由生成脚本同步插件版本 |
| `plugins/req/.codex-plugin/plugin.json` | `version` | req 插件独立版本 |
| `plugins/pm/.codex-plugin/plugin.json` | `version` | pm 插件独立版本 |
| `plugins/api/.codex-plugin/plugin.json` | `version` | api 插件独立版本 |
| `plugins/diag/.codex-plugin/plugin.json` | `version` | diag 插件独立版本 |

---

## 工作流程

### 1. 读取当前版本

用 Read 工具读取所有版本文件，记录各插件当前版本号。

### 2. 检测各插件变更文件

```bash
git diff --name-only <FROM_REF>..HEAD
```

`FROM_REF` 与 release 步骤 2 中一致（平台最新 Release 的 tag，无则最新 git tag，无则仓库首次 commit）。

按文件路径前缀归属插件：

| 路径前缀 | 归属插件 |
|---------|---------|
| `plugins/req/` | req |
| `plugins/pm/` | pm |
| `plugins/api/` | api |
| `plugins/diag/` | diag |
| 其他（根目录、docs/、.agents/ 等） | 仅影响 marketplace 整体版本 |

### 3. 推导各插件 bump 等级

对每个有变更的插件，分析其目录下的 commit 信息：

```bash
git log <FROM_REF>..HEAD --pretty=format:"%s" -- plugins/<name>/
```

按最高优先级确定该插件的 bump 等级：

| commit 特征 | bump 等级 |
|------------|---------|
| `!:` 或 `BREAKING CHANGE` | major |
| `feat:` / `新功能:` | minor |
| `fix:` / `perf:` / `refactor:` / `修复:` / `优化:` / `重构:` | patch |
| `docs:` / `chore:` / `ci:` / `test:` / `build:` | 不 bump（插件功能无变化） |

无变更或仅 docs/chore 的插件：保持版本号不变。

### 4. 更新 marketplace 整体版本

`marketplace.json` 不手写整体版本字段；release 步骤完成插件版本更新后，运行生成脚本同步 marketplace 清单。

### 5. 展示版本变更预览

```
版本更新预览：

  marketplace.json:  2.26.0 → 2.27.0  (与 tag v2.27.0 同步)

  req:   3.18.0 → 3.19.0  (minor - 新增命令)
  pm:    0.2.0  → 0.2.0   (无变更)
  api:   0.3.0  → 0.3.1   (patch - 修复解析)
  diag:  0.1.0  → 0.1.0   (无变更)
```

### 6. 更新版本文件

用 Edit 工具更新各插件 JSON 文件中的 `version` 字段。`marketplace.json` 由生成脚本同步，不手写版本字段。

### 7. 暂存版本文件

```bash
git add .agents/plugins/marketplace.json plugins/req/.codex-plugin/plugin.json \
        plugins/pm/.codex-plugin/plugin.json plugins/api/.codex-plugin/plugin.json \
        plugins/diag/.codex-plugin/plugin.json
```

版本文件的修改会在 release 步骤 10 的统一 commit 中一起提交（`chore(release): prepare <version>`），**不单独提交**。

---

## 边界情况

| 场景 | 处理 |
|------|------|
| 版本号已与 tag 一致 | 跳过该文件，不重复写入 |
| 插件仅有 docs/chore 变更 | 插件版本不 bump，仅更新 marketplace |
| 无任何 Release 也无 git tag（首次发版） | FROM_REF 取仓库首次 commit，视所有 commit 为新增，各插件 minor bump |
| 版本号格式不符合 X.Y.Z | 打印警告并跳过该插件的 bump，不阻塞发版 |
