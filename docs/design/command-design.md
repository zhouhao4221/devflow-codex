# DevFlow Codex 命令设计方案

日期：2026-09-14。用于新增、修改及评审 DevFlow 命令时选择流程、执行模型和规则归属。根 [AGENTS.md](../../AGENTS.md) 保留长期设计原则，本文件保存对照依据与具体方法。

参考 devflow-claude 远端 main 的 [94b1bc7 / v2.42.1](https://github.com/zhouhao4221/devflow-claude/commit/94b1bc7e74779342f6610da12287190fd84dd257)，与 Codex `31813b2` 对照。两者是同一维护者的并行实现。此次核对根规范、五个插件的目录规范，以及需求粒度、开发、验证、提交、发布和代表性查询/报告规则；不是对全部命令行为的完整审计。

## 对照结论

| 设计主题 | Claude 的做法与依据 | Codex 的处理 |
|---|---|---|
| 维护与使用分开 | [项目本质与核心原则](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/CLAUDE.md#L3-L16)明确维护插件不等于调用插件 | 补进根 AGENTS；讨论 release 设计不能触发真实发布 |
| 单一作者源 | [命令与技能结构](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/CLAUDE.md#L30-L42)以 command 为作者源，helper 另存 | 保留 Codex 的 SKILL 作者源、生成 command 包装，不照搬删除同名 skill 的菜单处理 |
| 文档承载流程 | [核心原则](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/CLAUDE.md#L11-L16)将流程判断放在指令文档，脚本承担确定性处理 | 补进根 AGENTS；生成器可以校验档位和生成命令表，不替代模型判断用户意图 |
| 按需加载 | [主流程与 rationale 拆分](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/docs/design/token-optimization.md#L100-L111)缩短常见路径 | 保留必要输入、操作顺序、关键分支与结果；背景解释和详细边界在需要时读取，不用绝对文件大小阈值代替判断 |
| 命令与子任务两层分级 | [模型分级与委派](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/CLAUDE.md#L55-L81)区分规则化操作、成文、开放推理，以及命令内部执行单元 | Codex 已有 executionTier 与子任务规则；继续按所需推理分档，不因包含写操作就把 release 升到最强模型 |
| 可交付的功能粒度 | [需求粒度](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/req/shared/_granularity.md#L7-L21)围绕用户可感知的完整功能拆分 | 已在共享粒度规则中保留；命令设计也以独立结果为单位，不按文件或技术层机械新增命令 |
| 验收前置 | [执行后验证](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/req/shared/_verify.md#L7-L32)把验收与行为变化写进方案 | 保留 Codex 的相关检查、实际证据和输入一致性复用；有进展可继续修复，不机械移植“两轮即停止”或“每次补测试都询问” |
| 项目规则按任务读取 | [Req 目录规范](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/req/CLAUDE.md)将架构、测试、发布规则拆进 docs/prompt | Codex 已有对应约定；可选知识缺失时继续，必需输入缺失时明确指出，不内置下游项目架构 |
| 配置与权限要查实际命令 | [commit 的保护分支与配置读取](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/req/commands/commit.md#L18-L47)仍包含强制分支处理及旧配置路径 | 学习约束目的，不把具体实现当成通用规则；Codex 保留 `.devflow` 配置和用户已授权的分支/提交偏好 |

五个插件并不需要再复制一套根规则：API 的[实时接口数据与生成前影响检查](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/api/CLAUDE.md)、PM 的[只读数据消费](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/pm/CLAUDE.md)、Diag 的[生产访问边界](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/diag/CLAUDE.md)、UAT 的[实际执行与结果状态](https://github.com/zhouhao4221/devflow-claude/blob/94b1bc7/plugins/uat/CLAUDE.md)，均已有对应的 Codex 插件级 AGENTS。继续在所属插件维护；未实际分发的 hooks 不能被描述为运行时保障。

## 设计一个命令时先明确什么

设计记录按变化规模展开。小修正可用几句话说明；新增流程或跨命令行为变更才需要完整方案，不自动增加用户确认轮次。

| 要素 | 需要回答的问题 |
|---|---|
| 用户结果与入口 | 用户最终得到什么？何时触发？相邻命令是否已经负责？直接 skill、斜杠命令和自然语言入口是否一致？ |
| 输入与事实源 | 参数、默认值、互斥项是什么？配置和项目数据从哪里读取？哪些缺失可以降级，哪些会阻塞下一步？ |
| 变化与授权 | 会修改哪些文件、状态或外部资源？哪些已有授权可以沿用？只读角色具体限制什么？ |
| 执行与模型 | 哪些步骤是查表或机械操作，哪些需要综合推理？命令使用哪档模型？是否有值得单独委派的执行单元？ |
| 失败与续接 | 出错后已完成什么、尚未完成什么？能否复用产物或续接原执行者？如何避免重复提交或发布？ |
| 验收与输出 | 用哪个命令或可观察行为判定完成？如何区分失败、环境错误、未执行和部分完成？ |

流程应先完成已有授权范围内的准备，拿到可检查产物，再处理尚未授权的外部动作。用户已明确的分支、提交、发布或不创建 PR 偏好持续有效；不能从“自动”“快速”推导额外操作授权，也不能反复询问已确认事项。

## 各类命令如何应用

下面说明设计依据，不维护第二份逐命令模型清单；实际档位以 [skill-bindings.json](../../skill-bindings.json) 为准，运行方式见[命令模型路由](../../shared/command-model-routing.md)。

| 类型与例子 | 推荐设计 |
|---|---|
| 查询：status、show、modules、api:search | 经济档；只读必要范围，直接返回事实。一次工具调用就能完成时不增加派发开销 |
| 规则化状态/配置：review、done、config | 经济档；校验当前状态、目标状态和允许写入的资源。模型价格与写入授权分开判断 |
| Git 与发布：commit、pr、release | 经济档承担取数和准备。版本、分支、检查结果与 draft/tag 语义必须明确；主会话核对产物并按授权执行外部步骤 |
| 报告：weekly、monthly、stats、risk | 标准档；先汇总真实数据，再形成结论。PM 不修改需求状态，缺少需求数据时可按 Git 范围报告 |
| API：gen、map | 标准档；读取当前配置和接口定义，比较字段与调用方影响，输出位置取项目配置，保留已有代码 |
| 需求与开发：new、edit、dev、do、fix | 主会话保留需求和设计判断；方案明确后按独立行为单元分派执行，不把整个需求重复交给多个代理 |
| 诊断与验收：diag:diagnose、uat:run、req:test | 保留需要上下文的判断，按需委派有界执行；明确服务/时间/场景范围，只把实际执行结果记为通过 |

release 是“写操作不等于高推理成本”的例子；pm:ask 与 pm:plan 是“输出文档不一定只是模板成文”的例子。遇到不明确的业务规则或复杂契约，调整实际任务的执行方式，不能为了低价隐去不确定性。

## 规则放在哪里

| 内容 | 唯一维护位置 |
|---|---|
| 所有命令通用的设计原则 | 根 AGENTS.md |
| 插件业务边界、项目输入和特殊约定 | `plugins/<plugin>/AGENTS.md` |
| 具体命令的触发、参数、流程和输出 | 对应 SKILL.md；生成的 command 保持薄包装 |
| 多命令共同依赖的专题规则 | 插件 shared Markdown，在实际使用步骤链接 |
| 跨插件执行模型策略 | `shared/command-model-routing.md`，生成器打包到各插件 |
| 命令/技能映射、参数提示、执行档位 | `skill-bindings.json` |
| 生成、导出与机械一致性检查 | `scripts/`，不在脚本中复制自然语言业务判断 |
| 设计原因、平台差异与对照证据 | 本文或具体变更文档，不塞进每次都加载的入口 |

详细命令参数与生成包装的提示也要一致。例如本次对照发现 Codex release 的 `argument-hint` 仍使用通用 `[arguments]`，而正文已有完整参数；后续修改该入口时应在 bindings 中同步提示。这是识别出的后续改进点，本次没有改动该命令参数或流程。

## 采纳与验收方式

本次已将维护/使用边界、命令设计要素、按需加载、模型选择依据、授权和验收原则写入根 AGENTS，并保留现有插件级规则。模型路由、角色隔离、验证与续接是此前已实现的能力；本次不把学习方案当作批量重写全部命令的授权，也不提高插件版本号。

以后适配 Claude 的一项变化时，记录“来源提交与文件 → 原问题 → Codex 决策 → 验证依据”。涉及已有参数或行为时检查实际调用方；不要只依据全局规范或旧 README 推断所有命令都已对齐。业务结果与权限原则可以复用，Claude 的模型字段、工具名称、hook/缓存目录和命令/skill 布局按 Codex 能力重新设计。

修改命令后执行仓库一致性检查；改变路由或生成器时跑命令模型回归，改变共享资源或导出适配时跑导出回归。改变决策、失败路径或副作用时，再用对应的真实场景或隔离夹具核实行为。静态通过只能证明结构和生成物一致，不能证明所有命令实际执行正确。
