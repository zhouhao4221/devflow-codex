# 能力感知的交互走查

日期：2026-09-15

## 问题

`req:test` 原本把自动化未覆盖项固定交给用户手动验证；`uat-executor` 虽会检查浏览器工具，却依赖旧的抽象工具名，并把“Codex 桌面端”与“实际具备 UI 控制能力”混在一起。客户端类型不能证明 Chrome、内置浏览器或 Computer Use 已安装、获授权且可由当前模型调用。

## Codex 实现

- `req:test` 保持 `primary` 档，将交互走查和最终验收留在主会话；机械测试命令及大段日志仍可由经济档 `test-runner` 执行。
- 交互阶段检查当前会话实际暴露的工具及可用应用、浏览器和标签页表面，不读取环境变量猜测客户端类型。
- 需要现有登录态时优先 Chrome；localhost、公开页面或隔离会话优先内置浏览器；原生桌面与跨应用流程使用 Computer Use。用户明确指定的表面始终优先。
- 已有 UAT flow 时复用其场景和证据格式；否则从需求测试点生成本次临时走查步骤。能力不可用时输出手动清单，未执行项不计为通过。
- 自动操作限于已确认的测试环境和测试数据。生产环境或难以恢复的外部动作仍需明确授权，同一应用或测试账号串行操作。

平台依据：[Use your computer with ChatGPT](https://learn.chatgpt.com/use-cases/use-your-computer-with-codex)。官方说明 Computer Use 用于桌面应用与本地文件，Chrome 适合使用现有浏览器登录态；localhost 或公开页面也可使用独立的内置浏览器。

## 验收

- 生成后的 `/req:test` command 暴露 `--skip-walkthrough` 参数提示。
- `req:test` 与 `uat:run` 的执行档位保持 `primary`，UI 走查不降档；现有测试运行子任务仍遵循共享模型分级。
- UAT 在缺少脚本求值能力时如实记录 Console Error 未采集，不误报为“无错误”。
- 运行 marketplace 生成、skills 一致性检查、命令模型回归与导出布局测试。
