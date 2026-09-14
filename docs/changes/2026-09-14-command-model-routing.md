# 命令级执行模型分配

在子任务模型分级基础上，为全部命令增加 `executionTier`：`economy` 优先 Luna，`standard` 默认 Terra，`primary` 保留主会话。`req:release` 属于经济档，发布准备中的规则化步骤交给经济型执行者；主会话核对产物、处理交互及已授权的提交和平台发布操作。

分级保存在 `skill-bindings.json`。统一[路由策略](../../shared/command-model-routing.md)由生成器随各插件打包，并附本插件命令表；生成命令包装和直接 skill 入口均接入，单独安装插件和两种兼容导出都可读取。helper skill 继承执行者模型，执行子代理不递归路由。

这不是 Codex skill frontmatter 的原生模型切换功能。运行时须支持原生子代理模型覆盖才会请求相应模型；否则说明原因并回退。保留用户模型偏好、权限、检查失败停止和已有授权，不为分级引入新的确认步骤。

插件版本：Req 3.27.0、API 0.5.0、PM 0.6.0、Diag 0.3.0、UAT 1.4.0。此次只更新插件行为和版本，不执行仓库的 Release 流程。

验证：一致性检查、8 项命令路由回归、6 项导出回归及 64 个命令 skill 格式检查通过；逐一比较确认原 skill 流程正文仅新增路由入口。

独立的隔离验证从生成的 release 命令入口处理“v1.0.1 --no-release，只准备产物”。协调者实际以 `gpt-5.6-luna`、`low`、`fork_turns=none` 派发执行者；首次遗漏 changelog，验收发现后用 `followup_task` 续接原执行者补齐。最终 VERSION 为 1.0.1，changelog 对应本地 tag 之后的一条修复提交，发布前检查和 diff 检查通过；HEAD、分支和 tag 未变，未执行提交、推送或平台发布。此测试覆盖经济档派发、实际产物验收和遗漏后的续接，未测量费用，也不代表已验证所有命令和平台发布路径。
