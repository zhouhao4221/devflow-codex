#!/usr/bin/env python3
"""验证升级归档保留真实状态，同时仍由需求守卫检查。"""
import importlib.util
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


GUARD_PATH = Path(__file__).resolve().parents[1] / "plugins/rd/scripts/check-requirements.py"
spec = importlib.util.spec_from_file_location("check_requirements", GUARD_PATH)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class RequirementsGuardTests(unittest.TestCase):
    def test_completed_quick_uses_table_status(self):
        text = """# QUICK-001 示例
| 状态 | 已完成 |
| 完成时间 | 2026-09-16 |
## 生命周期
- [x] 草稿
- [x] 开发中
- [x] 测试中
- [x] 已完成
"""

        self.assertEqual(guard.check_file("completed/QUICK-001-example.md", "completed", text), [])
        self.assertTrue(guard.check_file("completed/QUICK-001-example.md", "completed",
                                         text.replace("| 状态 | 已完成 |", "| 状态 | 测试中 |\nstatus: 已完成")))

    def test_superseded_quick_retains_previous_status(self):
        text = """# QUICK-001 示例
| 状态 | 开发中 |
## 生命周期
- [x] 草稿
- [x] 开发中
- [ ] 测试中
- [ ] 已完成
## 开发记录
已升级为 REQ-002（2026-09-16）
"""

        self.assertEqual(guard.check_file("superseded/QUICK-001-example.md", "superseded", text), [])
        self.assertTrue(guard.check_file("completed/QUICK-001-example.md", "completed", text))
        self.assertTrue(guard.check_file("superseded/QUICK-001-example.md", "superseded",
                                         text.replace("已升级为 REQ-002", "等待升级")))

    def test_guard_scans_superseded_and_rejects_duplicate_number(self):
        text = """# QUICK-001 示例
| 状态 | 草稿 |
## 生命周期
- [x] 草稿
- [ ] 开发中
- [ ] 测试中
- [ ] 已完成
## 开发记录
已升级为 REQ-002（2026-09-16）
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            req_root = Path(temp_dir) / "docs/requirements"
            archive = req_root / "superseded"
            archive.mkdir(parents=True)
            (archive / "QUICK-001-example.md").write_text(text, encoding="utf-8")
            with patch("sys.argv", ["check-requirements.py", "--root", temp_dir]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(guard.main(), 0)
            self.assertIn("superseded 1 个", output.getvalue())

            active = req_root / "active"
            active.mkdir()
            (active / "QUICK-001-duplicate.md").write_text(text, encoding="utf-8")
            with patch("sys.argv", ["check-requirements.py", "--root", temp_dir]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(guard.main(), 1)
            self.assertIn("编号 QUICK-001 重复", output.getvalue())


if __name__ == "__main__":
    unittest.main()
