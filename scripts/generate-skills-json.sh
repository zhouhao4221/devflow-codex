#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
用法: $0 [devflow-skills路径]

从 devflow-skills 的 plugins/ 目录自动生成 skills.json 清单，
包含全部技能的名称、插件、描述和 agentskills.io 扁平化名称。

参数:
  devflow-skills路径      默认当前目录
EOF
}

SKILLS_DIR="${1:-$(pwd)}"

if [ ! -d "$SKILLS_DIR/plugins" ]; then
  echo "错误: 未找到 plugins/ 目录，请确认 devflow-skills 路径: $SKILLS_DIR"
  exit 1
fi

OUTPUT="$SKILLS_DIR/skills.json"

echo "生成 skills.json → $OUTPUT"

cat > "$OUTPUT" <<'HEADER'
{
  "version": "2.0",
  "description": "DevFlow Skills 清单 — 从 plugins/ 自动生成",
HEADER

echo "  \"generated_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"," >> "$OUTPUT"

total=$(find "$SKILLS_DIR/plugins" -name 'SKILL.md' | wc -l | tr -d ' ')

echo "  \"total\": ${total}," >> "$OUTPUT"
echo '  "skills": [' >> "$OUTPUT"

first=true
while IFS= read -r -d '' skill_file; do
  relative="${skill_file#$SKILLS_DIR/plugins/}"
  plugin="$(echo "$relative" | cut -d/ -f1)"
  name="$(echo "$relative" | cut -d/ -f3)"
  flat_name="${plugin}-${name}"

  desc="$($SKILLS_DIR/scripts/_get-description.py "$skill_file" 2>/dev/null || echo '')"

  if $first; then
    first=false
  else
    echo '    ,' >> "$OUTPUT"
  fi

  cat >> "$OUTPUT" <<ENTRY
    {
      "plugin": "${plugin}",
      "name": "${name}",
      "flat_name": "${flat_name}",
      "description": "${desc}"
    }
ENTRY
done < <(find "$SKILLS_DIR/plugins" -name 'SKILL.md' -print0 | sort)

cat >> "$OUTPUT" <<'FOOTER'
  ]
}
FOOTER

echo "完成: 生成了 ${total} 条技能记录"
