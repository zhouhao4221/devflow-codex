#!/usr/bin/env bash
# DevFlow Skills Validation Script
# Run locally or in CI to validate skill name consistency.
# Usage: ./scripts/validate-skills.sh [--ci]
set -euo pipefail

CI_MODE=false
[ "${1:-}" = "--ci" ] && CI_MODE=true

errors=0

red()   { echo -e "\033[31m$*\033[0m"; }
green() { echo -e "\033[32m$*\033[0m"; }

ok() {
  [ "$errors" -eq 0 ] && green "OK: $*"
}

# 1. skill-bindings.json exists
echo "=== 1. skill-bindings.json ==="
if [ ! -f skill-bindings.json ]; then
  red "ERROR: skill-bindings.json not found"
  errors=$((errors + 1))
else
  green "OK: found"
fi

# 2. Frontmatter name == directory name and uses Codex-supported keys
echo ""
echo "=== 2. SKILL.md frontmatter ==="
while IFS= read -r -d '' f; do
  dir="$(basename "$(dirname "$f")")"
  fm="$(head -10 "$f" | grep "^name:" | head -1 | sed 's/^name: *//' | tr -d '"'"'" | xargs)"
  if [ -z "$fm" ]; then
    red "ERROR: $f — missing 'name' in frontmatter"
    errors=$((errors + 1))
  elif [ "$fm" != "$dir" ]; then
    red "ERROR: $f — name '$fm' != dir '$dir'"
    errors=$((errors + 1))
  fi
done < <(find plugins -name 'SKILL.md' -not -path '*/.git/*' -print0)

TMP_ERR="$(mktemp)"
python3 -c "
from pathlib import Path
import sys

errs = 0
allowed = {'name', 'description'}
for path in sorted(Path('plugins').glob('*/skills/*/SKILL.md')):
    text = path.read_text()
    if not text.startswith('---'):
        print(f'ERROR: {path} — missing YAML frontmatter')
        errs += 1
        continue
    parts = text.split('---', 2)
    if len(parts) < 3:
        print(f'ERROR: {path} — malformed YAML frontmatter')
        errs += 1
        continue
    keys = []
    for line in parts[1].splitlines():
        if line and not line.startswith((' ', '\\t')) and ':' in line:
            keys.append(line.split(':', 1)[0].strip())
    for key in keys:
        if key not in allowed:
            print(f'ERROR: {path} — unsupported frontmatter key {key!r}; Codex skills use only name and description')
            errs += 1
    for key in ('name', 'description'):
        if key not in keys:
            print(f'ERROR: {path} — missing frontmatter key {key!r}')
            errs += 1
sys.exit(errs)
" > "$TMP_ERR" 2>&1 || true
while IFS= read -r line; do
  red "$line"
  errors=$((errors + 1))
done < "$TMP_ERR"
rm -f "$TMP_ERR"
ok "all frontmatter names and keys are valid"

# 3. Parse bindings
echo ""
echo "=== 3. Parse skill-bindings.json ==="
if [ ! -f skill-bindings.json ]; then
  red "ERROR: cannot parse"
  errors=$((errors + 1))
else
  TMP_NAMES="$(mktemp)"
  python3 -c "
import json
with open('skill-bindings.json') as f:
    data = json.load(f)
for plugin, skills in data.get('allSkills', {}).items():
    for s in skills:
        print(s)
" > "$TMP_NAMES"

  # 4. Every SKILL.md in allSkills
  echo ""
  echo "=== 4. Every SKILL.md in allSkills ==="
  while IFS= read -r -d '' f; do
    dir="$(basename "$(dirname "$f")")"
    if ! grep -qxF "$dir" "$TMP_NAMES"; then
      red "ERROR: $f — skill '$dir' not in skill-bindings.json allSkills"
      errors=$((errors + 1))
    fi
  done < <(find plugins -name 'SKILL.md' -not -path '*/.git/*' -print0)
  ok "all SKILL.md files declared"

  # 5. Every allSkills entry has file
  echo ""
  echo "=== 5. Every allSkills entry has file ==="
  while IFS= read -r name; do
    found="$(find plugins -path "*/${name}/SKILL.md" -not -path '*/.git/*' -print -quit)"
    if [ -z "$found" ]; then
      red "ERROR: allSkills '$name' — no SKILL.md found"
      errors=$((errors + 1))
    fi
  done < "$TMP_NAMES"
  ok "all allSkills have files"

  # 6. Plugin command cross-reference
  echo ""
  echo "=== 6. Plugin command binding cross-ref ==="
  TMP_ERR="$(mktemp)"
  python3 -c "
