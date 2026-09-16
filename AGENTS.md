# Repository Guidelines

## Repository Purpose

Work in this repository maintains the DevFlow plugins. Mentioning a command while discussing its design does not request that command's workflow: editing release rules does not authorize a release. User documentation belongs in `README.md` and tutorials; maintainer instructions belong here and in plugin-level `AGENTS.md` files.

## Repository Relationship

The maintainer owns both [devflow-codex](https://github.com/zhouhao4221/devflow-codex) (this repository) and [devflow-claude](https://github.com/zhouhao4221/devflow-claude). They are parallel implementations of DevFlow, with workflows and conventions tailored to Codex and Claude respectively. Do not assume an upstream/downstream or fork relationship. When referencing or porting behavior between them, preserve the target repository's platform-specific style and conventions.

## Project Structure & Module Organization

This repository distributes DevFlow as Codex marketplace plugins. Each plugin lives under `plugins/<plugin>/` with `.codex-plugin/plugin.json`, generated `commands/*.md`, and authored `skills/<skill>/SKILL.md`. Skill directory names must match their frontmatter `name`. Plugin templates live in `plugins/<plugin>/templates/`; shared instructions belong in `shared/` and are loaded through direct relative links. Keep plugin-specific maintenance rules in that plugin's `AGENTS.md`. Adapter, generation, and validation scripts are in `scripts/`. Project docs and requirement/design notes are in `docs/`. `skill-bindings.json` maps plugins, commands, and skills and must stay synchronized with `plugins/`.

DevFlow project state is tool-neutral. Use `.devflow/settings.json` for shared project configuration and `.devflow/settings.local.json` for machine-private values. Do not introduce new default behavior that depends on `.claude/settings.local.json` or `~/.claude-requirements`; those paths are legacy compatibility fallbacks only. The canonical project instructions for Codex and other agents live in `AGENTS.md`; do not add a tool-specific duplicate instructions file in this repository.

## Build, Test, and Development Commands

- `python3 scripts/generate-codex-marketplace.py` - regenerate `.codex-plugin/plugin.json`, plugin `commands/*.md`, and `.agents/plugins/marketplace.json`.
- `./scripts/validate-skills.sh --ci` - run the required consistency checks used by CI.
- `./scripts/setup-claude.sh . ./dist/claude` - generate an isolated layered compatibility export; never use the separately maintained `devflow-claude` repository as the default output.
- `./scripts/setup-opencode.sh . ./dist/opencode` - generate flat-layout skills for OpenCode-compatible tools.
- `python3 scripts/check-layout.py` - check shared references and authoring layout.
- `python3 scripts/test-export-skills.py` - verify both export layouts, linked resources, and output protection in temporary directories.

## Coding Style & Naming Conventions

Use Python 3 for generation/validation helpers and POSIX-oriented Bash for shell scripts. Keep shell scripts strict with `set -euo pipefail` when practical. Skill and command names use lowercase kebab-case and must match `^[a-z0-9]+(-[a-z0-9]+)*$`. Preserve the SKILL.md format: YAML frontmatter, then concise Markdown instructions. Do not rename or rewrite large skill bodies unless the change is intentional across all affected adapters.

## Command Design

Use the [command design plan](docs/design/command-design.md) when adding or materially changing a command. Scale the design record to the change; a small correction does not need a new plan document or another approval round.

- Design around one user-visible outcome. Define the trigger, arguments and defaults, required data sources, allowed changes, failure/continuation behavior, and observable acceptance. Reuse an existing workflow when it already owns that outcome.
- Author workflow decisions in `SKILL.md` and focused shared Markdown. Scripts handle deterministic generation, parsing and validation; generated command wrappers remain thin. Document platform constraints and non-obvious rules, not generic tool tutorials.
- Keep the common path short. Load project knowledge, detailed rationale and edge cases where needed; link actual dependencies directly instead of loading a shared index or copying the same rules into every skill.
- Choose the command's execution tier by required reasoning, not by whether it writes files. Rule-driven release/state operations can be economical; report synthesis and open-ended design have different needs. Command routing and independent subtask delegation are separate decisions.
- Preserve explicit user authorization, scope and branch preferences across steps. Read-only roles restrict the relevant resources, not every local output. Missing optional knowledge should degrade gracefully; missing required input or failed required checks must be reported before dependent actions.
- Attach acceptance to the intended behavior and verify actual artifacts. Keep failures and unexecuted checks visible; reuse results only while their relevant inputs remain valid. Fix implementation defects rather than weakening checks to obtain a pass.
- When learning from devflow-claude, record the source revision, problem solved, Codex equivalent and verification. Inspect the actual command and shared rule as well as global guidance; retain Codex source layout, runtime capabilities and authorization semantics.

## Testing Guidelines

Treat `./scripts/validate-skills.sh --ci` as the minimum required test before committing. Run `python3 scripts/test-export-skills.py` when changing shared resources or adapters. When adding or changing a command, update `skill-bindings.json`, regenerate marketplace artifacts, and verify both the new file and bindings pass validation. Do not reintroduce npm package distribution unless explicitly requested.

## Subagent Model Selection

Delegate concrete, independent execution tasks when doing so reduces total work or cost. Keep planning, cross-file decisions, and final acceptance in the primary session; when the user selects Astra, it retains those responsibilities. Follow [the shared delegation rules](plugins/rd/shared/_delegate.md) to choose an economical available worker model and reasoning effort for the task. Simple work should use a cheaper capable model or a direct tool call; do not automatically inherit the primary model for every worker. Respect explicit user model choices and runtime constraints, and check the actual changes and validation evidence before accepting a worker's result.

Command execution tiers belong in `skill-bindings.json` (`executionTier`: `economy`, `standard`, or `primary`). Author the common routing policy in `shared/command-model-routing.md`; the marketplace generator packages it with each plugin's command table as `shared/_command-models.md`. Keep the direct skill entrypoint linked to that policy, and run `python3 scripts/test-command-models.py` after changing routing or its generation. Do not put model fields in skill or UI frontmatter.

## Commit & Contribution Guidelines

Recent history uses concise release numbers and Chinese conventional-style messages, for example `重构: 精简技能文档并引入插件模板`. Prefer short, imperative commits that describe the changed behavior or release version. For this repository, do not add `Co-Authored-By` lines. Do not create PRs or feature branches unless explicitly requested; commit and push directly to the main branch according to the maintainer workflow.
