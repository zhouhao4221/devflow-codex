# Codex Marketplace 分发需求

## 背景

DevFlow 之前尝试通过 npm CLI 将 skills 安装到多个 AI 工具目录。该方案会把 Codex 原生插件能力降级成通用文件复制流程，也会引入 npm 发布、全局命令冲突和本地 hook 迁移问题。

当前决策：停止维护 npm package 分发，改为 Codex marketplace-first。

## 目标

- 用户通过 Codex marketplace 安装 DevFlow 插件。
- 插件自带 Codex 原生 commands 和 skills。
- 不默认启用 SessionStart hook。
- `skill-bindings.json` 继续作为命令到 skill 的事实来源。
- 非 Codex 工具适配保留为脚本能力，但不作为主要用户路径。

## 用户故事

- 作为 Codex 用户，我希望通过 marketplace 一次安装全部 DevFlow 插件。
- 作为 Codex 用户，我希望只安装 `req`、`api` 等单个插件。
- 作为 Codex 用户，我希望用 `/req:init`、`/req:new`、`/pm:weekly` 这样的原生命令启动工作流。
- 作为维护者，我希望 command 文件由映射表生成，避免手工维护 64 个命令入口。

## 安装方式

安装全部插件：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex --plugins
```

安装单个插件：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex/plugins/req --plugin
```

## 插件结构

每个插件必须包含：

```text
plugins/<plugin>/
  .codex-plugin/plugin.json
  commands/*.md
  skills/<skill>/SKILL.md
```

仓库级 marketplace 清单：

```text
.agents/plugins/marketplace.json
```

## 非功能需求

- 不需要 npm package metadata。
- 不需要全局 `devflow-codex` CLI。
- 不默认安装 hooks。
- 修改命令或 skill 后必须运行：

```bash
python3 scripts/generate-codex-marketplace.py
./scripts/validate-skills.sh --ci
```
