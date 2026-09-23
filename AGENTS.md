# Repository Guidelines

## Repository Purpose

Work in this repository maintains the DevFlow plugins. Mentioning a command while discussing its design does not request that command's workflow: editing release rules does not authorize a release. Read the affected plugin's `AGENTS.md` before editing it. User documentation belongs in `README.md` and tutorials; maintainer instructions belong here and in plugin-level `AGENTS.md` files. Keep root instructions repository-wide and put plugin-specific constraints in the nearest `AGENTS.md`.

## Repository Relationship

The maintainer owns both [devflow-codex](https://github.com/zhouhao4221/devflow-codex) (this repository) and [devflow-claude](https://github.com/zhouhao4221/devflow-claude). They are parallel implementations of DevFlow, with workflows and conventions tailored to Codex and Claude respectively. Do not assume an upstream/downstream or fork relationship. When referencing or porting behavior between them, preserve the target repository's platform-specific style and conventions.

## Project Structure & Module Organization

This repository distributes DevFlow as Codex marketplace plugins under `plugins/<plugin>/`. Edit the authoring source, then regenerate derived files:

| Content | Authoring source |
|---|---|
| Workflow, trigger and description | `plugins/<plugin>/skills/<skill>/SKILL.md` |
| Skill inventory, command bindings, argument hints and execution tiers | `skill-bindings.json` |
| Plugin metadata/versions and generated UI fields | `scripts/generate-codex-marketplace.py` |
| Cross-plugin model routing | `shared/command-model-routing.md` |
| Plugin-specific reusable rules and output templates | `plugins/<plugin>/shared/` (except generated `_command-models.md`) and `templates/` |

The generator owns plugin `.codex-plugin/plugin.json`, `commands/*.md`, `skills/*/agents/openai.yaml`, `shared/_command-models.md`, and `.agents/plugins/marketplace.json`. Hand edits there will be overwritten. Update bindings only when inventory, mappings, arguments or tiers change; a workflow-body correction does not itself require a bindings change. Adapters and validation live in `scripts/`; design and audit records belong in `docs/`.

DevFlow project state is tool-neutral. Use `.devflow/settings.json` for shared project configuration and `.devflow/settings.local.json` for machine-private values. Do not read `.claude/settings.local.json` or `~/.claude-requirements` as DevFlow configuration or storage. The canonical project instructions for Codex and other agents live in `AGENTS.md`; do not add a tool-specific duplicate instructions file in this repository.

## Skill Authoring

- Skill directory names must match frontmatter `name`, use lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), and stay within 64 characters. This repository limits frontmatter to `name` and `description`; that is a local validator/generator contract, not a claim that Codex supports no optional fields.
- Make `description` state the capability and triggering request. Add exclusions where adjacent skills would otherwise overlap; avoid catchalls such as “any project question.” Put detailed modes and procedures in the body. Preserve invocation policy unless the user requests a change; generated UI changes belong in the generator.
- A required helper must be reachable through the command binding or an explicit skill reference at the relevant step. Saying it “automatically activates” does not guarantee loading; keep helper trigger descriptions consistent with actual callers.
- Keep the entrypoint focused on decisions, required inputs, scope and acceptance. Link substantial conditional detail at the step that needs it. Do not repeat shared rules, load whole reference collections, or add generic tool tutorials. File length alone is not a defect.
- Use real scripts for repeatable deterministic operations. Mark illustrative pseudocode clearly; do not imply example helpers are installed tools. Referenced tools must exist or have a defined capability check and fallback.
- Keep runtime-critical rules reachable from the skill and its packaged references. Maintainer `AGENTS.md` files are not a substitute for instructions needed by an installed skill. Check direct skill invocation as well as generated command entrypoints.

Use Python 3 for helpers and Bash with `set -euo pipefail` where practical. Preserve supported adapter layouts when renaming skills or moving resources.

## Command Design

