# Codex Marketplace-First 分发设计

## 状态

旧的 npm/CLI 分发方案已废弃。DevFlow 当前采用 Codex marketplace-first：

- 主分发：Codex plugin marketplace
- 主结构：`plugins/<plugin>/.codex-plugin/plugin.json`
- 主入口：plugin-scoped slash commands，例如 `/req:init`
- 底层能力：`plugins/<plugin>/skills/<skill>/SKILL.md`
- 兼容能力：保留 `setup-opencode.sh` 和 `setup-claude.sh`，但不作为主路径

## 目录结构

```text
devflow-codex/
  .agents/plugins/marketplace.json
  plugins/
    req/
      .codex-plugin/plugin.json
      commands/*.md
      skills/*/SKILL.md
      templates/
    api/
    pm/
    diag/
    uat/
  scripts/
    generate-codex-marketplace.py
    validate-skills.sh
  skill-bindings.json
```

## 设计原则

1. Codex marketplace 是唯一主分发面。
2. skills 仍是真实工作流说明，不做成单独产品入口。
3. commands 从 `skill-bindings.json` 生成，避免命令和 skill 漂移。
4. 不默认安装 hooks，尤其不使用 `SessionStart` 欢迎提示。
5. npm package 不再发布；仓库不保留 `package.json`、`package-lock.json` 或 `install.js`。

## 用户安装

安装全部插件：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex --plugins
```

安装单个插件：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex/plugins/req --plugin
```

## 本地开发流程

修改 `skill-bindings.json`、skill 或插件 metadata 后：

```bash
python3 scripts/generate-codex-marketplace.py
./scripts/validate-skills.sh --ci
```

校验范围：

- SKILL.md frontmatter 与目录名一致
- `skill-bindings.json` 覆盖所有 skills
- command 绑定的 primary/additional skills 存在
- 每个插件存在 `.codex-plugin/plugin.json`
- 每个 command 存在 `plugins/<plugin>/commands/<command>.md`
- `.agents/plugins/marketplace.json` 覆盖所有插件
