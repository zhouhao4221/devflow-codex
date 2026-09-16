# Codex Skill 规范调研

调研日期：2026-06-15。

本仓库以 Codex plugin 作为分发单位，以 skill 作为可复用工作流的作者格式。当前依据来自：

- OpenAI Codex manual `https://developers.openai.com/codex/codex-manual.md`
- 本机 Codex 内置 `skill-creator` 技能及其 `references/openai_yaml.md`

## 结构规范

一个 Codex skill 是目录加 `SKILL.md`：

```text
skills/<skill>/
  SKILL.md
  agents/openai.yaml      # 推荐：Codex App UI/调用策略/依赖声明
  scripts/                # 可选：确定性脚本
  references/             # 可选：按需加载的详细参考
  assets/                 # 可选：输出资产、模板、图标等
```

`SKILL.md` frontmatter 只使用：

```yaml
---
name: skill-name
description: 清楚说明能力、触发场景和边界。
---
```

`name` 必须与目录名一致，使用 lowercase kebab-case。`description` 是隐式触发的主要依据，应前置关键词、保持聚焦，避免把触发条件只写在正文里。

## agents/openai.yaml

`agents/openai.yaml` 是 Codex/OpenAI 产品侧元数据，推荐为每个 skill 提供：

```yaml
interface:
  display_name: "DevFlow Req: New"
  short_description: "创建新需求"
  default_prompt: "使用 $new 处理：创建新需求。"
```

可选字段包括图标、品牌色、MCP 工具依赖和 `policy.allow_implicit_invocation`。只有确实需要隐藏隐式触发时才设置：

```yaml
policy:
  allow_implicit_invocation: false
```

如果 skill 依赖 MCP，应在 `dependencies.tools` 中声明，便于 Codex 安装和连接。

## Progressive Disclosure

Codex 会先读取所有可用 skill 的 `name`、`description` 和路径，再在选中 skill 后加载完整 `SKILL.md`。因此：

- `SKILL.md` 保持短、准、流程化。
- 大段参考、示例、枚举、接口说明放入 `references/`，并在 `SKILL.md` 中说明何时读取。
- 重复、易错、需要确定性的操作放入 `scripts/`。
- 不在 skill 目录里放 README、安装指南、变更日志等辅助文档。

## Plugin 分发

Codex manual 建议本地迭代可直接使用 skill，跨团队或 marketplace 分发应打包为 plugin。本仓库采用：

```text
plugins/<plugin>/
  .codex-plugin/plugin.json
  commands/*.md
  skills/<skill>/SKILL.md
```

`skill-bindings.json` 是 commands 与 skills 的同步源。修改 skill 或 command 后运行：

```bash
python3 scripts/generate-codex-marketplace.py
./scripts/validate-skills.sh --ci
```

## Model 设置结论

当前规范没有支持在 `SKILL.md` frontmatter 或 `agents/openai.yaml` 中为单个 skill 指定 `model` 的字段。不要向 skill 元数据添加 `model`、`model_provider` 或 `model_reasoning_effort`。

Codex 支持在这些层级选择不同模型：

- `~/.codex/config.toml` 或项目 `.codex/config.toml`：设置会话默认 `model`、`model_reasoning_effort` 等。
- CLI 一次性覆盖：例如 `codex --model gpt-5.4` 或 `codex --config model='"gpt-5.4"'`。
- `~/.codex/profile-name.config.toml`：保存不同模型/推理力度 profile。
- 自定义 subagent 文件：可包含 `model`、`model_reasoning_effort`、`sandbox_mode`、`mcp_servers` 和 `skills.config`。
- 原生子代理工具：当前接口支持时，派发时显式传入模型与推理强度；参数名与上下文继承限制以会话暴露的工具说明为准。

本仓库通过[共享委派规则](../plugins/rd/shared/_delegate.md)按任务复杂度选择可用的执行模型，由主会话保留方案设计和最终验收。模型选择通过原生工具的实际参数生效，不向 skill 元数据添加未支持字段，不自动修改用户会话模型或安装 custom agent。具体支持方式参见 [OpenAI Subagents 文档](https://learn.chatgpt.com/docs/agent-configuration/subagents#choosing-models-and-reasoning)。

命令级分配由 `skill-bindings.json` 的 `executionTier` 声明，这是 DevFlow 自有生成配置，不是 Codex 原生元数据。生成器将[统一策略](../shared/command-model-routing.md)和本插件命令表打包进各插件 `shared/_command-models.md`；命令包装和对应的直接 skill 入口都先读取它。`release` 等规则化命令用经济档，报告与常规生成用标准档，需求与开发决策保留主会话。执行子代理和内部 helper 不重复路由；发布等外部操作仍由主会话按授权处理，因此不能把执行模型分配描述为整个会话自动换模型。

## 本仓库已对齐项

- 生成每个 `plugins/<plugin>/skills/<skill>/agents/openai.yaml`。
- `SKILL.md` frontmatter 限定为 `name` 和 `description`。
- 校验脚本检查 skill 名称、bindings、plugin manifests、commands、marketplace、`agents/openai.yaml`。
- 校验脚本禁止在 skill UI 元数据中写 model 相关字段，避免误用未支持配置。
