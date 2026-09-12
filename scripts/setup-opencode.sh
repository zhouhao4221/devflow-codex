#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="${1:-$(pwd)}"
OUTPUT_DIR="${2:-${SOURCE_DIR}/.agents/skills}"
python3 "$SCRIPT_DIR/export-skills.py" "$SOURCE_DIR" "$OUTPUT_DIR" --layout flat
