import json
import tempfile
import unittest
from pathlib import Path

from engine.installer import CerberusEnvironmentInstaller


class TestInstaller(unittest.TestCase):
    def test_json_install_is_idempotent_and_backup_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            home = base / "home"
            root = base / "DM Cerebro"
            home.mkdir()
            root.mkdir()
            settings = home / ".claude" / "settings.json"
            settings.parent.mkdir()
            original = '{"theme":"dark","mcpServers":{"other":{"command":"x"}}}'
            settings.write_text(original, encoding="utf-8")
            installer = CerberusEnvironmentInstaller(cerebro_root=root, user_home=home)
            installer.install_claude_code()
            first = settings.read_bytes()
            installer.install_claude_code()
            self.assertEqual(first, settings.read_bytes())
            self.assertEqual(original, settings.with_suffix(".json.bak-cerberus").read_text(encoding="utf-8"))
            config = json.loads(settings.read_text(encoding="utf-8"))
            self.assertIn("other", config["mcpServers"])

    def test_invalid_json_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            home = base / "home"
            root = base / "root"
            (home / ".claude").mkdir(parents=True)
            root.mkdir()
            settings = home / ".claude" / "settings.json"
            settings.write_text("{broken", encoding="utf-8")
            installer = CerberusEnvironmentInstaller(cerebro_root=root, user_home=home)
            with self.assertRaises(ValueError):
                installer.install_claude_code()
            self.assertEqual("{broken", settings.read_text(encoding="utf-8"))

    def test_codex_hooks_preserve_other_handlers_and_never_write_trust(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            home, root = base / "home", base / "DM Cerebro"
            directory = home / ".codex"
            directory.mkdir(parents=True)
            root.mkdir()
            (root / "hooks").mkdir()
            for script in ("codex_context.py", "claude_session_capture.py"):
                (root / "hooks" / script).write_text("# isolated installer fixture\n", encoding="utf-8")
            hooks = directory / "hooks.json"
            other = {"type": "command", "command": "other-hook", "timeout": 42}
            hooks.write_text(json.dumps({"description": "my hooks", "hooks": {
                "Stop": [{"hooks": [other]}]}}), encoding="utf-8")
            config = directory / "config.toml"
            config.write_text('[hooks.state.example]\ntrusted_hash = "unchanged"\n', encoding="utf-8")
            original_config = config.read_bytes()
            installer = CerberusEnvironmentInstaller(root, home)
            self.assertTrue(hasattr(installer, "install_codex_hooks"), "reproducible Codex hooks installer is missing")
            installer.install_codex_hooks()
            first = hooks.read_bytes()
            result = installer.install_codex_hooks()
            self.assertEqual(first, hooks.read_bytes())
            self.assertEqual(original_config, config.read_bytes())
            self.assertEqual("ALREADY_PRESENT", result["status"])
            document = json.loads(first)
            self.assertEqual(other, document["hooks"]["Stop"][0]["hooks"][0])
            self.assertEqual("my hooks", document["description"])
            for event in ("SessionStart", "UserPromptSubmit", "Stop", "PreCompact", "SessionEnd"):
                owned = [handler for group in document["hooks"][event] for handler in group["hooks"]
                    if str(root) in handler["command"]]
                self.assertEqual(1, len(owned), event)
                script = root / "hooks" / ("codex_context.py" if event in ("SessionStart", "UserPromptSubmit")
                                           else "claude_session_capture.py")
                expected = "& " + " ".join("'" + str(path).replace("'", "''") + "'"
                                           for path in (installer.python_exe, script))
                if event not in ("SessionStart", "UserPromptSubmit"):
                    expected += " --agent CODEX --quiet"
                self.assertEqual(expected, owned[0]["commandWindows"])
            self.assertEqual(3, document["hooks"]["SessionEnd"][0]["hooks"][0]["timeout"])

    def test_codex_hook_preview_does_not_create_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            installer = CerberusEnvironmentInstaller(base / "root", base / "home")
            self.assertTrue(hasattr(installer, "install_codex_hooks"))
            result = installer.install_codex_hooks(dry_run=True)
            self.assertEqual("PREVIEW", result["status"])
            self.assertFalse((base / "home").exists())

    def test_codex_hook_invalid_config_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            folder = base / "home" / ".codex"
            folder.mkdir(parents=True)
            path = folder / "hooks.json"
            installer = CerberusEnvironmentInstaller(base / "root", base / "home")
            self.assertTrue(hasattr(installer, "install_codex_hooks"))
            for original in ('{broken', '{"hooks":{"Stop":{}}}'):
                path.write_text(original, encoding="utf-8")
                with self.assertRaises(ValueError):
                    installer.install_codex_hooks()
                self.assertEqual(original, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