import json, sys
with open('skill-bindings.json') as f:
    data = json.load(f)
all_skills = data.get('allSkills', {})
errs = 0
for plugin, plugin_data in data.get('plugins', {}).items():
    commands = plugin_data.get('commands', {})
    for cmd, cmd_data in commands.items():
        primary = cmd_data.get('primarySkill', '')
        if primary and primary not in all_skills.get(plugin, []):
            print(f'ERROR: plugin/{plugin} command/{cmd} — primarySkill \"{primary}\" not in allSkills.{plugin}')
            errs += 1
        for extra in cmd_data.get('additionalSkills', []):
            if extra not in all_skills.get(plugin, []):
                print(f'ERROR: plugin/{plugin} command/{cmd} — additionalSkill \"{extra}\" not in allSkills.{plugin}')
                errs += 1
sys.exit(errs)
" > "$TMP_ERR" 2>&1 || true
  while IFS= read -r line; do
    red "$line"
    errors=$((errors + 1))
  done < "$TMP_ERR"
  ok "plugin command bindings consistent"

  # 7. Codex plugin manifests
  echo ""
  echo "=== 7. Codex plugin manifests ==="
  TMP_ERR="$(mktemp)"
  python3 -c "
import json, re, sys
from pathlib import Path

root = Path('.')
data = json.loads(Path('skill-bindings.json').read_text())
errs = 0
semver = re.compile(r'^[0-9]+\\.[0-9]+\\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$')
for plugin in data.get('plugins', {}):
    plugin_dir = root / 'plugins' / plugin
    manifest_file = plugin_dir / '.codex-plugin' / 'plugin.json'
    if not manifest_file.exists():
        print(f'ERROR: plugins/{plugin} — missing .codex-plugin/plugin.json')
        errs += 1
        continue
    manifest = json.loads(manifest_file.read_text())
    if manifest.get('name') != plugin:
        print(f'ERROR: plugins/{plugin} plugin.json — name {manifest.get(\"name\")!r} != {plugin!r}')
        errs += 1
    if not semver.match(str(manifest.get('version', ''))):
        print(f'ERROR: plugins/{plugin} plugin.json — version must be semver')
        errs += 1
    if manifest.get('skills') != './skills/':
        print(f'ERROR: plugins/{plugin} plugin.json — skills must be ./skills/')
        errs += 1
    interface = manifest.get('interface') or {}
    for key in ['displayName', 'shortDescription', 'longDescription', 'developerName', 'category']:
        if not interface.get(key):
            print(f'ERROR: plugins/{plugin} plugin.json — missing interface.{key}')
            errs += 1
sys.exit(errs)
" > "$TMP_ERR" 2>&1 || true
  while IFS= read -r line; do
    red "$line"
    errors=$((errors + 1))
  done < "$TMP_ERR"
  ok "Codex plugin manifests valid"

  # 8. Codex plugin commands
  echo ""
  echo "=== 8. Codex plugin commands ==="
  TMP_ERR="$(mktemp)"
  python3 -c "
import json, sys
from pathlib import Path

data = json.loads(Path('skill-bindings.json').read_text())
errs = 0
for plugin, plugin_data in data.get('plugins', {}).items():
    commands_dir = Path('plugins') / plugin / 'commands'
    if not commands_dir.exists():
        print(f'ERROR: plugins/{plugin} — missing commands/')
        errs += 1
        continue
    expected = set(plugin_data.get('commands', {}).keys())
    actual = {p.stem for p in commands_dir.glob('*.md')}
    for command in sorted(expected - actual):
        print(f'ERROR: plugins/{plugin}/commands — missing {command}.md')
        errs += 1
    for command in sorted(actual - expected):
        print(f'ERROR: plugins/{plugin}/commands — unexpected {command}.md')
        errs += 1
    for command in sorted(expected & actual):
        text = (commands_dir / f'{command}.md').read_text()
        primary = plugin_data['commands'][command].get('primarySkill')
        expected_ref = chr(96) + f'{plugin}:{primary}' + chr(96)
        if expected_ref not in text:
            print(f'ERROR: plugins/{plugin}/commands/{command}.md — missing skill reference {plugin}:{primary}')
            errs += 1
