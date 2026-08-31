"""
Cerberus Memory Intelligence - Inspector Web UI / REST API Tests
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P3: tests for the localhost management plane.
"""

import json
import socket
import tempfile
import threading
import time
import unittest
import urllib.parse
import urllib.request
from contextlib import contextmanager
from http.client import HTTPConnection
from pathlib import Path

from engine.capture import AutoCaptureEngine
from engine.index import SQLiteMemoryIndex
from engine.retrieval import CerberusMemoryService
from engine.server import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    UI_HTML,
    _is_safe_bind_host,
    make_server,
)


def _pick_free_port() -> int:
    """Bind a socket to port 0 to let the OS pick a free port, then release."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((DEFAULT_HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


class _ServerHandle:
    """Helper that boots the server in a background thread and shuts it down."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = 0,
                 application_root: Path = None,
                 service: CerberusMemoryService = None,
                 capture_engine: AutoCaptureEngine = None,
                 auth_disabled: bool = True) -> None:
        if port == 0:
            port = _pick_free_port()
        self.host = host
        self.port = port
        self.server = make_server(
            host=host, port=port,
            application_root=application_root,
            service=service,
            capture_engine=capture_engine,
            auth_disabled=auth_disabled,
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            name=f"cerberus-test-server-{port}",
            daemon=True,
        )

    def __enter__(self):
        self.thread.start()
        # wait for the socket to accept connections
        for _ in range(50):
            try:
                with socket.create_connection((self.host, self.port), timeout=0.5):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            raise RuntimeError("Server did not become ready in time")
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.server.shutdown()
            self.server.server_close()
        finally:
            self.thread.join(timeout=2.0)

    def url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"

    def request(self, method: str, path: str, body: dict = None,
                headers: dict = None):
        url = self.url(path)
        data = None
        h = {"Accept": "application/json"}
        if headers:
            h.update(headers)
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, resp.read().decode("utf-8"), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8"), dict(e.headers or {})


