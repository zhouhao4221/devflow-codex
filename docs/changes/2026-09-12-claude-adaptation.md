# 2026 年 9 月 Claude 平行实现适配

范围：2026-08-12 至 2026-09-12。参考 `zhouhao4221/devflow-claude` 的 21 次提交，最终状态固定为 [94b1bc7 / v2.42.1](https://github.com/zhouhao4221/devflow-claude/commit/94b1bc7e74779342f6610da12287190fd84dd257)。[区间差异](https://github.com/zhouhao4221/devflow-claude/compare/6151031025b43cd4fc4acbf605028238915b3550...94b1bc7e74779342f6610da12287190fd84dd257)。两个仓库是同一维护者的平行实现，本次按 Codex 行为适配，不建立上下游关系。

| 月内变化 | Codex 处理 |
|----------|------------|
| 8/24 子代理分工、共享内容去互引 | 将 20 个 req skill 的重复附录抽到 `shared/`，角色说明按需加载，默认继承模型 |
| 8/24 Claude 菜单去重、manifest 修复 | 保留 Codex skill 正文和生成 command 包装；添加引用检查，不删除命令对应的 Codex skills，不引入 Claude manifest 字段 |
| 8/25 `.devflow` 与 readonly 路径修复 | 使用共享配置解析规则；测试 Specs 读取主仓配置的需求目录；移除不存在的迁移脚本引用，不安装默认 hooks |
| 8/26 实施、成文、diff 摘要代理及质量修正 | 增加五类角色约束，限定实施范围、真实统计、部分结果、批量摘要和文档事实/结构一致性；不保留已撤销的 file-reviewer |
| 9/11 指导文件精简 | 插件专属规则放入目录级 `AGENTS.md`，不新建 CLAUDE.md |
| 9/11 固定验证流程与架构读取 | do/fix 接入验收和验证结果；test-new 增加 `--files` UT 模式和 dry-run 边界；架构/测试优先读取 docs/prompt，保留旧项目回退 |
| 9/11 大 PR 审查与创建后提示 | 按实际 PR base/head SHA 固定范围，用 numstat 判规模；low/medium/high 表示审查深度；有合适的能力时委派完整审查，否则按模块内联审查；创建后提示规模及审查下一步 |

## Codex 行为差异

角色说明是可传给当前子代理工具的任务约束，不是自动安装的 custom agent。不可委派时由主会话完成同一工作，不修改模型配置。Claude 的 `/code-review`、Agent/Skill 工具、固定模型和 hook 配置不照搬。

后续按 Codex 原生多代理运行方式进一步调整：按需继承上下文、共享目录内按行为单元分配实现与测试、区分运行中消息和空闲代理续接、消费完成通知并避免重复派发。任务状态和测试结论分开，复用验证时核对相关工作区内容。详见 [子任务委派](../../plugins/req/shared/_delegate.md) 和 [证据契约](../../plugins/req/shared/_evidence.md)。

验证保留有序检查、必要覆盖、真实结果和禁止迎合测试的要求。连续两轮没有进展时停止盲目重试；有新证据并可修复时继续，不强制在第二轮截断。小修复的必要测试在授权范围内补充，新增框架或扩大范围再询问。

不创建 `.req-auto` 标记绕过权限。评论必须有明确授权；既有用户授权和项目分支约定优先。大 PR 摘要不能代替全量审查，未审范围和未知二进制行数必须明确报告。

## 分发与验证

保留 79 个 skills 和 64 个 commands。Req 升到 3.25.0；其余插件因目录级指导文件更新各升一个 patch。`skill-bindings.json` 保存新增参数提示，生成器同步 command 元数据。

两个导出脚本都携带共享规则和模板，扁平导出重写引用及 skill 名称。分层导出默认到 `dist/claude`，不覆盖另一个维护中的仓库。非本导出器创建的非空目录拒绝覆盖。

验证命令：

```bash
python3 scripts/generate-codex-marketplace.py
./scripts/validate-skills.sh --ci
python3 scripts/test-export-skills.py
```

结构检查覆盖本地引用、命令目录与内联附录。导出回归覆盖资源传递、循环引用、路径含空格、元数据、可执行文件、失效引用、越界资源、已有目录保护和真实仓库两种布局。工作流语义还需人工核对验证分支、readonly、PR 范围和子代理降级路径；静态校验不代表已在目标项目执行过真实 PR 审查。
