---
description: "代码审查 - AI 审查 PR 并按授权提交评论，或按人工评审评论修改代码"
argument-hint: "[comments] [PR-ID|REQ-XXX|QUICK-XXX] [--level=low|medium|high] [--auto]"
---

Before executing, read [command model routing](../shared/_command-models.md) for `rd:review` (execution tier: `primary`). An already delegated executor must not route again.

Use the `rd:review` skill and follow its `SKILL.md` instructions.

User arguments:

```text
$ARGUMENTS
```

If no arguments are supplied, follow the skill's no-argument behavior.
