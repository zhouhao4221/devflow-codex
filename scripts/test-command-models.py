#!/usr/bin/env python3
"""Exercise routing metadata, both entrypoints, and safe generation in fixtures."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("command_models", ROOT / "scripts/check-command-models.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CommandModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="devflow-command-models-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        for name in ("generate-codex-marketplace.py", "check-command-models.py"):
            shutil.copy2(ROOT / "scripts" / name, self.root / "scripts" / name)
        (self.root / "shared").mkdir()
        shutil.copy2(ROOT / "shared/command-model-routing.md", self.root / "shared/command-model-routing.md")
        selected = {"rd": ("release", "dev"), "pm": ("weekly",), "api": ("search",),
                    "diag": ("audit",), "uat": ("run",)}
        original = json.loads((ROOT / "skill-bindings.json").read_text())
        self.bindings = {"plugins": {}, "allSkills": {}}
        for plugin, names in selected.items():
            commands = {name: original["plugins"][plugin]["commands"][name] for name in names}
            self.bindings["plugins"][plugin] = {"commands": commands}
            self.bindings["allSkills"][plugin] = [data["primarySkill"] for data in commands.values()]
            for command, data in commands.items():
                self.write_skill(plugin, data["primarySkill"],
                                 f"[Route](../../shared/_command-models.md) `{plugin}:{command}`\n")
        self.bindings["allSkills"]["rd"].append("fixture-helper")
        self.write_skill("rd", "fixture-helper", "Use the caller's execution context.\n")
        self.save_bindings()
        self.generate()

    def write_skill(self, plugin, name, body):
        path = self.root / "plugins" / plugin / "skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname: {name}\ndescription: Fixture\n---\n\n# Fixture\n\n{body}")

    def save_bindings(self):
        (self.root / "skill-bindings.json").write_text(json.dumps(self.bindings))

    def generate(self, success=True):
        result = subprocess.run([sys.executable, str(self.root / "scripts/generate-codex-marketplace.py")],
                                cwd=self.root, capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in (self.root / "plugins").rglob("*") if p.is_file()}

    def test_command_tiers_and_helper_inheritance(self):
        expected = {("rd", "release"): "economy", ("rd", "dev"): "primary",
                    ("pm", "weekly"): "standard"}
        for (plugin, command), tier in expected.items():
            self.assertEqual(self.bindings["plugins"][plugin]["commands"][command]["executionTier"], tier)
        self.assertEqual(checker.check(self.root), [])

    def test_bad_tier_fails_before_touching_generated_artifacts(self):
        entry = self.bindings["plugins"]["uat"]["commands"]["run"]
        original = entry["executionTier"]
        before = self.snapshot()
        for value in (None, "typo", ["economy"], {"tier": "economy"}):
            with self.subTest(value=value):
                entry["executionTier"] = value
                self.save_bindings()
                self.assertTrue(checker.check(self.root))
                self.generate(success=False)
                self.assertEqual(self.snapshot(), before)
        del entry["executionTier"]
        self.save_bindings()
        self.assertTrue(checker.check(self.root))
        self.generate(success=False)
        self.assertEqual(self.snapshot(), before)
        entry["executionTier"] = original

    def test_route_change_requires_regeneration(self):
        self.bindings["plugins"]["rd"]["commands"]["release"]["executionTier"] = "standard"
        self.save_bindings()
        self.assertTrue(checker.check(self.root))
        self.generate()
        self.assertEqual(checker.check(self.root), [])

    def test_incomplete_plugin_bindings_do_not_leave_a_partial_generation(self):
        before = self.snapshot()
        del self.bindings["plugins"]["uat"]
        self.save_bindings()
        self.generate(success=False)
        self.assertEqual(self.snapshot(), before)

    def test_direct_skill_entrypoint_is_required(self):
        self.write_skill("rd", "release", "Execute release.\n")
        errors = checker.check(self.root)
        self.assertTrue(any("release/SKILL.md" in error for error in errors), errors)

    def test_missing_packaged_policy_and_command_are_reported(self):
        policy = self.root / "plugins/pm/shared/_command-models.md"
        command = self.root / "plugins/rd/commands/release.md"
        policy.unlink()
        command.unlink()
        errors = checker.check(self.root)
        self.assertTrue(any(str(policy) in error for error in errors), errors)
        self.assertTrue(any(str(command) in error for error in errors), errors)

    def test_model_fields_are_rejected_only_in_frontmatter(self):
        helper = self.root / "plugins/rd/skills/fixture-helper/SKILL.md"
        text = helper.read_text()
        helper.write_text(text + "\nExample body text:\nmodel: example\n")
        self.assertEqual(checker.check(self.root), [])
        helper.write_text(text.replace("description: Fixture", "description: Fixture\nmodel: example"))
        self.assertTrue(any("frontmatter" in error for error in checker.check(self.root)))

    def test_unreadable_or_invalid_bindings_report_errors(self):
        path = self.root / "skill-bindings.json"
        for content in ("{", "[]"):
            path.write_text(content)
            self.assertTrue(checker.check(self.root))
        path.unlink()
        self.assertTrue(checker.check(self.root))


if __name__ == "__main__":
    unittest.main()
