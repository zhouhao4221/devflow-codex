# Codex 原生子代理行为验证

日期：2026-09-12。目标是验证 DevFlow 的任务拆分、共享目录分工、原生续接和验收证据。所有实施均在无 remote 的临时 Git 项目完成，不改用户项目，不提交或推送。

## 平台适配依据

[OpenAI Subagents 文档](https://learn.chatgpt.com/docs/agent-configuration/subagents)说明了原生委派、上下文隔离、模型配置和沙箱继承。具体 `fork_turns`、`send_message`、`followup_task`、等待通知和共享文件系统行为，依据本次会话实际暴露的 `collaboration` 工具说明；不假定所有 Codex 客户端都有相同参数。

对应改动在 [_delegate.md](../../plugins/rd/shared/_delegate.md)、[_evidence.md](../../plugins/rd/shared/_evidence.md) 和五个角色文件，调用方包括 do/dev/fix/test/review-pr 与共享验证规则。保留简短返回，内容快照只在并发、可变审查或结果复用需要时使用。

## 真实并行实施与续接

隔离项目：`/private/tmp/devflow-codex-agents-g72mlag4/parallel`。Python 3.9.6，标准库，无依赖安装。协调代理读取真实委派规则和项目授权方案，使用 `fork_turns=none`、自包含说明和默认模型配置派发两个原生代理。

| 参与者 | 文件归属 | 实际结果 |
|--------|----------|----------|
| `/root/codex_parallel_eval/ranges_impl` | src/ranges.py、tests/test_ranges.py | 区间排序、重叠与整数相邻合并、空输入、反向区间、生成器与输入不变；9 项通过 |
| `/root/codex_parallel_eval/records_impl` | src/records.py、tests/test_records.py | key=value 解析、注释、空值、首个等号、重复键与物理行号；9 项通过 |
| `/root/codex_parallel_eval` | tests/test_integration.py | 子代理运行期间独立编写 3 项 API 组合测试；整合后全量 21 项通过，退出码 0 |

协调代理通过 `followup_task` 续接已完成的 ranges 代理，完成只读集成审查，返回 DONE + N/A；没有创建替代代理或重复测试。实际改动只有方案内的 5 个文件，没有文件交叉写入，用户预存的 notes.txt 修改保留。

外层主会话复核了实现、集成测试、原始测试日志，以及当前全文件哈希与执行前后快照。快照一致、HEAD 和 main 分支未变、用户笔记未变；21 项结果可复用。`git diff --check` 通过。

证据在同级 `evidence/`：`coordinator-result.md`、两个 `*-validation.json`、`parallel-full-validation.json`、`parallel-full-tests.log`、`parent-audit.json`。临时文件可能被系统清理，本报告保存关键结论。

## 验收异常与部分结果

另一个独立代理 `/root/codex_acceptance_eval` 读取真实规则和原始验收材料，未获得预期结论。隔离项目为同根目录下的 `acceptance/`，原测试实际运行 2 项通过后，夹具修改工作区并保留 HEAD 不变。

| 场景 | 观察到的行为 |
|------|----------------|
| 旧 PASS 对应的源码已在工作区改变，HEAD 未变 | 发现内容哈希不一致，补跑必要测试，2 项均失败、退出码 1，没有沿用旧 PASS |
| 审查声称 DONE，但 covered 漏掉请求中的配置文件 | 识别遗漏和缺失快照，重新核对当前实现并补查配置，没有认定原审查完整 |
| 已有用户修改与本轮范围外变更混在同一 git diff | 通过派发基线保留 notes.txt；报告 config.json 与未跟踪 scratch.txt 来源未明，不把它们擅自归因给原代理，也未回滚 |
| 指定业务映射文件缺失 | 返回 PARTIAL + FAIL，给出已有实现与测试调用证据，不编造映射 |

这两项测试失败是刻意构造的验收输入，检出失败即为该行为场景符合预期。验收代理没有修复夹具，运行前后项目快照一致。原始材料、首次报告与日志保存在 `acceptance-evidence/`。

主会话随后只补入 `docs/mapping.md`，通过原生 `followup_task` 唤醒同一个验收代理。代理只补齐 `src.calc.double → quantity.double → 数量翻倍` 的映射依据，保留首次报告；核对测试相关输入未变后，没有重复跑测试，也没有因映射补全而掩盖之前的失败或范围问题。续接结果保存在 `continuation-result.md`。主会话独立快照核对确认：首次执行只读，后续唯一项目变化为主会话添加的映射文件。

## 仓库验证与边界

- `./scripts/validate-skills.sh --ci`：通过。
- `python3 scripts/test-export-skills.py`：6 项通过，覆盖两种导出布局和新共享引用。
- `git diff --check`：通过。

本轮验证了真实原生派发、共享目录内按功能归属实施、协调会话同时推进工作、完成代理续接、部分材料续接、当前内容验证、遗漏覆盖与改动归属处理。异常材料由测试夹具构造；没有注入真实运行中断/超时，没有覆盖所有 Codex 客户端、无子代理能力降级或大型真实 PR。未做耗时/token 的对照实验，不宣称性能提升比例。所有 DevFlow 修改留在工作区，未提交或推送。
