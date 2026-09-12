#!/usr/bin/env python3
"""Export skills with their linked resources, preserving the source repository."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit


MARKER = ".devflow-export.json"
LINK = re.compile(r"(\]\()([^\s)]+)(\))")


def export(source: Path, output: Path, layout: str) -> int:
    source, output = source.resolve(), output.resolve()
    plugins = source / "plugins"
    if not plugins.is_dir():
        raise ValueError(f"missing plugins directory: {plugins}")
    if source == output or source.is_relative_to(output) or output.is_relative_to(plugins):
        raise ValueError("output must not contain the source or overwrite plugin sources")
    if (output / ".git").exists():
        raise ValueError("output is a Git repository; choose a separate export directory")
    if output.exists() and any(output.iterdir()):
        marker = output / MARKER
        if not marker.is_file() or json.loads(marker.read_text()).get("generator") != "devflow-skills":
            raise ValueError("nonempty output was not created by this exporter; choose an empty directory")

    # Build in a sibling directory first. Failed exports leave an existing bundle intact.
    import tempfile

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".devflow-export-", dir=output.parent) as scratch:
        stage = Path(scratch)
        skills = sorted(plugins.glob("*/skills/*/SKILL.md"))
        for entry in skills:
            plugin, name = entry.relative_to(plugins).parts[0:3:2]
            owner = stage / f"{plugin}-{name}"
            visited: set[Path] = set()

            def target_for(path: Path) -> Path:
                rel = path.relative_to(plugins)
                if layout == "layered":
                    return stage / "plugins" / rel
                if len(rel.parts) >= 3 and rel.parts[1] == "skills":
                    return stage / f"{rel.parts[0]}-{rel.parts[2]}" / Path(*rel.parts[3:])
                return owner / "references" / "plugins" / rel

            def copy_resource(path: Path) -> None:
                path = path.resolve()
                if not path.is_relative_to(plugins):
                    raise ValueError(f"resource outside plugins: {path}")
                if not path.exists():
                    raise ValueError(f"missing resource: {path}")
                if path in visited:
                    return
                visited.add(path)
                dest = target_for(path)
                if path.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                    for child in sorted(path.iterdir()):
                        copy_resource(child)
                    return
                dest.parent.mkdir(parents=True, exist_ok=True)
                if path.suffix != ".md":
                    shutil.copy2(path, dest)
                    if layout == "flat" and path.name == "openai.yaml":
                        rel = path.relative_to(plugins)
                        text = dest.read_text().replace(f"${rel.parts[2]} ", f"${rel.parts[0]}-{rel.parts[2]} ")
                        dest.write_text(text)
                    return
                text = path.read_text()

                def rewrite(match: re.Match) -> str:
                    value = match[2]
                    parsed = urlsplit(value)
                    if (parsed.scheme or parsed.netloc or not parsed.path
                            or value.startswith(("$", "/")) or "<" in value):
                        return match[0]
                    linked = (path.parent / unquote(parsed.path)).resolve()
                    copy_resource(linked)
                    relative = os.path.relpath(target_for(linked), dest.parent).replace(os.sep, "/")
                    relative = relative.replace(" ", "%20")
                    suffix = ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
                    return f"]({relative}{suffix})"

                if "templates" not in path.relative_to(plugins).parts:
                    text = LINK.sub(rewrite, text)
                if layout == "flat" and path.name == "SKILL.md":
                    rel = path.relative_to(plugins)
                    text = re.sub(r"^name:.*$", f"name: {rel.parts[0]}-{rel.parts[2]}", text, count=1, flags=re.M)
                    if (plugins / rel.parts[0] / "templates").is_dir():
                        resource_root = target_for(plugins / rel.parts[0] / "templates").parent
                        relative = os.path.relpath(resource_root, dest.parent).replace(os.sep, "/")
                        note = f"\n\n> 兼容导出资源：本 skill 中的 `<plugin-path>` 指 `{relative}`，模板位于其 `templates/`。\n"
                        sections = text.split("---", 2)
                        text = "---" + sections[1] + "---" + note + sections[2]
                dest.write_text(text)

            copy_resource(entry.parent)
            # Some workflow templates are selected dynamically by requirement type.
            templates = plugins / plugin / "templates"
            if templates.exists():
                copy_resource(templates)
        (stage / MARKER).write_text(json.dumps({"generator": "devflow-skills", "layout": layout}, indent=2) + "\n")
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)
    return len(skills)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--layout", choices=("flat", "layered"), required=True)
    args = parser.parse_args()
    try:
        count = export(args.source, args.output, args.layout)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    print(f"Exported {count} skills ({args.layout}) to {args.output}")


if __name__ == "__main__":
    main()
