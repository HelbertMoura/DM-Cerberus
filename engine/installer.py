"""
Cerberus Memory Intelligence - Multi-Agent Automated MCP & Environment Installer
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import os
import sys
import json
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class CerberusEnvironmentInstaller:
    def __init__(self, cerebro_root: Optional[Path] = None, user_home: Optional[Path] = None):
        self.cerebro_root = Path(cerebro_root or "C:/DevManiacs/DM-Cerebro").resolve()
        self.user_home = Path(user_home or os.path.expanduser("~")).resolve()
        self.python_exe = sys.executable

        self.mcp_config_entry = {
            "command": self.python_exe,
            "args": ["-m", "engine.cli", "mcp"],
            "cwd": str(self.cerebro_root)
        }

    def backup_file(self, file_path: Path):
        if file_path.exists():
            bak_path = file_path.with_suffix(file_path.suffix + ".bak-cerberus")
            if not bak_path.exists():
                shutil.copy2(file_path, bak_path)

    def install_claude_code(self) -> Dict[str, Any]:
        """
        Configures Claude Code in ~/.claude/settings.json
        """
        claude_dir = self.user_home / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        settings_file = claude_dir / "settings.json"

        settings = {}
        if settings_file.exists():
            try:
                settings = json.loads(settings_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON config; refusing to overwrite: {settings_file}") from exc

        self.backup_file(settings_file)

        if "mcpServers" not in settings:
            settings["mcpServers"] = {}

        settings["mcpServers"]["cerberus-memory"] = self.mcp_config_entry
        settings_file.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")

        return {"target": "Claude Code", "status": "INSTALLED", "file": str(settings_file)}

    def install_cursor(self) -> Dict[str, Any]:
        """
        Configures Cursor in ~/.cursor/mcp.json
        """
        cursor_dir = self.user_home / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        mcp_file = cursor_dir / "mcp.json"

        config = {}
        if mcp_file.exists():
            try:
                config = json.loads(mcp_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON config; refusing to overwrite: {mcp_file}") from exc

        self.backup_file(mcp_file)

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"]["cerberus-memory"] = self.mcp_config_entry
        mcp_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

        return {"target": "Cursor IDE", "status": "INSTALLED", "file": str(mcp_file)}

    def install_codex(self) -> Dict[str, Any]:
        """
        Configures OpenAI Codex in ~/.codex/config.toml
        """
        codex_dir = self.user_home / ".codex"
        codex_dir.mkdir(parents=True, exist_ok=True)
        config_file = codex_dir / "config.toml"

        content = ""
        if config_file.exists():
            content = config_file.read_text(encoding="utf-8", errors="replace")

        self.backup_file(config_file)

        # Check if already installed
        if '[mcp_servers."cerberus-memory"]' not in content:
            toml_block = f"""
[mcp_servers."cerberus-memory"]
command = "{self.python_exe.replace('\\', '\\\\')}"
args = ["-m", "engine.cli", "mcp"]
cwd = "{str(self.cerebro_root).replace('\\', '\\\\')}"
"""
            config_file.write_text(content + "\n" + toml_block, encoding="utf-8")
            status = "INSTALLED"
        else:
            status = "ALREADY_PRESENT"

        return {"target": "Codex CLI", "status": status, "file": str(config_file)}

    def install_global_cli(self) -> Dict[str, Any]:
        r"""
        Creates global .cmd and .ps1 wrappers in ~/.local/bin and C:\DevManiacs\DM-Cerebro\bin
        """
        local_bin = self.user_home / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)

        cerebro_bin = self.cerebro_root / "bin"
        cerebro_bin.mkdir(parents=True, exist_ok=True)

        cmd_content = f"""@echo off
pushd "{self.cerebro_root}"
"{self.python_exe}" -m engine.cli %*
set "CERBERUS_EXIT=%ERRORLEVEL%"
popd
exit /b %CERBERUS_EXIT%
"""
        ps1_content = f"""Push-Location -LiteralPath "{str(self.cerebro_root)}"
