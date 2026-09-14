# Codex 子代理按任务选择模型

Req 3.26.0 将子代理从默认继承主模型改为按任务复杂度主动选择可用模型与推理强度。主会话保留需求分析、设计、跨文件判断和最终验收；用户选择 Astra 时，由 Astra 承担这些工作。

明确的重复性工作优先 Luna，常规有界实现使用 Terra，更深入的多步执行按需选择 Sol。小任务直接调用工具，避免派发开销。选择依据是任务所需能力和运行时可用信息，不宣称模型价格排名或固定节省比例。完整策略集中在[子任务委派](../../plugins/req/shared/_delegate.md)。

派发时通过当前原生工具传入模型和推理强度。当前 `collaboration` 完整历史继承不支持模型覆盖，因此经济型执行通常使用自包含说明；需要完整历史或缺少模型覆盖能力时说明继承原因。保留原有实施准入、文件归属、代理续接和证据验收要求。

该策略取代 [9 月 12 日适配记录](2026-09-12-claude-adaptation.md)中的默认继承选择；历史行为报告保留原样。不向 `SKILL.md` frontmatter 或 `agents/openai.yaml` 添加模型字段，不修改用户的全局模型配置或插件缓存。

验证：本轮通过原生 `collaboration.spawn_agent` 以 `gpt-5.6-luna`、`low`、`fork_turns=none` 派发规则文档修改，子代理完成后由主会话核对实际 diff。这验证了显式模型参数的派发与协作流程，未测量实际费用或所有模型档位。`./scripts/validate-skills.sh --ci` 通过，`python3 scripts/test-export-skills.py` 的 6 项回归通过，`git diff --check` 通过。
