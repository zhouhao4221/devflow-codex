#!/usr/bin/env python3
"""Generate Codex plugin manifests, commands, and skill UI metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/zhouhao4221/devflow-codex"
AUTHOR = {"name": "zhouhao4221", "url": "https://github.com/zhouhao4221"}
EXECUTION_TIERS = frozenset({"economy", "standard", "primary"})
COMMAND_MODEL_ROUTING_SOURCE = ROOT / "shared" / "command-model-routing.md"

PLUGIN_META = {
    "rd": {
        "version": "4.0.3",
        "description": "需求全流程工作流管理 - 从需求分析到测试的完整生命周期管理",
        "displayName": "DevFlow RD",
        "shortDescription": "需求分析、PRD、开发、测试和发布工作流",
        "longDescription": "DevFlow RD provides Codex-native requirement workflows for PRDs, branching, requirement docs, development, testing, review, release notes, and project status tracking.",
        "category": "Productivity",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["requirements", "prd", "workflow", "release", "project-management"],
        "defaultPrompt": [
            "初始化当前仓库的需求工作流",
            "创建一个新需求并拆分开发步骤",
            "查看当前需求状态和下一步",
        ],
        "brandColor": "#10A37F",
    },
    "api": {
        "version": "0.6.2",
        "description": "前端 API 对接工具 - Swagger 解析、字段映射、代码生成",
        "displayName": "DevFlow API",
        "shortDescription": "Swagger/OpenAPI 搜索、映射和前端代码生成",
        "longDescription": "DevFlow API helps Codex import Swagger/OpenAPI definitions, search endpoints, map request and response fields, and generate TypeScript API integration code.",
        "category": "Developer Tools",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["api", "swagger", "openapi", "typescript", "frontend"],
        "defaultPrompt": [
            "导入 Swagger 并列出接口",
            "搜索用户相关接口",
            "为接口生成 TypeScript 请求代码",
        ],
        "brandColor": "#2563EB",
    },
    "pm": {
        "version": "0.6.2",
        "description": "项目管理助手 - 从 PRD、需求文档和 Git 记录生成汇报、统计、方案",
        "displayName": "DevFlow PM",
        "shortDescription": "项目周报、月报、风险、进度和里程碑总结",
        "longDescription": "DevFlow PM turns requirement docs and Git history into project reports, standup notes, risks, progress summaries, milestones, and planning documents.",
        "category": "Productivity",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["project-management", "weekly-report", "milestone", "risk", "planning"],
        "defaultPrompt": [
            "生成本周项目周报",
            "扫描项目风险",
            "总结当前里程碑进展",
        ],
        "brandColor": "#7C3AED",
    },
    "diag": {
        "version": "0.3.2",
        "description": "生产诊断 - 只读拉日志、AI 解析堆栈、关联代码、给修复建议",
        "displayName": "DevFlow Diag",
        "shortDescription": "生产日志诊断、堆栈分析和代码关联",
        "longDescription": "DevFlow Diag guides read-only production diagnostics, log collection, stack trace analysis, local code correlation, and remediation suggestions.",
        "category": "Developer Tools",
        "capabilities": ["Interactive", "Read"],
        "keywords": ["diagnostics", "logs", "stack-trace", "production", "debugging"],
        "defaultPrompt": [
            "初始化生产诊断配置",
            "分析最近一次生产报错",
            "查看诊断审计日志",
        ],
        "brandColor": "#DC2626",
    },
    "uat": {
        "version": "1.5.2",
        "description": "用户验收测试（UAT）- AI 驱动的 UI 验收测试",
        "displayName": "DevFlow UAT",
        "shortDescription": "创建、执行和上报用户验收测试流程",
        "longDescription": "DevFlow UAT helps Codex create natural-language UAT flows, execute acceptance scenarios, report failures, and summarize test results.",
        "category": "Testing",
        "capabilities": ["Interactive", "Read", "Write"],
        "keywords": ["uat", "testing", "acceptance", "qa", "playwright"],
        "defaultPrompt": [
            "创建一个 UAT 测试流程",
            "执行当前模块的验收测试",
            "查看最近一次测试报告",
        ],
        "brandColor": "#F59E0B",
    },
}


def skill_description(plugin: str, skill: str) -> str:
    text = (ROOT / "plugins" / plugin / "skills" / skill / "SKILL.md").read_text()
    for line in text.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return f"{plugin} {skill}"


def titleize_skill(name: str) -> str:
    acronyms = {"api", "pm", "pr", "prd", "uat"}
    return " ".join(part.upper() if part in acronyms else part.title() for part in name.split("-"))


def compact_summary(description: str, max_length: int = 58) -> str:
    summary = re.split(r"[。.!?；;]", description, maxsplit=1)[0]
    summary = re.split(r"\s+-\s+", summary, maxsplit=1)[0].strip()
    if len(summary) > max_length:
        summary = summary[: max_length - 1].rstrip() + "…"
    return summary


def skill_openai_yaml(plugin: str, skill: str, meta: dict) -> str:
    description = skill_description(plugin, skill)
    display_name = f"{meta['displayName']}: {titleize_skill(skill)}"
    short_description = compact_summary(description)
    default_prompt = f"使用 ${skill} 处理：{short_description}。"
    return (
        "interface:\n"
        f"  display_name: {json.dumps(display_name, ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(short_description, ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(default_prompt, ensure_ascii=False)}\n"
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def validate_command_routes(bindings: dict) -> None:
    """Reject missing or unsupported execution tiers before generation writes files."""
    if not isinstance(bindings, dict):
        raise ValueError("Invalid command model routing: bindings must be an object")
    errors = []
    plugins = bindings.get("plugins")
    if not isinstance(plugins, dict):
        raise ValueError("Invalid command model routing: plugins must be an object")
    for plugin, plugin_data in plugins.items():
        if not isinstance(plugin_data, dict):
            errors.append(f"{plugin} command bindings must be an object")
            continue
        commands = plugin_data.get("commands")
        if not isinstance(commands, dict):
            errors.append(f"{plugin} commands must be an object")
            continue
        for command, command_data in commands.items():
            if not isinstance(command_data, dict):
                errors.append(f"{plugin}:{command} command binding must be an object")
                continue
            tier = command_data.get("executionTier")
            if not isinstance(tier, str) or tier not in EXECUTION_TIERS:
                errors.append(
                    f"{plugin}:{command} has invalid executionTier {tier!r}; "
                    f"expected one of {sorted(EXECUTION_TIERS)}"
                )
    if errors:
        raise ValueError("Invalid command model routing:\n" + "\n".join(errors))


def validate_generation_bindings(bindings: dict) -> None:
    """Validate all data main() needs before it starts writing generated files."""
    validate_command_routes(bindings)
    plugins = bindings["plugins"]
    all_skills = bindings.get("allSkills")
    errors = []
    if not isinstance(all_skills, dict):
        errors.append("allSkills must be an object")
    for plugin in PLUGIN_META:
        if plugin not in plugins:
            errors.append(f"missing plugin bindings for {plugin}")
        if not isinstance(all_skills, dict) or not isinstance(all_skills.get(plugin), list):
            errors.append(f"missing allSkills list for {plugin}")
    unexpected = sorted(set(plugins) - set(PLUGIN_META))
    if unexpected:
        errors.append(f"unsupported plugin bindings: {', '.join(unexpected)}")
    if errors:
        raise ValueError("Invalid generation bindings:\n" + "\n".join(errors))


def command_models_body(plugin: str, commands: dict, policy_text: str) -> str:
    """Render the self-contained command-routing document installed with a plugin."""
    rows = [
        f"| `{plugin}:{command}` | `{data['executionTier']}` |"
        for command, data in commands.items()
    ]
    return (
        "<!-- Generated from shared/command-model-routing.md. Do not edit directly. -->\n\n"
        + policy_text.rstrip()
        + "\n\n## Command routing\n\n"
        + "| Command | Execution tier |\n"
        + "| --- | --- |\n"
        + "\n".join(rows)
        + "\n"
    )


def command_body(
    plugin: str,
    command: str,
    primary: str,
    extras: list[str],
    argument_hint: str = "[arguments]",
    *,
    execution_tier: str,
) -> str:
    description = skill_description(plugin, primary)
    skill_ref = f"{plugin}:{primary}"
    extra_line = ""
    if extras:
        extra_refs = ", ".join(f"`{plugin}:{name}`" for name in extras)
        extra_line = f"\nRelated helper skills: {extra_refs}.\n"

    return f"""---
