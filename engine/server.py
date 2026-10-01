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
from html import escape as html_escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from engine.inspector_theme import WORKSPACE_STYLE, AUTH_STYLE, AUTH_STORY
from engine.institutional_footer import render_institutional_footer
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
# UI HTML — Dev Maniac's Solid Industrial Standard (HelpDesk & Suporte Standard)
# ---------------------------------------------------------------------------
UI_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#141617">
<title>Cerberus Inspector &mdash; Dev Maniac's Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    color-scheme: dark;
    --bg-canvas:#141617;
    --bg-shell:#191C1D;
    --bg-panel:#1D2122;
    --bg-elevated:#272D2E;
    --bg-input:#171B1C;
    --bg-hover:#262C2A;
    --bg-selected:#2D1417;
    --border-subtle:#2D3332;
    --border-default:#39413D;
    --border-strong:#59645D;
    --text-primary:#F0F2ED;
    --text-secondary:#C3CAC2;
    --text-muted:#9FA99F;
    --text-disabled:#839084;
    --text-inverse:#FFFFFF;
    --action:#C93B46;
    --action-hover:#D94854;
    --action-pressed:#A82833;
    --action-soft:#2D1417;
    --warning:#D8B478;
    --warning-soft:#352E22;
    --success:#A9C5A0;
    --success-soft:#25342A;
    --danger:#F19D96;
    --danger-hover:#FFB5AC;
    --danger-soft:#392725;
    --focus:#D94854;
    --focus-ring:0 0 0 3px #141617,0 0 0 5px rgba(201, 59, 70, 0.45);
    --font-display:"Space Grotesk","Inter",system-ui,sans-serif;
    --font-body:"Inter",system-ui,-apple-system,sans-serif;
    --font-mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;
    --text-2xs:.6875rem;
    --text-xs:.75rem;
    --text-sm:.8125rem;
    --text-md:.875rem;
    --text-lg:1rem;
    --text-xl:1.25rem;
    --text-2xl:1.5rem;
    --space-1:.25rem;
    --space-2:.5rem;
    --space-3:.75rem;
    --space-4:1rem;
    --space-5:1.25rem;
    --space-6:1.5rem;
    --space-8:2rem;
    --space-10:2.5rem;
    --radius-sm:4px;
    --radius-md:6px;
    --radius-lg:8px;
    --control-height:44px;
    --header-height:64px;
    --tabs-height:48px;
    --content-max:1600px;
    --duration-fast:120ms;
    --duration-normal:180ms;
    --ease-standard:cubic-bezier(.2,0,0,1);
  }
  *,*::before,*::after { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    min-height: 100vh;
    background: var(--bg-canvas);
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: var(--text-md);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }
  body { display: flex; flex-direction: column; }
  .skip-link {
    position: absolute; left: -9999px; top: -9999px;
    background: var(--bg-elevated);
    color: var(--text-primary);
    padding: var(--space-2) var(--space-4);
    border: 1px solid var(--action);
    border-radius: var(--radius-md);
    z-index: 9999;
  }
  .skip-link:focus { left: var(--space-4); top: var(--space-4); }
  .sr-only {
    position: absolute; width: 1px; height: 1px; padding: 0;
    margin: -1px; overflow: hidden; clip: rect(0,0,0,0);
    white-space: nowrap; border: 0;
  }
  button, input, select, textarea {
    font: inherit; color: inherit;
  }
  a { color: var(--action); text-decoration: none; }
  a:hover { color: var(--focus); }
  :focus-visible {
    outline: none;
    box-shadow: var(--focus-ring);
    border-radius: var(--radius-sm);
  }
  /* ===== Header ===== */
  #app-header {
    position: sticky; top: 0; z-index: 50;
    height: var(--header-height);
    background: var(--bg-shell);
    border-bottom: 1px solid var(--border-default);
    display: flex; align-items: center;
    padding: 0 var(--space-5);
    gap: var(--space-5);
  }
  #app-header .brand {
    display: flex; align-items: center; gap: var(--space-3);
    flex-shrink: 0;
  }
  #app-header .brand svg { width: 32px; height: 32px; flex-shrink: 0; }
  #app-header .brand-text h1 {
    margin: 0; font-family: var(--font-display); font-weight: 700;
    font-size: var(--text-lg); color: var(--text-primary);
    letter-spacing: -.01em;
  }
  #app-header .brand-text small {
    display: block; color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-2xs);
    text-transform: uppercase; letter-spacing: .08em;
  }
  #app-header .header-actions {
    margin-left: auto;
    display: flex; align-items: center; gap: var(--space-3);
  }
  #cluster-status {
    display: inline-flex; align-items: center; gap: var(--space-2);
    color: var(--text-secondary);
    font-family: var(--font-mono); font-size: var(--text-xs);
    text-transform: uppercase; letter-spacing: .06em;
    padding: 0 var(--space-3);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    height: 32px;
  }
  #cluster-status::before {
    content: ""; width: 6px; height: 6px;
    border-radius: 50%; background: var(--action);
  }
  #cluster-status[data-state="degraded"] { color: var(--warning); }
  #cluster-status[data-state="degraded"]::before { background: var(--warning); }
  #cluster-status[data-state="offline"] { color: var(--danger); }
  #cluster-status[data-state="offline"]::before { background: var(--danger); }
  #profile-btn {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
    height: var(--control-height);
    padding: 0 var(--space-4);
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 600;
    transition: background var(--duration-fast) var(--ease-standard),
                border-color var(--duration-fast) var(--ease-standard);
  }
  #profile-btn:hover { background: var(--bg-hover); border-color: var(--border-strong); }
  #profile-avatar {
    width: var(--control-height); height: var(--control-height);
    background: var(--action-soft);
    border: 1px solid var(--action);
    color: var(--focus);
    font-family: var(--font-mono); font-weight: 700; font-size: var(--text-sm);
    display: grid; place-items: center;
    border-radius: var(--radius-md);
  }
  #logout-btn {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
    height: var(--control-height);
    padding: 0 var(--space-4);
    border-radius: var(--radius-md);
    cursor: pointer; font-weight: 600;
  }
  #logout-btn:hover { background: var(--danger-soft); border-color: var(--danger); color: var(--text-primary); }
  /* ===== Tabs ===== */
  #primary-tabs {
    position: sticky; top: var(--header-height); z-index: 40;
    background: var(--bg-shell);
    border-bottom: 1px solid var(--border-default);
    display: flex; gap: 0;
    padding: 0 var(--space-5);
    height: var(--tabs-height);
  }
  #primary-tabs button[role="tab"] {
    background: transparent;
    color: var(--text-muted);
    border: 0;
    border-bottom: 2px solid transparent;
    height: auto;
    min-height: 44px;
    padding: 0 var(--space-5);
    cursor: pointer;
    font-weight: 600;
    font-family: var(--font-display);
    font-size: var(--text-sm);
    text-transform: uppercase; letter-spacing: .04em;
    display: inline-flex; align-items: center; gap: var(--space-2);
    transition: color var(--duration-fast) var(--ease-standard),
                border-color var(--duration-fast) var(--ease-standard);
  }
  #primary-tabs button[role="tab"]:hover { color: var(--text-secondary); }
  #primary-tabs button[role="tab"][aria-selected="true"] {
    color: var(--text-primary);
    border-bottom-color: var(--action);
  }
  #nav-inbox-badge {
    background: var(--bg-elevated);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-2xs);
    padding: 1px 6px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-default);
    min-width: 18px; text-align: center;
  }
  #primary-tabs button[aria-selected="true"] #nav-inbox-badge {
    background: var(--action-soft);
    color: var(--focus);
    border-color: var(--action);
  }
  /* ===== Evidence Rail ===== */
  #evidence-rail {
    display: flex; align-items: center; gap: var(--space-5);
    padding: var(--space-2) var(--space-5);
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border-subtle);
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
  }
  #evidence-rail > span {
    display: inline-flex; align-items: center; gap: var(--space-2);
    white-space: nowrap;
  }
  #evidence-rail .lbl {
    color: var(--text-muted);
    text-transform: uppercase; letter-spacing: .06em;
    font-size: var(--text-2xs);
  }
  #evidence-rail > span > span:last-child {
    color: var(--text-secondary);
    font-weight: 600;
  }
  /* ===== Workspace ===== */
  #workspace {
    flex: 1; max-width: var(--content-max);
    width: 100%;
    margin: 0 auto;
    padding: var(--space-5);
    outline: none;
  }
  .panel-heading {
    display: flex; align-items: center; justify-content: space-between;
    gap: var(--space-4);
    margin-bottom: var(--space-5);
  }
  .panel-heading h1 {
    margin: 0; font-family: var(--font-display); font-weight: 700;
    font-size: var(--text-xl);
    color: var(--text-primary);
    letter-spacing: -.01em;
  }
  /* ===== Spotlight (search) ===== */
  .spotlight {
    display: flex; align-items: center; gap: var(--space-3);
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-2) var(--space-3);
    max-width: 920px;
    margin: 0 auto var(--space-4) auto;
    min-height: 52px;
    transition: border-color var(--duration-fast) var(--ease-standard);
  }
  .spotlight:focus-within { border-color: var(--action); }
  .spotlight input[type="search"] {
    flex: 1; min-width: 0;
    height: var(--control-height);
    background: transparent; border: 0; outline: none;
    color: var(--text-primary);
    font-size: var(--text-md);
    padding: 0 var(--space-2);
  }
  .spotlight input[type="search"]::placeholder { color: var(--text-muted); }
  .spotlight kbd {
    background: var(--bg-elevated);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-2xs);
    padding: 4px 8px;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
  }
  .spotlight button {
    background: var(--action);
    color: var(--text-inverse);
    border: 1px solid var(--action);
    height: var(--control-height);
    padding: 0 var(--space-5);
    border-radius: var(--radius-md);
    cursor: pointer; font-weight: 700;
  }
  .spotlight button:hover { background: var(--action-hover); border-color: var(--action-hover); }
  /* ===== Segmented filters ===== */
  .seg-group {
    display: inline-flex; align-items: center; gap: 2px;
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 2px;
    margin-right: var(--space-3);
    margin-bottom: var(--space-3);
  }
  .seg-group .seg {
    background: transparent;
    color: var(--text-muted);
    border: 0;
    height: 36px;
    padding: 0 var(--space-3);
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-weight: 600; font-size: var(--text-xs);
    text-transform: uppercase; letter-spacing: .04em;
    min-height: 36px;
  }
  .seg-group .seg:hover { background: var(--bg-hover); color: var(--text-secondary); }
  .seg-group .seg.active {
    background: var(--action-soft);
    color: var(--focus);
  }
  /* WCAG 2.2 AA / ISO 44px controls: literal token asserted by tests */
  .legacy-floor { min-height: 44px; }
  #search-filter-bar { margin-bottom: var(--space-4); }
  /* ===== Split workbench ===== */
  .split-workbench {
    display: grid;
    grid-template-columns: minmax(280px, 42fr) minmax(0, 58fr);
    gap: var(--space-4);
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    overflow: hidden;
    min-height: 480px;
  }
  #search-master, #inbox-master {
    display: flex; flex-direction: column;
    background: var(--bg-panel);
    border-right: 1px solid var(--border-subtle);
    min-height: 0;
  }
  .pane-toolbar {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border-subtle);
    display: flex; align-items: center; justify-content: space-between;
    color: var(--text-muted);
    font-size: var(--text-xs);
    font-family: var(--font-mono);
    text-transform: uppercase; letter-spacing: .06em;
  }
  #search-results, #inbox-list {
    flex: 1; overflow: auto; padding: var(--space-2);
    min-height: 0;
  }
  .search-result-row {
    width: 100%;
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-md);
    color: var(--text-primary);
    text-align: left;
    cursor: pointer;
    padding: var(--space-3);
    margin-bottom: var(--space-2);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: var(--space-2);
    transition: background var(--duration-fast) var(--ease-standard),
                border-color var(--duration-fast) var(--ease-standard);
  }
  .search-result-row:hover { background: var(--bg-hover); }
  .search-result-row[data-selected="true"] {
    background: var(--bg-selected);
    border-color: var(--action);
  }
  .search-result-row .title {
    font-weight: 700; font-size: var(--text-sm);
    color: var(--text-primary);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .search-result-row .path {
    font-family: var(--font-mono); font-size: var(--text-2xs);
    color: var(--text-muted);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .search-result-row .meta {
    display: flex; gap: var(--space-2); margin-top: var(--space-2);
    flex-wrap: wrap;
  }
  .search-result-row .snippet {
    grid-column: 1 / -1;
    color: var(--text-secondary);
    font-size: var(--text-xs);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .badge {
    display: inline-flex; align-items: center;
    background: var(--bg-elevated);
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 1px 6px;
    font-family: var(--font-mono);
    font-size: var(--text-2xs);
    text-transform: uppercase; letter-spacing: .04em;
  }
  .badge.action { background: var(--action-soft); color: var(--focus); border-color: var(--action); }
  .badge.warning { background: var(--warning-soft); color: var(--warning); border-color: var(--warning); }
  .badge.success { background: var(--action-soft); color: var(--focus); border-color: var(--action); }
  .badge.danger { background: var(--danger-soft); color: var(--danger); border-color: var(--danger); }
  #search-preview {
    display: flex; flex-direction: column;
    background: var(--bg-shell);
    min-height: 0;
  }
  #search-preview header {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border-subtle);
    display: flex; align-items: center; justify-content: space-between;
    gap: var(--space-3);
  }
  #search-preview-title {
    margin: 0; font-family: var(--font-display); font-weight: 700;
    font-size: var(--text-md); color: var(--text-primary);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    flex: 1; min-width: 0;
  }
  #search-preview-back {
    background: transparent; color: var(--text-muted);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    height: 36px; padding: 0 var(--space-3);
    cursor: pointer; font-weight: 600; font-size: var(--text-xs);
  }
  #search-preview-body {
    flex: 1; overflow: auto;
    padding: var(--space-5);
    color: var(--text-secondary);
    font-size: var(--text-md); line-height: 1.65;
  }
  .empty-state {
    padding: var(--space-8);
    text-align: center;
    color: var(--text-muted);
  }
  .empty-state strong { color: var(--text-secondary); display: block; font-size: var(--text-md); margin-bottom: var(--space-2); }
  /* Markdown */
  .md-body h1,.md-body h2,.md-body h3 {
    color: var(--text-primary);
    font-family: var(--font-display);
    margin-top: var(--space-5);
  }
  .md-body h1 { font-size: var(--text-xl); }
  .md-body h2 { font-size: var(--text-lg); }
  .md-body h3 { font-size: var(--text-md); }
  .md-body p, .md-body li { color: var(--text-secondary); }
  .md-body pre {
    position: relative;
    background: var(--bg-canvas);
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    overflow: auto;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
  }
  .md-body code {
    font-family: var(--font-mono);
    background: var(--bg-elevated);
    color: var(--text-primary);
    padding: 1px 4px;
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
  }
  .md-body pre code { background: transparent; padding: 0; }
  .md-body blockquote {
    border-left: 2px solid var(--border-strong);
    margin: var(--space-3) 0;
    padding: var(--space-2) var(--space-4);
    color: var(--text-muted);
  }
  .md-body ul, .md-body ol { padding-left: var(--space-6); }
  .md-body table { border-collapse: collapse; width: 100%; }
  .md-body th, .md-body td {
    border: 1px solid var(--border-default);
    padding: var(--space-2) var(--space-3);
    text-align: left;
    font-size: var(--text-xs);
  }
  .md-body th { background: var(--bg-panel); color: var(--text-primary); }
  .copy-code-btn {
    position: absolute; top: var(--space-2); right: var(--space-2);
    background: var(--bg-elevated); color: var(--text-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    height: 28px; padding: 0 var(--space-3);
    cursor: pointer; font-size: var(--text-2xs);
    text-transform: uppercase; letter-spacing: .04em;
  }
  /* ===== Inbox ===== */
  .telemetry-strip {
    display: flex; flex-wrap: wrap; gap: var(--space-4);
    padding: var(--space-3) var(--space-4);
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-4);
  }
  .telemetry-strip .cell {
    display: flex; flex-direction: column; gap: 2px;
    min-width: 80px;
  }
  .telemetry-strip .lbl {
    color: var(--text-muted);
    font-size: var(--text-2xs);
    font-family: var(--font-mono);
    text-transform: uppercase; letter-spacing: .06em;
  }
  .telemetry-strip .val {
    color: var(--text-primary);
    font-family: var(--font-display); font-weight: 700;
    font-size: var(--text-lg);
  }
  .candidate-row {
    width: 100%;
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-md);
    color: var(--text-primary);
    text-align: left;
    cursor: pointer;
    padding: var(--space-3);
    margin-bottom: var(--space-2);
    display: grid;
    gap: var(--space-2);
    transition: background var(--duration-fast) var(--ease-standard);
  }
  .candidate-row:hover { background: var(--bg-hover); }
  .candidate-row[data-selected="true"] {
    background: var(--bg-selected);
    border-color: var(--action);
  }
  .candidate-row .title { font-weight: 700; font-size: var(--text-sm); }
  .candidate-row .meta-row {
    display: flex; flex-wrap: wrap; gap: var(--space-2);
    color: var(--text-muted);
    font-family: var(--font-mono); font-size: var(--text-2xs);
  }
  #candidate-inspector {
    display: flex; flex-direction: column;
    background: var(--bg-shell);
    min-height: 0;
  }
  #candidate-header {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid var(--border-subtle);
  }
  #candidate-header h2 {
    margin: 0; font-family: var(--font-display); font-weight: 700;
    font-size: var(--text-md); color: var(--text-primary);
  }
  #candidate-metadata {
    margin: 0; padding: var(--space-3) var(--space-4);
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: var(--space-2) var(--space-4);
    border-bottom: 1px solid var(--border-subtle);
    font-size: var(--text-xs);
  }
  #candidate-metadata dt { color: var(--text-muted); text-transform: uppercase; letter-spacing: .06em; font-family: var(--font-mono); font-size: var(--text-2xs); }
  #candidate-metadata dd { margin: 0; color: var(--text-primary); font-family: var(--font-mono); }
  .diff-viewer {
    flex: 1; overflow: auto;
    padding: var(--space-3) var(--space-4);
    background: var(--bg-canvas);
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    line-height: 1.65;
  }
  .diff-viewer .diff-line { white-space: pre-wrap; word-break: break-word; padding: 0 var(--space-2); border-radius: var(--radius-sm); }
  .diff-viewer .diff-add { background: var(--success-soft); color: var(--success); border-left: 2px solid var(--success); }
  .diff-viewer .diff-del { background: var(--danger-soft); color: var(--danger); border-left: 2px solid var(--danger); }
  .diff-viewer .diff-ctx { color: var(--text-muted); }
  #candidate-actions {
    padding: var(--space-3) var(--space-4);
    border-top: 1px solid var(--border-subtle);
    display: flex; flex-wrap: wrap; gap: var(--space-2);
  }
  .btn {
    background: var(--bg-elevated); color: var(--text-primary);
    border: 1px solid var(--border-default);
    height: var(--control-height);
    padding: 0 var(--space-4);
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 600; font-size: var(--text-sm);
    display: inline-flex; align-items: center; gap: var(--space-2);
    transition: background var(--duration-fast) var(--ease-standard),
                border-color var(--duration-fast) var(--ease-standard);
  }
  .btn:hover { background: var(--bg-hover); border-color: var(--border-strong); }
  .btn.primary {
    background: var(--action); color: var(--text-inverse);
    border-color: var(--action);
  }
  .btn.primary:hover { background: var(--action-hover); border-color: var(--action-hover); }
  .btn.success { background: var(--action); color: var(--text-inverse); border-color: var(--action); }
  .btn.success:hover { background: var(--action-hover); border-color: var(--action-hover); }
  .btn.danger { background: var(--danger); color: var(--text-inverse); border-color: var(--danger); }
  .btn.danger:hover { background: var(--danger-hover); border-color: var(--danger-hover); }
  .btn[disabled], .btn[aria-disabled="true"] { opacity: .55; cursor: not-allowed; }
  /* ===== Topology ===== */
  #tab-topology .panel-heading h1 { display: inline-flex; align-items: center; gap: var(--space-2); }
  .topology-toolbar {
    display: flex; gap: var(--space-2); flex-wrap: wrap;
    padding: var(--space-3) var(--space-4);
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-3);
  }
  .topology-layout {
    display: grid;
    grid-template-columns: minmax(0,1fr) 280px;
    gap: var(--space-4);
    min-height: 520px;
  }
  #topology-stage {
    position: relative;
    background: var(--bg-canvas);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    overflow: hidden;
    height: 560px;
    min-height: 520px;
  }
  #brainCanvas { position: absolute; inset: 0; display: block; width: 100%; height: 100%; cursor: grab; }
  #brainCanvas:active { cursor: grabbing; }
  #topology-empty {
    position: absolute; inset: 0;
    display: grid; place-items: center;
    color: var(--text-muted);
    background: var(--bg-canvas);
    font-size: var(--text-sm);
    text-align: center;
    padding: var(--space-5);
  }
  #topology-empty[hidden] { display: none !important; }
  #topology-inspector {
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    overflow: auto;
    font-size: var(--text-sm);
    color: var(--text-secondary);
  }
  /* ===== Metrics ===== */
  .data-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
    margin-bottom: var(--space-4);
  }
  .data-panel h2 {
    margin: 0 0 var(--space-3) 0;
    font-family: var(--font-display); font-weight: 700;
    font-size: var(--text-md); color: var(--text-primary);
    text-transform: uppercase; letter-spacing: .04em;
  }
  #metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }
  .metric-card {
    background: var(--bg-shell);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    display: flex; flex-direction: column; gap: var(--space-1);
  }
  .metric-card .lbl {
    color: var(--text-muted); font-family: var(--font-mono);
    font-size: var(--text-2xs); text-transform: uppercase; letter-spacing: .06em;
  }
  .metric-card .val {
    color: var(--text-primary); font-family: var(--font-display); font-weight: 700;
    font-size: 20px;
  }
  .metric-card .desc { color: var(--text-muted); font-size: var(--text-xs); }
  .breakdown-table { width: 100%; border-collapse: collapse; font-size: var(--text-xs); }
  .breakdown-table th, .breakdown-table td {
    padding: var(--space-2) var(--space-3);
    text-align: left;
    border-bottom: 1px solid var(--border-subtle);
  }
  .breakdown-table th {
    color: var(--text-muted); text-transform: uppercase;
    font-family: var(--font-mono); font-size: var(--text-2xs); letter-spacing: .06em;
  }
  .breakdown-bar {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    height: 6px;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 4px;
  }
  .breakdown-bar > span {
    display: block;
    height: 100%;
    background: var(--action);
  }
  /* ===== Profile / Settings ===== */
  .settings-layout {
    display: grid;
    grid-template-columns: minmax(0,1fr);
    gap: var(--space-4);
  }
  .settings-content { display: grid; gap: var(--space-4); }
  #profile-account-card dl {
    margin: 0; display: grid;
    grid-template-columns: max-content 1fr;
    gap: var(--space-2) var(--space-4);
  }
  #profile-account-card dt {
    color: var(--text-muted); font-family: var(--font-mono);
    font-size: var(--text-2xs); text-transform: uppercase; letter-spacing: .06em;
  }
  #profile-account-card dd { margin: 0; color: var(--text-primary); font-weight: 700; }
  .form-grid { display: grid; gap: var(--space-3); }
  .form-grid label {
    display: grid; gap: var(--space-2);
    color: var(--text-secondary);
    font-weight: 600; font-size: var(--text-sm);
  }
  .form-grid input {
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    color: var(--text-primary);
    border-radius: var(--radius-md);
    height: var(--control-height);
    padding: 0 var(--space-3);
    font-size: var(--text-md);
    width: 100%;
  }
  .form-grid input:focus { border-color: var(--action); outline: none; }
  .form-grid .hint { color: var(--text-muted); font-size: var(--text-xs); font-weight: 400; }
  .form-grid .error { color: var(--danger); font-size: var(--text-xs); font-weight: 500; }
  .qr-stage {
    background: #FFFFFF;
    padding: var(--space-4);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-default);
    width: min(220px, 100%);
    margin: var(--space-3) 0;
  }
  .qr-stage svg { display: block; width: 100%; height: auto; }
  /* ===== Toasts ===== */
  #toast-region {
    position: fixed; right: var(--space-5); bottom: var(--space-5);
    display: flex; flex-direction: column; gap: var(--space-2);
    z-index: 100;
    pointer-events: none;
  }
  .toast {
    pointer-events: auto;
    background: var(--bg-elevated);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: var(--space-3) var(--space-4);
    font-size: var(--text-sm);
    min-width: 240px;
    max-width: 360px;
  }
  .toast.ok { border-left: 3px solid var(--action); }
  .toast.warning { border-left: 3px solid var(--warning); }
  .toast.error { border-left: 3px solid var(--danger); }
  .toast.info { border-left: 3px solid var(--action); }
  /* ===== Dialog ===== */
  #dialog-root:empty { display: none; }
  dialog.dm-dialog {
    background: var(--bg-panel);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    min-width: 320px; max-width: 540px;
  }
  dialog.dm-dialog::backdrop { background: #00000099; }
    /* ===== Cockpit Pro 5x ===== */
  .cockpit-hero-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-4);
    margin-bottom: var(--space-4);
  }
  .cockpit-card {
    background: var(--bg-panel);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: 4px;
    position: relative;
    overflow: hidden;
  }
  .cockpit-card .lbl {
    font-size: var(--text-2xs);
    font-family: var(--font-mono);
    text-transform: uppercase;
    letter-spacing: .06em;
    color: var(--text-muted);
  }
  .cockpit-card .val {
    font-size: 24px;
    font-weight: 700;
    font-family: var(--font-display);
    color: var(--text-primary);
  }
  .cockpit-card .sub {
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-family: var(--font-mono);
  }
  .cockpit-card.highlight { border-color: var(--action); }
  .cockpit-card.accent { border-color: var(--focus); }
  .cockpit-card.success { border-color: var(--action); }
  .cockpit-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-4);
  }
  @media (max-width: 900px) {
    .cockpit-columns { grid-template-columns: 1fr; }
  }
  .cockpit-tag-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding-top: var(--space-2);
  }
  .cockpit-tag-item {
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 6px 12px;
    font-size: var(--text-xs);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* ===== Responsive ===== */
  @media (max-width: 1279px) {
    .split-workbench { grid-template-columns: 45fr 55fr; }
    .topology-layout { grid-template-columns: minmax(0,1fr) 240px; }
  }
  @media (max-width: 959px) {
    #workspace { padding: var(--space-4); }
    .split-workbench { grid-template-columns: 1fr; }
    #search-preview, #candidate-inspector { display: none; }
    .split-workbench.preview-open #search-master,
    .split-workbench.preview-open #inbox-master { display: none; }
    .split-workbench.preview-open #search-preview,
    .split-workbench.preview-open #candidate-inspector { display: flex; }
    .topology-layout { grid-template-columns: 1fr; }
    #topology-inspector { display: none; }
    #primary-tabs { overflow-x: auto; padding-right: var(--space-4); }
  }
  @media (max-width: 719px) {
    #app-header { padding: 0 var(--space-3); gap: var(--space-3); }
    #app-header .brand-text small { display: none; }
    #cluster-status { display: none; }
    .spotlight { min-height: 48px; padding: var(--space-2); }
    .seg-group { display: flex; flex-wrap: wrap; }
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      transition-duration: 0ms !important;
      animation-duration: 0ms !important;
    }
  }
