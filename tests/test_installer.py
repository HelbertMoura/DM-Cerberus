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


if __name__ == "__main__":
    unittest.main()
