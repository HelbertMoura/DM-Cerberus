import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestMCPProtocol(unittest.TestCase):
    def test_subprocess_capture_is_candidate_only_and_no_promotion_tool(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            learning = root / "LEARNINGS.md"
            learning.write_text("# Untouched\n", encoding="utf-8")
            (root / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
            env = dict(os.environ, CERBERUS_ROOT=str(root), CERBERUS_ALLOWED_ROOTS=str(root), PYTHONPATH=str(repo))
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "cerberus_capture_learning", "arguments": {
                    "title": "Safe MCP", "content": "MCP capture must only create a candidate.",
                    "project_id": "test", "task_id": "TASK-MCP", "agent_role": "QA"}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "not_a_tool", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "cerberus_capture_learning", "arguments": {"title": "missing fields"}}},
            ]
            proc = subprocess.run(
                [sys.executable, "-m", "engine.mcp_server"], cwd=repo, env=env,
                input="".join(json.dumps(value) + "\n" for value in requests),
                text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            responses = [json.loads(line) for line in proc.stdout.splitlines()]
            self.assertEqual([1, 2, 3, 4, 5], [value["id"] for value in responses])
            tools = {tool["name"] for tool in responses[1]["result"]["tools"]}
            self.assertNotIn("cerberus_promote", tools)
            self.assertNotIn("cerberus_rebuild_index", tools)
            capture = json.loads(responses[2]["result"]["content"][0]["text"])
            self.assertEqual("CANDIDATE", capture["status"])
            self.assertEqual("# Untouched\n", learning.read_text(encoding="utf-8"))
            self.assertEqual(-32601, responses[3]["error"]["code"])
            self.assertEqual(-32602, responses[4]["error"]["code"])
            self.assertTrue((root / ".cerberus" / "inbox").is_dir())

    def test_jsonrpc_version_and_argument_types_are_strict(self) -> None:
        from engine.index import SQLiteMemoryIndex
        from engine.mcp_server import CerberusMCPServer
        from engine.retrieval import CerberusMemoryService

        with tempfile.TemporaryDirectory() as tmp:
            service = CerberusMemoryService(SQLiteMemoryIndex(Path(tmp) / "index.db"))
            server = CerberusMCPServer(service=service)
            for message in (
                {"id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "1.0", "id": 2, "method": "initialize", "params": {}},
            ):
                with self.subTest(message=message):
                    self.assertEqual(-32600, server.handle_message(message)["error"]["code"])

            response = server.handle_message({
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "cerberus_search_memory", "arguments": {"query": 123}},
            })
            self.assertEqual(-32602, response["error"]["code"])

    def test_mcp_root_must_be_inside_explicit_allowlist(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as allowed_tmp, tempfile.TemporaryDirectory() as outside_tmp:
            env = dict(
                os.environ, CERBERUS_ROOT=outside_tmp, CERBERUS_ALLOWED_ROOTS=allowed_tmp,
                PYTHONPATH=str(repo), PYTHONDONTWRITEBYTECODE="1",
            )
            proc = subprocess.run(
                [sys.executable, "-m", "engine.mcp_server"], cwd=repo, env=env,
                input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n",
                text=True, capture_output=True, timeout=10,
            )
            self.assertNotEqual(0, proc.returncode)
            self.assertEqual("", proc.stdout)
            self.assertIn("outside allowed roots", proc.stderr)

            cli_proc = subprocess.run(
                [sys.executable, "-m", "engine.cli", "mcp"], cwd=repo, env=env,
                input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n",
                text=True, capture_output=True, timeout=10,
            )
            self.assertNotEqual(0, cli_proc.returncode)
            self.assertFalse((Path(outside_tmp) / ".cerberus").exists())


if __name__ == "__main__":
    unittest.main()
