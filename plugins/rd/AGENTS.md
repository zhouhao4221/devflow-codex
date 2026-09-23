# RD 维护约定

Skill 是工作流正文的唯一作者格式，`commands/` 由生成器生成。公共规则放在 `shared/`，在对应步骤直接链接并按需读取；不要把整组参考重新内联到每个 skill。

项目架构优先读 `docs/prompt/architecture.md`；测试命令优先读 `docs/prompt/testing.md`，缺失时兼容 AGENTS.md。初始化仅在 AGENTS.md 留指针，保留用户已有文档。

需求路径按 `.devflow/settings.json` 与 `.devflow/settings.local.json` 合并配置解析。readonly 直读 `requirementSource.path` 主仓自身的 `requirementsDir`，不可回写，也不读全局缓存。

子任务角色在 `shared/roles/`，不是已安装的 agent 类型。遵循 `_delegate.md` 的 Codex 运行时适配、模型路由、按需传递上下文、共享目录文件归属和原生代理续接规则；不将 App 独立任务或嵌套 CLI 当作子代理替代。返回与验收遵循 `_evidence.md`，保持简短且可核实。模板成文不能擅加事实或标题层级。

修改 `dev/new-quick/do/fix/test-new` 时同时检查 `_verify.md` 的行为一致性；`dev` 统一实施流程，`dev-guide` 只提供按需专项参考。修改 PR 流程时核对实际 base/head、完整审查覆盖和评论授权。用户已经明确的分支、提交和确认偏好优先。