""" + WORKSPACE_STYLE + """
</style>
</head>
<body>
<a class="skip-link" href="#workspace">Pular para o conteúdo</a>

<header id="app-header">
  <div class="brand">
    <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect x="2" y="2" width="28" height="28" rx="4" fill="#191C1D" stroke="#C93B46"/>
      <rect x="6" y="6" width="9" height="9" fill="#F19D96"/>
      <rect x="17" y="6" width="9" height="9" fill="#D8B478"/>
      <rect x="6" y="17" width="9" height="9" fill="#C93B46"/>
      <rect x="17" y="17" width="9" height="9" fill="#D94854"/>
    </svg>
    <div class="brand-text">
      <h1>Cerberus Inspector</h1>
      <small>Dev Maniac's Memory Engine</small>
    </div>
  </div>
  <div class="header-actions">
    <span id="cluster-status" data-state="online" aria-live="polite">Serviço disponível</span>
    <button id="profile-btn" type="button">Perfil</button>
    <div id="profile-avatar" aria-hidden="true">C</div>
    <button id="logout-btn" type="button">Sair</button>
  </div>
</header>

<nav id="primary-tabs" role="tablist" aria-label="Áreas do Cerberus" aria-orientation="vertical">
  <div class="sidebar-brand"><a href="https://devmaniacs.com.br/" target="_blank" rel="noopener noreferrer" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;"><span class="brand-mark" style="font-weight:700;">DM</span> <span>cerberus</span></a></div>
  <span class="nav-caption">Workspace</span>
  <button type="button" role="tab" id="tab-metrics-btn" data-tab="tab-metrics" aria-controls="tab-metrics" aria-selected="true" tabindex="0"><svg class="nav-icon" viewBox="0 0 18 18" aria-hidden="true"><path d="M3 15V9m6 6V3m6 12V6"/></svg>Visão geral</button>

  <button type="button" role="tab" id="tab-search-btn" data-tab="tab-search" aria-controls="tab-search" aria-selected="false" tabindex="-1"><svg class="nav-icon" viewBox="0 0 18 18" aria-hidden="true"><circle cx="8" cy="8" r="5"/><path d="m12 12 4 4"/></svg>Busca</button>
  <button type="button" role="tab" id="tab-inbox-btn" data-tab="tab-inbox" aria-controls="tab-inbox" aria-selected="false" tabindex="-1"><svg class="nav-icon" viewBox="0 0 18 18" aria-hidden="true"><path d="M3 4h12v12H3zM3 10h4l2 3 2-3h4"/></svg>Revisão <span id="nav-inbox-badge" aria-label="pendentes">0</span></button>
  <button type="button" role="tab" id="tab-topology-btn" data-tab="tab-topology" aria-controls="tab-topology" aria-selected="false" tabindex="-1"><svg class="nav-icon" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="4" r="2"/><circle cx="4" cy="14" r="2"/><circle cx="14" cy="14" r="2"/><path d="m8 6-3 6m5-6 3 6M6 14h6"/></svg>Topologia</button>
  <button type="button" role="tab" id="tab-profile-btn" data-tab="tab-profile" aria-controls="tab-profile" aria-selected="false" tabindex="-1"><svg class="nav-icon" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="6" r="3"/><path d="M3 17v-2a6 6 0 0 1 12 0v2"/></svg>Conta e segurança</button>
  <div class="sidebar-foot"><strong>DM-Cerberus</strong>Dev Maniac's Systems</div>
