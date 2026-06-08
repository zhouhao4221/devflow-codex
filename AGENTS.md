# Repository Guidelines

## Project Structure & Module Organization

This repository distributes DevFlow as Codex marketplace plugins. Each plugin lives under `plugins/<plugin>/` with `.codex-plugin/plugin.json`, `commands/*.md`, and `skills/<skill>/SKILL.md`. Skill directory names must match their frontmatter `name`. Plugin templates live in `plugins/<plugin>/templates/`. Adapter, generation, and validation scripts are in `scripts/`. Project docs and requirement/design notes are in `docs/`. `skill-bindings.json` maps plugins, commands, and skills and must stay synchronized with `plugins/`.

DevFlow project state is tool-neutral. Use `.devflow/settings.json` for shared project configuration and `.devflow/settings.local.json` for machine-private values. Do not introduce new default behavior that depends on `.claude/settings.local.json` or `~/.claude-requirements`; those paths are legacy compatibility fallbacks only. The canonical project instructions for Codex and other agents live in `AGENTS.md`; do not add a tool-specific duplicate instructions file in this repository.

## Build, Test, and Development Commands

- `python3 scripts/generate-codex-marketplace.py` - regenerate `.codex-plugin/plugin.json`, plugin `commands/*.md`, and `.agents/plugins/marketplace.json`.
- `./scripts/validate-skills.sh --ci` - run the required consistency checks used by CI.
- `./scripts/setup-claude.sh . ../devflow-claude` - generate Claude Code's layered layout.
- `./scripts/setup-opencode.sh . ~/.agents/skills` - generate flat-layout skills for OpenCode-compatible tools.

## Coding Style & Naming Conventions

Use Python 3 for generation/validation helpers and POSIX-oriented Bash for shell scripts. Keep shell scripts strict with `set -euo pipefail` when practical. Skill and command names use lowercase kebab-case and must match `^[a-z0-9]+(-[a-z0-9]+)*$`. Preserve the SKILL.md format: YAML frontmatter, then concise Markdown instructions. Do not rename or rewrite large skill bodies unless the change is intentional across all affected adapters.

## Testing Guidelines

There is no separate unit test suite. Treat `./scripts/validate-skills.sh --ci` as the minimum required test before committing. When adding or changing a command, update `skill-bindings.json`, regenerate marketplace artifacts, and verify both the new file and bindings pass validation. Do not reintroduce npm package distribution unless explicitly requested.

## Commit & Contribution Guidelines

Recent history uses concise release numbers and Chinese conventional-style messages, for example `重构: 精简技能文档并引入插件模板`. Prefer short, imperative commits that describe the changed behavior or release version. For this repository, do not add `Co-Authored-By` lines. Do not create PRs or feature branches unless explicitly requested; commit and push directly to the main branch according to the maintainer workflow.
