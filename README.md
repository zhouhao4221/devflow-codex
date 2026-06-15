# DevFlow Codex Plugins

DevFlow 是面向 Codex marketplace 的工作流插件集合，包含 79 个 skills 和 64 个 plugin-scoped slash commands。

## 安装手册

### 前置条件

- 已安装 Codex CLI。
- 已登录可访问 GitHub 的网络环境。
- 本仓库按 Codex marketplace 结构提供插件，不再提供 `devflow-codex` npm CLI。

### 安装全部插件

从 GitHub 安装全部 DevFlow 插件：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex --plugins
```

安装内容：

- `.agents/plugins/marketplace.json`
- `req / api / pm / diag / uat` 五个 Codex plugins
- 每个插件的 `.codex-plugin/plugin.json`
- 每个插件的 `commands/*.md` 和 `skills/*/SKILL.md`

### 只安装一个插件

例如只安装需求工作流：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex/plugins/req --plugin
```

其他插件路径：

```text
zhouhao4221/devflow-codex/plugins/api
zhouhao4221/devflow-codex/plugins/pm
zhouhao4221/devflow-codex/plugins/diag
zhouhao4221/devflow-codex/plugins/uat
```

### 使用命令

安装后重启 Codex，使用 plugin-scoped slash commands：

```text
/req:init my-project
/req:new 登录流程优化
/req:status
/api:import
/pm:weekly
```

### 从旧版迁移

旧版 npm CLI 和本地生成目录已废弃。如果机器上曾安装过旧版，可以清理：

```bash
npm uninstall -g @zhouhao4221/devflow-skills
rm -rf .agents/skills .codex/commands
```

本仓库的项目说明已迁移到 `AGENTS.md`。根目录不再保留工具专属说明文件。

### 更新插件

重新执行安装命令即可拉取最新插件内容。更新后重启 Codex，让 marketplace 缓存和 slash command 列表刷新。

## 插件

| 插件 | Skills | Commands | 用途 |
|------|--------|----------|------|
| `req` | 45 | 34 | 需求全生命周期：PRD、需求、开发、测试、发布 |
| `api` | 8 | 7 | Swagger/OpenAPI 解析、字段映射、代码生成 |
| `pm` | 14 | 13 | 周报、月报、风险、进度、里程碑 |
| `diag` | 5 | 4 | 生产日志诊断、堆栈分析、代码关联 |
| `uat` | 7 | 6 | 用户验收测试、失败上报、测试报告 |

## 仓库结构

```text
plugins/<plugin>/
  .codex-plugin/plugin.json   # Codex plugin manifest
  commands/*.md               # Codex marketplace slash commands
  skills/<skill>/SKILL.md     # Codex skills
  skills/<skill>/agents/openai.yaml # Codex App UI metadata
  templates/                  # 插件模板资源，可选

.agents/plugins/marketplace.json
skill-bindings.json
scripts/
```

`skill-bindings.json` 是 commands 与 skills 的映射表。新增、删除或重命名 skill 时，必须同步更新映射表并重新生成 marketplace 文件。

## 本地开发

重新生成 Codex plugin manifest、command 文件和 skill UI 元数据：

```bash
python3 scripts/generate-codex-marketplace.py
```

校验 skills、commands、plugin manifest 和 marketplace 清单：

```bash
./scripts/validate-skills.sh --ci
```

为非 Codex 工具生成扁平 skills 目录仍保留为兼容能力，但不是主分发路径：

```bash
./scripts/setup-opencode.sh . ~/.agents/skills
./scripts/setup-claude.sh . ../devflow-claude
```

## Codex 行为约定

- 不安装默认 `SessionStart` hook。
- 初始化提示只在用户主动执行 `/req:init` 或 `/req:help` 等命令时出现。
- hooks 如果未来需要，必须作为显式 opt-in 插件或命令开启。
- DevFlow 项目状态使用 `.devflow/settings.json` 和 `.devflow/settings.local.json`，不再依赖 Claude 专属目录。
- Skill 规范见 `docs/codex-skill-spec.md`。不要在 `SKILL.md` 或 `agents/openai.yaml` 中写 model 选择；需要不同模型时使用 Codex config/profile/custom agent。

## 许可证

[Apache License 2.0](LICENSE)
