#!/usr/bin/env python3
"""Validate local Markdown references and Codex authoring boundaries."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


LINK = re.compile(r"\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def local_links(text: str):
    # Examples in fenced code blocks are not resource dependencies.
    text = re.sub(r"^(`{3,}|~{3,}).*?^\1\s*$", "", text, flags=re.M | re.S)
    for match in LINK.finditer(text):
        value = match[1].strip("<>")
        if value.startswith(("#", "$", "/")) or "<" in value:
            continue
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield unquote(parsed.path)


def check(root: Path) -> list[str]:
    errors = []
    for path in sorted(root.rglob("*.md")):
        if any(p.startswith(".") for p in path.relative_to(root).parts) or "templates" in path.relative_to(root).parts:
            continue
        text = path.read_text()
        for target in local_links(text):
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path}: missing reference {target}")
            elif not resolved.is_relative_to(root.resolve()):
                errors.append(f"{path}: reference escapes package root: {target}")
        if path.name == "SKILL.md":
            if "# 附录（自动内联" in text or "（见附录：" in text:
                errors.append(f"{path}: shared rules must be linked, not inlined")
        if path.parent.name == "commands" and path.stem.startswith("_"):
            errors.append(f"{path}: shared document in command directory")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("plugins"))
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"not a directory: {args.root}")
    errors = check(args.root)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("OK: local references and authoring layout")


if __name__ == "__main__":
    main()