try {{ & "{self.python_exe}" -m engine.cli @args; exit $LASTEXITCODE }} finally {{ Pop-Location }}
"""

        for b_dir in [local_bin, cerebro_bin]:
            (b_dir / "cerberus.cmd").write_text(cmd_content, encoding="utf-8")
            (b_dir / "cerberus.ps1").write_text(ps1_content, encoding="utf-8")
            (b_dir / "dm-cerebro.cmd").write_text(cmd_content, encoding="utf-8")

        return {
            "target": "Global CLI Wrappers",
            "status": "INSTALLED",
            "locations": [str(local_bin), str(cerebro_bin)]
        }

    def install_codex_hooks(self, dry_run: bool = False,
                            codex_home: Optional[Path] = None) -> Dict[str, Any]:
        """Merge owned hooks only; preserve unrelated handlers and all trust state."""
        from engine.agent_hooks import atomic_json, CONTEXT_EVENTS, CAPTURE_EVENTS

        directory = Path(codex_home) if codex_home else self.user_home / ".codex"
        target = directory / "hooks.json"
        document = {}
        if target.exists():
            try:
                document = json.loads(target.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as exc:
                raise ValueError(f"Invalid hooks config; refusing to overwrite: {target}") from exc
        if not isinstance(document, dict) or not isinstance(document.get("hooks", {}), dict):
            raise ValueError(f"Invalid hooks object; refusing to overwrite: {target}")
        hooks = document.setdefault("hooks", {})
        for groups in hooks.values():
            if not isinstance(groups, list) or any(not isinstance(group, dict) or
                    not isinstance(group.get("hooks"), list) or
                    any(not isinstance(handler, dict) for handler in group["hooks"]) for group in groups):
                raise ValueError(f"Invalid hook groups; refusing to overwrite: {target}")
        before = json.dumps(document, sort_keys=True)
        sources = []
        for event in sorted(CONTEXT_EVENTS | CAPTURE_EVENTS):
            context_event = event in CONTEXT_EVENTS
            script = self.cerebro_root / "hooks" / ("codex_context.py" if context_event else "claude_session_capture.py")
            sources.append(script)
            command = f'"{self.python_exe}" "{script}"'
            # PowerShell needs its invocation operator for a quoted executable.
            # Literal quotes also keep $, backticks and apostrophes in paths inert.
            windows_command = "& " + " ".join("'" + str(path).replace("'", "''") + "'"
                                                for path in (self.python_exe, script))
            if not context_event:
                command += " --agent CODEX --quiet"
                windows_command += " --agent CODEX --quiet"
            handler = {"type": "command", "command": command, "commandWindows": windows_command,
                       "timeout": 10 if context_event else 3}
            if context_event:
                handler.update({"statusMessage": "Consultando o DM-Cerebro", "additionalContextLimit": 2000})
            owned = []
            normalized_script = str(script).replace("\\", "/").casefold()
            for group in hooks.setdefault(event, []):
                for existing in group["hooks"]:
                    normalized_command = str(existing.get("command", "")).replace("\\", "/").casefold()
                    # Exact quoted path, not a substring of a different installation.
                    if f'"{normalized_script}"' in normalized_command and existing.get("type") == "command":
                        owned.append(existing)
            if owned:
                for existing in owned:
                    existing.update(handler)
            else:
                hooks[event].append({"matcher": "", "hooks": [handler]})
        result = {"target": "Codex hooks", "file": str(target),
                  "events": sorted(CONTEXT_EVENTS | CAPTURE_EVENTS),
                  "trust": "Review new or changed definitions in Codex /hooks; no trust is granted by this installer."}
        if dry_run:
            return {**result, "status": "PREVIEW"}
        if any(not source.is_file() for source in sources):
            raise ValueError("Hook scripts are missing from this DM-Cerebro installation")
        if target.exists() and before == json.dumps(document, sort_keys=True):
            return {**result, "status": "ALREADY_PRESENT"}
        if target.exists():
            backup = target.with_name(f"{target.name}.bak-cerberus-hooks-{time.time_ns()}.bak")
            shutil.copy2(target, backup)
            result["backup"] = str(backup)
        atomic_json(target, document)
        return {**result, "status": "INSTALLED"}

    def install_all(self) -> List[Dict[str, Any]]:
        results = []
        results.append(self.install_claude_code())
        results.append(self.install_codex())
        results.append(self.install_cursor())
        results.append(self.install_global_cli())
        return results


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    installer = CerberusEnvironmentInstaller()
    print("🚀 Instalando Cerberus Memory Engine em todos os Agentes e IDEs...")
    results = installer.install_all()
    for res in results:
        print(f"✅ {res['target']}: {res['status']} ({res.get('file') or res.get('locations')})")
    print("\n🎉 Instalação concluída com sucesso! Todos os agentes agora possuem acesso direto ao Cerberus MCP.")


if __name__ == "__main__":
    main()
