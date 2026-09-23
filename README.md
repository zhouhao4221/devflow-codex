# DevFlow Codex Plugins

DevFlow 是面向 Codex marketplace 的工作流插件集合，包含 78 个 skills 和 63 个 plugin-scoped slash commands。

[devflow-codex](https://github.com/zhouhao4221/devflow-codex) 与 [devflow-claude](https://github.com/zhouhao4221/devflow-claude) 均由同一维护者维护，分别采用 Codex 和 Claude 风格。两者是平行实现，功能适配记录见 [2026 年 9 月更新](docs/changes/2026-09-12-claude-adaptation.md)。

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
- `rd / api / pm / diag / uat` 五个 Codex plugins
- 每个插件的 `.codex-plugin/plugin.json`
- 每个插件的 `commands/*.md` 和 `skills/*/SKILL.md`

### 只安装一个插件

例如只安装需求工作流：

```bash
npx codex-marketplace add zhouhao4221/devflow-codex/plugins/rd --plugin
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
/rd:init my-project
/rd:new 登录流程优化
/rd:status
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

从 `req` 插件升级时，安装 `rd` 插件并停用旧的 `req` 插件。命令前缀改为 `/rd:`；PR 创建、状态、评论查看和合并由 `/rd:pr` 处理，代码审查与按评论改代码用 `/rd:review`，需求评审用 `/rd:req-review`。项目需求文档和 `.devflow/` 配置保持原路径；QUICK 文档现在按 `new-quick → dev → test → done` 流转。

### 更新插件

重新执行安装命令即可拉取最新插件内容。更新后重启 Codex，让 marketplace 缓存和 slash command 列表刷新。

## 插件

| 插件 | Skills | Commands | 用途 |
|------|--------|----------|------|
| `rd` | 44 | 33 | 研发工作流：PRD、需求、开发、测试、PR 和发布 |
| `api` | 8 | 7 | Swagger/OpenAPI 解析、字段映射、代码生成 |
| `pm` | 14 | 13 | 周报、月报、风险、进度、里程碑 |
| `diag` | 5 | 4 | 生产日志诊断、堆栈分析、代码关联 |
| `uat` | 7 | 6 | 用户验收测试、失败上报、测试报告 |

## 命令执行模型

命令按工作类型选择执行模型：`release`、查询和规则化操作优先经济档（GPT-6 Luna）；报告和常规生成使用标准档（GPT-6 Sol，`medium`）；需求、开发和设计保留用户选择的主会话模型。经济档中，固定输入的机械摘取用 `low`，需要解释测试结果或归纳 diff 语义时用 `medium`；陌生调用链探索和深入多步实施按需使用 Sol / `high`。直接调用 skill 同样生效。主会话仍负责交互、验收和已授权的外部操作；派发前核对当前工具可用的型号与推理强度，不可用时说明并回退。详见[命令模型路由](shared/command-model-routing.md)。

## 仓库结构

```text
plugins/<plugin>/
  .codex-plugin/plugin.json   # Codex plugin manifest
  commands/*.md               # Codex marketplace slash commands
  skills/<skill>/SKILL.md     # Codex skills
  skills/<skill>/agents/openai.yaml # Codex App UI metadata
  shared/                     # 按需读取的公共规则和子任务角色
  AGENTS.md                   # 插件专属维护约定
  templates/                  # 插件模板资源，可选

.agents/plugins/marketplace.json
skill-bindings.json
scripts/
```

`skill-bindings.json` 是 commands 与 skills 的映射表。新增、删除或重命名 skill 时，必须同步更新映射表并重新生成 marketplace 文件。

Claude 平行实现的最近对照提交及采纳结果见[更新记录](docs/changes/2026-09-16-claude-sync.md)。Codex 保留 UAT 插件，因为桌面会话具备可探测的交互能力。

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
./scripts/setup-claude.sh . ./dist/claude
```

导出会携带共享参考和模板，并重写扁平布局的相对链接。输出目录必须为空或由本导出器创建；已有非导出目录请使用新路径。分层导出只生成兼容资源，不会更新另一个平行实现仓库。

验证共享引用及两种导出：

```bash
python3 scripts/check-layout.py
python3 scripts/test-export-skills.py
```

## Codex 行为约定

- 不安装默认 `SessionStart` hook。
- 初始化提示只在用户主动执行 `/rd:init` 或 `/rd:help` 等命令时出现。
- hooks 如果未来需要，必须作为显式 opt-in 插件或命令开启。
- DevFlow 项目状态使用 `.devflow/settings.json` 和 `.devflow/settings.local.json`，不再依赖 Claude 专属目录。
- Skill 规范见 `docs/codex-skill-spec.md`。不要在 `SKILL.md` 或 `agents/openai.yaml` 中写 model 选择；需要不同模型时使用 Codex config/profile/custom agent。

## 许可证

[Apache License 2.0](LICENSE)
