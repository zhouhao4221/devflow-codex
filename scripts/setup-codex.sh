#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
用法: $0 [devflow-skills路径] [输出路径] [--gen-openai-yaml]

从 devflow-skills 源头生成 Codex .agents/skills/ 技能目录。
命名规则: <plugin>-<name> 扁平化，复制时自动更新 frontmatter name 字段。
可选: --gen-openai-yaml 额外生成 agents/openai.yaml 清单。

参数:
  devflow-skills路径      默认当前目录
  输出路径                  默认当前目录下的 .agents/skills/
  --gen-openai-yaml        额外生成 agents/openai.yaml
EOF
}

GEN_OPENAI=false
SKILLS_DIR=""
OUTPUT_DIR=""

for arg in "$@"; do
  case "$arg" in
    --gen-openai-yaml) GEN_OPENAI=true ;;
    *)
      if [ -z "$SKILLS_DIR" ]; then
        SKILLS_DIR="$arg"
      elif [ -z "$OUTPUT_DIR" ]; then
        OUTPUT_DIR="$arg"
      fi
      ;;
  esac
done

SKILLS_DIR="${SKILLS_DIR:-$(pwd)}"
OUTPUT_DIR="${OUTPUT_DIR:-${SKILLS_DIR}/.agents/skills}"

if [ ! -d "$SKILLS_DIR/plugins" ]; then
  echo "错误: 未找到 plugins/ 目录，请确认 devflow-skills 路径: $SKILLS_DIR"
  exit 1
fi

echo "生成 Codex 技能目录: $OUTPUT_DIR"
echo ""

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
count=0

while IFS= read -r -d '' skill_file; do
  relative="${skill_file#$SKILLS_DIR/plugins/}"
  plugin="$(echo "$relative" | cut -d/ -f1)"
  name="$(echo "$relative" | cut -d/ -f3)"

  flat_name="${plugin}-${name}"
  target_dir="$OUTPUT_DIR/$flat_name"
  mkdir -p "$target_dir"

  sed "s/^name:.*/name: ${flat_name}/" "$skill_file" > "$target_dir/SKILL.md"
  count=$((count + 1))
done < <(find "$SKILLS_DIR/plugins" -name 'SKILL.md' -print0)

echo "完成: 生成了 $count 个技能到 $OUTPUT_DIR"

if $GEN_OPENAI; then
  YAML_DIR="$(dirname "$OUTPUT_DIR")/openai.yaml"
  echo ""
  echo "生成 agents/openai.yaml → $YAML_DIR"

  cat > "$YAML_DIR" <<YAML_HEADER
# DevFlow Skills — OpenAI Agent Manifest
# 自动生成于 $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# 工具: Codex / OpenAI

agents:
YAML_HEADER

  while IFS= read -r -d '' skill_file; do
    relative="${skill_file#$SKILLS_DIR/plugins/}"
    plugin="$(echo "$relative" | cut -d/ -f1)"
    name="$(echo "$relative" | cut -d/ -f3)"
    flat_name="${plugin}-${name}"

    desc="$($SKILLS_DIR/scripts/_get-description.py "$skill_file" | head -c 200)"

    cat >> "$YAML_DIR" <<YAML_ENTRY
  - name: ${flat_name}
    description: "${desc}"
    instructions: skills/${flat_name}/SKILL.md
YAML_ENTRY
  done < <(find "$SKILLS_DIR/plugins" -name 'SKILL.md' -print0)

  echo "完成: agents/openai.yaml 已生成"
fi