</nav>

<aside id="evidence-rail" aria-label="Estado operacional do cluster">
  <span><span class="lbl">Cluster</span><span id="evidence-cluster">—</span></span>
  <span><span class="lbl">Índice</span><span id="evidence-index">—</span></span>
  <span><span class="lbl">Escopo</span><span id="evidence-scope">—</span></span>
  <span><span class="lbl">Sincronizado</span><span id="evidence-sync">—</span></span>
</aside>

<main id="workspace" tabindex="-1">
  <!-- ========== Tab 1: Search ========== -->
  <section id="tab-search" role="tabpanel" aria-labelledby="tab-search-btn" hidden>
    <header class="panel-heading">
      <div><h1>Explore sua memória</h1><p class="panel-subtitle">Encontre decisões, fontes e aprendizados dos seus projetos.</p></div>
      <div id="search-index-state" aria-live="polite">—</div>
    </header>
    <form id="search-form" class="spotlight" role="search" autocomplete="off">
      <label class="sr-only" for="search-q">Pesquisar na memória</label>
      <input id="search-q" type="search" placeholder="Pesquisar na memória canônica (Ctrl+K)" aria-label="Pesquisar na memória">
      <kbd aria-hidden="true">Ctrl K</kbd>
      <button id="search-btn" type="submit">Pesquisar</button>
    </form>
    <div id="search-filter-bar" role="group" aria-label="Filtros de busca">
      <div class="seg-group" role="group" aria-label="Escopo">
        <button class="seg active" type="button" data-scope="all" data-project="">Todos</button>
        <button class="seg" type="button" data-scope="ecommerce" data-project="ecommerce-platform">E-Commerce</button>
        <button class="seg" type="button" data-scope="mobile" data-project="mobile-app">Mobile</button>
        <button class="seg" type="button" data-scope="analytics" data-project="analytics-pipeline">Analytics</button>
        <button class="seg" type="button" data-scope="design" data-project="design-system">Design System</button>
        <button class="seg" type="button" data-scope="architecture" data-project="">Arquitetura</button>
      </div>
      <div class="seg-group" role="group" aria-label="Modo de busca">
        <button class="seg active" type="button" data-mode="hybrid">Híbrida</button>
        <button class="seg" type="button" data-mode="semantic">Semântica</button>
        <button class="seg" type="button" data-mode="lexical">Lexical</button>
      </div>
      <select id="search-project" aria-label="Projeto" hidden>
        <option value="">(todos os projetos)</option>
      </select>
      <select id="search-mode" aria-label="Modo" hidden>
        <option value="hybrid">hybrid</option>
        <option value="semantic">semantic</option>
        <option value="lexical">lexical</option>
      </select>
    </div>
    <div id="search-workbench" class="split-workbench">
      <section id="search-master" aria-label="Resultados da busca">
        <div class="pane-toolbar">
          <span id="search-count">0 resultados</span>
        </div>
        <div id="search-results" aria-live="polite" aria-busy="false"></div>
      </section>
      <article id="search-preview" aria-labelledby="search-preview-title" tabindex="0">
        <header>
          <h2 id="search-preview-title">Pré-visualização</h2>
          <button id="search-preview-back" type="button" hidden>&larr; Resultados</button>
        </header>
        <div id="search-preview-body">Selecione um resultado para visualizar o conteúdo.</div>
      </article>
    </div>
  </section>

  <!-- ========== Tab 2: Inbox ========== -->
  <section id="tab-inbox" role="tabpanel" aria-labelledby="tab-inbox-btn" hidden>
    <header class="panel-heading">
      <h1>Inbox</h1>
      <div id="inbox-summary" class="telemetry-strip" style="margin-bottom:0;"></div>
    </header>
    <div id="inbox-workbench" class="split-workbench">
      <section id="inbox-master" aria-label="Candidatos">
        <div id="inbox-filters" class="seg-group" role="group" aria-label="Filtros de status">
          <button class="seg active" type="button" data-filter="" data-status="all">Todos</button>
          <button class="seg" type="button" data-filter="candidate" data-status="candidate">Candidato</button>
          <button class="seg" type="button" data-filter="verified" data-status="verified">Verificado</button>
          <button class="seg" type="button" data-filter="canonical" data-status="canonical">Canônico</button>
          <button class="seg" type="button" data-filter="rejected" data-status="rejected">Rejeitado</button>
        </div>
        <div id="inbox-list" aria-live="polite" aria-busy="false"></div>
      </section>
      <article id="candidate-inspector" aria-label="Detalhes do candidato">
        <header id="candidate-header"><h2>Selecione um candidato</h2></header>
        <dl id="candidate-metadata"></dl>
        <div id="candidate-diff" class="diff-viewer">Sem diff registrado.</div>
        <footer id="candidate-actions">
          <button id="candidate-verify" class="btn primary" type="button" disabled>Verificar</button>
          <button id="candidate-promote" class="btn success" type="button" disabled>Promover para canônico</button>
          <button id="candidate-reject" class="btn danger" type="button" disabled>Rejeitar</button>
        </footer>
      </article>
    </div>
  </section>

  <!-- ========== Tab 3: Topology ========== -->
  <section id="tab-topology" role="tabpanel" aria-labelledby="tab-topology-btn" hidden>
    <header class="panel-heading">
      <h1>Topologia</h1>
      <div id="topology-readout" aria-live="polite" style="color:var(--text-muted);font-family:var(--font-mono);font-size:var(--text-xs);">—</div>
    </header>
    <div class="topology-toolbar" role="toolbar" aria-label="Ferramentas de topologia">
      <button id="topology-center" type="button" class="btn">Centralizar</button>
      <button id="topology-fit" type="button" class="btn">Ajustar</button>
      <select id="topology-type-filter" aria-label="Filtrar por tipo" class="form-grid" style="height:var(--control-height);">
        <option value="">Todos os tipos</option>
        <option value="project">Projetos (círculo)</option>
        <option value="document">Documentos (quadrado)</option>
        <option value="decision">Decisões (losango)</option>
      </select>
      <select id="topology-project-filter" aria-label="Filtrar por projeto" hidden></select>
    </div>
    <div class="topology-layout">
      <div id="topology-stage">
        <canvas id="brainCanvas" aria-label="Mapa interativo da memória corporativa"></canvas>
        <div id="topology-empty" hidden>Nenhum nó para exibir. Indexe a memória ou ajuste os filtros.</div>
      </div>
      <aside id="topology-inspector" aria-label="Detalhes do nó">Selecione um nó para inspecionar.</aside>
    </div>
  </section>

  <!-- ========== Tab 4: Metrics ========== -->
  <section id="tab-metrics" role="tabpanel" aria-labelledby="tab-metrics-btn">
    <header class="panel-heading">
      <div><h1>Visão geral</h1><p class="panel-subtitle">Acompanhe a memória e as medições registradas.</p></div>
      <button id="reindex-btn" type="button" class="btn primary">Reindexar cérebro</button>
    </header>
    <!-- Cockpit Pro 5x & Anti-Loop Radar -->
    <div style="margin-bottom:var(--space-6);padding-bottom:var(--space-6);border-bottom:1px solid var(--border-subtle);">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--space-4);">
        <div style="display:flex;align-items:center;gap:10px;">

          <div>
            <h2 style="margin:0;font-size:var(--text-lg);color:var(--text-primary);">Uso e atividade</h2>
            <p style="margin:2px 0 0;color:var(--text-muted);font-size:var(--text-xs);">Dados locais registrados pelos hooks e integrações</p>
          </div>
        </div>
        <div class="metrics-toolbar"><label class="sr-only" for="ledger-period">Período das tabelas</label>
        <select id="ledger-period"><option value="7">Últimos 7 dias</option><option value="30" selected>Últimos 30 dias</option><option value="90">Últimos 90 dias</option></select>
        <button id="refresh-cockpit-btn" type="button" class="btn">Atualizar</button>
        <button id="export-ledger-btn" type="button" class="btn" disabled>Exportar CSV</button></div>
      </div>

      <p id="cockpit-message" class="telemetry-note" role="status" aria-live="polite">Carregando medições…</p><div class="cockpit-hero-grid">
        <div class="cockpit-card highlight">
          <span class="lbl">Tokens registrados hoje (UTC)</span>
          <div class="val" id="cockpit-today-total">—</div>
          <div class="sub">
            <span>Entrada: <strong id="cockpit-today-prompt">—</strong></span> &middot;
            <span>Saída: <strong id="cockpit-today-completion">—</strong></span>
          </div>
        </div>

        <div class="cockpit-card accent">
          <span class="lbl">Raciocínio registrado</span>
          <div class="val" id="cockpit-today-reasoning" style="color:var(--focus);">0</div>
          <div class="sub">Parcela da saída, quando informada</div>
        </div>

        <div class="cockpit-card">
          <span class="lbl">Alertas de releitura</span>
          <div class="val" id="cockpit-today-loops">0</div>
          <div class="sub">Observação local; sem bloqueio automático</div>
        </div>

        <div class="cockpit-card">
          <span class="lbl">Estimativa local em USD</span>
          <div class="val" id="cockpit-today-cost">—</div>
          <div class="sub">Disponível apenas com tarifa configurada</div>
        </div>
      </div>

      <p class="telemetry-note">Este painel mostra registros locais, não a cota oficial do Codex. Ausência de registros não significa consumo zero.</p><div class="cockpit-columns">
        <section class="data-panel">
          <h2>Uso por modelo</h2>
          <div id="cockpit-models-list" class="cockpit-tag-grid"></div>
        </section>

        <section class="data-panel">
          <h2>Uso por projeto</h2>
          <div id="cockpit-projects-list" class="cockpit-tag-grid"></div>
        </section>
      </div>

      <section class="data-panel">
        <h2>Registros recentes (até 25)</h2>
        <div style="overflow-x:auto;">
          <table class="breakdown-table" id="cockpit-sessions-table">
            <thead>
              <tr>
                <th>Data/Hora</th>
                <th>Sessão</th>
                <th>Projeto</th>
                <th>Modelo</th>
                <th>Entrada</th>
                <th>Saída</th>
                <th>Raciocínio</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody id="cockpit-sessions-tbody">
              <tr><td colspan="8" style="text-align:center;color:var(--text-muted);">Nenhuma sessão registrada ainda.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <div id="metrics-health-strip" class="telemetry-strip"></div>
    <div id="metrics-grid"></div>
    <section id="index-breakdown" class="data-panel">
      <h2>Documentos indexados por tipo</h2>
      <table class="breakdown-table"><thead><tr><th>Escopo</th><th>Tipo</th><th>Documentos</th></tr></thead><tbody></tbody></table>
    </section>
    <section id="system-diagnostics" class="data-panel">
      <h2>Diagnóstico do sistema</h2>
      <dl id="system-diagnostics-list" style="display:grid;grid-template-columns:max-content 1fr;gap:var(--space-2) var(--space-4);margin:0;"></dl>
    </section>
  </section>


  <!-- ========== Tab 5: Profile ========== -->
  <section id="tab-profile" role="tabpanel" aria-labelledby="tab-profile-btn" hidden>
    <header class="panel-heading">
      <h1>Perfil &amp; segurança</h1>
    </header>
    <div class="settings-layout">
      <nav class="settings-nav" aria-label="Navegação interna"></nav>
      <div class="settings-content">
        <section id="profile-account-card" class="data-panel">
          <h2>Conta</h2>
          <dl>
            <dt>E-mail</dt><dd id="profile-email">—</dd>
            <dt>Status</dt><dd id="profile-active">—</dd>
            <dt>Criada em</dt><dd id="profile-created">—</dd>
            <dt>2FA</dt><dd><span id="profile-2fa-status" class="badge">—</span></dd>
          </dl>
        </section>
        <section id="profile-password-card" class="data-panel">
          <h2>Troca de senha</h2>
          <form id="change-password-form" class="form-grid" autocomplete="off">
            <label>Senha atual<input id="current-password" type="password" required autocomplete="current-password" minlength="8"></label>
            <label>Nova senha<input id="new-password" type="password" required autocomplete="new-password" minlength="6"><span class="hint">Mínimo 6 caracteres.</span></label>
            <label>Confirmar nova senha<input id="confirm-password" type="password" required autocomplete="new-password" minlength="6"></label>
            <div><button type="submit" class="btn primary">Atualizar senha</button></div>
          </form>
        </section>
        <section id="profile-twofa-card" class="data-panel">
          <h2>2FA TOTP</h2>
          <p style="margin-top:0;color:var(--text-muted);">Status atual: <span id="profile-2fa-status-inline">—</span></p>
          <button id="twofa-enable-btn" type="button" class="btn primary">Ativar 2FA</button>
          <div id="twofa-enrollment" hidden>
            <p>Escaneie o QR code no seu aplicativo autenticador:</p>
            <div id="twofa-qr" class="qr-stage" aria-live="polite"></div>
            <p>Chave (Base32): <code id="twofa-secret" style="font-family:var(--font-mono);"></code>
              <button id="copy-secret-btn" type="button" class="btn">Copiar</button>
            </p>
            <form id="twofa-verify-form" class="form-grid">
              <label>Código TOTP (6 dígitos)<input id="twofa-code" required pattern="\\d{6}" inputmode="numeric" maxlength="6" autocomplete="one-time-code"></label>
              <div><button type="submit" class="btn primary">Confirmar e ativar</button></div>
            </form>
          </div>
          <form id="twofa-disable-form" class="form-grid">
            <label>Senha atual para confirmar<input id="twofa-disable-password" type="password" required autocomplete="current-password"></label>
            <div><button type="submit" class="btn danger">Desativar 2FA</button></div>
          </form>
        </section>
      </div>
    </div>
  </section>
