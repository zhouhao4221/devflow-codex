# DevFlow 技能规范与优化检查

日期：2026-09-23。检查基线：`675f355eb02d522935a78b6c222c7c32e0485e3e`。

## 结论与范围

5 个插件、79 个技能通过基础格式与仓库一致性检查；正文抽查发现运行依赖、验收预期和入口契约问题。因此结论是“结构合规，部分工作流需要修正”，不能把静态通过解释为所有技能可直接执行。

全量检查 frontmatter、目录命名、绑定、生成元数据、相对 Markdown 链接和导出布局。正文重点覆盖 RD 的 do/dev/review/release/new-quick/test，PM 的 ask/export/report-generator，UAT 的 init/run/uat-executor，以及 API、Diag 的代表性流程；未逐条执行全部命令，也未连接生产主机、发布版本或运行真实 UI 验收。

依据为本机 `skill-creator` 及其基础校验器、仓库实际生成/校验代码，以及 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills)和[插件技能编写文档](https://developers.openai.com/plugins/build/skills)。官方要求技能包含名称和描述，按需读取正文与资源；本仓 frontmatter 仅允许 `name`、`description`、强制生成 UI 文件等，是项目约定，不能当成平台全部能力的限制。

## 优先修正项（尚未修改技能正文）

### P1：Diag 依赖缺失且只读承诺与命令冲突

[diagnose](../../plugins/diag/skills/diagnose/SKILL.md) 第 12、80–86、156 行宣称自动风控和审计；[init](../../plugins/diag/skills/init/SKILL.md) 第 25、95 行依赖 `init-diag.sh`、`services-config.sh`。当前 Diag 包没有 scripts 目录，没有这些实现，也没有文档宣称的风控链路。diagnose 第 34、61–75、133–143 行又包含远端 `tee -a` 和 `rm -f`，与“全程只读”和报告中的“未改动任何远程资源”冲突。

建议先确定真实可执行路径：配置与日志读取使用已分发实现或明确的能力检测；默认流式读取到本地。报告仅声明实际执行过的保护与审计，远端写入不能由诊断请求自动推导授权。不能只在 AGENTS.md 添加约束便宣称该缺陷已修复。

### P1：UAT 用实际表现自动修改验收预期

[uat-executor](../../plugins/uat/skills/uat-executor/SKILL.md) 第 228 行和 [run](../../plugins/uat/skills/run/SKILL.md) 第 79 行要求发现差异后直接更新 flow。提示文本、步骤等差异可能是产品回归，自动改预期会掩盖失败。

建议保存原始预期、实际结果和证据；仅在用户授权维护测试流程时修订，仍保留原始发现。执行时间元数据更新与验收标准修改应区分。

### P2：UAT 初始化把源码仓库路径当成安装路径

[init](../../plugins/uat/skills/init/SKILL.md) 的两处复制命令使用 `plugins/uat/...` 相对路径。在普通目标项目中，插件可能安装于缓存目录，目标项目并无该源码布局，因而会被误判为未安装。现有 `cp` 也没有保护已定制的目标技能和约定文件。

建议从实际技能文件位置解析资源，已有文件按差异更新或保留。用没有 `plugins/uat/` 的临时目标项目验证首次安装和再次初始化。

### P2：辅助技能的加载契约不一致

[report-generator](../../plugins/pm/skills/report-generator/SKILL.md) 声称随 8 个报告命令自动激活，但 [bindings](../../skill-bindings.json) 仅在 `pm:plan` 中声明该辅助技能，其他 7 个正文也没有明确加载引用。隐式发现可能加载它，但不能保证生成命令所承诺的一致行为。

`uat-executor` 声明仅在 run 时激活，却同时作为 init 的 additional skill；初始化复制资源不需要加载整套验收步骤。建议按实际依赖校准绑定与直接技能入口，避免一边缺少必要指导、一边额外加载无关正文。

### P2：PM 导出的无参数承诺与执行分支相反

[export](../../plugins/pm/skills/export/SKILL.md) 第 12、18、22、29 行允许省略命令、保存最近报告或只指定路径，但第 38–47 行在没有命令时直接要求补充命令并退出。

建议优先使用当前对话中明确的最近报告；确实没有可用内容或存在歧义时再询问。验证“刚生成周报后执行 `/pm:export --path=报告.md`”这一完整场景。

## 后续优化建议

- `pm:ask` 的“任何项目相关问题”边界过宽，第 55–57 行的 `collect_all()` 兜底会扩大读取范围。将描述限定为基于项目数据的查询，按问题读取必要事实。
- PM 中的 `collect_*()` 等是示意流程，并非已分发 API；可用简短自然语言表达数据选择，减少伪代码造成的工具误解。
- [历史规范说明](../codex-skill-spec.md) 和校验器错误提示混用了“本仓限制”与“Codex 支持范围”。后续更新说明时保持这一层次区别；本轮没有放宽现有校验约束。
- Release 的授权应按实际用户请求和共享路由共同判断。显式执行发布命令可以包含既定发布步骤，不能仅因流程写着“自动继续”便判定违规或加上逐步确认；如果用户只要求预览/准备，则需核对该受限范围。此项没有列为已证实缺陷。

## 本轮维护文档修改

- 根 AGENTS.md 明确作者源与全部生成文件，补充触发边界、辅助技能加载、可用依赖和安装后指令可达性。
- 将验证组织为按改动类型选择的命令与行为检查，区分静态一致性和真实场景验收。
- 模型选择细节集中引用共享委派规则；保留不创建 PR/功能分支及不加 Co-Authored-By 的偏好，并说明实际 master 与显式 main 请求的差异。
- 修正 RD 标题；细化 PM 保存授权、Diag 实际依赖与远端修改、UAT 预期保留和安装路径约定。

这些维护规则用于指导后续修订，不替代上列技能正文的修复。本轮未调整技能行为、bindings、插件版本或安装缓存。

## 验证证据

| 检查 | 结果 |
|---|---|
| skill-creator `quick_validate.py` 中的 `validate_skill` 全量调用 | 79/79 通过 |
| `./scripts/validate-skills.sh --ci` | 15 个检查阶段通过；需求目录不存在，该目录检查跳过，生命周期夹具测试通过 |
| `python3 scripts/test-command-models.py` | 8 个测试通过 |
| `python3 scripts/test-export-skills.py` | 6 个测试通过 |
| 重新生成 marketplace 后核对所有生成文件 | 与 Git 基线一致，无生成漂移 |
| 修改后 `git diff --check` | 通过 |

所有运行依赖与行为发现来自源码和分发目录核对，不声称已经在真实业务环境复现。
