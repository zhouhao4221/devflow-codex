#!/usr/bin/env python3
"""Exercise resource portability and safe replacement for both adapter layouts."""

from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load("exporter", "export-skills.py")
checker = load("checker", "check-layout.py")


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="devflow-export-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source with spaces"
        self.plugin = self.source / "plugins" / "rd"
        self.write("skills/do/SKILL.md", "---\nname: do\ndescription: Test\n---\n\n[Verify](../../shared/verify.md#steps)\n")
        self.write("skills/do/agents/openai.yaml", 'interface:\n  default_prompt: "使用 $do 处理"\n')
        self.write("skills/test-new/SKILL.md", "---\nname: test-new\ndescription: Test\n---\n\nTests\n")
        self.write("shared/verify.md", "# Steps\n[Role](roles/test%20runner.md)\n[Tests](../skills/test-new/SKILL.md)\n")
        self.write("shared/roles/test runner.md", "Keep failing assertions.\n[Verify](../verify.md)\n")
        self.write("templates/example.md", "[Generated destination](./active/)\n")
        self.write("skills/do/scripts/check.sh", "#!/bin/sh\nexit 0\n")
        (self.plugin / "skills/do/scripts/check.sh").chmod(0o755)

    def write(self, rel, text):
        path = self.plugin / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_transitive_resources_and_metadata(self):
        for layout in ("flat", "layered"):
            out = self.base / layout
            self.assertEqual(exporter.export(self.source, out, layout), 2)
            self.assertEqual(checker.check(out), [])
            roles = list(out.rglob("test runner.md"))
            self.assertTrue(roles)
            self.assertTrue(all("Keep failing assertions." in p.read_text() for p in roles))
            skill = out / ("rd-do" if layout == "flat" else "plugins/rd/skills/do")
            expected = "rd-do" if layout == "flat" else "do"
            self.assertIn(f"name: {expected}\n", (skill / "SKILL.md").read_text())
            self.assertIn(f"${expected} ", (skill / "agents/openai.yaml").read_text())
            self.assertTrue((skill / "scripts/check.sh").stat().st_mode & 0o111)
            self.assertTrue(list(out.rglob("templates/example.md")))

    def test_refuses_unowned_output_and_source(self):
        out = self.base / "user files"
        out.mkdir()
        keep = out / "notes.txt"
        keep.write_text("keep")
        with self.assertRaises(ValueError):
            exporter.export(self.source, out, "flat")
        self.assertEqual(keep.read_text(), "keep")
        with self.assertRaises(ValueError):
            exporter.export(self.source, self.source, "flat")

    def test_failed_refresh_preserves_previous_export(self):
        out = self.base / "bundle"
        exporter.export(self.source, out, "flat")
        previous = (out / "rd-do/SKILL.md").read_text()
        self.write("shared/verify.md", "[Missing](missing.md)\n")
        self.assertTrue(checker.check(self.source / "plugins"))
        with self.assertRaises(ValueError):
            exporter.export(self.source, out, "flat")
        self.assertEqual((out / "rd-do/SKILL.md").read_text(), previous)

    def test_refresh_removes_stale_export_only(self):
        out = self.base / "bundle"
        exporter.export(self.source, out, "flat")
        (out / "stale.txt").write_text("old generated content")
        exporter.export(self.source, out, "flat")
        self.assertFalse((out / "stale.txt").exists())
        self.assertTrue((self.plugin / "skills/do/SKILL.md").exists())

    def test_rejects_resources_outside_plugin(self):
        external = self.base / "private.txt"
        external.write_text("private")
        (self.plugin / "shared/external.md").symlink_to(external)
        self.write("shared/verify.md", "[Outside](external.md)\n")
        with self.assertRaises(ValueError):
            exporter.export(self.source, self.base / "bundle", "flat")

    def test_real_repository_bundles(self):
        expected = len(list((ROOT / "plugins").glob("*/skills/*/SKILL.md")))
        for layout in ("flat", "layered"):
            out = self.base / f"real-{layout}"
            self.assertEqual(exporter.export(ROOT, out, layout), expected)
            self.assertEqual(len(list(out.rglob("SKILL.md"))), expected)
            self.assertEqual(checker.check(out), [])
            self.assertTrue(list(out.rglob("swagger-parser.py")))
            self.assertTrue(list(out.rglob("check-requirements.py")))


if __name__ == "__main__":
    unittest.main()