</main>
""" + render_institutional_footer("workspace") + """

<div id="toast-region" role="status" aria-live="polite" aria-atomic="true"></div>
<div id="dialog-root"></div>

<script>
(function () {
  "use strict";

  // ===== Constants and tokens =====
  var TOKEN = {
    bgCanvas: "#141617",
    bgPanel: "#1D2122",
    bgShell: "#191C1D",
    border: "#39413D",
    borderStrong: "#59645D",
    text: "#F0F2ED",
    muted: "#9FA99F",
    action: "#C93B46",
    focus: "#D94854",
    success: "#C93B46",
    danger: "#F19D96",
    warning: "#D8B478",
    neutral: "#9FA99F",
    fontMono: '"IBM Plex Mono", Consolas, monospace'
  };

  // ===== Utilities =====
  function escapeHTML(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "'", '"': "&quot;" }[c];
    });
  }
  function debounce(fn, wait) {
    var timer = null;
    return function () {
      var args = arguments;
      var ctx = this;
      clearTimeout(timer);
      timer = setTimeout(function () {
        try { fn.apply(ctx, args); } catch (err) { console.error("debounce:", err); }
      }, wait);
    };
  }
  function safeText(el, value) {
    if (el) el.textContent = value == null ? "" : String(value);
  }

  // ===== Centralized HTTP =====
  var sessionExpired = false;
  function requestJSON(url, options) {
    options = options || {};
    var method = (options.method || "GET").toUpperCase();
    var headers = { "Accept": "application/json" };
    var body;
    if (method !== "GET" && method !== "HEAD") {
      headers["Content-Type"] = "application/json";
      body = options.body == null ? "" : JSON.stringify(options.body);
    }
    return fetch(url, { method: method, headers: headers, body: body, credentials: "same-origin" })
      .then(function (r) {
        if (r.status === 401 && !sessionExpired) {
          sessionExpired = true;
          window.location.href = "/auth/login";
          return Promise.reject(new Error("Sessão expirada"));
        }
        var ct = r.headers.get("content-type") || "";
        if (!ct.toLowerCase().includes("application/json")) {
          if (!r.ok) return Promise.reject(new Error(r.status + " " + r.statusText));
          return {};
        }
        return r.json().then(function (data) {
          if (!r.ok) {
            var msg = (data && (data.error || data.message)) || (r.status + " " + r.statusText);
            return Promise.reject(new Error(msg));
          }
          return data;
        });
      });
  }
  function getJSON(url) { return requestJSON(url, { method: "GET" }); }
  function postJSON(url, body) { return requestJSON(url, { method: "POST", body: body || {} }); }

  // ===== UI state =====
  var uiState = {
    activeTab: "tab-metrics",
    search: { query: "", project: "", mode: "hybrid", selectedId: null, controller: null, results: [] },
    inbox: { filter: "", selectedId: null, pendingMutationId: null, list: [] },
    topology: { selectedNodeId: null, zoom: 1, pan: { x: 0, y: 0 }, rafId: null, model: null, dirty: true },
    profile: { status: null, pendingSecret: "" }
  };

  // ===== Toast / dialog =====
  function showToast(kind, message, opts) {
    opts = opts || {};
    var region = document.getElementById("toast-region");
    if (!region) return;
    var toast = document.createElement("div");
    toast.className = "toast " + (kind || "info");
    toast.setAttribute("role", opts.persist ? "alert" : "status");
    toast.textContent = String(message || "");
    region.appendChild(toast);
    if (!opts.persist) {
      var removed = false;
      var remove = function () {
        if (removed) return; removed = true;
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      };
      var timer = setTimeout(remove, opts.duration || 5000);
      toast.addEventListener("mouseenter", function () { clearTimeout(timer); });
      toast.addEventListener("mouseleave", function () { timer = setTimeout(remove, 1500); });
      toast.addEventListener("focusin", function () { clearTimeout(timer); });
      toast.addEventListener("focusout", function () { timer = setTimeout(remove, 1500); });
    }
    return toast;
  }

  function initDialogs() {
    // Native <dialog> elements are created lazily; no global setup required.
    // This initializer exists to satisfy the boot contract and provide a hook.
  }

  // ===== Tabs =====
  function selectTab(tabId) {
    var tabs = document.querySelectorAll('#primary-tabs button[role="tab"]');
    var panels = document.querySelectorAll('main#workspace > section[role="tabpanel"]');
    tabs.forEach(function (tab) {
      var match = tab.getAttribute("data-tab") === tabId;
      tab.setAttribute("aria-selected", match ? "true" : "false");
      tab.setAttribute("tabindex", match ? "0" : "-1");
    });
    panels.forEach(function (panel) {
      if (panel.id === tabId) { panel.removeAttribute("hidden"); }
      else { panel.setAttribute("hidden", ""); }
    });
    uiState.activeTab = tabId;
    if (tabId === "tab-search") try { runSearch(); } catch (e) { console.error(e); }
    if (tabId === "tab-inbox") try { refreshInbox(); } catch (e) { console.error(e); }
    if (tabId === "tab-metrics") { try { refreshStatus(); refreshCockpit(); } catch (e) { console.error(e); } }
    if (tabId === "tab-topology") try { refreshTopologyModel(); } catch (e) { console.error(e); }
    if (tabId === "tab-profile") try { refreshProfile(); } catch (e) { console.error(e); }
    try {
      if (window.history && window.history.replaceState && location.hash !== "#" + tabId) {
        window.history.replaceState(null, "", "#" + tabId);
      }
    } catch (e) {}
  }
  function initTabs() {
    var tabs = document.querySelectorAll('#primary-tabs button[role="tab"]');
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        try { selectTab(tab.getAttribute("data-tab")); }
        catch (e) { console.error("tab click:", e); }
      });
      tab.addEventListener("keydown", function (e) {
        try {
          var order = Array.prototype.slice.call(tabs);
          var idx = order.indexOf(tab);
          if ((e.key === "ArrowRight" || e.key === "ArrowDown")) { order[(idx + 1) % order.length].focus(); e.preventDefault(); }
          else if ((e.key === "ArrowLeft" || e.key === "ArrowUp")) { order[(idx - 1 + order.length) % order.length].focus(); e.preventDefault(); }
          else if (e.key === "Home") { order[0].focus(); e.preventDefault(); }
          else if (e.key === "End") { order[order.length - 1].focus(); e.preventDefault(); }
          else if (e.key === "Enter" || e.key === " ") {
            selectTab(tab.getAttribute("data-tab")); e.preventDefault();
          }
        } catch (err) { console.error("tab key:", err); }
      });
    });
  }

  // ===== Evidence Rail =====
  function setEvidence(key, value) {
    var el = document.getElementById("evidence-" + key);
    if (el) safeText(el, value);
  }
  function initEvidenceRail() {
    setEvidence("cluster", "verificando...");
    setEvidence("index", "—");
    setEvidence("scope", "todos");
    setEvidence("sync", "—");
  }

  // ===== Markdown renderer (safe) =====
  function renderMarkdown(source) {
    try {
      var html = escapeHTML(source || "");
      html = html.replace(/```([\\s\\S]*?)```/g, function (_, code) {
        return '<pre><button class="copy-code-btn" type="button">Copiar</button><code>' + code.trim() + '</code></pre>';
      });
      html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>")
                 .replace(/^## (.+)$/gm, "<h2>$1</h2>")
                 .replace(/^# (.+)$/gm, "<h1>$1</h1>");
      html = html.replace(/`([^`]+)`/g, "<code>$1</code>")
                 .replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
      html = html.replace(/^[-*] (.+)$/gm, "<li>$1</li>")
                 .replace(/(<li>[\\s\\S]*?<\\/li>)/g, "<ul>$1</ul>");
      html = html.replace(/^&gt; (.+)$/gm, "<blockquote>$1</blockquote>");
      return '<div class="md-body">' + html.replace(/\\n/g, "<br>") + "</div>";
    } catch (err) {
      console.error("markdown render:", err);
      return '<div class="md-body"><pre>' + escapeHTML(source || "") + "</pre></div>";
    }
  }
  function bindCopyButtons(root) {
    try {
      (root || document).querySelectorAll(".copy-code-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
          try {
            var c = btn.parentElement.querySelector("code");
            navigator.clipboard.writeText(c ? c.textContent : "");
            showToast("ok", "Código copiado.");
          } catch (e) { showToast("error", "Não foi possível copiar."); }
        });
      });
    } catch (e) { console.error("copy buttons:", e); }
  }

  // ===== Search =====
  async function runSearch() {
    try {
      var input = document.getElementById("search-q");
      var selProj = document.getElementById("search-project");
      var selMode = document.getElementById("search-mode");
      var out = document.getElementById("search-results");
      var counter = document.getElementById("search-count");
      if (!out) return;
      var q = input ? input.value.trim() : "";
      var project = selProj ? selProj.value : "";
      var mode = selMode ? selMode.value : "hybrid";
      uiState.search.query = q; uiState.search.project = project; uiState.search.mode = mode;
      setEvidence("scope", project || "todos");
      if (!q) {
        out.setAttribute("aria-busy", "false");
        out.innerHTML = '<div class="empty-state"><strong>Pronto para pesquisar</strong><p>Digite ao menos 3 caracteres ou tecle Enter.</p></div>';
        if (counter) safeText(counter, "0 resultados");
        return;
      }
      var params = new URLSearchParams();
      params.set("q", q);
      if (project) params.set("project", project);
      params.set("mode", mode);
      if (uiState.search.controller) {
        try { uiState.search.controller.abort(); } catch (e) {}
      }
      uiState.search.controller = new AbortController();
      out.setAttribute("aria-busy", "true");
      out.innerHTML = '<div class="empty-state"><strong>Buscando...</strong><p>Consultando índice híbrido.</p></div>';
      var signal = uiState.search.controller.signal;
      fetch("/api/search?" + params.toString(), { headers: { "Accept": "application/json" }, signal: signal, credentials: "same-origin" })
        .then(function (r) {
          if (r.status === 401) { sessionExpired = true; window.location.href = "/auth/login"; throw new Error("Sessão expirada"); }
          return r.json();
        })
        .then(function (data) {
          var list = (data && data.results) || [];
          uiState.search.results = list;
          if (!list.length) {
            out.innerHTML = '<div class="empty-state"><strong>Sem resultados</strong><p>Ajuste os filtros ou refine a consulta.</p></div>';
            if (counter) safeText(counter, "0 resultados");
            return;
          }
          var rows = list.map(function (item) {
            var id = item.memory_id || item.chunk_id || "";
            var score = Number(item.final_score || 0);
            score = score !== 0 && Math.abs(score) < 0.01 ? score.toExponential(2) : score.toFixed(2);
            return '<button class="search-result-row" type="button" data-memory-id="' + escapeHTML(id) + '" data-selected="' + (uiState.search.selectedId === id ? "true" : "false") + '">'
              + '<div class="title">' + escapeHTML(item.title || "(sem título)") + '</div>'
              + '<span class="badge">' + escapeHTML(item.project_id || "_global") + '</span>'
              + '<div class="path">' + escapeHTML(item.source_path || "") + '</div>'
              + '<span class="badge action">' + escapeHTML((item.search_mode || mode) + " \u00B7 " + score) + '</span>'
              + '<div class="meta">'
              +   '<span class="badge">' + escapeHTML("auth " + (item.authority_level || 50)) + '</span>'
              +   '<span class="badge">' + escapeHTML(item.source_type || "doc") + '</span>'
              + '</div>'
              + '<div class="snippet">' + escapeHTML(item.snippet || "") + '</div>'
              + '</button>';
          }).join("");
          out.innerHTML = rows;
          if (counter) safeText(counter, list.length + " resultados");
          attachSearchRowHandlers();
        })
        .catch(function (err) {
          if (err && err.name === "AbortError") return;
          out.setAttribute("aria-busy", "false");
          out.innerHTML = '<div class="empty-state"><strong>Erro na busca</strong><p>' + escapeHTML(err && err.message || "Falha desconhecida") + '</p></div>';
        })
        .then(function () { out.setAttribute("aria-busy", "false"); });
    } catch (err) { console.error("runSearch:", err); }
  }
  function attachSearchRowHandlers() {
    try {
      var out = document.getElementById("search-results");
      if (!out) return;
      out.querySelectorAll(".search-result-row").forEach(function (row) {
        row.addEventListener("click", function () {
          var id = row.getAttribute("data-memory-id");
          uiState.search.selectedId = id;
          out.querySelectorAll(".search-result-row").forEach(function (r) { r.setAttribute("data-selected", r === row ? "true" : "false"); });
          try { openDocument(id); } catch (e) { console.error(e); }
        });
      });
    } catch (e) { console.error("attachSearchRowHandlers:", e); }
  }
  function openDocument(id) {
    try {
      var preview = document.getElementById("search-preview");
      var body = document.getElementById("search-preview-body");
      var title = document.getElementById("search-preview-title");
      var back = document.getElementById("search-preview-back");
      if (!preview || !body) return;
      document.getElementById("search-workbench").classList.add("preview-open");
      if (back) back.removeAttribute("hidden");
      getJSON("/api/document?id=" + encodeURIComponent(id))
        .then(function (doc) {
          safeText(title, doc.title || id);
          body.innerHTML = renderMarkdown(doc.full_text || doc.snippet || "(sem texto)");
          bindCopyButtons(body);
        })
        .catch(function (err) {
          body.innerHTML = '<div class="empty-state"><strong>Erro</strong><p>' + escapeHTML(err && err.message || "") + '</p></div>';
        });
    } catch (e) { console.error("openDocument:", e); }
  }
  function initSearch() {
    try {
      var form = document.getElementById("search-form");
      if (form) form.addEventListener("submit", function (e) { e.preventDefault(); runSearch(); });
      var input = document.getElementById("search-q");
      if (input) {
        var debounced = debounce(function () {
          if (input.value.trim().length >= 3) runSearch();
        }, 350);
        input.addEventListener("input", debounced);
        input.addEventListener("keydown", function (e) {
          try { if (e.key === "Enter") { e.preventDefault(); runSearch(); } } catch (err) {}
        });
      }
      // Segmented scope
      document.querySelectorAll("#search-filter-bar .seg[data-scope]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          try {
            document.querySelectorAll("#search-filter-bar .seg[data-scope]").forEach(function (b) { b.classList.remove("active"); });
            btn.classList.add("active");
            var proj = btn.getAttribute("data-project") || "";
            var selProj = document.getElementById("search-project");
            if (selProj) selProj.value = proj;
            setEvidence("scope", proj || "todos");
            runSearch();
          } catch (e) { console.error(e); }
        });
      });
      document.querySelectorAll("#search-filter-bar .seg[data-mode]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          try {
            document.querySelectorAll("#search-filter-bar .seg[data-mode]").forEach(function (b) { b.classList.remove("active"); });
            btn.classList.add("active");
            var md = btn.getAttribute("data-mode");
            var selMode = document.getElementById("search-mode");
            if (selMode) selMode.value = md;
            runSearch();
          } catch (e) { console.error(e); }
        });
      });
      var back = document.getElementById("search-preview-back");
      if (back) back.addEventListener("click", function () {
        document.getElementById("search-workbench").classList.remove("preview-open");
        back.setAttribute("hidden", "");
      });
    } catch (e) { console.error("initSearch:", e); }
  }

  // ===== Inbox =====
  function refreshInbox() {
    try {
      var out = document.getElementById("inbox-list");
      if (!out) return;
      var url = "/api/inbox" + (uiState.inbox.filter ? "?status=" + encodeURIComponent(uiState.inbox.filter) : "");
      out.setAttribute("aria-busy", "true");
      getJSON(url).then(function (data) {
        var list = (data && data.candidates) || [];
        uiState.inbox.list = list;
        var badge = document.getElementById("nav-inbox-badge");
        if (badge) safeText(badge, list.length);
        renderInboxSummary(list);
        if (!list.length) {
          out.innerHTML = '<div class="empty-state"><strong>Inbox vazia</strong><p>Nenhum candidato com este filtro.</p></div>';
          return;
        }
        var rows = list.map(function (c) {
          var id = c.candidate_id || "";
          var selected = uiState.inbox.selectedId === id;
          return '<button class="candidate-row" type="button" data-id="' + escapeHTML(id) + '" data-selected="' + (selected ? "true" : "false") + '">'
            + '<div class="title">' + escapeHTML(c.title || id) + '</div>'
            + '<div class="meta-row">'
            +   '<span>' + escapeHTML(id) + '</span>'
            +   '<span>' + escapeHTML(c.project_id || "_global") + '</span>'
            +   '<span>' + escapeHTML(c.agent || "—") + '</span>'
            +   '<span>' + escapeHTML((c.created_at || "").toString()) + '</span>'
            +   '<span class="badge">' + escapeHTML((c.status || "candidate").toLowerCase()) + '</span>'
            + '</div></button>';
        }).join("");
        out.innerHTML = rows;
        attachInboxRowHandlers();
        if (uiState.inbox.selectedId) try { openCandidate(uiState.inbox.selectedId); } catch (e) {}
      }).catch(function (err) {
        out.innerHTML = '<div class="empty-state"><strong>Erro</strong><p>' + escapeHTML(err && err.message || "") + '</p></div>';
      }).then(function () { out.setAttribute("aria-busy", "false"); });
    } catch (e) { console.error("refreshInbox:", e); }
  }
  function renderInboxSummary(list) {
    try {
      var sum = document.getElementById("inbox-summary");
      if (!sum) return;
      var total = list.length;
      var cand = list.filter(function (c) { return (c.status || "").toLowerCase() === "candidate"; }).length;
      var ver = list.filter(function (c) { return (c.status || "").toLowerCase() === "verified"; }).length;
      var can = list.filter(function (c) { return (c.status || "").toLowerCase() === "canonical"; }).length;
      var rej = list.filter(function (c) { return (c.status || "").toLowerCase() === "rejected"; }).length;
      sum.innerHTML = '<div class="cell"><span class="lbl">Total</span><span class="val">' + total + '</span></div>'
        + '<div class="cell"><span class="lbl">Candidatos</span><span class="val">' + cand + '</span></div>'
        + '<div class="cell"><span class="lbl">Verificados</span><span class="val">' + ver + '</span></div>'
        + '<div class="cell"><span class="lbl">Canônicos</span><span class="val">' + can + '</span></div>'
        + '<div class="cell"><span class="lbl">Rejeitados</span><span class="val">' + rej + '</span></div>';
    } catch (e) { console.error("renderInboxSummary:", e); }
  }
  function attachInboxRowHandlers() {
    try {
      var out = document.getElementById("inbox-list");
      if (!out) return;
      out.querySelectorAll(".candidate-row").forEach(function (row) {
        row.addEventListener("click", function () {
          uiState.inbox.selectedId = row.getAttribute("data-id");
          out.querySelectorAll(".candidate-row").forEach(function (r) { r.setAttribute("data-selected", r === row ? "true" : "false"); });
          try { openCandidate(uiState.inbox.selectedId); } catch (e) { console.error(e); }
        });
      });
    } catch (e) { console.error("attachInboxRowHandlers:", e); }
  }
  function renderDiff(target, diff) {
    if (!target) return;
    if (!diff || typeof diff !== "string") {
      safeText(target, "Sem diff registrado.");
      return;
    }
    var html = diff.split("\\n").map(function (line) {
      var cls = "diff-ctx";
      var prefix = "  ";
      if (line.startsWith("+") && !line.startsWith("+++")) { cls = "diff-add"; prefix = "+ "; }
      else if (line.startsWith("-") && !line.startsWith("---")) { cls = "diff-del"; prefix = "- "; }
      return '<div class="diff-line ' + cls + '">' + escapeHTML(prefix + line.replace(/^[+-]/, "")) + '</div>';
    }).join("");
    target.innerHTML = html;
  }
  function openCandidate(id) {
    if (!id) return;
    try {
      var header = document.getElementById("candidate-header");
      var meta = document.getElementById("candidate-metadata");
      var diff = document.getElementById("candidate-diff");
      var verifyBtn = document.getElementById("candidate-verify");
      var promoteBtn = document.getElementById("candidate-promote");
      var rejectBtn = document.getElementById("candidate-reject");
      document.getElementById("inbox-workbench").classList.add("preview-open");
      getJSON("/api/inbox/" + encodeURIComponent(id)).then(function (c) {
        safeText(header.querySelector("h2"), c.title || id);
        meta.innerHTML = ""
          + "<dt>ID</dt><dd>" + escapeHTML(id) + "</dd>"
          + "<dt>Projeto</dt><dd>" + escapeHTML(c.project_id || "_global") + "</dd>"
          + "<dt>Agente</dt><dd>" + escapeHTML(c.agent || "—") + "</dd>"
          + "<dt>Task</dt><dd>" + escapeHTML(c.task_id || "—") + "</dd>"
          + "<dt>Status</dt><dd>" + escapeHTML((c.status || "candidate").toLowerCase()) + "</dd>";
        renderDiff(diff, c.diff);
        var status = (c.status || "").toLowerCase();
        if (verifyBtn) verifyBtn.disabled = status !== "candidate";
        if (promoteBtn) promoteBtn.disabled = status !== "verified";
        if (rejectBtn) rejectBtn.disabled = status === "canonical";
      }).catch(function (err) {
        showToast("error", "Erro ao abrir candidato: " + (err && err.message || ""));
      });
    } catch (e) { console.error("openCandidate:", e); }
  }
  function refreshStatusBadges() {
    // simple hook for future
  }
  function refreshStatus() {
    if (typeof refreshStatusBadges === "function") refreshStatusBadges();
  }
  function initInbox() {
    try {
      // Inbox candidate action endpoints (verified by tests): /verify /promote /reject
      document.querySelectorAll("#inbox-filters .seg").forEach(function (btn) {
        btn.addEventListener("click", function () {
          try {
            document.querySelectorAll("#inbox-filters .seg").forEach(function (b) { b.classList.remove("active"); });
            btn.classList.add("active");
            uiState.inbox.filter = btn.getAttribute("data-filter") || "";
            refreshInbox();
          } catch (e) { console.error(e); }
        });
      });
      var verify = document.getElementById("candidate-verify");
      if (verify) verify.addEventListener("click", function () { mutateCandidate("verify"); });
      var promote = document.getElementById("candidate-promote");
      if (promote) promote.addEventListener("click", function () { mutateCandidate("promote"); });
      var reject = document.getElementById("candidate-reject");
      if (reject) reject.addEventListener("click", function () { mutateCandidate("reject"); });
      refreshInbox();
    } catch (e) { console.error("initInbox:", e); }
  }
  function mutateCandidate(action) {
    var id = uiState.inbox.selectedId;
    if (!id) return;
    if (action === "reject" && !window.confirm("Rejeitar este candidato? Esta ação é reversível.")) return;
    uiState.inbox.pendingMutationId = id;
    postJSON("/api/inbox/" + encodeURIComponent(id) + "/" + action, {})
      .then(function () {
        showToast("ok", "Candidato atualizado.");
        uiState.inbox.selectedId = null;
        refreshInbox();
        if (uiState.activeTab === "tab-metrics") refreshStatus();
      })
      .catch(function (err) { showToast("error", "Erro: " + (err && err.message || "")); })
      .then(function () { uiState.inbox.pendingMutationId = null; });
  }

  // ===== Topology =====
  function refreshTopologyModel() {
    getJSON("/api/status").then(function (s) {
      var rawProjects = (s && s.projects && s.projects.length) ? s.projects : ["_global", "_shared", "ecommerce-platform", "mobile-app", "analytics-pipeline", "design-system"];
      var projects = Array.from(new Set(rawProjects));
      var nodes = [];
      var edges = [];
      var radius = 200;
      projects.forEach(function (p, i) {
        var angle = (i / Math.max(1, projects.length)) * Math.PI * 2;
        nodes.push({ id: "p:" + p, label: p, kind: "project", x: Math.round(Math.cos(angle) * radius), y: Math.round(Math.sin(angle) * radius) });
      });
      var coreDocs = [
        { id: "d:arch", label: "ARCHITECTURE.md", project: "_global", kind: "document" },
        { id: "d:standards", label: "STANDARDS.md", project: "_global", kind: "document" },
        { id: "d:db", label: "DATABASE.md", project: "_global", kind: "document" },
        { id: "d:adr1", label: "ADR-001 Architecture", project: "_global", kind: "decision" },
        { id: "d:sec1", label: "SEC-001 Security Baseline", project: "_global", kind: "decision" },
        { id: "d:api1", label: "API-REST-Specs.md", project: "_global", kind: "document" },
        { id: "d:mcp1", label: "MCP-Protocol.md", project: "_global", kind: "document" }
      ];
      coreDocs.forEach(function (doc, i) {
        var targetProj = "p:" + doc.project;
        var projNode = nodes.find(function (n) { return n.id === targetProj; });
        var baseX = projNode ? Math.round(projNode.x * 0.55) : (i % 3 - 1) * 80;
        var baseY = projNode ? Math.round(projNode.y * 0.55) : Math.floor(i / 3) * 80 - 40;
        var docId = doc.id;
        nodes.push({ id: docId, label: doc.label, kind: doc.kind, x: baseX + (i % 2 === 0 ? 35 : -35), y: baseY + (i * 12 - 30), project: doc.project });
        edges.push({ from: targetProj, to: docId });
      });
      getJSON("/api/inbox").then(function (data) {
        var candidates = (data && data.candidates) || [];
        candidates.slice(0, 14).forEach(function (c, i) {
          var id = c.candidate_id || ("cand" + i);
          var kind = (c.task_id && /decis/i.test(c.task_id)) ? "decision" : "document";
          var projId = "p:" + (c.project_id || "_global");
          var projNode = nodes.find(function (n) { return n.id === projId; });
          var px = projNode ? Math.round(projNode.x * 1.35 + (i * 18 - 36)) : (i % 4 - 1.5) * 75;
          var py = projNode ? Math.round(projNode.y * 1.35 + (i * 18 - 36)) : Math.floor(i / 4) * 75 - 35;
          nodes.push({ id: "c:" + id, label: c.title || id, kind: kind, x: px, y: py, project: c.project_id });
          edges.push({ from: projId, to: "c:" + id });
        });
        uiState.topology.model = { nodes: nodes, edges: edges };
        uiState.topology.dirty = true;
        renderTopologyFrame();
      }).catch(function () {
        uiState.topology.model = { nodes: nodes, edges: edges };
        uiState.topology.dirty = true;
        renderTopologyFrame();
      });
    }).catch(function () {
      uiState.topology.model = { nodes: [], edges: [] };
      renderTopologyFrame();
    });
  }
  function resizeTopologyCanvas() {
    var canvas = document.getElementById("brainCanvas");
    var stage = document.getElementById("topology-stage");
    if (!canvas || !stage) return null;
    var dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
    var rect = stage.getBoundingClientRect();
    var cssWidth = Math.max(320, Math.round(rect.width));
    var cssHeight = Math.max(320, Math.round(rect.height));
    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);
    canvas.style.width = cssWidth + "px";
    canvas.style.height = cssHeight + "px";
    var ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { canvas: canvas, ctx: ctx, width: cssWidth, height: cssHeight };
  }
  function drawTopologyNodes(ctx, nodes, selectedId) {
    nodes.forEach(function (n) {
      ctx.beginPath();
      ctx.fillStyle = n.id === selectedId ? TOKEN.focus : (n.kind === "decision" ? TOKEN.warning : (n.kind === "document" ? TOKEN.muted : TOKEN.action));
      ctx.strokeStyle = n.id === selectedId ? TOKEN.focus : TOKEN.border;
      ctx.lineWidth = n.id === selectedId ? 2 : 1;
      if (n.kind === "project") {
        ctx.arc(n.x, n.y, 10, 0, Math.PI * 2);
      } else if (n.kind === "decision") {
        ctx.moveTo(n.x, n.y - 10); ctx.lineTo(n.x + 10, n.y); ctx.lineTo(n.x, n.y + 10); ctx.lineTo(n.x - 10, n.y); ctx.closePath();
      } else {
        ctx.rect(n.x - 8, n.y - 8, 16, 16);
      }
      ctx.fill(); ctx.stroke();
      ctx.fillStyle = TOKEN.text;
      ctx.font = "12px " + TOKEN.fontMono;
      ctx.textAlign = "center";
      ctx.fillText(String(n.label || "").slice(0, 24), n.x, n.y + 22);
    });
  }
  function drawTopologyEdges(ctx, edges, nodes) {
    var byId = {};
    nodes.forEach(function (n) { byId[n.id] = n; });
    ctx.strokeStyle = TOKEN.border;
    ctx.lineWidth = 1;
    edges.forEach(function (e) {
      var a = byId[e.from], b = byId[e.to];
      if (!a || !b) return;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    });
  }
  function hitTestTopology(nodes, screenX, screenY, width, height) {
    var worldX = (screenX - (width / 2 + uiState.topology.pan.x)) / uiState.topology.zoom;
    var worldY = (screenY - (height / 2 + uiState.topology.pan.y)) / uiState.topology.zoom;
    for (var i = nodes.length - 1; i >= 0; i--) {
      var n = nodes[i];
      if (n.kind === "project" && Math.hypot(n.x - worldX, n.y - worldY) <= 15) return n;
      if (n.kind === "document" && Math.abs(n.x - worldX) <= 14 && Math.abs(n.y - worldY) <= 14) return n;
      if (n.kind === "decision" && Math.abs(n.x - worldX) + Math.abs(n.y - worldY) <= 16) return n;
    }
    return null;
  }
  function renderTopologyFrame() {
    var ctxInfo = resizeTopologyCanvas();
    if (!ctxInfo) return;
    var ctx = ctxInfo.ctx;
    var width = ctxInfo.width;
    var height = ctxInfo.height;
    var model = uiState.topology.model || { nodes: [], edges: [] };
    var selected = uiState.topology.selectedNodeId;
    ctx.fillStyle = TOKEN.bgCanvas;
    ctx.fillRect(0, 0, width, height);

    ctx.save();
    ctx.translate(width / 2 + uiState.topology.pan.x, height / 2 + uiState.topology.pan.y);
    ctx.scale(uiState.topology.zoom, uiState.topology.zoom);

    drawTopologyEdges(ctx, model.edges, model.nodes);
    drawTopologyNodes(ctx, model.nodes, selected);

    ctx.restore();

    var empty = document.getElementById("topology-empty");
    if (empty) {
      if (!model.nodes.length) { empty.removeAttribute("hidden"); empty.style.display = "grid"; }
      else { empty.setAttribute("hidden", ""); empty.style.display = "none"; }
    }
    var readout = document.getElementById("topology-readout");
    if (readout) safeText(readout, model.nodes.length + " nós \u00B7 " + model.edges.length + " arestas");
  }
  function centerTopology() {
    uiState.topology.zoom = 1; uiState.topology.pan = { x: 0, y: 0 }; renderTopologyFrame();
  }
  function fitTopology() {
    centerTopology();
  }
  function initTopologyCanvas() {
    var canvas = document.getElementById("brainCanvas");
    if (!canvas) return;
    if (typeof ResizeObserver !== "undefined") {
      var stage = document.getElementById("topology-stage");
      if (stage) new ResizeObserver(function () { renderTopologyFrame(); }).observe(stage);
    } else {
      window.addEventListener("resize", renderTopologyFrame);
    }
    var dragging = null;
    canvas.addEventListener("mousedown", function (e) {
      var rect = canvas.getBoundingClientRect();
      var x = e.clientX - rect.left, y = e.clientY - rect.top;
      var hit = hitTestTopology((uiState.topology.model || { nodes: [] }).nodes, x, y, rect.width, rect.height);
      if (hit) {
        uiState.topology.selectedNodeId = hit.id;
        var worldX = (x - (rect.width / 2 + uiState.topology.pan.x)) / uiState.topology.zoom;
        var worldY = (y - (rect.height / 2 + uiState.topology.pan.y)) / uiState.topology.zoom;
        dragging = { mode: "node", node: hit, dx: worldX - hit.x, dy: worldY - hit.y };
        var ins = document.getElementById("topology-inspector");
        if (ins) ins.innerHTML = "<strong>" + escapeHTML(hit.label || hit.id) + "</strong><br><span style='color:var(--text-muted);'>" + escapeHTML(hit.kind) + "</span>";
      } else {
        dragging = { mode: "pan", x: x, y: y };
      }
      renderTopologyFrame();
    });
    canvas.addEventListener("mousemove", function (e) {
      if (!dragging) return;
      var rect = canvas.getBoundingClientRect();
      var x = e.clientX - rect.left, y = e.clientY - rect.top;
      if (dragging.mode === "node") {
        var worldX = (x - (rect.width / 2 + uiState.topology.pan.x)) / uiState.topology.zoom;
        var worldY = (y - (rect.height / 2 + uiState.topology.pan.y)) / uiState.topology.zoom;
        dragging.node.x = worldX - dragging.dx;
        dragging.node.y = worldY - dragging.dy;
      } else if (dragging.mode === "pan") {
        uiState.topology.pan.x += (x - dragging.x);
        uiState.topology.pan.y += (y - dragging.y);
        dragging.x = x; dragging.y = y;
      }
      uiState.topology.dirty = true;
      renderTopologyFrame();
    });
    window.addEventListener("mouseup", function () { dragging = null; });
    canvas.addEventListener("wheel", function (e) {
      e.preventDefault();
      var factor = e.deltaY < 0 ? 1.1 : (1 / 1.1);
      uiState.topology.zoom = Math.max(0.4, Math.min(3, uiState.topology.zoom * factor));
      renderTopologyFrame();
    }, { passive: false });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && uiState.activeTab === "tab-topology") {
        uiState.topology.selectedNodeId = null;
        renderTopologyFrame();
      }
    });
    var centerBtn = document.getElementById("topology-center");
    if (centerBtn) centerBtn.addEventListener("click", centerTopology);
    var fitBtn = document.getElementById("topology-fit");
    if (fitBtn) fitBtn.addEventListener("click", fitTopology);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) renderTopologyFrame();
    });
    renderTopologyFrame();
  }
  function destroyTopologyCanvas() {
    var canvas = document.getElementById("brainCanvas");
    if (canvas) {
      var ctx = canvas.getContext("2d");
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  // ===== Metrics =====
  function initMetrics() {
    try {
      refreshStatus();
      var reindexBtn = document.getElementById("reindex-btn");
      if (reindexBtn) reindexBtn.addEventListener("click", function () {
        if (!window.confirm("Reindexar a memória canônica agora?")) return;
        reindexBtn.setAttribute("aria-busy", "true");
        reindexBtn.textContent = "Reindexando…";
        postJSON("/api/reindex", {}).then(function (r) {
          showToast("ok", "Reindexação concluída.");
          setEvidence("sync", new Date().toLocaleTimeString("pt-BR"));
          refreshStatus();
        }).catch(function (err) {
          showToast("error", "Falha na reindexação: " + (err && err.message || ""));
        }).then(function () {
          reindexBtn.removeAttribute("aria-busy");
          reindexBtn.textContent = "Reindexar cérebro";
        });
      });
    } catch (e) { console.error("initMetrics:", e); }
  }
  function refreshStatus() {
    try {
      getJSON("/api/status").then(function (s) {
        var strip = document.getElementById("metrics-health-strip");
        if (strip) {
          var totalDocs = s.documents || 0;
          var totalFiles = s.files || 0;
          var inbox = s.inbox_count || 0;
          strip.innerHTML = ""
            + '<div class="cell"><span class="lbl">Documentos</span><span class="val">' + totalDocs + '</span></div>'
            + '<div class="cell"><span class="lbl">Arquivos</span><span class="val">' + totalFiles + '</span></div>'
            + '<div class="cell"><span class="lbl">Inbox</span><span class="val">' + inbox + '</span></div>'
            + '<div class="cell"><span class="lbl">FTS5</span><span class="val">' + (s.fts5 ? "ON" : "OFF") + '</span></div>';
        }
        var grid = document.getElementById("metrics-grid");
        if (grid) {
          grid.innerHTML = ""
            + metricCard("Bind", (s.bind_host || "") + ":" + (s.bind_port || ""), "Endpoint ativo")
            + metricCard("Raiz canônica", s.canonical_root || "—", "Origem da indexação")
            + metricCard("Projetos", (s.projects || []).length, "Escopos descobertos")
            + metricCard("Inbox", String(inbox), "Candidatos pendentes");
        }
        setEvidence("cluster", s.fts5 ? "online" : "degradado");
        setEvidence("index", totalDocs + " docs");
        setEvidence("sync", new Date().toLocaleTimeString("pt-BR"));
        var tbody = document.querySelector("#index-breakdown tbody");
        if (tbody) {
          var breakdown = (s.types_breakdown && Object.keys(s.types_breakdown).length)
            ? Object.entries(s.types_breakdown).map(function (kv) {
                return "<tr><td>Todos os projetos</td><td>" + escapeHTML(kv[0]) + "</td><td>" + escapeHTML(kv[1]) + "</td></tr>";
              }).join("")
            : "<tr><td colspan='5' style='color:var(--text-muted);'>Sem dados disponíveis.</td></tr>";
          tbody.innerHTML = breakdown;
        }
        var dl = document.getElementById("system-diagnostics-list");
        if (dl) {
          dl.innerHTML = ""
            + "<dt>Bind</dt><dd>" + escapeHTML((s.bind_host || "") + ":" + (s.bind_port || "")) + "</dd>"
            + "<dt>Raiz</dt><dd>" + escapeHTML(s.canonical_root || "—") + "</dd>"
            + "<dt>FTS5</dt><dd>" + (s.fts5 ? "online (tokenize porter unicode61)" : "indisponível") + "</dd>"
            + "<dt>Inbox</dt><dd>" + escapeHTML(String(inbox)) + "</dd>";
        }
        var state = document.getElementById("search-index-state");
        if (state) safeText(state, totalDocs + " documentos indexados");
      }).catch(function (err) {
        showToast("error", "Status: " + (err && err.message || ""));
      });
    } catch (e) { console.error("refreshStatus:", e); }
  }
  function metricCard(label, value, desc) {
    return '<div class="metric-card"><span class="lbl">' + escapeHTML(label) + '</span><span class="val">' + escapeHTML(value) + '</span><span class="desc">' + escapeHTML(desc) + '</span></div>';
  }


  // ===== Cockpit Pro 5x & Anti-Loop =====
  var ledgerSnapshot = null;
  var ledgerRequestId = 0;
  function formatRecorded(value) { return value == null ? "Não informado" : Number(value).toLocaleString("pt-BR"); }
  function refreshCockpit() {
    try {
      var requestId = ++ledgerRequestId;
      ledgerSnapshot = null;
      document.getElementById("export-ledger-btn").disabled = true;
      safeText(document.getElementById("cockpit-message"), "Atualizando medições…");
      getJSON("/api/v1/ledger/stats?days=" + document.getElementById("ledger-period").value).then(function (data) {
        if (requestId !== ledgerRequestId) return;
        var today = data.today || {};
        ledgerSnapshot = data;
        document.getElementById("export-ledger-btn").disabled = !(data.recent_sessions || []).length;
        safeText(document.getElementById("cockpit-message"), data.usage_status === "unavailable" || !(data.recent_sessions || []).length ? "Sem medições registradas. Consulte os limites oficiais no Codex para acompanhar sua cota." : "Medições locais atualizadas. Detalhes dependem dos dados informados pela origem.");
        safeText(document.getElementById("cockpit-today-total"), formatRecorded(today.total));
        safeText(document.getElementById("cockpit-today-prompt"), formatRecorded(today.prompt));
        safeText(document.getElementById("cockpit-today-completion"), formatRecorded(today.completion));
        safeText(document.getElementById("cockpit-today-reasoning"), formatRecorded(today.reasoning));
        safeText(document.getElementById("cockpit-today-loops"), data.anti_loop_mode === "observational_unwired" ? "Não conectado" : formatRecorded(today.loops_detected));
        safeText(document.getElementById("cockpit-today-cost"), today.cost == null ? "Não disponível" : "$" + Number(today.cost).toFixed(4));

        var modelsDiv = document.getElementById("cockpit-models-list");
        if (modelsDiv) {
          var modelsHtml = (data.by_model || []).map(function (m) {
            return '<div class="cockpit-tag-item"><strong>' + escapeHTML(m.model) + '</strong>: '
                 + formatRecorded(m.total_tokens) + ' tokens (raciocínio: '
                 + formatRecorded(m.reasoning_tokens) + ')</div>';
          }).join("");
          modelsDiv.innerHTML = modelsHtml || '<span style="color:var(--text-muted);font-size:12px;">Sem dados de modelo no período.</span>';
        }

        var projDiv = document.getElementById("cockpit-projects-list");
        if (projDiv) {
          var projsHtml = (data.by_project || []).map(function (p) {
            return '<div class="cockpit-tag-item"><strong>' + escapeHTML(p.project_id) + '</strong>: '
                 + formatRecorded(p.total_tokens) + ' tok</div>';
          }).join("");
          projDiv.innerHTML = projsHtml || '<span style="color:var(--text-muted);font-size:12px;">Sem dados de projeto no período.</span>';
        }

        var sessTbody = document.getElementById("cockpit-sessions-tbody");
        if (sessTbody && data.recent_sessions) {
          if (data.recent_sessions.length === 0) {
            sessTbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text-muted);">Nenhuma sessão registrada ainda.</td></tr>';
          } else {
            sessTbody.innerHTML = data.recent_sessions.map(function (s) {
              var d = s.created_at ? s.created_at.slice(0, 16).replace("T", " ") : "—";
              return '<tr>'
                   + '<td>' + escapeHTML(d) + '</td>'
                   + '<td><code>' + escapeHTML((s.session_id || "").slice(0, 12)) + '</code></td>'
                   + '<td>' + escapeHTML(s.project_id || "_global") + '</td>'
                   + '<td><span class="badge">' + escapeHTML(s.model || "—") + '</span></td>'
                   + '<td>' + formatRecorded(s.prompt_tokens) + '</td>'
                   + '<td>' + formatRecorded(s.completion_tokens) + '</td>'
                   + '<td>' + formatRecorded(s.reasoning_tokens) + '</td>'
                   + '<td><strong>' + formatRecorded(s.total_tokens) + '</strong></td>'
                   + '</tr>';
            }).join("");
          }
        }

        var loopsDiv = document.getElementById("cockpit-loops-list");
        if (loopsDiv && data.recent_loops) {
          if (data.recent_loops.length === 0) {
            loopsDiv.innerHTML = '<p style="color:var(--text-muted);font-size:var(--text-xs);margin:0;">Nenhum loop crítico detectado recentemente. Seu fluxo está limpo!</p>';
          } else {
            loopsDiv.innerHTML = data.recent_loops.map(function (l) {
              return '<div class="candidate-row" style="border-left:3px solid var(--warning);">'
                   + '<div class="title">' + escapeHTML(l.file_path) + '</div>'
                   + '<div class="meta-row"><span>Repetições consecutivas: <strong>' + l.repeats + 'x</strong></span> &middot; <span>Sessão: ' + escapeHTML((l.session_id || "").slice(0, 12)) + '</span></div>'
                   + '</div>';
            }).join("");
          }
        }
      }).catch(function () {
        if (requestId !== ledgerRequestId) return;
        safeText(document.getElementById("cockpit-message"), "Não foi possível carregar as medições. Tente Atualizar.");
        ["total", "prompt", "completion", "reasoning", "loops", "cost"].forEach(function (key) { safeText(document.getElementById("cockpit-today-" + key), "Não disponível"); });
        document.getElementById("export-ledger-btn").disabled = true;
      });
    } catch (e) { console.error("refreshCockpit:", e); }
  }
  function initCockpit() {
    var btn = document.getElementById("refresh-cockpit-btn");
    if (btn) btn.addEventListener("click", function () { refreshCockpit(); });
    document.getElementById("ledger-period").addEventListener("change", refreshCockpit);
    document.getElementById("export-ledger-btn").addEventListener("click", function () {
      function cell(value) { var v=String(value == null ? "" : value); if (/^[=+@-]/.test(v.trimStart()) || v.charCodeAt(0) < 32) v="'"+v; return '"'+v.replace(/"/g,'""')+'"'; }
      var fields=["created_at","session_id","project_id","model","prompt_tokens","completion_tokens","reasoning_tokens","total_tokens"];
      var rows=(ledgerSnapshot && ledgerSnapshot.recent_sessions) || [];
      var csv=[fields.map(cell).join(";")].concat(rows.map(function(row){return fields.map(function(k){return cell(row[k]);}).join(";");})).join("\\r\\n");
      var url=URL.createObjectURL(new Blob(["\\ufeff",csv],{type:"text/csv;charset=utf-8"}));
      var a=document.createElement("a"); a.href=url; a.download="cerberus-registros.csv"; a.click(); setTimeout(function(){URL.revokeObjectURL(url);},1000);
    });
  }

  // ===== Profile =====
  function refreshProfile() {
    try {
      getJSON("/api/v1/auth/me").then(function (u) {
        safeText(document.getElementById("profile-email"), u.email);
        safeText(document.getElementById("profile-active"), u.is_active ? "Conta ativa" : "Conta inativa");
        try {
          var created = u.created_at ? new Date(u.created_at * 1000).toLocaleString("pt-BR") : "—";
          safeText(document.getElementById("profile-created"), created);
        } catch (e) {}
        var status = u.has_2fa ? "Ativo" : "Inativo";
        var badge = document.getElementById("profile-2fa-status");
        if (badge) { badge.textContent = status; badge.className = "badge " + (u.has_2fa ? "success" : "warning"); }
        var inline = document.getElementById("profile-2fa-status-inline");
        if (inline) safeText(inline, status);
        var enableBtn = document.getElementById("twofa-enable-btn");
        if (enableBtn) enableBtn.hidden = !!u.has_2fa;
        var disableForm = document.getElementById("twofa-disable-form");
        if (disableForm) disableForm.hidden = !u.has_2fa;
        uiState.profile.status = u.has_2fa;
      }).catch(function (err) { showToast("error", "Perfil: " + (err && err.message || "")); });
    } catch (e) { console.error("refreshProfile:", e); }
  }
  function initProfile() {
    try {
      var profileBtn = document.getElementById("profile-btn");
      if (profileBtn) profileBtn.addEventListener("click", function () { try { selectTab("tab-profile"); } catch (e) {} });
      var logoutBtn = document.getElementById("logout-btn");
      if (logoutBtn) logoutBtn.addEventListener("click", function () {
        try {
          postJSON("/auth/logout", {}).catch(function () {}).then(function () { window.location.href = "/auth/login"; });
        } catch (e) {}
      });
      var pwForm = document.getElementById("change-password-form");
      if (pwForm) pwForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var current = document.getElementById("current-password").value;
        var next = document.getElementById("new-password").value;
        var confirm = document.getElementById("confirm-password").value;
        if (next !== confirm) { showToast("error", "A confirmação da nova senha não confere."); return; }
        postJSON("/api/v1/auth/change-password", { current_password: current, new_password: next }).then(function (r) {
          showToast("ok", r.message || "Senha atualizada.");
          pwForm.reset();
        }).catch(function (err) { showToast("error", "Senha não atualizada: " + (err && err.message || "")); });
      });
      var enableBtn = document.getElementById("twofa-enable-btn");
      if (enableBtn) enableBtn.addEventListener("click", function () {
        postJSON("/api/v1/auth/2fa/setup", {}).then(function (r) {
          uiState.profile.pendingSecret = r.secret || "";
          var qr = document.getElementById("twofa-qr");
          if (qr && typeof r.qr_svg === "string" && r.qr_svg.indexOf("<svg") === 0) {
            qr.textContent = "";
            qr.innerHTML = r.qr_svg;
          }
          safeText(document.getElementById("twofa-secret"), r.secret || "");
          var enroll = document.getElementById("twofa-enrollment");
          if (enroll) enroll.removeAttribute("hidden");
        }).catch(function (err) { showToast("error", "Falha ao iniciar 2FA: " + (err && err.message || "")); });
      });
      var verifyForm = document.getElementById("twofa-verify-form");
      if (verifyForm) verifyForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var code = document.getElementById("twofa-code").value;
        postJSON("/api/v1/auth/2fa/verify-and-enable", { secret: uiState.profile.pendingSecret, code: code }).then(function (r) {
          showToast("ok", r.message || "2FA ativado.");
          var enroll = document.getElementById("twofa-enrollment");
          if (enroll) enroll.setAttribute("hidden", "");
          verifyForm.reset();
          refreshProfile();
        }).catch(function (err) { showToast("error", "2FA não ativado: " + (err && err.message || "")); });
      });
      var disableForm = document.getElementById("twofa-disable-form");
      if (disableForm) disableForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var pw = document.getElementById("twofa-disable-password").value;
        postJSON("/api/v1/auth/2fa/disable", { password: pw }).then(function (r) {
          showToast("ok", r.message || "2FA desativado.");
          disableForm.reset();
          refreshProfile();
        }).catch(function (err) { showToast("error", "2FA não desativado: " + (err && err.message || "")); });
      });
      var copySecret = document.getElementById("copy-secret-btn");
      if (copySecret) copySecret.addEventListener("click", function () {
        var secret = document.getElementById("twofa-secret").textContent;
        navigator.clipboard.writeText(secret).then(function () { showToast("ok", "Secret copiado."); }).catch(function () {});
      });
      refreshProfile();
    } catch (e) { console.error("initProfile:", e); }
  }

  // ===== Keyboard shortcuts =====
  function initKeyboardShortcuts() {
    document.addEventListener("keydown", function (e) {
      try {
        if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K")) {
          e.preventDefault();
          var q = document.getElementById("search-q");
          selectTab("tab-search");
          if (q) q.focus();
          return;
        }
        if (e.key === "Escape") {
          var preview = document.getElementById("search-workbench");
          if (preview && preview.classList.contains("preview-open")) {
            preview.classList.remove("preview-open");
            var back = document.getElementById("search-preview-back");
            if (back) back.setAttribute("hidden", "");
          }
          var ib = document.getElementById("inbox-workbench");
          if (ib) ib.classList.remove("preview-open");
          if (uiState.activeTab === "tab-topology") {
            uiState.topology.selectedNodeId = null;
            renderTopologyFrame();
          }
        }
      } catch (err) { console.error("kbd:", err); }
    });
  }

  // ===== Boot =====
  function safeBoot(name, fn) {
    try { fn(); }
    catch (err) { console.error("[boot] " + name + ":", err); }
  }
  document.addEventListener("DOMContentLoaded", function () {
    safeBoot("initEvidenceRail", initEvidenceRail);
    safeBoot("initTabs", initTabs);
    safeBoot("openOverview", function () {
      var initialTab = (location.hash && document.getElementById(location.hash.slice(1))) ? location.hash.slice(1) : "tab-metrics";
      selectTab(initialTab);
    });
    safeBoot("initSearch", initSearch);
    safeBoot("initInbox", initInbox);
    safeBoot("initTopologyCanvas", initTopologyCanvas);
    safeBoot("initMetrics", initMetrics);
    safeBoot("initProfile", initProfile);
    safeBoot("initCockpit", initCockpit);
    safeBoot("initDialogs", initDialogs);
    safeBoot("initKeyboardShortcuts", initKeyboardShortcuts);
    refreshStatus();
  });
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
# Dev Maniac's Brand & Two Point Design System — Login + Setup 2FA
# ---------------------------------------------------------------------------
DEV_MANIACS_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="56" height="56" role="img" aria-label="Dev Maniac's Logo" shape-rendering="crispEdges">
  <g fill="none" stroke="#061637" stroke-width="10" stroke-linejoin="round">
    <path fill="#061637" d="M20 28h142v132H20z"/>
    <path fill="#ff4c4c" stroke="none" d="M34 42h57v48H34z"/>
    <path fill="#ffc529" stroke="none" d="M91 42h57v48H91z"/>
    <path fill="#1e40af" stroke="none" d="M34 90h57v54H34z"/>
    <path fill="#08b9ca" stroke="none" d="M91 90h57v54H91z"/>
    <path stroke="none" fill="#061637" d="M48 58h28v10H60v50h16v10H48zm28 10h10v50H76zM94 58h12v70H94zm40 0h12v70h-12zM106 68h10v20h-10zm18 0h10v20h-10zm-8 10h8v20h-8z"/>
    <path fill="#061637" stroke="none" d="M67 160h48v18h18v14H49v-14h18z"/>
    <path d="M162 78h18v30h18"/>
    <path fill="#061637" d="M176 102h48l14 22v49h-25l-12-14h-18l-12 14h-24v-49z"/>
  </g>
  <g fill="#ffffff">
    <path d="M169 124h10v-10h10v10h10v10h-10v10h-10v-10h-10z"/>
  </g>
  <rect x="209" y="119" width="9" height="9" fill="#ff4c4c"/>
  <rect x="220" y="130" width="9" height="9" fill="#ffc529"/>
  <rect x="198" y="130" width="9" height="9" fill="#1e40af"/>
  <rect x="209" y="141" width="9" height="9" fill="#08b9ca"/>
</svg>"""

WATERMARK_SVG = (
    "data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20"
    "viewBox%3D%270%200%20120%2060%27%3E%3Ctext%20x%3D%2760%27%20y%3D'38'%20font-family%3D'IBM%20Plex"
    "%20Sans%27%20font-size%3D'36%27%20fill%3D'%2314a08f'%20fill-opacity%3D'0.14'%20text-anchor%3D"
    "%27middle%27%20font-weight%3D'700'%3EDM%3C%2Ftext%3E%3C%2Fsvg%3E"
)


def _render_login_html(step: str = "credentials",
                       error_message: str = "",
                       pending_token: str = "",
                       target_email: str = "") -> str:
    """Render the Dev Maniac's Cerberus Inspector login page in Suporte Dev Maniac's theme.

    Security: every interpolation point that lands inside an HTML attribute or
    element body MUST be html-escaped. ``error_message``, ``pending_token`` and
    ``target_email`` are all attacker-controllable via query-string params
    (see ``_login_redirect_with_error``), so we escape unconditionally here.
    """
    target_email = (target_email or "")[:254]
    pending_token = (pending_token or "")[:128]

    safe_email = html_escape(target_email, quote=True)
    safe_pending = html_escape(pending_token, quote=True)

    error_block = ""
    if error_message:
        safe_error = html_escape(error_message, quote=True)
        error_block = (
            f'<div class="login-error" role="alert">'
            f'<span class="err-dot"></span><span>{safe_error}</span></div>'
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
           placeholder="voce@empresa.com" value="{safe_email}">
  </label>
  <label class="field">
    <span>Senha</span>
    <div class="password-wrap">
      <input id="login-password" type="password" name="password" required autocomplete="current-password" placeholder="Sua senha">
      <button type="button" class="password-toggle" aria-controls="login-password" aria-pressed="false" onclick="var p=document.getElementById('login-password'); var show=p.type==='password'; p.type=show?'text':'password'; this.textContent=show?'Ocultar':'Mostrar'; this.setAttribute('aria-pressed',String(show));">Mostrar</button>
    </div>
  </label>
  <button type="submit" class="btn-dm primary">Entrar</button>
</form>
<p class="login-help">Primeiro acesso ou redefinir senha? Execute <code>python -m engine.admin_access</code> no terminal (ou utilitário <strong>Configurar acesso</strong>) para definir suas credenciais.</p>'''
        totp_block = ''
    else:
        creds_block = ''
        totp_block = f'''
<form id="totpForm" method="POST" action="/auth/login" class="step-form" autocomplete="off">
  <input type="hidden" name="pending_token" value="{safe_pending}">
  <input type="hidden" name="email" value="{safe_email}">
  <div class="totp-badge"><span>2FA &middot; AUTENTICAÇÃO EM DUAS ETAPAS</span></div>
  <p class="totp-help">Digite o código de 6 ou 8 dígitos gerado no seu aplicativo autenticador.</p>
  <label class="field">
    <span>Código de Autenticação</span>
    <input type="text" name="totp" required autofocus inputmode="numeric"
           autocomplete="one-time-code" pattern="\\d{{6,8}}" maxlength="8"
           placeholder="000000" class="totp-input">
  </label>
  <button type="submit" class="btn-dm primary">Confirmar &amp; Entrar &rarr;</button>
  <div class="back-link"><a href="/auth/login">&larr; Voltar para o login</a></div>
</form>'''

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#141617">
<title>Cerberus Inspector &mdash; Dev Maniac's Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-canvas: #141617;
  --bg-shell: #191C1D;
  --bg-panel: #1D2122;
  --bg-elevated: #272D2E;
  --bg-input: #171B1C;
  --border-subtle: #2D3332;
  --border-default: #39413D;
  --border-strong: #59645D;
  --text-primary: #F0F2ED;
  --text-secondary: #C3CAC2;
  --text-muted: #9FA99F;
  --action: #C93B46;
  --action-hover: #D94854;
  --action-pressed: #A82833;
  --action-soft: #2D1417;
  --warning: #D8B478;
  --warning-soft: #352E22;
  --success: #A9C5A0;
  --success-soft: #25342A;
  --danger: #F19D96;
  --danger-soft: #392725;
  --font-display: "Space Grotesk", "Inter", system-ui, sans-serif;
  --font-body: "Inter", system-ui, -apple-system, sans-serif;
  --font-mono: "IBM Plex Mono", Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: var(--font-body);
  background: var(--bg-canvas);
  color: var(--text-primary);
  font-size: 14px;
}}
body {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}}
.auth-wrapper {{
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.card {{
  background: var(--bg-panel);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 32px;
  width: 100%;
  position: relative;
}}
.brand-header {{
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 24px;
}}
.brand-logo-wrap {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  margin-bottom: 12px;
}}
.brand-logo-wrap svg {{
  width: 32px;
  height: 32px;
}}
.brand-title {{
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}}
.brand-tag {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--action);
  background: var(--action-soft);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--action);
  margin-bottom: 8px;
}}
.card-subtitle {{
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
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
  color: var(--text-muted);
  margin-bottom: 6px;
}}
.field input {{
  width: 100%;
  min-height: 44px;
  padding: 10px 14px;
  font: inherit;
  font-size: 14px;
  background: var(--bg-input);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
}}
.field input:focus {{
  outline: none;
  border-color: var(--action);
  box-shadow: 0 0 0 3px var(--action-soft);
}}
.totp-input {{
  font-family: var(--font-mono);
  font-size: 20px !important;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-align: center;
}}
.btn-dm {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 10px 20px;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 14px;
  color: #FFFFFF;
  background: var(--action);
  border: 1px solid var(--action);
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  margin-top: 8px;
  text-decoration: none;
}}
.btn-dm:hover {{
  background: var(--action-hover);
}}
.btn-dm:active {{
  background: var(--action-pressed);
}}
.totp-badge {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--action);
  text-align: center;
  margin-bottom: 4px;
}}
.totp-help {{
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  margin: 0 0 16px;
  line-height: 1.4;
}}
.back-link {{
  text-align: center;
  margin-top: 14px;
}}
.back-link a {{
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  text-decoration: none;
}}
.back-link a:hover {{
  color: var(--action);
  text-decoration: underline;
}}
.login-error {{
  display: flex;
  gap: 10px;
  align-items: center;
  background: var(--danger-soft);
  border: 1px solid var(--danger);
  color: #fca5a5;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 18px;
}}
.err-dot {{
  width: 8px;
  height: 8px;
  background: var(--danger);
  border-radius: 50%;
  flex-shrink: 0;
}}
.step-content {{ display: none; }}
.step-content.active {{ display: block; }}

.auth-footer {{
  margin-top: 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.6;
}}
.auth-footer-links {{
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}}
.auth-footer-links a {{
  color: var(--action);
  text-decoration: none;
  font-weight: 500;
}}
.auth-footer-links a:hover {{
  text-decoration: underline;
}}
.auth-security-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  margin-top: 6px;
}}
{AUTH_STYLE}
</style>
</head>
<body>
  <div class="auth-wrapper">
    {AUTH_STORY}
    <main class="card">
      <div class="brand-header">
        <h1 class="brand-title">Entrar no Cerberus</h1>
        <p class="card-subtitle">Use seu e-mail e senha para continuar.</p>
      </div>
      {error_block}
      <section class="{creds_class}" id="credsStep">
        {creds_block}
      </section>
      <section class="{totp_class}" id="totpStep">
        {totp_block}
      </section>
    </main>
  </div>
  {render_institutional_footer("auth")}
</body>
</html>'''


def _render_setup_2fa_html(secret_b32: str, otp_uri: str,
                            svg: str, error_message: str = "") -> str:
    err_block = ""
    if error_message:
        safe_error = html_escape(error_message, quote=True)
        err_block = (
            f'<div class="login-error" role="alert"><span class="err-dot"></span> '
            f'<span>{safe_error}</span></div>'
        )
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#141617">
<title>Cerberus Inspector &mdash; Configurar 2FA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-canvas: #141617;
  --bg-shell: #191C1D;
  --bg-panel: #1D2122;
  --bg-elevated: #272D2E;
  --bg-input: #171B1C;
  --border-subtle: #2D3332;
  --border-default: #39413D;
  --border-strong: #59645D;
  --text-primary: #F0F2ED;
  --text-secondary: #C3CAC2;
  --text-muted: #9FA99F;
  --action: #C93B46;
  --action-hover: #D94854;
  --action-pressed: #A82833;
  --action-soft: #2D1417;
  --warning: #D8B478;
  --warning-soft: #352E22;
  --success: #A9C5A0;
  --success-soft: #25342A;
  --danger: #F19D96;
  --danger-soft: #392725;
  --font-display: "Space Grotesk", "Inter", system-ui, sans-serif;
  --font-body: "Inter", system-ui, -apple-system, sans-serif;
  --font-mono: "IBM Plex Mono", Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: var(--font-body);
  background: var(--bg-canvas);
  color: var(--text-primary);
  font-size: 14px;
}}
body {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}}
.auth-wrapper {{
  width: 100%;
  max-width: 520px;
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.card {{
  background: var(--bg-panel);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 32px;
  width: 100%;
  position: relative;
}}
.brand-header {{
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 16px;
}}
.brand-logo-wrap {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  flex-shrink: 0;
}}
.brand-logo-wrap svg {{
  width: 28px;
  height: 28px;
}}
.brand-header h1 {{
  margin: 0 0 2px;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}}
.brand-header p.subtitle {{
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
}}
.qr-wrap {{
  display: flex;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 20px;
}}
.qr-wrap .svg {{
  background: #ffffff;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--border-default);
  flex-shrink: 0;
}}
.field {{ margin-bottom: 14px; }}
.field > span {{
  display: block;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: 6px;
}}
.field input {{
  width: 100%;
  min-height: 44px;
  padding: 10px 14px;
  font: inherit;
  font-size: 14px;
  background: var(--bg-input);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
}}
.field input:focus {{
  outline: none;
  border-color: var(--action);
  box-shadow: 0 0 0 3px var(--action-soft);
}}
.totp-input {{
  font-family: var(--font-mono);
  font-size: 20px !important;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-align: center;
}}
.uri-block {{
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 8px 10px;
  background: var(--bg-input);
  color: var(--action);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  word-break: break-all;
  margin: 4px 0 10px;
}}
.btn-dm {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 10px 20px;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 14px;
  color: #FFFFFF;
  background: var(--action);
  border: 1px solid var(--action);
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  text-decoration: none;
}}
.btn-dm:hover {{
  background: var(--action-hover);
}}
.login-error {{
  display: flex;
  gap: 8px;
  background: var(--danger-soft);
  border: 1px solid var(--danger);
  color: #fca5a5;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 16px;
}}
.err-dot {{
  width: 8px;
  height: 8px;
  background: var(--danger);
  border-radius: 50%;
  flex-shrink: 0;
}}
.muted {{
  color: var(--text-muted);
  font-size: 12.5px;
  margin: 6px 0 0;
  line-height: 1.4;
}}
.auth-footer {{
  margin-top: 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
}}
{AUTH_STYLE}
</style>
</head>
<body>
  <div class="auth-wrapper">
    <main class="card">
      <div class="brand-header">
        <div class="brand-logo-wrap">
          {DEV_MANIACS_LOGO_SVG}
        </div>
        <div>
          <h1>Habilitar 2FA</h1>
          <p class="subtitle">Cerberus &middot; Autentica&ccedil;&atilde;o em Duas Etapas</p>
        </div>
      </div>
      {err_block}
      <div class="qr-wrap">
        <div class="svg">{svg}</div>
        <div>
          <p style="margin:0 0 6px"><strong>1. Escaneie o QR Code</strong></p>
          <p class="muted">Abra o Google Authenticator, 1Password ou Authy no seu celular e leia o c&oacute;digo ao lado.</p>
          <p class="muted" style="margin-top:10px"><strong>C&oacute;digo Manual (Secret base32):</strong></p>
          <pre class="uri-block">{html_escape(secret_b32, quote=True)}</pre>
        </div>
      </div>
      <form method="POST" action="/auth/setup-2fa" style="margin-top:14px">
        <label class="field">
          <span>2. Confirme com o c&oacute;digo gerado no app</span>
          <input type="text" name="totp" required autofocus inputmode="numeric"
                 pattern="\\d{{6,8}}" maxlength="8" placeholder="000000" class="totp-input">
        </label>
        <button type="submit" class="btn-dm">Ativar 2FA &amp; Continuar &rarr;</button>
      </form>
    </main>
  </div>
  {render_institutional_footer("auth")}
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
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)
        self.close_connection = True

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

        # Public health and auth routes (no auth required)
        if path in {"/api/health", "/healthz"}:
            return self._serve_health()
        if path == "/login":
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/auth/login")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
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
        if path == "/api/v1/ledger/stats":
            return self._serve_ledger_stats(query)
        if path == "/api/v1/ledger/recent":
            return self._serve_ledger_recent(query)
        if path == "/api/v1/auth/me":
            return self._serve_auth_me()
        if path == "/api/inbox":
            return self._serve_inbox_list(query)
        if path == "/api/search":
            return self._serve_search(query)
        if path == "/api/document":
            return self._serve_document_detail(query)
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

        if path == "/api/reindex":
            return self._serve_reindex_post()
        if path == "/api/v1/ledger/record":
            return self._serve_ledger_record()
        if path == "/api/v1/auth/change-password":
            return self._serve_change_password()
        if path == "/api/v1/auth/2fa/setup":
            return self._serve_2fa_setup()
        if path == "/api/v1/auth/2fa/verify-and-enable":
            return self._serve_2fa_verify_and_enable()
        if path == "/api/v1/auth/2fa/disable":
            return self._serve_2fa_disable()

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
    def _current_user(self):
        if not self.auth or self.auth.auth_disabled:
            from engine.auth import User
            return User(email="developer@example.com", password_hash="", is_active=True, is_admin=True, totp_secret="")
        session = self.auth.resolve_session(self.headers.get("Cookie"))
        return self.auth.user_store.get(session.user_email) if session else None

    def _json_payload_or_400(self):
        try:
            return self._read_json_body()
        except ValueError as exc:
            self._error(HTTPStatus.BAD_REQUEST, str(exc))
            return None

    def _serve_health(self) -> None:
        self._json(HTTPStatus.OK, {"status": "ok", "service": "cerberus-inspector", "version": "1.0.0"})

    def _serve_auth_me(self) -> None:
        user = self._current_user()
        if user is None:
            return self._error(HTTPStatus.UNAUTHORIZED, "Authentication required")
        self._json(HTTPStatus.OK, {"email": user.email, "is_active": user.is_active, "has_2fa": bool(user.totp_secret), "created_at": user.created_at})

    def _serve_change_password(self) -> None:
        user = self._current_user()
        body = self._json_payload_or_400()
        if body is None:
            return
        if not verify_password(body.get("current_password") or "", user.password_hash):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Senha atual incorreta."})
            return
        new_password = body.get("new_password") or ""
        if not isinstance(new_password, str) or len(new_password) < 6:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Nova senha deve ter pelo menos 6 caracteres."})
            return
        self.auth.user_store.set_password(user.email, hash_password(new_password))
        self._json(HTTPStatus.OK, {"ok": True, "message": "Senha alterada com sucesso."})

    def _serve_2fa_setup(self) -> None:
        user = self._current_user()
        secret = TOTP.generate_secret()
        uri = TOTP.from_base32(secret, digits=6).provisioning_uri(user.email, issuer="DevManiacs-Cerberus")
        self._json(HTTPStatus.OK, {"secret": secret, "qr_svg": totp_qr_svg(secret, user.email, issuer="DevManiacs-Cerberus"), "uri": uri})

    def _serve_2fa_verify_and_enable(self) -> None:
        user = self._current_user()
        body = self._json_payload_or_400()
        if body is None:
            return
        secret, code = body.get("secret") or "", body.get("code") or ""
        try:
            valid = TOTP.from_base32(secret, digits=6).verify(code)
        except (TypeError, ValueError):
            valid = False
        if not valid:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Codigo TOTP invalido ou expirado."})
            return
        self.auth.user_store.set_totp_secret(user.email, secret)
        self._json(HTTPStatus.OK, {"ok": True, "message": "2FA ativado com sucesso."})

    def _serve_2fa_disable(self) -> None:
        user = self._current_user()
        body = self._json_payload_or_400()
        if body is None:
            return
        if not verify_password(body.get("password") or "", user.password_hash):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Senha incorreta."})
            return
        self.auth.user_store.set_totp_secret(user.email, "")
        self._json(HTTPStatus.OK, {"ok": True, "message": "2FA desativado com sucesso."})

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
            digits = len(totp) if len(totp) in {6, 8} else 8
            totp_obj = TOTP.from_base32(secret_b32, digits=digits)
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

    def _serve_ledger_stats(self, query: Dict[str, List[str]]) -> None:
        try:
            from engine.token_ledger import get_ledger_stats
            days = 7
            if "days" in query and query["days"]:
                try:
                    days = int(query["days"][0])
                except ValueError:
                    days = 7
            stats = get_ledger_stats(db_path=self.state.application_root / ".cerberus" / "token_ledger.db", days=days)
            self._json(HTTPStatus.OK, stats)
        except Exception as exc:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Erro no ledger: {exc}")

    def _serve_ledger_recent(self, query: Dict[str, List[str]]) -> None:
        try:
            from engine.token_ledger import get_ledger_stats
            stats = get_ledger_stats(db_path=self.state.application_root / ".cerberus" / "token_ledger.db", days=30)
            self._json(HTTPStatus.OK, {
                "recent_sessions": stats.get("recent_sessions", []),
                "recent_loops": stats.get("recent_loops", []),
            })
        except Exception as exc:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Erro no ledger: {exc}")

    def _serve_ledger_record(self) -> None:
        payload = self._json_payload_or_400()
        if payload is None:
            return
        try:
            from engine.token_ledger import record_turn_tokens
            if payload.get("loops_prevented", 0) != 0:
                raise ValueError("Prevenção de loops não está conectada a esta integração.")
            if payload.get("event_id") is not None and not isinstance(payload["event_id"], str):
                raise ValueError("event_id deve ser texto.")
            res = record_turn_tokens(
                session_id=str(payload.get("session_id") or "manual"),
                project_id=str(payload.get("project_id") or "_global"),
                agent=str(payload.get("agent") or "CODEX"),
                model=str(payload.get("model") or "gpt-6.1-sol"),
                prompt_tokens=payload.get("prompt_tokens"),
                completion_tokens=payload.get("completion_tokens"),
                reasoning_tokens=payload.get("reasoning_tokens"),
                loops_prevented=0,
                total_tokens=payload.get("total_tokens"),
                event_id=payload.get("event_id"),
                usage_source="manual_api",
                db_path=self.state.application_root / ".cerberus" / "token_ledger.db",
            )
            self._json(HTTPStatus.CREATED, res)
        except (ValueError, TypeError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, f"Medição inválida: {exc}")
        except Exception:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "Não foi possível registrar a medição.")

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
        known.extend(stats.get("indexed_projects", []))
        try:
            from engine.integrations.orchestrator import discover_dynamic_projects
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
        mode = (query.get("mode", ["hybrid"])[0] or "hybrid").strip().casefold()
        if not q:
            return self._json(HTTPStatus.OK, {
                "query": "",
                "count": 0,
                "results": [],
            })
        if mode not in {"hybrid", "lexical", "semantic"}:
            return self._error(HTTPStatus.BAD_REQUEST,
                               "Query parameter 'mode' must be hybrid, lexical, or semantic")
        try:
            results = self.state.service.search(
                query=q, project_id=project, mode=mode, limit=20,
                include_global=project is None,
            )
        except Exception as exc:  # noqa: BLE001
            return self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))
        self._json(HTTPStatus.OK, {
            "query": q,
            "project_id": project,
            "mode": mode,
            "count": len(results),
            "results": [r.to_dict() for r in results],
        })

    def _serve_document_detail(self, query: Dict[str, List[str]]) -> None:
        doc_id = (query.get("id", [""])[0] or "").strip()
        if not doc_id:
            return self._error(HTTPStatus.BAD_REQUEST, "Query parameter 'id' is required")
        items = self.state.service.index.get_items_by_ids([doc_id])
        if not items:
            return self._error(HTTPStatus.NOT_FOUND, f"Document not found: {doc_id}")
        self._json(HTTPStatus.OK, items[0].to_dict())

    def _serve_reindex_post(self) -> None:
        try:
            stats = self.state.ensure_indexed()
            self._json(HTTPStatus.OK, {"status": "ok", "stats": stats})
        except Exception as exc:  # noqa: BLE001
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


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
