#!/usr/bin/env python3
"""Extract description from a SKILL.md YAML frontmatter."""
import re
import sys

def get_description(filepath):
    with open(filepath) as f:
        content = f.read()
    m = re.search(r'^description:\s*\|?\s*\n\s*(.+?)(\n\S|\n\n|\n---|\Z)', content, re.MULTILINE | re.DOTALL)
    if m:
        d = m.group(1).strip()
        d = re.sub(r'\n\s+', ' ', d)
    else:
        m2 = re.search(r'^description:\s*(.+)', content, re.MULTILINE)
        d = m2.group(1).strip() if m2 else ''
    d = d.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')[:300]
    return d

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(get_description(sys.argv[1]))