description: {json.dumps(description, ensure_ascii=False)}
argument-hint: {json.dumps(argument_hint, ensure_ascii=False)}
---

Before executing, read [command model routing](../shared/_command-models.md) for `{plugin}:{command}` (execution tier: `{execution_tier}`). An already delegated executor must not route again.

Use the `{skill_ref}` skill and follow its `SKILL.md` instructions.{extra_line}

User arguments:

```text
$ARGUMENTS
```

If no arguments are supplied, follow the skill's no-argument behavior.
"""


def main() -> None:
    bindings = json.loads((ROOT / "skill-bindings.json").read_text())
    validate_generation_bindings(bindings)
    command_model_policy = COMMAND_MODEL_ROUTING_SOURCE.read_text()

    marketplace = {
        "name": "devflow",
        "interface": {"displayName": "DevFlow"},
        "plugins": [],
    }

    for plugin, meta in PLUGIN_META.items():
        plugin_root = ROOT / "plugins" / plugin
        manifest = {
            "name": plugin,
            "version": meta["version"],
            "description": meta["description"],
            "author": AUTHOR,
            "homepage": REPOSITORY,
            "repository": REPOSITORY,
            "license": "Apache-2.0",
            "keywords": meta["keywords"],
            "skills": "./skills/",
            "interface": {
                "displayName": meta["displayName"],
                "shortDescription": meta["shortDescription"],
                "longDescription": meta["longDescription"],
                "developerName": "zhouhao4221",
                "category": meta["category"],
                "capabilities": meta["capabilities"],
                "websiteURL": REPOSITORY,
                "defaultPrompt": meta["defaultPrompt"],
                "brandColor": meta["brandColor"],
                "screenshots": [],
            },
        }
        write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)

        commands_dir = plugin_root / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        for old in commands_dir.glob("*.md"):
            old.unlink()

        for command, data in bindings["plugins"][plugin]["commands"].items():
            primary = data["primarySkill"]
            extras = data.get("additionalSkills", [])
            (commands_dir / f"{command}.md").write_text(
                command_body(
                    plugin,
                    command,
                    primary,
                    extras,
                    data.get("argumentHint", "[arguments]"),
                    execution_tier=data["executionTier"],
                )
            )

        shared_dir = plugin_root / "shared"
        shared_dir.mkdir(parents=True, exist_ok=True)
        (shared_dir / "_command-models.md").write_text(
            command_models_body(
                plugin,
                bindings["plugins"][plugin]["commands"],
                command_model_policy,
            )
        )

        for skill in bindings["allSkills"][plugin]:
            skill_dir = plugin_root / "skills" / skill
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            (agents_dir / "openai.yaml").write_text(skill_openai_yaml(plugin, skill, meta))

        marketplace["plugins"].append(
            {
                "name": plugin,
                "source": {"source": "local", "path": f"./plugins/{plugin}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": meta["category"],
            }
        )

    write_json(ROOT / ".agents" / "plugins" / "marketplace.json", marketplace)


if __name__ == "__main__":
    main()
