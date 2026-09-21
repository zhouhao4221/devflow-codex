# 2026-09-21 Claude 平行实现对照

本轮对照 `zhouhao4221/devflow-claude` 的 `main`，前次基准为 [`525bf60bfbfcca07218ba0ca9e6f51f13c7d534b`](https://github.com/zhouhao4221/devflow-claude/commit/525bf60bfbfcca07218ba0ca9e6f51f13c7d534b)，本轮固定到 [`0c5b80242fe19aa6be4c2e0478b461a83660ea1b`](https://github.com/zhouhao4221/devflow-claude/commit/0c5b80242fe19aa6be4c2e0478b461a83660ea1b)。[比较区间](https://github.com/zhouhao4221/devflow-claude/compare/525bf60bfbfcca07218ba0ca9e6f51f13c7d534b...0c5b80242fe19aa6be4c2e0478b461a83660ea1b)。两仓仍是同一维护者的平行实现，此 SHA 只标记对照终点。

| 参考变更 | 解决的问题 | Codex 等价实现 | 验证 |
|----------|------------|------------------|------|
| [`78b4d3e`](https://github.com/zhouhao4221/devflow-claude/commit/78b4d3e26f34203e1a62abca03d3a09686811111) | 纯文档、样式、lock 或生成物变更会被文件数/行数阈值误判为重审 | `rd:review` 先分类逻辑、展示与非代码文件；非逻辑改动至少 80% 时只完整读逻辑 diff，对其余改动抽读 | 生成、布局、命令模型路由与导出测试 |
| [`a14b3d7`](https://github.com/zhouhao4221/devflow-claude/commit/a14b3d761a6726d0f3508520ba26c6f94f5b106d)、[`c0c38b4`](https://github.com/zhouhao4221/devflow-claude/commit/c0c38b480fcf2158d09cda7f87539fadf6e451d1) | 需求评审、代码审查和 PR CLI 操作挤在同一入口，语义与模型档位混杂 | 新增 `rd:req-review` 处理 REQ 提审、AI 预审和 pass/reject；`rd:review` 专注代码审查与按评论修改；`rd:pr comments` 只读，保留 Codex 的真实 base/head SHA、临时 worktree 和 `codex exec review --ephemeral` 适配 | 旧 pass/reject 只提示迁移；readonly 不写需求；评论查看不读源码不改文件 |
| [`fb4fbb1`](https://github.com/zhouhao4221/devflow-claude/commit/fb4fbb106041c1d2f1a92e3decec6246dd467bc9)–[`0c5b802`](https://github.com/zhouhao4221/devflow-claude/commit/0c5b80242fe19aa6be4c2e0478b461a83660ea1b) | Claude 命令级 Fable 覆盖会被确认闸门和额度锁死，后改为只读思考代理与当前模型降级 | 不引入 Claude/Fable frontmatter 或 agent。Codex 保留 `executionTier`：主会话负责设计、跨文件判断和验收，有界只读子任务才按 `_delegate.md` 选实际可用的 Codex worker，不可用时由主会话继续 | `check-command-models.py` 既有通用 frontmatter 禁止、`test-command-models.py`、CI 验证 |

未移植 Claude 的 `planner` / `root-cause` agent、`model: best` / Fable 字段、`/code-review` 调用形式、`.claude` 路径或版本号。这些属于 Claude 运行时约束，不是 Codex 的作者模型或授权语义。
