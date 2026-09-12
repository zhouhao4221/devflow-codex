# 项目架构与测试规范读取

在 dev/do/fix 生成方案前，优先读取项目 `docs/prompt/architecture.md` 获取分层、目录与契约；不存在时兼容读取 `AGENTS.md` 的架构章节。两者均缺失时从实际代码确定可验证事实，说明缺失，并可提示 `/req:init --reinit`。不为通过检查重复询问已经明确的项目约定。

测试相关流程优先读取 `docs/prompt/testing.md` 的命令、目录、环境配置；缺失时依次回退 `architecture.md` 的测试规范和 `AGENTS.md`。创建测试时另按需读取 `docs/prompt/test-generation.md`。仍缺少命令时检查实际项目脚本，不编造框架和验证结果。

`AGENTS.md` 保存行为约束与架构文档指针，具体架构放在 `docs/prompt/architecture.md`，不要复制整段架构到多个文件。初始化模板位于 `templates/agent-snippets/`；更新只补缺失文件，保留用户内容。
