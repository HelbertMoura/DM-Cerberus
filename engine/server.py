"""
Cerberus Memory Intelligence - Local Inspector & Web UI Server
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P3: lightweight HTTP server (stdlib only) that exposes a single-page
Web UI + REST API for inspecting the Cerberus corpus and operating the
candidate inbox.

Security defaults (fail-closed):

  * Binds to **127.0.0.1** by default — never LAN-reachable without an
    explicit env override (`CERBERUS_UI_HOST`).
  * Rejects any other bind host with a clear error.
  * No filesystem writes outside `LEARNINGS.md` / `DECISIONS.md` — the
    promote endpoint only triggers `AutoCaptureEngine.promote()` which
    is itself allowlist-bound.
  * Quarantined candidates are surfaced for review but can never be
    promoted through the UI (server enforces status check).
  * No external network calls; pure stdlib `http.server.ThreadingHTTPServer`.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote_plus as urllib_quote_plus, urlparse

from engine.auth import (
    DEFAULT_DEV_ADMIN_EMAIL,
    DEFAULT_DEV_ADMIN_PASSWORD,
    RateLimiter,
    SESSION_COOKIE_NAME,
    SESSION_TTL_SECONDS,
    SessionStore,
    TOTP,
    UserStore,
    build_set_cookie_header,
    get_secret_key,
    hash_password,
    parse_cookie_header,
    totp_qr_svg,
    verify_cookie,
    verify_password,
)
from engine.capture import AutoCaptureEngine, CandidateStore
from engine.integrations.orchestrator import (
    OrchestratorAdapter,
    _select_index_roots,
    _resolve_root_or_default,
)
from engine.models import Candidate, CandidateStatus
from engine.retrieval import CerberusMemoryService


# ---------------------------------------------------------------------------
# Security defaults
# ---------------------------------------------------------------------------
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7331
ALLOWED_BIND_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def _is_safe_bind_host(host: str) -> bool:
    """Return True when `host` is a loopback / localhost address."""
    lowered = host.strip().lower()
    if lowered in ALLOWED_BIND_HOSTS:
        return True
    # Reject literal "0.0.0.0" or LAN IPs by default.
    return False


# ---------------------------------------------------------------------------
# UI HTML (single-page, industrial theme, WCAG-friendly)
# ---------------------------------------------------------------------------
UI_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cerberus Inspector — Dev Maniac's</title>
<style>
:root {
  --bg: #0F172A;
  --bg-elev: #1E293B;
  --bg-card: #111827;
  --border: #334155;
  --text: #E2E8F0;
  --text-muted: #94A3B8;
  --accent: #1E40AF;
  --accent-strong: #2563EB;
  --accent-soft: rgba(37, 99, 235, 0.18);
  --success: #047857;
  --warning: #B45309;
  --danger: #B91C1C;
  --font: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
          "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "IBM Plex Mono", Menlo,
               Consolas, monospace;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 15px;
  line-height: 1.5;
  min-height: 100vh;
}
header {
  background: var(--bg-elev);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
header .brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
header .badge {
  background: var(--accent);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  padding: 4px 10px;
  border-radius: 4px;
  text-transform: uppercase;
}
header .status-pill {
  font-size: 12px;
  color: var(--text-muted);
}
header .header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
.ghost-btn {
  min-height: 44px;
  padding: 8px 14px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
}
.ghost-btn:hover { background: var(--bg-elev); }
main {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 18px;
}
.card h2 {
  margin: 0 0 4px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.card .value {
  font-size: 24px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.card .sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.toolbar input[type="search"] {
  flex: 1 1 280px;
  min-height: 44px;
  padding: 10px 14px;
  background: var(--bg-card);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}
.toolbar input[type="search"]:focus,
.toolbar select:focus {
  outline: 2px solid var(--accent-strong);
  outline-offset: 1px;
  border-color: var(--accent-strong);
}
.toolbar select {
  min-height: 44px;
  padding: 8px 12px;
  background: var(--bg-card);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}
button {
  min-height: 44px;
  min-width: 44px;
  padding: 10px 16px;
  background: var(--accent);
  color: #fff;
  border: 1px solid var(--accent-strong);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
}
button:hover { background: var(--accent-strong); }
button:focus-visible { outline: 2px solid #fff; outline-offset: 2px; }
button.secondary { background: transparent; color: var(--text); border-color: var(--border); }
button.secondary:hover { background: var(--bg-elev); }
button.danger { background: var(--danger); border-color: var(--danger); }
button.success { background: var(--success); border-color: var(--success); }
button:disabled { opacity: 0.5; cursor: not-allowed; }
table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
th, td {
  padding: 10px 14px;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
}
th {
  background: var(--bg-elev);
  color: var(--text-muted);
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
tr:last-child td { border-bottom: none; }
.tag {
  display: inline-block;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  border-radius: 4px;
  text-transform: uppercase;
}
.tag.candidate { background: rgba(37, 99, 235, 0.2); color: #93C5FD; }
.tag.verified { background: rgba(4, 120, 87, 0.2); color: #6EE7B7; }
.tag.quarantined { background: rgba(180, 83, 9, 0.25); color: #FCD34D; }
.tag.canonical { background: rgba(37, 99, 235, 0.4); color: #BFDBFE; }
.tag.rejected { background: rgba(185, 28, 28, 0.2); color: #FCA5A5; }
.muted { color: var(--text-muted); }
.code {
  font-family: var(--font-mono);
  font-size: 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 8px 10px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 360px;
  overflow: auto;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 24px 0 8px;
}
.row-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.empty {
  padding: 32px;
  text-align: center;
  color: var(--text-muted);
  border: 1px dashed var(--border);
  border-radius: 8px;
}
.error {
  padding: 12px 16px;
  background: rgba(185, 28, 28, 0.15);
  color: #FCA5A5;
  border: 1px solid var(--danger);
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 13px;
}
.ok {
  padding: 12px 16px;
  background: rgba(4, 120, 87, 0.15);
  color: #6EE7B7;
  border: 1px solid var(--success);
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 13px;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.85);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 24px;
}
.modal-backdrop.open { display: flex; }
.modal {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: auto;
  padding: 20px;
}
.modal h3 { margin: 0 0 12px; font-size: 16px; }
@media (max-width: 600px) {
  main { padding: 16px; }
  th, td { padding: 8px 10px; }
}
</style>
</head>
<body>
<header>
  <div class="brand">
    <h1>Cerberus Inspector</h1>
    <span class="badge">Localhost</span>
  </div>
  <div class="header-actions">
    <span class="status-pill" id="status-pill">connecting&hellip;</span>
    <button id="setup-2fa-btn" class="ghost-btn" type="button"
            title="Habilitar ou re-cadastrar 2FA">2FA</button>
    <button id="logout-btn" class="ghost-btn" type="button"
            title="Encerrar sess&atilde;o">Sair</button>
  </div>
</header>
<main>
  <div id="flash"></div>
  <section>
    <div class="grid" id="metrics">
      <div class="card"><h2>Files tracked</h2><div class="value" id="m-files">&mdash;</div></div>
      <div class="card"><h2>Documents</h2><div class="value" id="m-docs">&mdash;</div></div>
      <div class="card"><h2>Inbox candidates</h2><div class="value" id="m-inbox">&mdash;</div></div>
      <div class="card"><h2>FTS5</h2><div class="value" id="m-fts">&mdash;</div></div>
    </div>
  </section>

  <h3 class="section-title">Search</h3>
  <div class="toolbar">
    <input type="search" id="search-q" placeholder="Search the corpus&hellip;" aria-label="Search query">
    <select id="search-project" aria-label="Project filter">
      <option value="">(all projects)</option>
    </select>
    <button id="search-btn" type="button">Search</button>
  </div>
  <div id="search-results"></div>

  <h3 class="section-title">Candidate inbox</h3>
  <div class="toolbar">
    <select id="inbox-filter" aria-label="Filter by status">
      <option value="">(all statuses)</option>
      <option value="CANDIDATE">CANDIDATE</option>
      <option value="VERIFIED">VERIFIED</option>
      <option value="QUARANTINED">QUARANTINED</option>
      <option value="CANONICAL">CANONICAL</option>
      <option value="REJECTED">REJECTED</option>
    </select>
    <button id="refresh-btn" class="secondary" type="button">Refresh inbox</button>
  </div>
  <div id="inbox-table"></div>
</main>

<div class="modal-backdrop" id="modal" role="dialog" aria-modal="true">
  <div class="modal">
    <h3 id="modal-title">Candidate</h3>
    <div id="modal-body"></div>
    <div class="row-actions" style="margin-top:16px;">
      <button class="secondary" id="modal-close" type="button">Close</button>
      <button id="modal-promote" type="button">Promote to canonical</button>
      <button class="danger" id="modal-reject" type="button">Reject</button>
    </div>
  </div>
</div>

<script>
(function () {
  "use strict";
  const flash = document.getElementById("flash");
  function notice(kind, msg) {
    flash.innerHTML = "";
    if (!msg) return;
    const div = document.createElement("div");
    div.className = kind;
    div.textContent = msg;
    flash.appendChild(div);
    setTimeout(() => { div.remove(); }, 4500);
  }
  async function getJSON(url) {
    const r = await fetch(url, { headers: { "Accept": "application/json" } });
    const text = await r.text();
    if (!r.ok) { throw new Error(text || (r.status + " " + r.statusText)); }
    return JSON.parse(text);
  }
  async function postJSON(url) {
    const r = await fetch(url, { method: "POST", headers: { "Accept": "application/json" } });
    const text = await r.text();
    if (!r.ok) { throw new Error(text || (r.status + " " + r.statusText)); }
    return JSON.parse(text);
  }
  function esc(v) {
    return String(v == null ? "" : v).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
  }
  function statusTag(status) {
    const s = String(status || "").toUpperCase();
    return '<span class="tag ' + esc(s.toLowerCase()) + '">' + esc(s) + '</span>';
  }

  // ------- status -------
  async function refreshStatus() {
    try {
      const s = await getJSON("/api/status");
      document.getElementById("m-files").textContent = s.files;
      document.getElementById("m-docs").textContent = s.documents;
      document.getElementById("m-inbox").textContent = s.inbox_count;
      document.getElementById("m-fts").textContent = s.fts5 ? "online" : "offline";
      document.getElementById("status-pill").textContent =
        "loopback-only · bind " + esc(s.bind_host) + ":" + s.bind_port;
      const sel = document.getElementById("search-project");
      sel.innerHTML = '<option value="">(all projects)</option>';
      (s.projects || []).forEach(p => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p;
        sel.appendChild(opt);
      });
    } catch (e) { notice("error", "status: " + e.message); }
  }

  // ------- search -------
  async function runSearch() {
    const q = document.getElementById("search-q").value.trim();
    const project = document.getElementById("search-project").value;
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (project) params.set("project", project);
    const out = document.getElementById("search-results");
    out.innerHTML = '<div class="muted">searching&hellip;</div>';
    try {
      const r = await getJSON("/api/search?" + params.toString());
      if (!r.results.length) { out.innerHTML = '<div class="empty">No results.</div>'; return; }
      const rows = r.results.map(item => (
        '<tr>' +
        '<td><span class="tag ' + esc(String(item.project_id || "").toLowerCase()) + '">' + esc(item.project_id) + '</span></td>' +
        '<td>' + esc(item.title) + '<div class="muted">' + esc(item.source_path) + '</div></td>' +
        '<td>' + esc(item.authority_level) + '</td>' +
        '<td>' + esc(item.snippet) + '</td>' +
        '</tr>'
      )).join("");
      out.innerHTML =
        '<table><thead><tr><th>Project</th><th>Title</th><th>Auth</th><th>Snippet</th></tr></thead>' +
        '<tbody>' + rows + '</tbody></table>';
    } catch (e) { out.innerHTML = '<div class="error">' + esc(e.message) + '</div>'; }
  }

  // ------- inbox -------
  async function refreshInbox() {
    const filter = document.getElementById("inbox-filter").value;
    const url = "/api/inbox" + (filter ? "?status=" + encodeURIComponent(filter) : "");
    const out = document.getElementById("inbox-table");
    try {
      const r = await getJSON(url);
      if (!r.candidates.length) { out.innerHTML = '<div class="empty">Inbox is empty.</div>'; return; }
      const rows = r.candidates.map(c => (
        '<tr>' +
        '<td>' + statusTag(c.status) + '</td>' +
        '<td><strong>' + esc(c.title) + '</strong>' +
          '<div class="muted">' + esc(c.candidate_id) + '</div></td>' +
        '<td><span class="tag ' + esc(String(c.project_id || "").toLowerCase()) + '">' + esc(c.project_id) + '</span></td>' +
        '<td class="muted">' + esc(c.task_id) + '</td>' +
        '<td class="muted">' + esc(c.created_at) + '</td>' +
        '<td><button data-id="' + esc(c.candidate_id) + '" class="open-btn secondary" type="button">Open</button></td>' +
        '</tr>'
      )).join("");
      out.innerHTML =
        '<table><thead><tr><th>Status</th><th>Title</th><th>Project</th><th>Task</th><th>Created</th><th></th></tr></thead>' +
        '<tbody>' + rows + '</tbody></table>';
      out.querySelectorAll(".open-btn").forEach(b => b.addEventListener("click", () => openCandidate(b.dataset.id)));
    } catch (e) { out.innerHTML = '<div class="error">' + esc(e.message) + '</div>'; }
  }

  // ------- modal -------
  let currentCandidate = null;
  async function openCandidate(id) {
    try {
      const c = await getJSON("/api/inbox/" + encodeURIComponent(id));
      currentCandidate = c;
      document.getElementById("modal-title").textContent = c.title + " (" + c.candidate_id + ")";
      const body = document.getElementById("modal-body");
      body.innerHTML =
        '<p>' + statusTag(c.status) +
        ' <span class="tag ' + esc(String(c.project_id || "").toLowerCase()) + '">' + esc(c.project_id) + '</span></p>' +
        '<p class="muted">Task ' + esc(c.task_id) + ' · Agent ' + esc(c.agent) + ' · ' +
        'Fingerprint ' + esc(c.fingerprint.slice(0, 16)) + '&hellip;</p>' +
        '<div class="section-title">Content</div>' +
        '<div class="code">' + esc(c.content) + '</div>' +
        '<div class="section-title">Diff preview (promote)</div>' +
        '<div class="code">' + esc(c.diff || "(no diff)") + '</div>';
      const canPromote = c.status === "VERIFIED";
      const canReject = c.status !== "CANONICAL";
      document.getElementById("modal-promote").disabled = !canPromote;
      document.getElementById("modal-reject").disabled = !canReject;
      document.getElementById("modal").classList.add("open");
    } catch (e) { notice("error", "open: " + e.message); }
  }
  document.getElementById("modal-close").addEventListener("click", () => {
    document.getElementById("modal").classList.remove("open");
  });
  document.getElementById("modal-promote").addEventListener("click", async () => {
    if (!currentCandidate) return;
    try {
      const r = await postJSON("/api/inbox/" + encodeURIComponent(currentCandidate.candidate_id) + "/promote");
      notice("ok", "Promoted: " + r.status + " -> " + r.target_file);
      document.getElementById("modal").classList.remove("open");
      refreshInbox();
      refreshStatus();
    } catch (e) { notice("error", "promote: " + e.message); }
  });
  document.getElementById("modal-reject").addEventListener("click", async () => {
    if (!currentCandidate) return;
    try {
      await postJSON("/api/inbox/" + encodeURIComponent(currentCandidate.candidate_id) + "/reject");
      notice("ok", "Rejected.");
      document.getElementById("modal").classList.remove("open");
      refreshInbox();
      refreshStatus();
    } catch (e) { notice("error", "reject: " + e.message); }
  });

  document.getElementById("refresh-btn").addEventListener("click", refreshInbox);
  document.getElementById("search-btn").addEventListener("click", runSearch);
  document.getElementById("search-q").addEventListener("keydown", e => {
    if (e.key === "Enter") runSearch();
  });
  document.getElementById("logout-btn").addEventListener("click", async () => {
    try {
      await postJSON("/auth/logout");
      window.location.href = "/auth/login";
    } catch (e) { notice("error", "logout: " + e.message); }
  });
  document.getElementById("setup-2fa-btn").addEventListener("click", () => {
    window.location.href = "/auth/setup-2fa";
  });
  // Show setup success notice if redirected from /auth/setup-2fa
  if (window.location.search.includes("setup=ok")) {
    notice("ok", "2FA habilitado com sucesso.");
  }

  refreshStatus();
  refreshInbox();
})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Server factory
# ---------------------------------------------------------------------------
def _serialize_candidate(candidate: Candidate) -> Dict[str, Any]:
    return candidate.to_dict()


class CerberusInspectorState:
    """Holds the references the request handler uses to serve requests."""

    def __init__(self, application_root: Path,
                 service: Optional[CerberusMemoryService] = None,
                 capture_engine: Optional[AutoCaptureEngine] = None) -> None:
        self.application_root = Path(application_root).resolve()
        self.service = service or CerberusMemoryService(
            _default_index(self.application_root)
        )
        self.capture_engine = capture_engine or AutoCaptureEngine(
            service=self.service, cerebro_root=self.application_root
        )
        self.inbox: CandidateStore = self.capture_engine.store

    def ensure_indexed(self) -> Dict[str, Any]:
        roots = _select_index_roots(self.application_root)
        if not roots:
            return {"indexed_files": 0, "skipped_files": 0,
                    "total_chunks": 0, "errors": 0, "roots": []}
        return self.service.index.index_roots(roots)


def _default_index(application_root: Path):
    from engine.index import SQLiteMemoryIndex
    return SQLiteMemoryIndex(application_root / ".cerberus" / "index.db")


def _sqlite_fts5_available() -> bool:
    try:
        import sqlite3
        con = sqlite3.connect(":memory:")
        try:
            con.execute("CREATE VIRTUAL TABLE _cerberus_health USING fts5(value)")
            con.execute("INSERT INTO _cerberus_health(value) VALUES ('x')")
            cur = con.execute(
                "SELECT count(*) FROM _cerberus_health "
                "WHERE _cerberus_health MATCH 'x'"
            )
            row = cur.fetchone() if hasattr(cur, "fetchone") else cur
            return bool(row)
        finally:
            con.close()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Two Point Design System — Login + Setup 2FA pages
# ---------------------------------------------------------------------------
WATERMARK_SVG = (
    "data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20"
    "viewBox%3D%270%200%20120%2060%27%3E%3Ctext%20x%3D%2760%27%20y%3D'38'%20font-family%3D'IBM%20Plex"
    "%20Sans%27%20font-size%3D'36%27%20fill%3D'%2314a08f'%20fill-opacity%3D'0.18'%20text-anchor%3D"
    "%27middle%27%20font-weight%3D'700'%3EDM%3C%2Ftext%3E%3C%2Fsvg%3E"
)


def _render_login_html(step: str = "credentials",
                       error_message: str = "",
                       pending_token: str = "",
                       target_email: str = "") -> str:
    """Render the Two Point login page (Hub-style)."""
    error_block = ""
    if error_message:
        escaped = (error_message.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
        error_block = (
            f'<div class="login-error" role="alert">⚠ '
            f'<span>{escaped}</span></div>'
        )
    # Step rendering
    creds_class = "step-content active" if step == "credentials" else "step-content"
    totp_class = "step-content active" if step == "totp" else "step-content"
    if step == "credentials":
        creds_block = f'''
<form id="loginForm" method="POST" action="/auth/login" class="step-form" autocomplete="on">
  <label class="field">
    <span>E-mail</span>
    <input type="email" name="email" required autofocus autocomplete="username"
           placeholder="helbert.moura@devmaniacs.com.br" value="{target_email}">
  </label>
  <label class="field">
    <span>Senha</span>
    <input type="password" name="password" required autocomplete="current-password"
           placeholder="••••••••" minlength="8">
  </label>
  <button type="submit" class="btn-3d primary">Entrar &rarr;</button>
  <p class="muted">Primeiro acesso? Senha inicial exibida no log do servidor.</p>
</form>'''
        totp_block = ''
    else:
        creds_block = ''
        totp_block = f'''
<form id="totpForm" method="POST" action="/auth/login" class="step-form" autocomplete="off">
  <input type="hidden" name="pending_token" value="{pending_token}">
  <input type="hidden" name="email" value="{target_email}">
  <p class="muted">Confirme com o código TOTP do seu aplicativo autenticador.</p>
  <label class="field">
    <span>Código TOTP (8 dígitos)</span>
    <input type="text" name="totp" required autofocus inputmode="numeric"
           autocomplete="one-time-code" pattern="\\d{{8}}" maxlength="8"
           placeholder="00000000">
  </label>
  <button type="submit" class="btn-3d primary">Validar &rarr;</button>
</form>'''

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cerberus Inspector &mdash; Login</title>
<style>
:root {{
  --bg-deep: #175047;
  --bg-deep-2: #134339;
  --card: #fdf7ea;
  --ink: #22304A;
  --ink-soft: #5B6770;
  --accent: #14a08f;
  --accent-deep: #0f7e72;
  --shadow: rgba(16,26,24,.45);
  --font: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
          "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "IBM Plex Mono", Menlo,
               Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; min-height: 100vh; font-family: var(--font); }}
body {{
  background: var(--bg-deep);
  background-image: url("{WATERMARK_SVG}");
  background-repeat: repeat;
  background-size: 240px 120px;
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  min-height: 100vh;
}}
.card {{
  background: var(--card);
  border: 3px solid var(--ink);
  border-radius: 16px;
  padding: 32px 32px 28px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 8px 0 var(--shadow);
}}
.card h1 {{
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--ink);
}}
.card .subtitle {{
  margin: 0 0 20px;
  font-size: 13px;
  color: var(--ink-soft);
}}
.field {{
  display: block;
  margin-bottom: 16px;
}}
.field > span {{
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--ink);
  margin-bottom: 6px;
}}
.field input {{
  width: 100%;
  min-height: 44px;
  padding: 10px 12px;
  font: inherit;
  font-size: 15px;
  background: #fff;
  color: var(--ink);
  border: 1.5px solid var(--ink);
  border-radius: 8px;
}}
.field input:focus {{
  outline: 3px solid var(--accent);
  outline-offset: 1px;
}}
.btn-3d {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 18px;
  font: inherit;
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 0.02em;
  color: #fff;
  background: var(--accent);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 5px 0 var(--ink);
  transition: transform 0.06s ease, box-shadow 0.06s ease;
  width: 100%;
  margin-top: 8px;
}}
.btn-3d:hover {{ background: var(--accent-deep); }}
.btn-3d:active {{
  transform: translateY(4px);
  box-shadow: 0 1px 0 var(--ink);
}}
.muted {{ color: var(--ink-soft); font-size: 12px; margin: 12px 0 0; }}
.login-error {{
  display: flex;
  gap: 8px;
  align-items: flex-start;
  background: #fff1ed;
  border: 1.5px solid #c14530;
  color: #8a1c0a;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}}
.step-content {{ display: none; }}
.step-content.active {{ display: block; }}
.step-fade {{ animation: fade 0.32s ease; }}
@keyframes fade {{ from {{ opacity: 0; transform: translateY(-4px); }}
                   to   {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>
  <main class="card">
    <h1>Cerberus Inspector</h1>
    <p class="subtitle">Dev Maniac&rsquo;s Memory Intelligence &mdash; Painel Localhost</p>
    {error_block}
    <section class="{creds_class}" id="credsStep">
      {creds_block}
    </section>
    <section class="{totp_class} step-fade" id="totpStep">
      {totp_block}
    </section>
  </main>
</body>
</html>'''


def _render_setup_2fa_html(secret_b32: str, otp_uri: str,
                            svg: str, error_message: str = "") -> str:
    err_block = ""
    if error_message:
        escaped = (error_message.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
        err_block = (
            f'<div class="login-error" role="alert">⚠ '
            f'<span>{escaped}</span></div>'
        )
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cerberus Inspector &mdash; Setup 2FA</title>
<style>
:root {{
  --bg-deep: #175047;
  --card: #fdf7ea;
  --ink: #22304A;
  --ink-soft: #5B6770;
  --accent: #14a08f;
  --accent-deep: #0f7e72;
  --shadow: rgba(16,26,24,.45);
  --font: ui-sans-serif, system-ui, -apple-system, "IBM Plex Sans", sans-serif;
  --font-mono: ui-monospace, "IBM Plex Mono", monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; font-family: var(--font); }}
body {{
  background: var(--bg-deep);
  color: var(--ink);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}}
.card {{
  background: var(--card);
  border: 3px solid var(--ink);
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 560px;
  box-shadow: 0 8px 0 var(--shadow);
}}
.card h1 {{ margin: 0 0 4px; font-size: 22px; }}
.card p.subtitle {{ margin: 0 0 20px; color: var(--ink-soft); font-size: 13px; }}
.qr-wrap {{ display: flex; gap: 16px; align-items: center; }}
.qr-wrap .svg {{ background: #fff; padding: 12px; border-radius: 8px;
                 border: 1.5px solid var(--ink); flex-shrink: 0; }}
.field {{ margin-bottom: 14px; }}
.field > span {{ display: block; font-size: 12px; font-weight: 600;
                  text-transform: uppercase; letter-spacing: 0.04em;
                  margin-bottom: 6px; }}
.field input {{ width: 100%; min-height: 44px; padding: 10px 12px;
                font: inherit; border: 1.5px solid var(--ink); border-radius: 8px; }}
.uri-block {{ font-family: var(--font-mono); font-size: 11px; padding: 10px;
               background: #fff; border: 1.5px solid var(--ink); border-radius: 8px;
               word-break: break-all; }}
.btn-3d {{
  display: inline-flex; align-items: center; justify-content: center;
  min-height: 48px; padding: 12px 18px; font: inherit; font-weight: 700;
  font-size: 15px; color: #fff; background: var(--accent); border: none;
  border-radius: 10px; cursor: pointer;
  box-shadow: 0 5px 0 var(--ink); width: 100%;
}}
.btn-3d:hover {{ background: var(--accent-deep); }}
.btn-3d:active {{ transform: translateY(4px); box-shadow: 0 1px 0 var(--ink); }}
.login-error {{ display: flex; gap: 8px; background: #fff1ed;
                border: 1.5px solid #c14530; color: #8a1c0a; padding: 10px 12px;
                border-radius: 8px; font-size: 13px; margin-bottom: 16px; }}
.muted {{ color: var(--ink-soft); font-size: 12px; margin: 8px 0 0; }}
</style>
</head>
<body>
  <main class="card">
    <h1>Habilitar 2FA</h1>
    <p class="subtitle">Cadastre seu aplicativo autenticador (Google Authenticator, 1Password, Authy).</p>
    {err_block}
    <div class="qr-wrap">
      <div class="svg">{svg}</div>
      <div>
        <p><strong>Passo 1.</strong> Escaneie o QR no app ou cole a URI abaixo.</p>
        <p class="muted"><strong>Secret (base32):</strong></p>
        <pre class="uri-block">{secret_b32}</pre>
        <p class="muted">URI otpauth:</p>
        <pre class="uri-block">{otp_uri}</pre>
      </div>
    </div>
    <form method="POST" action="/auth/setup-2fa" style="margin-top:18px">
      <label class="field">
        <span>Passo 2. Confirme com um código gerado pelo app</span>
        <input type="text" name="totp" required autofocus inputmode="numeric"
               pattern="\\d{{8}}" maxlength="8" placeholder="00000000">
      </label>
      <button type="submit" class="btn-3d">Ativar 2FA</button>
    </form>
    <p class="muted">Sem 2FA, o login fica limitado a emails e senhas (menos seguro).</p>
  </main>
</body>
</html>'''


class AuthState:
    """Holds the authentication surface for the Inspector server.

    When `auth_disabled` is True, every request bypasses auth (used by
    tests and the dev escape hatch). When False, `/` and `/api/*`
    require a valid session cookie; `/auth/login` is the only public
    route.
    """

    def __init__(self, application_root: Path,
                 user_store: Optional[UserStore] = None,
                 session_store: Optional[SessionStore] = None,
                 rate_limiter: Optional[RateLimiter] = None,
                 secret_key: Optional[str] = None,
                 auth_disabled: bool = False) -> None:
        self.application_root = Path(application_root).resolve()
        self.auth_disabled = bool(auth_disabled)
        self.secret_key, self.is_secure = get_secret_key(secret_key)
        self.user_store = user_store or UserStore(
            self.application_root / ".cerberus" / "users.json"
        )
        self.session_store = session_store or SessionStore()
        self.rate_limiter = rate_limiter or RateLimiter(
            rate_per_minute=10, burst=6
        )
        # Pending TOTP step tokens (one-time-use) for two-step login.
        self._pending_lock = threading.Lock()
        self._pending: Dict[str, Dict[str, Any]] = {}
        self._pending_ttl = 5 * 60  # 5 minutes
        # Pending 2FA setup secrets keyed by session.sid.
        self._pending_setup_sessions: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Rate limit helpers
    # ------------------------------------------------------------------
    def login_key(self, ip: str, email: str) -> str:
        return f"login:{ip}:{email.casefold()}"

    def global_login_key(self, ip: str) -> str:
        return f"login:{ip}:*"

    # ------------------------------------------------------------------
    # Pending 2FA tokens (returned by step 1, consumed by step 2)
    # ------------------------------------------------------------------
    PENDING_MAX_ATTEMPTS = 3  # FIX-007: 3 retries per pending_token

    def create_pending(self, email: str) -> str:
        token = secrets.token_urlsafe(24)
        now = time.time()
        with self._pending_lock:
            self._pending[token] = {
                "email": email.casefold(),
                "created_at": now,
                "expires_at": now + self._pending_ttl,
                "attempts": 0,
            }
        return token

    def consume_pending(self, token: str) -> Optional[str]:
        """Pop the pending entry; returns None on missing/expiry/over-limit."""
        now = time.time()
        with self._pending_lock:
            entry = self._pending.pop(token, None)
        if entry is None:
            return None
        if now - entry["created_at"] > self._pending_ttl:
            return None
        if entry.get("attempts", 0) >= self.PENDING_MAX_ATTEMPTS:
            return None
        return entry["email"]

    def check_pending(self, token: str) -> Optional[Dict[str, Any]]:
        """Return an unexpired pending entry without consuming it."""
        now = time.time()
        with self._pending_lock:
            entry = self._pending.get(token)
            if entry is None:
                return None
            if now - entry["created_at"] > self._pending_ttl:
                self._pending.pop(token, None)
                return None
            return dict(entry)

    def record_pending_failure(self, token: str) -> Dict[str, Any]:
        """Increment the attempt count; return the updated entry.

        Returns an empty dict when the token has already expired or is
        unknown — callers should treat that as a final failure.
        """
        with self._pending_lock:
            entry = self._pending.get(token)
            if entry is None:
                return {}
            entry["attempts"] = entry.get("attempts", 0) + 1
            return dict(entry)

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------
    def issue_session(self, user_email: str, *,
                      two_factor_passed: bool = True) -> Session:
        return self.session_store.create(
            user_email, ttl=SESSION_TTL_SECONDS,
            two_factor_passed=two_factor_passed,
        )

    def resolve_session(self, cookie_header: Optional[str]) -> Optional[Session]:
        cookies = parse_cookie_header(cookie_header)
        value = cookies.get(SESSION_COOKIE_NAME, "")
        if not value:
            return None
        sid = verify_cookie(value, self.secret_key)
        if not sid:
            return None
        return self.session_store.get(sid)

    def build_session_cookie(self, session: Session,
                              request_headers: Optional[Dict[str, str]] = None
                              ) -> str:
        """Build the `cerberus_session` cookie.

        `Secure` attribute is enabled when `CERBERUS_SECURE_COOKIES=1`
        or when behind a TLS-terminating proxy (Cloudflare /
        X-Forwarded-Proto https / X-Forwarded-Ssl on). When the
        Inspector runs on plain loopback HTTP, the cookie stays
        insecure so it can survive the dev port.
        """
        from engine.auth import sign_cookie, should_use_secure_cookie
        headers = request_headers or {}
        secure = should_use_secure_cookie(
            forwarded_proto=headers.get("X-Forwarded-Proto")
        )
        return build_set_cookie_header(
            SESSION_COOKIE_NAME, sign_cookie(session.sid, self.secret_key),
            max_age=SESSION_TTL_SECONDS,
            secure=secure, httponly=True,
        )

    def build_clear_cookie(self, request_headers: Optional[Dict[str, str]] = None
                           ) -> str:
        from engine.auth import should_use_secure_cookie
        headers = request_headers or {}
        secure = should_use_secure_cookie(
            forwarded_proto=headers.get("X-Forwarded-Proto")
        )
        return build_set_cookie_header(
            SESSION_COOKIE_NAME, "", max_age=0,
            secure=secure, httponly=True,
        )


class CerberusRequestHandler(BaseHTTPRequestHandler):
    """Single request handler serving both UI and JSON API."""

    server_version = "CerberusInspector/1.0"
    state: CerberusInspectorState = None  # type: ignore[assignment]
    auth: "AuthState" = None  # type: ignore[assignment]
    bind_host: str = DEFAULT_HOST
    bind_port: int = DEFAULT_PORT

    # Quiet the default access-log spam; tests can still introspect via
    # overriding `log_message` if needed.
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _write(self, status: int, body: bytes,
               content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._write(status, body)

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message, "status": status})

    def _read_body_once(self) -> bytes:
        """Read the request body once; subsequent calls return empty."""
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return b""
        try:
            return self.rfile.read(length)
        except OSError:
            return b""

    def _read_request_payload(self) -> Dict[str, Any]:
        """Return the request body as a dict (JSON preferred, form fallback).

        Reads the body exactly once and tries both JSON and form-urlencoded
        decoders. If both fail, returns `{}`.
        """
        raw = self._read_body_once()
        if not raw:
            return {}
        # Try JSON first (the canonical API contract).
        try:
            data = json.loads(raw.decode("utf-8"))
            if isinstance(data, dict):
                return data
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        # Fallback to form-urlencoded.
        try:
            from urllib.parse import parse_qs
            parsed = parse_qs(raw.decode("utf-8", errors="replace"),
                              keep_blank_values=True)
            return {k: v[0] for k, v in parsed.items() if v}
        except Exception:
            return {}

    def _read_json_body(self) -> Dict[str, Any]:
        """Read body as JSON; raise ValueError on non-JSON content."""
        raw = self._read_body_once()
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON body: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        return data

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def _client_ip(self) -> str:
        """Resolve the client IP for rate limiting.

        Default trust boundary is the **socket peer** (`self.client_address`).
        Set `CERBERUS_TRUST_PROXY=1` (or pass `trust_proxy=True`) to trust
        the upstream proxy's `CF-Connecting-IP` / `X-Forwarded-For`
        headers instead.
        """
        from engine.auth import resolve_client_ip
        headers = {key: self.headers.get(key, "") or
                   "" for key in ("CF-Connecting-IP", "X-Forwarded-For")}
        return resolve_client_ip(
            headers,
            direct_address=self.client_address[0] if self.client_address else "",
        )

    def _is_authenticated(self) -> bool:
        if not self.auth or self.auth.auth_disabled:
            return True
        session = self.auth.resolve_session(self.headers.get("Cookie"))
        return bool(session and session.two_factor_passed)

    def _auth_redirect_or_401(self, accepts_html: bool) -> None:
        if accepts_html:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/auth/login")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._error(HTTPStatus.UNAUTHORIZED, "Authentication required")

    def _require_auth(self) -> bool:
        if self._is_authenticated():
            return True
        accepts_html = "text/html" in (self.headers.get("Accept") or "")
        self._auth_redirect_or_401(accepts_html)
        return False

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path or "/"
        query = parse_qs(parsed.query, keep_blank_values=True)

        # Public auth routes (no auth required)
        if path == "/auth/login":
            return self._serve_login_get(query)
        if path == "/auth/setup-2fa":
            if not self._require_auth():
                return
            return self._serve_setup_2fa_get()
        if path.startswith("/static/"):
            return self._serve_static(path)

        # All other routes require auth
        if not self._require_auth():
            return

        if path == "/" or path == "":
            return self._serve_ui()
        if path == "/api/status":
            return self._serve_status()
        if path == "/api/inbox":
            return self._serve_inbox_list(query)
        if path == "/api/search":
            return self._serve_search(query)
        if path.startswith("/api/inbox/"):
            tail = path[len("/api/inbox/"):]
            if not tail or "/" in tail:
                return self._error(HTTPStatus.NOT_FOUND, "Unknown inbox route")
            return self._serve_inbox_detail(tail)
        return self._error(HTTPStatus.NOT_FOUND, f"Unknown route: {path}")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path or "/"

        # Public auth routes
        if path == "/auth/login":
            return self._serve_login_post()
        if path == "/auth/logout":
            return self._serve_logout_post()
        if path == "/auth/setup-2fa":
            if not self._require_auth():
                return
            return self._serve_setup_2fa_post()
        if path.startswith("/static/"):
            return self._serve_static(path)

        # Everything else requires auth
        if not self._require_auth():
            return

        if not path.startswith("/api/inbox/"):
            return self._error(HTTPStatus.NOT_FOUND, f"Unknown route: {path}")
        tail = path[len("/api/inbox/"):]
        if "/" not in tail:
            return self._error(HTTPStatus.NOT_FOUND, "Missing action")
        candidate_id, action = tail.split("/", 1)
        action = action.strip("/")
        try:
            body = self._read_json_body()
        except ValueError as exc:
            return self._error(HTTPStatus.BAD_REQUEST, str(exc))
        if action == "promote":
            return self._serve_inbox_promote(candidate_id, body)
        if action == "reject":
            return self._serve_inbox_reject(candidate_id, body)
        if action == "verify":
            return self._serve_inbox_verify(candidate_id, body)
        return self._error(HTTPStatus.NOT_FOUND, f"Unknown action: {action}")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def _serve_static(self, path: str) -> None:
        # No static assets shipped today; reserved for future favicon / css.
        self._error(HTTPStatus.NOT_FOUND, "No static assets")

    def _serve_login_get(self, query: Dict[str, List[str]]) -> None:
        if self._is_authenticated():
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        step = (query.get("step", ["credentials"])[0] or "credentials").strip()
        pending = query.get("pending", [""])[0].strip()
        email = query.get("email", [""])[0].strip()
        err = query.get("err", [""])[0].strip()
        body = _render_login_html(
            step="totp" if step == "totp" else "credentials",
            error_message=err,
            pending_token=pending,
            target_email=email,
        ).encode("utf-8")
        self._write(HTTPStatus.OK, body,
                    content_type="text/html; charset=utf-8")

    def _serve_login_post(self) -> None:
        body = self._read_request_payload()
        email = (body.get("email") or "").strip()
        password = body.get("password") or ""
        totp = (body.get("totp") or "").strip()
        pending_token = (body.get("pending_token") or "").strip()
        ip = self._client_ip()

        # Rate limit (per IP, then per IP+email)
        if not self.auth.rate_limiter.allow(self.auth.global_login_key(ip)):
            self._login_redirect_with_error(
                "Muitas tentativas. Aguarde alguns segundos.", step="credentials",
                email=email)
            return
        if email and not self.auth.rate_limiter.allow(
                self.auth.login_key(ip, email)):
            self._login_redirect_with_error(
                "Muitas tentativas para este email. Aguarde alguns segundos.",
                step="credentials", email=email)
            return

        # Step 2 of two-step: pending token + TOTP code
        if pending_token:
            # FIX-007: rate-limit per-pending_token too (prevent brute
            # force on the 6-digit window while keeping the flow smooth
            # for legitimate users).
            ip = self._client_ip()
            if not self.auth.rate_limiter.allow(
                    self.auth.login_key(ip, pending_token)):
                self._login_redirect_with_error(
                    "Muitas tentativas. Aguarde alguns segundos.",
                    step="totp", pending=pending_token)
                return

            peek = self.auth.check_pending(pending_token)
            if peek is None:
                self._login_redirect_with_error(
                    "", error_code="session_expired")
                return
            # If the user already burned their attempts, fail-closed.
            if peek.get("attempts", 0) >= self.auth.PENDING_MAX_ATTEMPTS:
                self._login_redirect_with_error(
                    "Muitas tentativas de código. Faça login novamente.",
                    step="credentials")
                return
            resolved_email = peek["email"]
            user = self.auth.user_store.get(resolved_email)
            if user is None or not user.is_active:
                self._login_redirect_with_error("Conta inválida.",
                                                 step="credentials")
                return
            secret_b32 = user.totp_secret
            if not secret_b32:
                # 2FA not enrolled — issue session directly (acceptable for
                # the first-run operator, who can enroll from /auth/setup-2fa).
                self._issue_session_and_redirect(user.email)
                return
            totp_obj = TOTP.from_base32(secret_b32)
            if not totp_obj.verify(totp):
                # FIX-007: do NOT destroy the pending_token on attempt 1.
                # Track up to PENDING_MAX_ATTEMPTS within the 5-min window,
                # then invalidate.
                status = self.auth.record_pending_failure(pending_token)
                attempts_left = max(
                    0,
                    self.auth.PENDING_MAX_ATTEMPTS - status.get("attempts", 0),
                )
                if attempts_left <= 0:
                    # Burn the token — no further retries allowed.
                    self.auth._pending.pop(pending_token, None)
                    self._login_redirect_with_error(
                        "Muitas tentativas de código. Faça login novamente.",
                        step="credentials")
                    return
                self._login_redirect_with_error(
                    f"Código incorreto. {attempts_left} tentativa(s) restante(s).",
                    step="totp", pending=pending_token,
                    email=user.email)
                return
            # Success: consume the pending token now.
            consumed_email = self.auth.consume_pending(pending_token)
            if consumed_email is None or consumed_email != user.email.casefold():
                self._login_redirect_with_error(
                    "", error_code="session_expired")
                return
            self._issue_session_and_redirect(user.email)
            return

        # Step 1: email + password
        if not email or not password:
            self._login_redirect_with_error(
                "Informe e-mail e senha.", step="credentials", email=email)
            return
        user = self.auth.user_store.get(email)
        if user is None or not user.is_active or not verify_password(
                password, user.password_hash):
            self._login_redirect_with_error(
                "Credenciais inválidas.", step="credentials", email=email)
            return

        # Has TOTP enrolled? -> issue pending token, ask for step 2.
        if user.totp_secret:
            pending = self.auth.create_pending(user.email)
            self._login_redirect_with_error(
                "", step="totp", pending=pending, email=user.email)
            return

        # No TOTP enrolled -> direct session (operator-first-run mode).
        self._issue_session_and_redirect(user.email)

    def _issue_session_and_redirect(self, user_email: str) -> None:
        session = self.auth.issue_session(user_email,
                                          two_factor_passed=True)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Set-Cookie", self.auth.build_session_cookie(
            session, request_headers=self.headers))
        self.send_header("Location", "/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _login_redirect_with_error(self, message: str, *,
                                     step: str = "credentials",
                                     email: str = "",
                                     pending: str = "",
                                     error_code: str = "") -> None:
        target = "/auth/login"
        params: List[str] = []
        if error_code:
            params.append(f"error={urllib_quote_plus(error_code)}")
        if step and step != "credentials":
            params.append(f"step={step}")
        if pending:
            params.append(f"pending={pending}")
        if email:
            params.append(f"email={urllib_quote_plus(email)}")
        if message:
            params.append(f"err={urllib_quote_plus(message)}")
        if params:
            target += "?" + "&".join(params)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", target)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _parse_form_body(self) -> Dict[str, str]:
        # Backwards-compat shim — prefer `_read_request_payload()` which
        # handles both JSON and form-urlencoded in a single read.
        return self._read_request_payload()

    def _serve_logout_post(self) -> None:
        session = self.auth.resolve_session(self.headers.get("Cookie"))
        if session:
            self.auth.session_store.invalidate(session.sid)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Set-Cookie", self.auth.build_clear_cookie(
            request_headers=self.headers))
        self.send_header("Location", "/auth/login")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _serve_setup_2fa_get(self) -> None:
        session = self.auth.resolve_session(self.headers.get("Cookie"))
        if not session:
            self._auth_redirect_or_401(
                "text/html" in (self.headers.get("Accept") or ""))
            return
        user = self.auth.user_store.get(session.user_email)
        if user is None:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Set-Cookie", self.auth.build_clear_cookie(
                request_headers=self.headers))
            self.send_header("Location", "/auth/login")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if user.totp_secret:
            secret_b32 = user.totp_secret
            totp_obj = TOTP.from_base32(secret_b32)
            uri = totp_obj.provisioning_uri(user.email, issuer="Cerberus")
            svg = totp_qr_svg(uri)
            self._write_setup_2fa_html(secret_b32, uri, svg,
                                       error_message="2FA já está habilitado.",
                                       already_enabled=True)
            return
        # Generate new secret
        totp_obj = TOTP.generate()
        secret_b32 = totp_obj.to_base32()
        # Store temporarily in session pending_2fa_setup
        self.auth.session_store.create(
            f"pending_setup:{user.email}", ttl=600, two_factor_passed=False
        )
        # Save pending secret in a transient store keyed by session.sid
        self.auth._pending_setup_sessions[session.sid] = secret_b32  # type: ignore[attr-defined]
        uri = totp_obj.provisioning_uri(user.email, issuer="Cerberus")
        svg = totp_qr_svg(uri)
        self._write_setup_2fa_html(secret_b32, uri, svg)

    def _write_setup_2fa_html(self, secret_b32: str, uri: str, svg: str,
                              error_message: str = "",
                              already_enabled: bool = False) -> None:
        if already_enabled:
            error_message = (
                "2FA já está habilitado para esta conta. "
                "Faça logout para re-cadastrar."
            )
        body = _render_setup_2fa_html(secret_b32, uri, svg,
                                      error_message=error_message).encode("utf-8")
        self._write(HTTPStatus.OK, body,
                    content_type="text/html; charset=utf-8")

    def _serve_setup_2fa_post(self) -> None:
        session = self.auth.resolve_session(self.headers.get("Cookie"))
        if not session:
            self._auth_redirect_or_401(
                "text/html" in (self.headers.get("Accept") or ""))
            return
        body = self._read_request_payload()
        totp_code = (body.get("totp") or "").strip()
        secret_b32 = self.auth._pending_setup_sessions.pop(  # type: ignore[attr-defined]
            session.sid, None
        )
        if not secret_b32:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/auth/setup-2fa")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        totp_obj = TOTP.from_base32(secret_b32)
        if not totp_obj.verify(totp_code):
            # Re-show the form with the same secret
            user = self.auth.user_store.get(session.user_email)
            if user is None:
                self._login_redirect_with_error("Conta inválida.",
                                                 step="credentials")
                return
            uri = totp_obj.provisioning_uri(user.email, issuer="Cerberus")
            svg = totp_qr_svg(uri)
            self.auth._pending_setup_sessions[session.sid] = secret_b32  # type: ignore[attr-defined]
            self._write_setup_2fa_html(
                secret_b32, uri, svg,
                error_message="Código inválido. Tente novamente."
            )
            return
        # Activate 2FA
        try:
            self.auth.user_store.set_totp_secret(session.user_email, secret_b32)
        except KeyError:
            self._login_redirect_with_error("Conta inválida.",
                                             step="credentials")
            return
        # Redirect home with success indicator via query string
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/?setup=ok")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _serve_ui(self) -> None:
        body = UI_HTML.encode("utf-8")
        self._write(HTTPStatus.OK, body,
                    content_type="text/html; charset=utf-8")

    def _serve_status(self) -> None:
        try:
            stats = self.state.service.index.get_stats()
        except Exception as exc:  # noqa: BLE001
            stats = {"total_files": 0, "total_documents": 0,
                      "indexed_projects": [], "types_breakdown": {},
                      "db_path": "unavailable", "fts5_available": False,
                      "error": str(exc)}
        # Build the list of known projects (alphabetical, with global first).
        known: List[str] = ["_global", "_shared"]
        try:
            from engine.integrations.orchestrator import (
                PROJECT_ALIASES, _configured_allowed_roots,
                discover_dynamic_projects,
            )
            known.extend(sorted({v for v in PROJECT_ALIASES.values()}))
            known.extend(discover_dynamic_projects(self.state.application_root))
        except Exception:
            pass
        inbox_count = (len(list(self.state.inbox.inbox_dir.glob("*.json")))
                        if self.state.inbox.inbox_dir.exists() else 0)
        # fts5_available: prefer what the index reports; only probe the
        # interpreter when the index didn't expose the flag.
        fts5_available = stats.get("fts5_available")
        if fts5_available is None:
            fts5_available = _sqlite_fts5_available()
        payload = {
            "bind_host": self.bind_host,
            "bind_port": self.bind_port,
            "canonical_root": str(self.state.application_root),
            "files": stats.get("total_files", 0),
            "documents": stats.get("total_documents", 0),
            "inbox_count": inbox_count,
            "fts5": bool(fts5_available),
            "projects": [p for p in dict.fromkeys(known) if p],
            "types_breakdown": stats.get("types_breakdown", {}),
            "indexed_projects": stats.get("indexed_projects", []),
        }
        self._json(HTTPStatus.OK, payload)

    def _serve_inbox_list(self, query: Dict[str, List[str]]) -> None:
        status_filter = ""
        if "status" in query and query["status"]:
            status_filter = query["status"][0].strip().upper()
        candidates = list(self.state.inbox.list())
        if status_filter:
            candidates = [c for c in candidates
                          if c.status.value == status_filter]
        candidates.sort(key=lambda c: c.created_at, reverse=True)
        self._json(HTTPStatus.OK, {
            "count": len(candidates),
            "candidates": [_serialize_candidate(c) for c in candidates],
        })

    def _serve_inbox_detail(self, candidate_id: str) -> None:
        try:
            candidate = self.state.inbox.get(candidate_id)
        except ValueError as exc:
            return self._error(HTTPStatus.NOT_FOUND, str(exc))
        payload = _serialize_candidate(candidate)
        if candidate.status == CandidateStatus.VERIFIED:
            try:
                preview = self.state.capture_engine.promote(
                    candidate_id, apply=False
                )
                payload["diff"] = preview.get("diff", "")
                payload["target_file"] = preview.get("target_file", "")
            except ValueError as exc:
                payload["diff"] = ""
                payload["target_file"] = ""
                payload["diff_error"] = str(exc)
        else:
            payload["diff"] = ""
            payload["target_file"] = ""
        self._json(HTTPStatus.OK, payload)

    def _serve_inbox_promote(self, candidate_id: str,
                              _body: Dict[str, Any]) -> None:
        try:
            result = self.state.capture_engine.promote(candidate_id, apply=True)
        except ValueError as exc:
            return self._error(HTTPStatus.CONFLICT, str(exc))
        self._json(HTTPStatus.OK, result)

    def _serve_inbox_reject(self, candidate_id: str,
                             _body: Dict[str, Any]) -> None:
        try:
            result = self.state.capture_engine.reject(candidate_id)
        except ValueError as exc:
            return self._error(HTTPStatus.CONFLICT, str(exc))
        self._json(HTTPStatus.OK, result)

    def _serve_inbox_verify(self, candidate_id: str,
                             _body: Dict[str, Any]) -> None:
        try:
            result = self.state.capture_engine.verify(candidate_id)
        except ValueError as exc:
            return self._error(HTTPStatus.CONFLICT, str(exc))
        self._json(HTTPStatus.OK, result)

    def _serve_search(self, query: Dict[str, List[str]]) -> None:
        q = (query.get("q", [""])[0] or "").strip()
        project = (query.get("project", [""])[0] or "").strip() or None
        if not q:
            return self._error(HTTPStatus.BAD_REQUEST,
                                "Query parameter 'q' is required")
        try:
            results = self.state.service.search(
                query=q, project_id=project, limit=10
            )
        except Exception as exc:  # noqa: BLE001
            return self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
        self._json(HTTPStatus.OK, {
            "query": q,
            "project_id": project,
            "count": len(results),
            "results": [r.to_dict() for r in results],
        })


def make_server(host: str, port: int,
                 application_root: Path,
                 service: Optional[CerberusMemoryService] = None,
                 capture_engine: Optional[AutoCaptureEngine] = None,
                 auth: Optional[AuthState] = None,
                 auth_disabled: bool = False,
                 ) -> ThreadingHTTPServer:
    """Construct a bound, ready-to-serve `ThreadingHTTPServer`.

    Refuses non-loopback hosts unless `allow_lan=True` is also passed via
    the env var `CERBERUS_UI_ALLOW_LAN=1` (operator opt-in).
    Auth defaults to ENABLED. Pass `auth_disabled=True` for tests / dev.
    """
    if not _is_safe_bind_host(host):
        allow_lan = os.environ.get("CERBERUS_UI_ALLOW_LAN", "").lower() in {
            "1", "true", "yes"
        }
        if not allow_lan:
            raise ValueError(
                f"Refusing to bind UI to non-loopback host {host!r}. "
                "Pass --host 127.0.0.1 (or localhost / ::1), or set "
                "CERBERUS_UI_ALLOW_LAN=1 to override (operator-only)."
            )

    state = CerberusInspectorState(
        application_root=application_root,
        service=service,
        capture_engine=capture_engine,
    )
    if auth is None:
        # Honor env-var escape hatch so tests / dev don't need to thread
        # `auth_disabled=True` everywhere.
        env_disable = os.environ.get("CERBERUS_AUTH_DISABLE", "").lower() in {
            "1", "true", "yes"
        }
        auth = AuthState(
            application_root=application_root,
            auth_disabled=auth_disabled or env_disable,
        )

    # Subclass the handler so it carries references to state, auth, bind info.
    handler_cls = type(
        "BoundHandler",
        (CerberusRequestHandler,),
        {
            "state": state,
            "auth": auth,
            "bind_host": host,
            "bind_port": port,
        },
    )

    class _BoundServer(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = False

        def server_bind(self) -> None:
            # Suppress the noisy "SO_REUSEADDR in use" warning under tests.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            super().server_bind()

    server = _BoundServer((host, port), handler_cls)
    return server


def serve_forever(server: ThreadingHTTPServer,
                   ready_event: Optional[threading.Event] = None) -> None:
    """Run `server.serve_forever()`; signal `ready_event` once bound."""
    if ready_event is not None:
        ready_event.set()
    try:
        server.serve_forever()
    finally:
        server.server_close()


# ---------------------------------------------------------------------------
# CLI entry point helpers (consumed by engine/cli.py)
# ---------------------------------------------------------------------------
def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cerberus Inspector — Localhost Management Plane",
    )
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help=f"Bind host (default: {DEFAULT_HOST}; loopback-only by default)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Bind port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true",
                        help="Do not auto-open the system browser on launch.")
    parser.add_argument("--open-browser", dest="open_browser",
                        action="store_true", default=False,
                        help="Auto-open the system browser on launch.")
    parser.add_argument("--canonical-root", default=None,
                        help="Override CERBERUS_ROOT for this session.")
    return parser


def run_from_args(args: argparse.Namespace) -> int:
    application_root = (
        Path(args.canonical_root).resolve()
        if args.canonical_root
        else _resolve_root_or_default(Path.cwd())
    )
    server = make_server(args.host, args.port, application_root)
    url = f"http://{args.host}:{args.port}/"
    print(f"[cerberus] Inspector listening on {url}")
    print(f"[cerberus] Canonical root: {application_root}")
    if not args.no_browser and args.open_browser:
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as exc:  # noqa: BLE001
            print(f"[cerberus] could not open browser: {exc}", file=sys.stderr)
    try:
        serve_forever(server)
    except KeyboardInterrupt:
        print("\n[cerberus] shutting down…")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_argparser()
    args = parser.parse_args(argv)
    return run_from_args(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
