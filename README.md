# DevFlow Skills

DevFlow 插件技能集合 —— 独立技能包，包含 [DevFlow](https://github.com/zhouhao4221/devflow-claude) 所有插件的 AI 执行指令（SKILL.md）。

## 概述

本仓库从 [devflow-claude](https://github.com/zhouhao4221/devflow-claude) 主仓库中提取所有 SKILL.md 文件，作为独立的技能包提供给 CI 校验和版本管理。每个 SKILL.md 文件定义了 Claude Code 在执行对应命令时的行为指引。

## 仓库结构

```
plugins/
├── req/skills/     # 需求管理技能（46 个）
├── api/skills/     # API 对接技能（8 个）
├── pm/skills/      # 项目管理技能（14 个）
├── diag/skills/    # 生产诊断技能（5 个）
└── uat/skills/     # 验收测试技能（7 个）
skill-bindings.json  # 命令-技能映射关系
```

## 技能分类

### req — 需求全流程管理
覆盖从需求分析、评审、开发、测试到归档的完整生命周期，包括智能开发（`dev`）、规范提交（`commit`）、版本发布（`release`）、代码审查（`review-pr`）、自然语言调度（`natural-language-dispatcher`）等 46 个技能。

**自动触发技能**：
| 技能 | 触发场景 |
|------|---------|
| `requirement-analyzer` | 创建/编辑需求时自动分析 |
| `dev-guide` | 开发阶段按分层架构引导 |
| `quick-fix-guide` | 快速修复时引导 |
| `test-guide` | 测试阶段引导回归和新建 |
| `prd-analyzer` | PRD 编辑时辅助完善 |
| `code-impact-analyzer` | 需求变更时分析代码影响 |
| `changelog-generator` | 自动生成版本变更说明 |
| `version-bumper` | 发版时自动推导版本号 |

### api — API 对接
支持 Swagger/OpenAPI 解析、字段映射、代码生成、接口搜索等 8 个技能。

### pm — 项目管理助手
从 PRD、需求文档和 Git 记录中提取数据，生成汇报、统计、方案等 14 个技能。

### diag — 生产诊断
只读诊断 + 修复建议，包含审计、堆栈分析等 5 个技能，含安全风控 Hook。

### uat — 用户验收测试
UI 验收测试工作流，含测试执行器、报告生成等 7 个技能。

## skill-bindings.json

`skill-bindings.json` 声明了命令与技能之间的映射关系：

```json
{
  "plugins": {
    "req": {
      "commands": {
        "dev": {
          "primarySkill": "dev",
          "additionalSkills": ["dev-guide"]
        }
      }
    }
  },
  "allSkills": {
    "req": ["dev", "dev-guide", ...]
  }
}
```

- `commands.<name>.primarySkill`: 命令直接对应的技能
- `commands.<name>.additionalSkills`: 命令执行过程中自动触发的辅助技能
- `allSkills`: 各插件拥有的全部技能清单

CI 会验证：
1. `allSkills` 中声明的技能都有对应的 `SKILL.md` 文件
2. 实际存在的 `SKILL.md` 文件都在 `allSkills` 中有声明
3. 命令中引用的技能名都在 `allSkills` 中存在

## CI 校验

每次 push 或 PR 时自动运行 `.github/workflows/check-skill-bindings.yml`，确保技能名称一致性。

## 许可证

[Apache License 2.0](LICENSE)
