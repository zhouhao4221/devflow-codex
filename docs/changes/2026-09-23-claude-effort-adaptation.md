# 按任务条件细分推理强度

日期：2026-09-23。Codex 修改基线：`05d341bed26e95fcbf2d3335e81a0ebcdc4dcfc1`（v0.8.3）。

## 对照来源与适配边界

本轮对照 devflow-claude 的 `b80bb3a94e10b76b579602bd10a6b195c062ddc5`、[模型策略调整 8140d69](https://github.com/zhouhao4221/devflow-claude/commit/8140d69974c5d9a52002874cf9830015aa99ba23) 和 [v5.1.1](https://github.com/zhouhao4221/devflow-claude/releases/tag/v5.1.1)（`f3a95af316e6ab632f6b2ba109520bfc0299415a`）。两仓是平行实现，不建立 Git 上游或合并关系。

来源调整移除了 48 个命令的模型覆盖，让执行型 agent 继承会话模型，并把测试、摘要、成文设为 medium，定位、实施设为 high。已核对实际命令、agent 定义和 [共享委派规则](https://github.com/zhouhao4221/devflow-claude/blob/8140d69974c5d9a52002874cf9830015aa99ba23/plugins/rd/shared/_delegate.md)，不只依据发布摘要。

其命令覆盖失效的说明针对 Claude Code，不能据此断言 Codex 的原生子代理覆盖也失效。本仓继续保留 GPT-6 Luna / Sol 路由、用户主会话模型和 Codex 工具能力检查，不复制 Claude 的 frontmatter、Agent 工具或 Fable 规划层。根 AGENTS 已把模型细节委托给共享规则，本轮无需再复制一份默认值。

## Codex 改动

- 保留 `economy`、`standard`、`primary` 档位及命令绑定，不改变外部写入授权。
- 将原来统一归入 `low` 的工作拆开：已知输入摘取与机械回填仍可用 Luna / low；解释测试结果、归纳 diff 语义和核对多份素材采用 Luna / medium。
- 陌生调用链探索、遗漏影响排查和深入多步实施按需用 Sol / high；常规有界实现保持 Sol / medium。强度取决于工作内容，不按角色名一刀切。
- 输入缺失、日志截断和环境错误先处理其原因；不把升档当作这些问题的修复。范围覆盖、真实证据和最终验收仍由主会话核对。
- 作者源为 `shared/command-model-routing.md`、RD `_delegate.md` 和 README；五份插件 `_command-models.md` 由生成器更新。未修改技能正文、版本号、安装缓存，也未提交、推送或发布。

## 同输入行为对照

两个独立子代理收到相同任务说明和固定提交范围，分别请求 `gpt-6-luna` / `low` 与 `medium`，使用 `fork_turns=none`。输入角色为 `plugins/rd/shared/roles/diff-digest.md`，证据契约为 `plugins/rd/shared/_evidence.md`；任务只读，无实际发布或生产操作。

实际 diff 范围为 `675f355eb02d522935a78b6c222c7c32e0485e3e..05d341bed26e95fcbf2d3335e81a0ebcdc4dcfc1`。主会话以同范围的 `git diff --numstat` 和实际补丁核对输出，不用代理自述替代验收。

| 核对项 | low | medium |
|---|---|---|
| 逐文件统计 | 21 个文件，+244/-98；与 Git 一致 | 21 个文件，+244/-98；与 Git 一致 |
| 主要语义 | 正确区分版本、路由、维护规范和报告变更 | 正确区分版本、路由、维护规范和报告变更 |
| RD 维护文件 | 正确识别仅标题 Req → RD | 正确识别仅标题 Req → RD |
| 行为与维护规范边界 | 未将规范更新说成技能正文缺陷已修复 | 未将规范更新说成技能正文缺陷已修复 |
| 未执行验证 | 明示没有重跑提交中记载的检查 | 明示没有重跑提交中记载的检查 |

这是一组样本、每档一次，不证明 medium 比 low 更准确，也不支持全面升档。medium 默认值是对需要解释证据、漏报影响验收的任务采取的保守选择；机械任务保留 low。未采集实际计费、内部推理 token 或有效强度遥测，不声称性能、成本收益或服务端配置已得到独立验证。

## 修改后规则推演

另一个不继承对话历史的独立执行者（请求 Sol / medium）读取修改后的路由和委派规则，收到以下原始场景，没有给预期答案。主会话复核其处理方案，8 项均符合本次选择与授权边界：

| 输入场景 | 实际返回的处理方式 |
|---|---|
| 仅查询当前 Git 分支 | 主会话单次工具查询，不委派或切分支 |
| 25 文件固定 diff 的语义摘要，可并行 | Luna / medium；保留逐文件覆盖与主会话复核 |
| 汇总含通过、跳过和启动错误的测试日志 | Luna / medium；保留错误和未执行部分，不擅自重跑 |
| 陌生项目支付回调调用链探索 | Sol / high；只读，说明动态调用等搜索边界 |
| 测试程序不存在，exit 127，无用例执行 | 环境 ERROR，不升级模型、不声称测试通过 |
| 仅发布预览，兼容性选择和 SQL 回滚未定 | 主会话保留待决项，不猜测或实际发布 |
| 25 文件摘要，但环境没有子代理或覆盖能力 | 主会话继续，不借 App 任务或嵌套 CLI 伪造切换 |
| weekly worker 再次读到 helper 路由 | 继续当前执行，不递归派发 |

这是对新规则的只读决策推演，不是以上场景的实际端到端执行；未向生产、发布平台或用户项目写入。

## 验证

- `./scripts/validate-skills.sh --ci`：通过；需求目录不存在，该目录守卫跳过，生命周期夹具测试通过。
- `python3 scripts/test-command-models.py`：8 项通过，包含非法档位、缺失入口与生成失败不污染产物等路径。
- `python3 scripts/test-export-skills.py`：6 项通过，覆盖两种导出布局及资源链接。
- 重复运行生成器：286 个插件与 marketplace 文件字节一致；`git diff --check` 通过。

上述自动检查证明结构与生成一致性，不证明全部模型配置的运行质量。真实测试失败日志处理、高强度代码探索质量、SQL 回滚生成和真实发布未在本轮端到端执行。