Use the [command design plan](docs/design/command-design.md) when adding or materially changing a command. Scale the design record to the change; a small correction does not need a new plan document or another approval round.

- Design around one user-visible outcome. Define the trigger, arguments and defaults, required data sources, allowed changes, failure/continuation behavior, and observable acceptance. Reuse an existing workflow when it already owns that outcome.
- Author workflow decisions in `SKILL.md` and focused shared Markdown; generated command wrappers remain thin. Scripts handle deterministic generation, parsing and validation.
- Choose the command's execution tier by required reasoning, not by whether it writes files. Rule-driven release/state operations can be economical; report synthesis and open-ended design have different needs. Command routing and independent subtask delegation are separate decisions.
- Preserve explicit user authorization, scope and branch preferences across steps; do not ask again for already-authorized work. Read-only roles restrict the relevant resources, not every local output. Missing optional knowledge should degrade gracefully; missing required input or failed required checks must be reported before dependent actions. Keep command defaults, examples and failure paths consistent.
- Attach acceptance to the intended behavior and verify actual artifacts. Keep failures and unexecuted checks visible; reuse results only while their relevant inputs remain valid. Fix implementation defects rather than weakening checks to obtain a pass.
- When learning from devflow-claude, record the source revision, problem solved, Codex equivalent and verification. Inspect the actual command and shared rule as well as global guidance; retain Codex source layout, runtime capabilities and authorization semantics.

## Validation and Export

Run `./scripts/validate-skills.sh --ci` before committing. It includes layout, model-route consistency, review backend, Swagger and requirement-lifecycle checks. Match additional checks to the change:

| Change | Additional verification |
|---|---|
| Generation inputs, skill descriptions or command metadata | Run `python3 scripts/generate-codex-marketplace.py`; inspect generated diffs and ensure another run adds no changes |
| Routing or marketplace generator | `python3 scripts/test-command-models.py` |
| Shared resources, resource moves or adapters | `python3 scripts/test-export-skills.py` |
| Workflow decisions, defaults, fallback or side effects | Exercise the affected behavior with a realistic request or isolated fixture; include the relevant failure path |

Static checks establish structure and consistency, not that every workflow behaves correctly. Report audit coverage, failures, skips and unexecuted scenarios separately; avoid tests that only assert wording or headings. Existing valid evidence can be reused while relevant inputs remain unchanged.

Use `./scripts/setup-claude.sh . ./dist/claude` for a layered compatibility export, or `./scripts/setup-opencode.sh . ./dist/opencode` for a flat export. The separate `devflow-claude` repository is never the default export destination. Do not reintroduce npm distribution unless requested.

## Subagent Model Selection

Delegate concrete, independent execution tasks when doing so reduces total work or cost and the runtime permits it. Keep planning, cross-file decisions and final acceptance in the current primary session. Follow [the shared delegation rules](plugins/rd/shared/_delegate.md) for available worker models, reasoning effort, context and file ownership; keep specific model defaults there rather than duplicating them here. Use direct tools for small tasks, respect explicit user model choices, and verify actual changes and evidence before accepting a worker's result.

Command execution tiers are `economy`, `standard`, or `primary`; they are DevFlow routing metadata, not a session model switch. Keep command-backed direct skill entrypoints linked to their generated `_command-models.md`. Do not put model fields in skill or UI frontmatter.

## Commit & Contribution Guidelines

Recent history uses concise release numbers and Chinese conventional-style messages, for example `重构: 精简技能文档并引入插件模板`. Prefer short, imperative commits that describe the changed behavior or release version. For this repository, do not add `Co-Authored-By` lines. Do not create PRs or feature branches unless explicitly requested; commit and push directly to the main branch according to the maintainer workflow.

Resolve the actual branch name before an authorized commit/push: the repository currently configures `master` in `.devflow/settings.json` and CI. An explicit request for literal `main` is not permission to silently substitute `master` or rename branches; resolve that mismatch before pushing.
