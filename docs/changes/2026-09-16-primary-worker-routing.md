# 主会话判断与 5.6 执行分工

本次调整命令模型路由的执行边界。用户常以 Astra 或 5.6 Sol 作为主模型，希望主会话负责理解、方案、跨文件取舍和最终验收，让 5.6 worker 执行已经划定边界的任务。原先 `primary` 档容易被理解为主模型完成全部实施；`economy` / `standard` 又容易把整条命令连同未定选择一起交给 worker。

路由仍使用 `skill-bindings.json` 的 `economy`、`standard`、`primary` 三档，未修改逐命令档位。主会话先从运行时明确的当前任务模型标识识别自身；缺失时参考用户在当前会话中的明确选择，仍无法确定就标为未知，不猜测或更改模型。Astra 主会话可把深入的独立实施交给 Sol，常规实施交给 Terra，机械工作交给 Luna；Sol 主会话优先把常规、机械工作交给 Terra/Luna，不为不可拆任务再派同模型代理。

委派前由主会话定范围、授权、接口和验收。worker 遇到未定选择返回主会话；主会话复核实际产物后继续。`rd:test` 和 `uat:run` 的界面操作、视觉断言及最终验收仍由主会话承担。`rd:release` 可将机械准备交给 Luna，综合成文交给 Terra，版本取舍与发布操作由主会话处理。单次工具调用或无法独立验收的任务直接在当前会话完成。

验收：重新生成各插件的 `_command-models.md`，运行 `scripts/test-command-models.py`、`scripts/validate-skills.sh --ci` 与 `scripts/test-export-skills.py`；检查打包策略和 `skill-bindings.json` 的档位一致。运行时是否实际切换 worker 以对应工具返回的模型和执行证据为准，文档校验不代替真实委派验证。