def _build_corpus(root: Path) -> None:
    """Mirror the helper from test_orchestrator_integration.py."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "LEARNINGS.md").write_text("# Learnings\n", encoding="utf-8")
    (root / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
    ch_dir = root / "projects" / "canteirohub"
    ch_dir.mkdir(parents=True)
    (ch_dir / "learnings.md").write_text(
        "# Lições CanteiroHUB\n\nUse AES-256-GCM com HKDF para o cofre SEFAZ A1.\n",
        encoding="utf-8",
    )
    bio_dir = root / "projects" / "biolar"
    bio_dir.mkdir(parents=True)
    (bio_dir / "decisions.md").write_text(
        "# Decisões Biolar\n\nTaxonomia controlada ADR-001.\n",
        encoding="utf-8",
    )


def _build_state(tmp: Path):
    root = tmp / "cerebro"
    _build_corpus(root)
    service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
    capture_engine = AutoCaptureEngine(service=service, cerebro_root=root)
    return root, service, capture_engine


# ============================================================================
# TestServerLifecycle
# ============================================================================
class TestServerLifecycle(unittest.TestCase):
    def test_make_server_rejects_non_loopback_host_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError) as ctx:
                make_server(host="0.0.0.0", port=_pick_free_port(),
                             application_root=Path(tmp))
            self.assertIn("Refusing to bind", str(ctx.exception))

    def test_make_server_accepts_loopback_hosts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # Windows resolves "localhost" / "::1" via DNS at bind time;
            # 127.0.0.1 is the universally safe path. We exercise the
            # guard logic directly for "localhost" and "::1" instead.
            for host in ("127.0.0.1",):
                port = _pick_free_port()
                server = make_server(host=host, port=port,
                                      application_root=Path(tmp))
                self.assertEqual(port, server.server_address[1])
                server.server_close()
            # The guard accepts "localhost" and "::1" by name without
            # trying to bind.
            self.assertTrue(_is_safe_bind_host("localhost"))
            self.assertTrue(_is_safe_bind_host("::1"))
            self.assertFalse(_is_safe_bind_host("0.0.0.0"))
            self.assertFalse(_is_safe_bind_host("192.168.0.1"))

    def test_make_server_lan_override(self) -> None:
        import os
        old = os.environ.get("CERBERUS_UI_ALLOW_LAN")
        os.environ["CERBERUS_UI_ALLOW_LAN"] = "1"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                # Just make sure it doesn't raise ValueError now
                server = make_server(host="0.0.0.0", port=_pick_free_port(),
                                      application_root=Path(tmp))
                server.server_close()
        finally:
            if old is None:
                os.environ.pop("CERBERUS_UI_ALLOW_LAN", None)
            else:
                os.environ["CERBERUS_UI_ALLOW_LAN"] = old

    def test_server_starts_and_serves_root_via_helper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root, service, capture_engine = _build_state(tmp_path)
            with _ServerHandle(application_root=root,
                                service=service,
                                capture_engine=capture_engine) as srv:
                status, body, headers = srv.request("GET", "/")
            self.assertEqual(200, status)
            self.assertIn("text/html", headers.get("Content-Type", ""))
            self.assertIn("Cerberus Inspector", body)

    def test_ui_html_contains_required_affordances(self) -> None:
        # Static checks on the served HTML — verifies the spec.
        self.assertIn("min-height: 44px", UI_HTML)
        self.assertIn("#0F172A", UI_HTML)
        self.assertIn("#1E40AF", UI_HTML)
        # No emoji in UI copy (defensive: prevent the banned glyph set).
        banned = ["🎯", "🚀", "✅", "❌", "⚠", "🛡", "🔒", "📦"]
        for glyph in banned:
            self.assertNotIn(glyph, UI_HTML)

    def test_server_returns_404_for_unknown_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root, service, capture_engine = _build_state(tmp_path)
            with _ServerHandle(application_root=root,
                                service=service,
                                capture_engine=capture_engine) as srv:
                status, body, _ = srv.request("GET", "/no/such/route")
            self.assertEqual(404, status)
            payload = json.loads(body)
            self.assertEqual(404, payload["status"])


# ============================================================================
# TestStatusEndpoint
# ============================================================================
class TestStatusEndpoint(unittest.TestCase):
    def test_status_returns_metrics_and_projects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root, service, capture_engine = _build_state(tmp_path)
            # Index the corpus so /api/status reflects real numbers.
            capture_engine.capture_learning(
                title="Boot learning",
                content="Conteudo de boot para teste do status.",
                project_id="canteirohub",
                task_id="TASK-BOOT",
                agent_role="QA",
            )
            with _ServerHandle(application_root=root,
                                service=service,
                                capture_engine=capture_engine) as srv:
                status, body, _ = srv.request("GET", "/api/status")
            self.assertEqual(200, status)
            data = json.loads(body)
            self.assertEqual(DEFAULT_HOST, data["bind_host"])
            self.assertIn("files", data)
            self.assertIn("documents", data)
            self.assertIn("inbox_count", data)
            self.assertIn("fts5", data)
            self.assertIsInstance(data["projects"], list)
            self.assertIn("canteirohub", data["projects"])
            self.assertIn("_global", data["projects"])
            self.assertIn("_shared", data["projects"])
            self.assertGreaterEqual(data["inbox_count"], 1)
            self.assertTrue(data["fts5"])


# ============================================================================
# TestInboxEndpoints
# ============================================================================
class TestInboxEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root, self.service, self.capture_engine = _build_state(self.tmp)
        self.capture_engine.capture_learning(
            title="SEFAZ A1 learning",
            content="Cofre SEFAZ usa AES-256-GCM com HKDF para derivar chaves por tenant.",
            project_id="canteirohub",
            task_id="TASK-INBOX-1",
            agent_role="CODEX",
        )
        self.capture_engine.capture_learning(
            title="Quarantined learning",
            content="Token leak: client_secret=topsecretvalue9876 sempre ofuscar antes de indexar.",
            project_id="canteirohub",
            task_id="TASK-INBOX-2",
            agent_role="QA",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _open(self):
        return _ServerHandle(application_root=self.root,
                             service=self.service,
                             capture_engine=self.capture_engine)

    def test_inbox_list_returns_all_candidates(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/inbox")
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertGreaterEqual(payload["count"], 2)
        titles = [c["title"] for c in payload["candidates"]]
        self.assertIn("SEFAZ A1 learning", titles)
        self.assertIn("Quarantined learning", titles)

    def test_inbox_list_filters_by_status(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/inbox?status=CANDIDATE")
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertGreaterEqual(payload["count"], 1)
        for c in payload["candidates"]:
            self.assertEqual("CANDIDATE", c["status"])

        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/inbox?status=QUARANTINED")
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertGreaterEqual(payload["count"], 1)
        for c in payload["candidates"]:
            self.assertEqual("QUARANTINED", c["status"])

    def test_inbox_detail_for_verified_candidate_includes_diff(self) -> None:
        # Verify the first candidate and fetch detail.
        candidates = list(self.capture_engine.store.list())
        target = next(c for c in candidates if c.status.value == "CANDIDATE")
        self.capture_engine.verify(target.candidate_id)
        with self._open() as srv:
            status, body, _ = srv.request(
                "GET", f"/api/inbox/{target.candidate_id}"
            )
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertEqual(target.candidate_id, payload["candidate_id"])
        self.assertEqual("VERIFIED", payload["status"])
        # Diff preview present and includes provenance
        self.assertIn("diff", payload)
        self.assertIn("Task", payload["diff"])
        self.assertIn(target.task_id, payload["diff"])

    def test_inbox_detail_404_for_unknown_candidate(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/inbox/broken")
        self.assertEqual(404, status)
        payload = json.loads(body)
        self.assertIn("Candidate store entry is invalid", payload["error"])

    def test_inbox_promote_endpoint_marks_canonical(self) -> None:
        candidates = list(self.capture_engine.store.list())
        target = next(c for c in candidates if c.status.value == "CANDIDATE")
        self.capture_engine.verify(target.candidate_id)
        with self._open() as srv:
            status, body, _ = srv.request(
                "POST", f"/api/inbox/{target.candidate_id}/promote"
            )
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertEqual("CANONICAL", payload["status"])
        # LEARNINGS.md updated
        learnings = (self.root / "LEARNINGS.md").read_text(encoding="utf-8")
        self.assertIn(target.title, learnings)
        self.assertIn(target.task_id, learnings)

    def test_inbox_promote_rejects_candidate_candidate(self) -> None:
        candidates = list(self.capture_engine.store.list())
        target = next(c for c in candidates if c.status.value == "CANDIDATE")
        # Don't verify first.
        with self._open() as srv:
            status, body, _ = srv.request(
                "POST", f"/api/inbox/{target.candidate_id}/promote"
            )
        self.assertEqual(409, status)
        payload = json.loads(body)
        self.assertIn("VERIFIED", payload["error"])

    def test_inbox_promote_rejects_quarantined(self) -> None:
        candidates = list(self.capture_engine.store.list())
        target = next(c for c in candidates if c.status.value == "QUARANTINED")
        with self._open() as srv:
            status, body, _ = srv.request(
                "POST", f"/api/inbox/{target.candidate_id}/promote"
            )
        self.assertEqual(409, status)

    def test_inbox_reject_endpoint(self) -> None:
        candidates = list(self.capture_engine.store.list())
        target = next(c for c in candidates if c.status.value == "CANDIDATE")
        with self._open() as srv:
            status, body, _ = srv.request(
                "POST", f"/api/inbox/{target.candidate_id}/reject"
            )
        self.assertEqual(200, status)
        self.assertEqual("REJECTED", self.capture_engine.store.get(
            target.candidate_id).status.value)

    def test_inbox_verify_endpoint(self) -> None:
        candidates = list(self.capture_engine.store.list())
        target = next(c for c in candidates if c.status.value == "CANDIDATE")
        with self._open() as srv:
            status, body, _ = srv.request(
                "POST", f"/api/inbox/{target.candidate_id}/verify"
            )
        self.assertEqual(200, status)
        self.assertEqual("VERIFIED",
                         self.capture_engine.store.get(target.candidate_id).status.value)


# ============================================================================
# TestSearchEndpoint
# ============================================================================
class TestSearchEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root, self.service, self.capture_engine = _build_state(self.tmp)
        # Force index rebuild to ensure FTS is populated.
        from engine.index import normalize_roots
        self.capture_engine.capture_learning(
            title="SEFAZ learning",
            content="Use AES-256-GCM com HKDF para o cofre SEFAZ A1.",
            project_id="canteirohub",
            task_id="TASK-SEARCH-1",
            agent_role="QA",
        )
        self.capture_engine.capture_learning(
            title="Biolar taxonomy",
            content="Taxonomia controlada ADR-001.",
            project_id="biolar",
            task_id="TASK-SEARCH-2",
            agent_role="QA",
        )
        self.capture_engine.service.index.rebuild(
            normalize_roots([self.root])
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _open(self):
        return _ServerHandle(application_root=self.root,
                             service=self.service,
                             capture_engine=self.capture_engine)

    def test_search_returns_results(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request(
                "GET", "/api/search?q=" + urllib.parse.quote("SEFAZ")
            )
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertEqual("SEFAZ", payload["query"])
        self.assertGreaterEqual(payload["count"], 1)
        # The result may be either the inbox candidate or the markdown
        # chunk; both contain "SEFAZ" in either title or snippet.
        joined = " ".join(
            (r.get("title") or "") + " " + (r.get("snippet") or "")
            for r in payload["results"]
        )
        self.assertIn("SEFAZ", joined.upper())

    def test_search_requires_query(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/search")
        self.assertEqual(400, status)
        self.assertIn("q", json.loads(body)["error"])

    def test_search_filters_by_project(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request(
                "GET",
                "/api/search?q=" + urllib.parse.quote("ADR")
                + "&project=biolar",
            )
        self.assertEqual(200, status)
        payload = json.loads(body)
        for r in payload["results"]:
            self.assertEqual("biolar", r["project_id"])


class TestDocumentAndReindexEndpoints(unittest.TestCase):
    @contextmanager
    def _open(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root, service, capture_engine = _build_state(tmp_path)
            with _ServerHandle(application_root=root,
                                service=service,
                                capture_engine=capture_engine) as srv:
                yield srv

    def test_document_endpoint_returns_400_without_id(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/document")
        self.assertEqual(400, status)

    def test_document_endpoint_returns_404_for_unknown_id(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("GET", "/api/document?id=non_existent_id")
        self.assertEqual(404, status)

    def test_reindex_post_triggers_indexing_and_returns_ok(self) -> None:
        with self._open() as srv:
            status, body, _ = srv.request("POST", "/api/reindex", body={})
        self.assertEqual(200, status)
        payload = json.loads(body)
        self.assertEqual("ok", payload["status"])
        self.assertIn("stats", payload)


# ============================================================================
# TestServerSecurityDefaults
# ============================================================================
class TestServerSecurityDefaults(unittest.TestCase):
    def test_default_bind_is_loopback_only(self) -> None:
        # In code, the default host must be a loopback address.
        self.assertIn(DEFAULT_HOST, {"127.0.0.1", "localhost", "::1"})
        # And it must not be a wildcard or LAN-routable address.
        self.assertNotIn(DEFAULT_HOST, {"0.0.0.0", ""})

    def test_unknown_method_returns_405_or_501(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root, service, capture_engine = _build_state(tmp_path)
            with _ServerHandle(application_root=root,
                                service=service,
                                capture_engine=capture_engine) as srv:
                try:
                    status, _, _ = srv.request("DELETE", "/api/status")
                except urllib.error.HTTPError as e:
                    status = e.code
            # BaseHTTPRequestHandler returns 501 for unsupported methods.
            self.assertIn(status, {405, 501})


if __name__ == "__main__":
    unittest.main()