sys.exit(errs)
" > "$TMP_ERR" 2>&1 || true
  while IFS= read -r line; do
    red "$line"
    errors=$((errors + 1))
  done < "$TMP_ERR"
  ok "Codex plugin commands consistent"

  # 9. Codex skill UI metadata
  echo ""
  echo "=== 9. Codex skill agents/openai.yaml ==="
  TMP_ERR="$(mktemp)"
  python3 -c "
import sys
from pathlib import Path

errs = 0
for skill_file in sorted(Path('plugins').glob('*/skills/*/SKILL.md')):
    skill_dir = skill_file.parent
    skill_name = skill_dir.name
    metadata_file = skill_dir / 'agents' / 'openai.yaml'
    if not metadata_file.exists():
        print(f'ERROR: {skill_dir} — missing agents/openai.yaml')
        errs += 1
        continue
    text = metadata_file.read_text()
    required = [
        'interface:',
        '  display_name:',
        '  short_description:',
        '  default_prompt:',
    ]
    for marker in required:
        if marker not in text:
            print(f'ERROR: {metadata_file} — missing {marker.strip()}')
            errs += 1
    skill_ref = '$' + skill_name
    if skill_ref not in text:
        print(f'ERROR: {metadata_file} — default_prompt must mention {skill_ref}')
        errs += 1
    for unsupported in ('model:', 'model_reasoning_effort:', 'model_provider:'):
        if unsupported in text:
            print(f'ERROR: {metadata_file} — {unsupported[:-1]} belongs in Codex config or custom agents, not skill metadata')
            errs += 1
sys.exit(errs)
" > "$TMP_ERR" 2>&1 || true
  while IFS= read -r line; do
    red "$line"
    errors=$((errors + 1))
  done < "$TMP_ERR"
  ok "Codex skill UI metadata valid"

  # 10. Repo marketplace
  echo ""
  echo "=== 10. Codex marketplace ==="
  TMP_ERR="$(mktemp)"
  python3 -c "
import json, sys
from pathlib import Path

marketplace_file = Path('.agents/plugins/marketplace.json')
if not marketplace_file.exists():
    print('ERROR: missing .agents/plugins/marketplace.json')
    sys.exit(1)
marketplace = json.loads(marketplace_file.read_text())
data = json.loads(Path('skill-bindings.json').read_text())
expected = set(data.get('plugins', {}).keys())
entries = marketplace.get('plugins', [])
actual = {entry.get('name') for entry in entries}
errs = 0
for plugin in sorted(expected - actual):
    print(f'ERROR: marketplace missing plugin {plugin}')
    errs += 1
for plugin in sorted(actual - expected):
    print(f'ERROR: marketplace has unexpected plugin {plugin}')
    errs += 1
for entry in entries:
    name = entry.get('name')
    if entry.get('source', {}).get('path') != f'./plugins/{name}':
        print(f'ERROR: marketplace plugin {name} has invalid source.path')
        errs += 1
    policy = entry.get('policy') or {}
    if policy.get('installation') != 'AVAILABLE' or policy.get('authentication') != 'ON_INSTALL':
        print(f'ERROR: marketplace plugin {name} has invalid policy')
        errs += 1
sys.exit(errs)
" > "$TMP_ERR" 2>&1 || true
  while IFS= read -r line; do
    red "$line"
    errors=$((errors + 1))
  done < "$TMP_ERR"
  ok "Codex marketplace valid"

  rm -f "$TMP_NAMES" "$TMP_ERR"
fi

# Summary
echo ""
echo "============================================"
if [ "$errors" -gt 0 ]; then
  red "FAILED: $errors error(s)"
  $CI_MODE && exit 1
else
  green "SUCCESS: all validations passed"
fi
