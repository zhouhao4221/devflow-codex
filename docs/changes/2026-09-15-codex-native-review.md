# Codex 原生代码审查适配

日期：2026-09-15。

## 来源与问题

参考 `devflow-claude` 的 [e6fa0b4](https://github.com/zhouhao4221/devflow-claude/commit/e6fa0b49b0bbb3209d990fd7853705af5cf6f971)，其 `/req:review-pr review` 对大 PR 改用 Claude 原生 `/code-review`，解决逐文件代理难以覆盖跨文件调用且需要重复传递 diff 的问题。对照时远端 `main` 为 [94b1bc7 / v2.42.1](https://github.com/zhouhao4221/devflow-claude/commit/94b1bc7e74779342f6610da12287190fd84dd257)。两个仓库仍是平行实现，不复制 Claude 的工具名、模型档位或结果等级。

Codex 的 composer `/review` 会启动专用 reviewer，但它是用户入口，不是 skill 可稳定嵌套调用的工具；仅打开 review 面板也不会执行审查。Codex 同时提供面向脚本的 `codex exec review`，可输出审查结果并使用只读执行环境。平台依据：[Code review](https://learn.chatgpt.com/docs/code-review)、[Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)。

## Codex 实现

- `/req:review` 保持需求文档完整性检查和状态流转，不调用代码审查。
- `/req:review-pr review` 的小 PR 仍由主会话读取全量 diff；大 PR 优先使用能固定 base/head 的原生 Codex review 后端。
- 当前运行时没有直接可调用的 review 工具时，检测 `codex exec review --help`，再通过 `review-pr/scripts/run-codex-review.sh` 调用官方非交互入口。
- 适配器校验 fetch 后的 base ref 仍指向记录的 base SHA，在 head SHA 的临时 detached worktree 中执行 `codex exec review --ephemeral --base <BASE_REF> -`，不切换或改写用户工作区。
- custom review instructions 由主流程传入，包含需求、项目规则和审查深度；原生后端只返回本地 finding，不提交平台评论、不批准或合并 PR。
- 原生调用失败不修改用户 Codex 配置，也不重复重试；回退到现有 Codex 子代理按行为或模块审查，再由主会话核对跨模块契约和完整性。

## 验证

`scripts/test-codex-review-backend.py` 使用临时 Git 仓库和假的 `codex` 可执行文件验证：

- reviewer 运行在指定 head SHA，base ref 与记录 SHA 不一致时拒绝执行；
- 原工作区分支不变，临时 worktree 在成功或 reviewer 失败后都清理；
- CLI 不支持 review 时在创建 worktree 前失败，供主流程降级。

生成 marketplace 包装后运行 `./scripts/validate-skills.sh --ci`；共享资源与 skill 脚本的两种导出布局用 `python3 scripts/test-export-skills.py` 验证。
