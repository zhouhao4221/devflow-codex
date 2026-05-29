#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
用法: $0 [devflow-skills路径] [输出路径]

从 devflow-skills 源头生成 OpenCode .agents/skills/ 技能目录。
命名规则: <plugin>-<name> 扁平化，复制时自动更新 frontmatter name 字段。

参数:
  devflow-skills路径      默认当前目录
  输出路径                  默认当前目录下的 .agents/skills/
EOF
}

SKILLS_DIR="${1:-$(pwd)}"
OUTPUT_DIR="${2:-${SKILLS_DIR}/.agents/skills}"

if [ ! -d "$SKILLS_DIR/plugins" ]; then
  echo "错误: 未找到 plugins/ 目录，请确认 devflow-skills 路径: $SKILLS_DIR"
  exit 1
fi

echo "生成 OpenCode 技能目录: $OUTPUT_DIR"
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
