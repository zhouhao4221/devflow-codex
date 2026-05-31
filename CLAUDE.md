# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 本地测试
node install.js help
node install.js list
node install.js list --plugin req
node install.js install --tool opencode --skill req-dev
node install.js install --tool opencode --all

# 校验技能文件合规性
./scripts/validate-skills.sh --ci

# 通过适配器脚本生成工具兼容产物
./scripts/setup-claude.sh . ../devflow-claude
./scripts/setup-opencode.sh . ~/.agents/skills
```

## 架构

项目是纯 Node.js CLI（`install.js`），通过 npm 分发。`npx devflow-skills` 即时可用，零下载。

### 唯一分发入口

`package.json` 的 `files` 字段包含 `install.js` + `plugins/` + `package.json`。用户 `npm install` 或 `npx` 时，80 个 SKILL.md 随包下载到本地，由 install.js 直接读取并写入目标目录。

### 两种目录布局

- **分层布局（`flat: false`）**：仅 Claude Code，保持 `plugins/<plugin>/skills/<name>/SKILL.md`
- **扁平布局（`flat: true`）**：OpenCode、Codex、Cursor、Copilot、CodeBuddy、Windsurf，输出为 `.agents/skills/<plugin>-<name>/SKILL.md`，frontmatter `name` 自动加插件前缀

### 关键文件

- `install.js` — CLI 单一入口，包含 install / list / uninstall / add / version / help 全部子命令
- `plugins/*/skills/*/SKILL.md` — 80 个技能的唯一事实来源，遵循 agentskills.io 规范（YAML frontmatter + Markdown）
- `skill-bindings.json` — 命令-技能映射声明，CI 校验其与 `plugins/` 下文件的一致性
- `scripts/` — 适配器脚本（手动/CI 模式）和校验脚本

### 设计约束

- 80 个 SKILL.md 正文不修改，跨工具适配在复制时完成（frontmatter `name` 替换）
- 技能名必须匹配 `^[a-z0-9]+(-[a-z0-9]+)*$`
- 项目同时用作：
  - **npm 包** — `npx devflow-skills` 分发给终端用户
  - **上游仓库** — `devflow-claude` 通过 `scripts/setup-claude.sh` 从此仓库拉取技能
