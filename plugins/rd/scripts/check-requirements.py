#!/usr/bin/env python3
"""check-requirements.py — 需求目录一致性守卫。

需求文档分别放在 `<requirementsDir>/active/`（进行中）与
`<requirementsDir>/completed/`（已完成），文件名以 `REQ-XXX-` 或
`QUICK-XXX-` 开头（XXX 为三位数字）。本脚本校验：

  1. `completed/` 内文档状态必须为「已完成」。
  2. `active/` 内文档状态不得为「已完成」。
  3. 元信息「状态」与「## 生命周期」复选框最后一个已勾项一致
     （「评审驳回」特例：最后已勾应为「待评审」，模板无对应复选框）。
  4. 编号（REQ-XXX / QUICK-XXX）在 active + completed 中唯一。
  5. 状态值必须是合法状态之一。

用法：check-requirements.py [--check] [--root ROOT]
  --check   只报告，发现任何问题退出码 1（与默认行为相同，保留以对齐 check-layout 用法）
  --root    项目根，默认当前工作目录（本文件随 rd 插件分发，下游项目在仓库根执行：
            python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check-requirements.py --check）
  readonly 仓库（requirementRole=readonly）无本地需求目录，直接跳过退出 0。
"""
import argparse
import json
import os
import re
import sys

VALID_STATUSES = ["草稿", "待评审", "评审通过", "评审驳回", "开发中", "测试中", "已完成"]
STATUS_RE = re.compile(r"^\| 状态 \| (.+?) \|")
CHECKBOX_RE = re.compile(r"^- \[([ x])\] (.+)$")
NUM_RE = re.compile(r"^(REQ|QUICK)-(\d+)(?:-|\.md$)")


def load_settings(root):
    settings = {}
    for name in ("settings.json", "settings.local.json"):
        path = os.path.join(root, ".devflow", name)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            settings.update(data)
    return settings


def resolve_requirements_root(root, settings):
    req_dir = settings.get("requirementsDir")
    if not isinstance(req_dir, str) or not req_dir.strip():
        req_dir = "docs/requirements"
    req_dir = req_dir.strip().rstrip("/")
    # 绝对路径原样使用，不能拼到 root 下
    return req_dir if os.path.isabs(req_dir) else os.path.join(root, req_dir)


def parse_status(lines):
    for line in lines:
        m = STATUS_RE.match(line)
        if m:
            value = m.group(1).strip()
            # 状态值全为中文，容忍存量文档里前缀的状态 emoji（如「🎉 已完成」）
            return re.sub(r"^[^一-鿿]+", "", value)
    return None


def parse_lifecycle(lines):
    """返回 [(checked, label), ...]；找不到「## 生命周期」块返回 None。"""
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## 生命周期":
            start = i + 1
            break
    if start is None:
        return None
    items = []
    for line in lines[start:]:
        if line.startswith("## ") or line.strip() == "---":
            break
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        checked = m.group(1) == "x"
        label = re.split(r"[（(]", m.group(2), maxsplit=1)[0].strip()
        # 与状态值同样容忍前缀 emoji（如模板里的「✅ 评审通过」）
        label = re.sub(r"^[^一-鿿]+", "", label)
        if label == "方案确认":
            continue
        items.append((checked, label))
    return items


def lifecycle_monotonic(items):
    """已勾格必须连续位于列表前段：出现未勾之后再勾即为不连续。"""
    seen_unchecked = False
    for checked, _ in items:
        if not checked:
            seen_unchecked = True
        elif seen_unchecked:
            return False
    return True


def documented_upgrade_gap(items, text):
    """升级中的 QUICK 可跳过 REQ 评审格，但必须明确记录未经评审。"""
    if "升级自 QUICK-" not in text or "未经评审" not in text:
        return False
    by_label = {label: checked for checked, label in items}
    return (
        by_label.get("草稿") is True
        and by_label.get("待评审") is False
        and by_label.get("评审通过") is False
        and by_label.get("开发中") is True
        and not (by_label.get("已完成") and not by_label.get("测试中"))
    )


def last_checked(items):
    checked = [label for is_checked, label in items if is_checked]
    return checked[-1] if checked else None


def check_file(relpath, location, text):
    """返回该文件的违规说明列表（不含相对路径前缀）。"""
    lines = text.splitlines()
    problems = []
    status = parse_status(lines)
    lifecycle = parse_lifecycle(lines)

    if status is None:
        problems.append("缺少状态行")
    if lifecycle is None:
        problems.append("缺少生命周期")

    if status is not None:
        if location == "completed" and status != "已完成":
            problems.append(f"completed/ 内状态应为「已完成」，实际为「{status}」")
        if location == "active" and status == "已完成":
            problems.append("active/ 内状态不应为「已完成」")
        if status not in VALID_STATUSES:
            problems.append(f"非法状态值「{status}」")

    if status is not None and lifecycle is not None:
        last = last_checked(lifecycle)
        expected = "待评审" if status == "评审驳回" else status
        if last != expected:
            problems.append(
                f"状态与生命周期不一致：状态「{status}」，"
                f"生命周期最后勾选「{last or '无'}」")
        if not lifecycle_monotonic(lifecycle) and not (
                relpath.split("/")[-1].startswith("REQ-")
                and documented_upgrade_gap(lifecycle, text)):
            problems.append("生命周期勾选不连续（未勾格之后又有已勾格）")

    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=os.getcwd())
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    settings = load_settings(root)
    if settings.get("requirementRole") == "readonly":
        print("readonly 仓库无本地需求目录，跳过")
        return 0
    req_root = resolve_requirements_root(root, settings)
    active_dir = os.path.join(req_root, "active")
    completed_dir = os.path.join(req_root, "completed")

    if not os.path.isdir(req_root) or (
            not os.path.isdir(active_dir) and not os.path.isdir(completed_dir)):
        print("未找到需求目录，跳过")
        return 0

    problems = []
    numbers = {}
    counts = {"active": 0, "completed": 0}

    for location, dirpath in (("active", active_dir), ("completed", completed_dir)):
        if not os.path.isdir(dirpath):
            continue
        for fn in sorted(os.listdir(dirpath)):
            if not fn.endswith(".md"):
                continue
            if not (fn.startswith("REQ-") or fn.startswith("QUICK-")):
                continue
            counts[location] += 1
            path = os.path.join(dirpath, fn)
            relpath = os.path.relpath(path, root)
            m = NUM_RE.match(fn)
            if m:
                key = f"{m.group(1)}-{int(m.group(2)):03d}"
                numbers.setdefault(key, []).append(relpath)
            else:
                problems.append(f"  - {relpath}: 文件名不符合 REQ-XXX-<slug>.md / QUICK-XXX-<slug>.md 格式")
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for problem in check_file(relpath, location, text):
                problems.append(f"  - {relpath}: {problem}")

    for key, paths in numbers.items():
        if len(paths) > 1:
            problems.append(f"  - {', '.join(paths)}: 编号 {key} 重复")

    if problems:
        print(f"[X] {len(problems)} 处需求文档不一致:")
        for line in problems:
            print(line)
        return 1

    print(f"[OK] 需求目录一致：active {counts['active']} 个，completed {counts['completed']} 个，"
          f"编号唯一，状态与目录 / 生命周期一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
