#!/usr/bin/env python3
"""Validate generated command-model routing artifacts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


FORBIDDEN_MODEL_FIELDS = re.compile(
    r"^(?:model|model_reasoning_effort|model_provider)\s*:", re.MULTILINE
)


def load_generator(root: Path):
    path = root / "scripts" / "generate-codex-marketplace.py"
    spec = importlib.util.spec_from_file_location("generate_codex_marketplace", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    frontmatter_text, separator, _ = text[4:].partition("\n---\n")
    return frontmatter_text if separator else ""


def check(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    try:
        generator = load_generator(root)
        bindings = json.loads((root / "skill-bindings.json").read_text())
        generator.validate_command_routes(bindings)
        policy = (root / "shared" / "command-model-routing.md").read_text()
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError, SyntaxError) as exc:
        return [f"command model routing setup: {exc}"]

    for plugin, plugin_data in bindings.get("plugins", {}).items():
        if not isinstance(plugin_data, dict):
            errors.append(f"skill-bindings.json: plugin {plugin!r} must be an object")
            continue
        commands = plugin_data.get("commands", {})
        if not isinstance(commands, dict):
            errors.append(f"skill-bindings.json: plugin {plugin!r} commands must be an object")
            continue
        for command, data in commands.items():
            if not isinstance(data, dict):
                errors.append(f"skill-bindings.json: {plugin}:{command} binding must be an object")
                continue
            primary = data.get("primarySkill", "")
            tier = data["executionTier"]
            skill_file = root / "plugins" / plugin / "skills" / primary / "SKILL.md"
            if not skill_file.exists():
                errors.append(f"{skill_file}: missing primary SKILL.md for {plugin}:{command}")
            else:
                skill_text = skill_file.read_text()
                if "../../shared/_command-models.md" not in skill_text:
                    errors.append(f"{skill_file}: missing command model routing link for {plugin}:{command}")
                if f"{plugin}:{command}" not in skill_text:
                    errors.append(f"{skill_file}: missing command model routing reference {plugin}:{command}")

            command_file = root / "plugins" / plugin / "commands" / f"{command}.md"
            if not command_file.exists():
                errors.append(f"{command_file}: missing generated command")
            else:
                try:
                    expected = generator.command_body(
                        plugin,
                        command,
                        primary,
                        data.get("additionalSkills", []),
                        data.get("argumentHint", "[arguments]"),
                        execution_tier=tier,
                    )
                    if command_file.read_text() != expected:
                        errors.append(f"{command_file}: differs from generated command body")
                except (OSError, TypeError, ValueError, KeyError) as exc:
                    errors.append(f"{command_file}: cannot build expected command body: {exc}")

        routing_file = root / "plugins" / plugin / "shared" / "_command-models.md"
        expected_routing = generator.command_models_body(plugin, commands, policy)
        if not routing_file.exists():
            errors.append(f"{routing_file}: missing generated command model routing")
        elif routing_file.read_text() != expected_routing:
            errors.append(f"{routing_file}: differs from generated command model routing")

    for path in sorted(root.glob("plugins/*/skills/*/SKILL.md")):
        if FORBIDDEN_MODEL_FIELDS.search(frontmatter(path.read_text())):
            errors.append(f"{path}: model fields are not allowed in SKILL.md frontmatter")
    for path in sorted(root.glob("plugins/*/commands/*.md")):
        if FORBIDDEN_MODEL_FIELDS.search(frontmatter(path.read_text())):
            errors.append(f"{path}: model fields are not allowed in command frontmatter")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("OK: command model routing is consistent")


if __name__ == "__main__":
    main()
