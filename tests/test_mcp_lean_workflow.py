"""Behavioral contracts for bounded MCP memory delivery."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestResponseBudget(unittest.TestCase):
    def test_previews_bound_escaped_json_without_cutting_identity(self):
        from engine.response_budget import bounded_response, json_text
        source = "wiki/" + "source" * 20 + ".md"
        record = {"memory_id": "memory-123", "source_path": source,
                  "title": "T" * 900, "snippet": '\x00"\\' * 3000,
                  "full_text": "not a preview", "search_mode": "lexical"}
        result = bounded_response([record] * 12, 2400)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(json_text(result)), 2400)
        previews = [entry for entry in result if "memory_id" in entry]
        self.assertTrue(previews)
        self.assertEqual(source, previews[0]["source_path"])
        self.assertEqual("memory-123", previews[0]["memory_id"])
        self.assertEqual("lexical", previews[0]["search_mode"])
        self.assertLessEqual(len(previews[0]["title"]), 160)
        self.assertLessEqual(len(previews[0]["snippet"]), 240)
        self.assertNotIn("full_text", previews[0])
        self.assertTrue(any(entry.get("truncated") for entry in result))
        json.loads(json_text(result))

    def test_nested_stats_and_project_shapes_are_bounded(self):
        from engine.response_budget import bounded_response, json_text
        for payload in ({"indexed_projects": ["project" * 100] * 200,
                         "types_breakdown": {"type" * 1000: 99}, "total_documents": 200},
                        {"project_id": "p", "items": [{"memory_id": str(i),
                         "source_path": "wiki/file.md", "snippet": "x" * 8000}
                         for i in range(20)]}):
            result = bounded_response(payload, 512)
            self.assertIsInstance(result, dict)
            self.assertLessEqual(len(json_text(result)), 512)
            self.assertTrue(result["truncated"])

    def test_redaction_precedes_preview_cut(self):
        from engine.response_budget import bounded_response
        secret = "password=" + "z" * 500
        result = bounded_response([{"memory_id": "m", "source_path": "wiki/f.md",
                                    "snippet": "a" * 220 + " " + secret}])
        self.assertNotIn("zzzzz", result[0]["snippet"])
        self.assertIn("[REDACTED]", result[0]["snippet"])

    def test_quoted_json_and_incomplete_private_keys_are_redacted_before_cut(self):
        from engine.response_budget import bounded_response
        for secret in ("api_key='secret words with spaces'", '{"token": "secret words with spaces"}',
                       "-----BEGIN PRIVATE KEY-----\nsecret words with spaces\n"):
            result = bounded_response([{"memory_id": "m", "source_path": "wiki/f.md",
                                        "snippet": "a" * 190 + " " + secret}])
            self.assertNotIn("secret words", json.dumps(result))
            self.assertIn("[REDACTED]", result[0]["snippet"])

    def test_escaped_quotes_are_redacted_in_previews_before_trimming(self):
        from engine.response_budget import bounded_response
        values = (json.dumps({"api_key": 'QA-SYNTHETIC-ONE "QA-SYNTHETIC-TWO"'}),
                  r"api_key='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO\''")
        for raw in values:
            with self.subTest(raw=raw):
                result = bounded_response([{"memory_id": "m", "source_path": "wiki/f.md",
                    "snippet": "a" * 150 + " " + raw + " " + "tail " * 100}])
                self.assertNotIn("QA-SYNTHETIC", json.dumps(result))
                self.assertIn("[REDACTED]", result[0]["snippet"])

    def test_escaped_quotes_are_redacted_in_queries_before_trimming(self):
        from engine.response_budget import query_text
        values = (json.dumps({"api_key": 'QA-SYNTHETIC-ONE "QA-SYNTHETIC-TWO"'}),
                  r"api_key='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO\''")
        for raw in values:
            with self.subTest(raw=raw):
                query = query_text("a" * 1350 + " " + raw + " " + "tail " * 200)
                self.assertLessEqual(len(query), 1500)
                self.assertNotIn("QA-SYNTHETIC", query)
                self.assertIn("[REDACTED]", query)

    def test_quoted_line_continuations_are_redacted_before_preview_and_query(self):
        from engine.response_budget import bounded_response, query_text, redact_text
        for quote in ('"', "'"):
            raw = "token=" + quote + "QA-SYNTHETIC-ONE" + chr(92) + "\nQA-SYNTHETIC-TWO" + quote
            with self.subTest(quote=quote):
                self.assertEqual("[REDACTED]", redact_text(raw))
                self.assertEqual("[REDACTED]", query_text(raw))
                preview = bounded_response([{"memory_id": "m", "source_path": "wiki/f.md", "snippet": raw}])
                self.assertNotIn("QA-SYNTHETIC", json.dumps(preview))

    def test_incomplete_quoted_secrets_consume_escaped_quotes_and_trailing_backslash(self):
        from engine.response_budget import bounded_response, query_text, redact_text
        values = (r'api_key="QA-SYNTHETIC-ONE \"QA-SYNTHETIC-TWO',
                  r'api_key="QA-SYNTHETIC-ONE \"QA-SYNTHETIC-TWO' + "\\",
                  r"api_key='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO",
                  r"api_key='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO" + "\\")
        for raw in values:
            with self.subTest(raw=raw):
                preview = bounded_response([{"memory_id": "m", "source_path": "wiki/f.md", "snippet": raw}])
                self.assertNotIn("QA-SYNTHETIC", json.dumps(preview))
                self.assertEqual("[REDACTED]", redact_text(raw))
                self.assertEqual("[REDACTED]", query_text(raw))


class TestLeanMCP(unittest.TestCase):
    def setUp(self):
        from engine.index import SQLiteMemoryIndex
        from engine.mcp_server import CerberusMCPServer
        from engine.retrieval import CerberusMemoryService
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for number in range(7):
            path = self.root / "projects/p/wiki" / f"memory-{number}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# Arquitetura memória {number}\n\n" +
                            "Arquitetura evidência memória " * 500, encoding="utf-8")
        self.index = SQLiteMemoryIndex(self.root / ".cerberus/index.db")
        self.index.index_roots([self.root])
        with patch.dict(os.environ, CERBERUS_ROOT=str(self.root), CERBERUS_ALLOWED_ROOTS=str(self.root)):
            self.server = CerberusMCPServer(CerberusMemoryService(self.index))

    def call(self, name, **args):
        return self.server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": args}})

    def data(self, name, **args):
        response = self.call(name, **args)
        self.assertNotIn("error", response, response)
        text = response["result"]["content"][0]["text"]
        self.assertLessEqual(len(text), args.get("max_chars", 1200))
        return json.loads(text)

    def test_default_previews_are_at_most_two_records_and_stateless(self):
        definitions = {tool["name"]: tool for tool in self.server.get_tool_definitions()}
        for name in ("cerberus_search_memory", "cerberus_get_decisions", "cerberus_get_learnings", "cerberus_get_project_context"):
            props = definitions[name]["inputSchema"]["properties"]
            self.assertEqual(2, props["limit"]["default"])
            self.assertEqual(1200, props["max_chars"]["default"])
        for _ in range(2):
            result = self.data("cerberus_search_memory", query="arquitetura memória", mode="lexical")
            entries = [entry for entry in result if "memory_id" in entry]
            self.assertGreater(len(entries), 0)
            self.assertLessEqual(len(entries), 2)
            self.assertTrue(all(len(entry["snippet"]) <= 240 for entry in entries))
            self.assertTrue(all(entry["search_mode"] == "lexical" for entry in entries))

    def test_progressive_session_previews_exhaust_to_empty_content(self):
        ids = []
        for _ in range(10):
            response = self.call("cerberus_search_memory", query="arquitetura memória", mode="lexical",
                                 session_id="conversation-one")
            if not response["result"]["content"]:
                break
            text = response["result"]["content"][0]["text"]
            self.assertLessEqual(len(text), 1200)
            result = json.loads(text)
            ids.extend(entry["memory_id"] for entry in result if "memory_id" in entry)
        self.assertEqual(7, len(ids))
        self.assertEqual(7, len(set(ids)))
        response = self.call("cerberus_search_memory", query="arquitetura memória", mode="lexical",
                             session_id="conversation-one")
        self.assertEqual([], response["result"]["content"])
        status = self.data("cerberus_context_status", session_id="conversation-one")
        self.assertNotIn("conversation-one", json.dumps(status))
        self.assertRegex(json.dumps(status), "cbr-[0-9a-f]{24}")

    def test_detail_is_indexed_paged_and_redacted_before_slicing(self):
        item = self.index.all_items()[0]
        text = "A" * 150 + " password=" + "z" * 900 + " tail " + "B" * 900
        with self.index._get_connection() as con:
            con.execute("UPDATE documents SET full_text=? WHERE memory_id=?", (text, item.memory_id))
            con.commit()
        page = self.data("cerberus_get_memory", memory_id=item.memory_id, offset=0,
                         max_chars=512, session_id="detail")
        self.assertEqual(0, page["offset"])
        self.assertGreater(page["next_offset"], 0)
        self.assertNotIn("zzzzz", json.dumps(page))
        duplicate = self.call("cerberus_get_memory", memory_id=item.memory_id, offset=0,
                              max_chars=512, session_id="detail")
        self.assertEqual([], duplicate["result"]["content"])
        next_page = self.data("cerberus_get_memory", memory_id=item.memory_id,
                              offset=page["next_offset"], max_chars=512, session_id="detail")
        self.assertNotIn("zzzzz", json.dumps(next_page))
        self.assertEqual(-32602, self.call("cerberus_get_memory", memory_id=item.memory_id,
                         source_path=str(self.root / "outside.md"))["error"]["code"])
        with self.index._get_connection() as con:
            con.execute("UPDATE documents SET status='deprecated' WHERE memory_id=?", (item.memory_id,))
            con.commit()
        self.assertIn("error", self.call("cerberus_get_memory", memory_id=item.memory_id))

    def test_escaped_quotes_are_redacted_in_indexed_detail_before_paging(self):
        item = self.index.all_items()[0]
        values = (json.dumps({"api_key": 'QA-SYNTHETIC-ONE "QA-SYNTHETIC-TWO"'}),
                  r"api_key='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO\''",
                  r'api_key="QA-SYNTHETIC-ONE \"QA-SYNTHETIC-TWO' + "\\",
                  r"api_key='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO" + "\\")
        for raw in values:
            with self.subTest(raw=raw):
                text = "prefix " * 30 + raw
                if not raw.endswith("\\"):
                    text += " " + "tail " * 200
                with self.index._get_connection() as con:
                    con.execute("UPDATE documents SET full_text=? WHERE memory_id=?", (text, item.memory_id))
                    con.commit()
                offset, pages = 0, []
                while offset is not None:
                    page = self.data("cerberus_get_memory", memory_id=item.memory_id,
                                     offset=offset, max_chars=512)
                    pages.append(page["full_text"])
                    offset = page["next_offset"]
                delivered = "".join(pages)
                self.assertNotIn("QA-SYNTHETIC", delivered)
                self.assertIn("[REDACTED]", delivered)

    def test_task_state_tools_are_short_and_reset_is_explicit(self):
        receipt = self.data("cerberus_save_task_state", project_id="p", task_id="TASK-1",
                            objective="Retomar memória", next_step="Verificar resultado")
        self.assertTrue(receipt["saved"])
        state = self.data("cerberus_get_task_state", project_id="p", task_id="TASK-1")
        self.assertEqual("Retomar memória", state["objective"])
        self.assertEqual(-32602, self.call("cerberus_context_status", session_id="s",
                         reset_reason="task_changed")["error"]["code"])

    def test_shared_quota_counts_exact_json_and_stops_before_overspending(self):
        from engine.session_delivery import context_status
        item = self.index.all_items()[0]
        offset, charged = 0, 0
        for _ in range(40):
            response = self.call("cerberus_get_memory", memory_id=item.memory_id,
                                 session_id="quota", offset=offset, max_chars=512)
            self.assertNotIn("error", response, response)
            blocks = response["result"]["content"]
            if not blocks:
                break
            text = blocks[0]["text"]
            charged += len(text)
            self.assertLessEqual(charged, 12000)
            offset = json.loads(text)["next_offset"]
            self.assertIsNotNone(offset)
        else:
            self.fail("Memory delivery did not stop at the conversation quota")
        self.assertEqual(charged, context_status(self.root, "quota")["used_chars"])
        self.data("cerberus_context_status", session_id="quota", reset_reason="compact")
        self.assertEqual(0, context_status(self.root, "quota")["used_chars"])
        self.assertTrue(self.call("cerberus_get_memory", memory_id=item.memory_id,
                                 session_id="quota")["result"]["content"])

    def test_persistence_failure_withholds_memory_and_rolls_back_delivery(self):
        from engine.session_delivery import context_status
        with patch("engine.session_delivery.atomic_json", side_effect=OSError("persistence failed")):
            response = self.call("cerberus_search_memory", query="arquitetura", mode="lexical",
                                 session_id="rollback")
        self.assertIn("error", response)
        self.assertNotIn("result", response)
        self.assertEqual(0, context_status(self.root, "rollback")["used_chars"])
        result = self.data("cerberus_search_memory", query="arquitetura", mode="lexical",
                           session_id="rollback")
        self.assertTrue(any("memory_id" in entry for entry in result))

    def test_changed_canonical_version_is_available_again(self):
        first = self.data("cerberus_search_memory", query="arquitetura", mode="lexical",
                          session_id="changed", limit=20, max_chars=6000)
        identity = next(entry["memory_id"] for entry in first if "memory_id" in entry)
        with self.index._get_connection() as con:
            con.execute("UPDATE documents SET full_text=full_text || ' NEW-VERSION' WHERE memory_id=?", (identity,))
            con.commit()
        second = self.data("cerberus_search_memory", query="arquitetura", mode="lexical",
                           session_id="changed", limit=20, max_chars=6000)
        self.assertIn(identity, [entry["memory_id"] for entry in second if "memory_id" in entry])

    def test_hook_then_mcp_shares_fingerprints_and_actual_charge(self):
        from engine.agent_hooks import handle_context
        from engine.session_delivery import context_status, delivery_transaction, memory_fingerprint
        output = handle_context({"hook_event_name": "UserPromptSubmit", "session_id": "shared",
            "cwd": str(self.root / "projects/p"), "prompt": "arquitetura memória"}, self.root)
        text = output["hookSpecificOutput"]["additionalContext"]
        with delivery_transaction(self.root, "shared") as transaction:
            before = set(transaction.seen)
        self.assertFalse(before)
        self.assertEqual(len(text), context_status(self.root, "shared")["used_chars"])
        response = self.call("cerberus_search_memory", query="arquitetura memória", project_id="p",
                             mode="lexical", session_id="shared")
        wire_text = response["result"]["content"][0]["text"]
        entries = [entry for entry in json.loads(wire_text) if "memory_id" in entry]
        items = self.index.get_items_by_ids([entry["memory_id"] for entry in entries])
        self.assertTrue(items)
        self.assertFalse(before & {memory_fingerprint(item) for item in items})
        self.assertEqual(len(text) + len(wire_text), context_status(self.root, "shared")["used_chars"])

    def test_mcp_then_hook_uses_same_public_token_and_does_not_repeat_sources(self):
        from engine.agent_hooks import handle_context
        from engine.session_delivery import context_status, session_token
        response = self.call("cerberus_get_context_pack", project_id="p", task_summary="arquitetura memória",
                             session_id="reverse", max_chars=6000)
        text = response["result"]["content"][0]["text"]
        output = handle_context({"hook_event_name": "UserPromptSubmit", "session_id": "reverse",
            "cwd": str(self.root / "projects/p"), "prompt": "arquitetura memória"}, self.root)
        hook_text = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn(session_token("reverse"), hook_text)
        self.assertNotIn("memory-", hook_text)
        self.assertEqual(len(text) + len(hook_text), context_status(self.root, "reverse")["used_chars"])

    def test_query_redaction_and_cap_apply_before_actual_search(self):
        search = self.server.service.search
        with patch.object(self.server.service, "search", wraps=search) as observed:
            self.data("cerberus_search_memory", query="arquitetura password=" + "z" * 2000 +
                      " " + "memória " * 2000, mode="lexical")
        query = observed.call_args.kwargs["query"]
        self.assertLessEqual(len(query), 1500)
        self.assertNotIn("zzzzz", query)

    def test_real_process_bounds_gigantic_controls_and_queries(self):
        repo = Path(__file__).resolve().parents[1]
        requests = [{"jsonrpc": "2.0", "id": number, "method": "tools/call", "params": {
            "name": name, "arguments": args}} for number, (name, args) in enumerate((
            ("cerberus_search_memory", {"query": "arquitetura " + '\x00"\\' * 9000,
                                         "mode": "lexical", "max_chars": 512}),
            ("cerberus_get_context_pack", {"project_id": "p", "task_summary": '\x00"\\' * 9000,
                                           "role": '\x00"\\' * 9000, "max_chars": 512}),
            ("cerberus_get_stats", {"max_chars": 512})), 1)]
        env = dict(os.environ, CERBERUS_ROOT=str(self.root), CERBERUS_ALLOWED_ROOTS=str(self.root),
                   PYTHONPATH=str(repo))
        proc = subprocess.run([sys.executable, "-m", "engine.mcp_server"], cwd=repo, env=env,
            input="".join(json.dumps(request) + "\n" for request in requests),
            text=True, encoding="utf-8", capture_output=True, timeout=20)
        self.assertEqual(0, proc.returncode, proc.stderr)
        responses = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual(3, len(responses))
        for response in responses:
            self.assertNotIn("error", response, response)
            for block in response["result"]["content"]:
                self.assertLessEqual(len(block["text"]), 512)
                json.loads(block["text"])


if __name__ == "__main__":
    unittest.main()
