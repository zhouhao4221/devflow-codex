---
description: "颁布版本 - 合并 SQL、生成回滚、打 tag、创建 Release"
argument-hint: "[arguments]"
---

Before executing, read [command model routing](../shared/_command-models.md) for `req:release` (execution tier: `economy`). An already delegated executor must not route again.

Use the `req:release` skill and follow its `SKILL.md` instructions.
Related helper skills: `req:version-bumper`, `req:changelog-generator`, `req:release-rationale`.


User arguments:

```text
$ARGUMENTS
```

If no arguments are supplied, follow the skill's no-argument behavior.
