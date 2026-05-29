#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
用法: $0 <devflow-skills路径> [devflow-claude路径]

将 devflow-skills 中的 80 个 SKILL.md 同步到 devflow-claude 的 plugins/*/skills/ 目录。

参数:
  devflow-skills路径      devflow-skills 仓库根目录路径（默认为当前目录）
  devflow-claude路径      devflow-claude 仓库根目录路径（默认为 ../devflow-claude）
EOF
}

SKILLS_DIR="${1:-$(pwd)}"
TARGET_DIR="${2:-${SKILLS_DIR}/../devflow-claude}"

if [ ! -d "$SKILLS_DIR/plugins" ]; then
  echo "错误: 未找到 plugins/ 目录，请确认 devflow-skills 路径: $SKILLS_DIR"
  exit 1
fi

if [ ! -d "$TARGET_DIR/plugins" ]; then
  echo "错误: 未找到目标 plugins/ 目录，请确认 devflow-claude 路径: $TARGET_DIR"
  exit 1
fi

SKILLS_SRC="$SKILLS_DIR/plugins"
SKILLS_DST="$TARGET_DIR/plugins"

echo "同步 devflow-skills → devflow-claude"
echo "  源头: $SKILLS_SRC"
echo "  目标: $SKILLS_DST"
echo ""

synced=0

while IFS= read -r -d '' skill_file; do
  relative="${skill_file#$SKILLS_SRC/}"
  target="$SKILLS_DST/$relative"
  target_dir="$(dirname "$target")"

  mkdir -p "$target_dir"
  cp "$skill_file" "$target"
  synced=$((synced + 1))
done < <(find "$SKILLS_SRC" -name 'SKILL.md' -print0)

echo "完成: 同步了 $synced 个 SKILL.md 文件到 $SKILLS_DST"
