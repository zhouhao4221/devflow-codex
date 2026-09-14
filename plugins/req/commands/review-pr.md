---
description: "PR 审查与合并 - AI 代码审查、提交评论、合并 PR"
argument-hint: "[review|merge|fetch-comments] [REQ-XXX] [--level=low|medium|high] [--auto]"
---

Before executing, read [command model routing](../shared/_command-models.md) for `req:review-pr` (execution tier: `primary`). An already delegated executor must not route again.

Use the `req:review-pr` skill and follow its `SKILL.md` instructions.
Related helper skills: `req:natural-language-dispatcher`.


User arguments:

```text
$ARGUMENTS
```

If no arguments are supplied, follow the skill's no-argument behavior.
