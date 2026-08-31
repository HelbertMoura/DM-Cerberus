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
# UI HTML — Dev Maniac's Solid Industrial Standard (HelpDesk & Suporte Standard)
# ---------------------------------------------------------------------------
UI_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#061637">
<title>Cerberus Inspector &mdash; Dev Maniac's Intelligence &amp; Memory Engine</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-deep: #061637;
  --bg-surface: #0a192f;
  --bg-card: #0d2247;
  --bg-card-inner: #061637;
  --bg-legacy: #0F172A;
  --accent-legacy: #1E40AF;
  --border-dark: #1e3a6d;
  --border-subtle: #152e5a;
  --border-focus: #08b9ca;
  --ink-light: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;
  --dm-cyan: #08b9ca;
  --dm-red: #ff4c4c;
  --dm-yellow: #ffc529;
  --dm-purple: #8b35d1;
  --dm-blue: #1e40af;
  --font: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-display: 'Space Grotesk', var(--font);
  --font-mono: 'IBM Plex Mono', ui-monospace, monospace;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg-deep);
  color: var(--ink-light);
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.5;
  min-height: 100vh;
}

/* Header Navbar - Solid Industrial Style */
header {
  background: #061637;
  border-bottom: 1px solid var(--border-dark);
  padding: 12px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.brand-group {
  display: flex;
  align-items: center;
  gap: 14px;
}
.brand-icon-box {
  width: 44px;
  height: 44px;
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-icon-box svg { width: 30px; height: 30px; }
.brand-text h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-text p {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
}
.live-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--dm-cyan);
  background: #0a192f;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-dark);
}
.live-dot {
  width: 6px;
  height: 6px;
  background: var(--dm-cyan);
  border-radius: 50%;
}
.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Solid Buttons (ISO 44px) */
.btn-dm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 8px 18px;
  font-family: var(--font);
  font-weight: 600;
  font-size: 13.5px;
  color: #ffffff;
  background: var(--dm-cyan);
  border: 1px solid var(--dm-cyan);
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.1s ease, border-color 0.1s ease;
  text-decoration: none;
  white-space: nowrap;
}
.btn-dm:hover {
  background: #0aa7b7;
  border-color: #0aa7b7;
}
.btn-dm.secondary {
  background: #0d2247;
  color: var(--ink-light);
  border-color: var(--border-dark);
}
.btn-dm.secondary:hover {
  background: #122e5e;
  border-color: var(--dm-cyan);
}
.btn-dm.danger {
  background: #7f1d1d;
  color: #fecaca;
  border-color: #991b1b;
}
.btn-dm.danger:hover {
  background: #991b1b;
  color: #ffffff;
}
.btn-dm.sm {
  min-height: 38px;
  padding: 6px 14px;
  font-size: 12.5px;
}
.btn-dm:disabled { opacity: 0.5; cursor: not-allowed; }

/* Main Container */
main {
  max-width: 1400px;
  margin: 20px auto;
  padding: 0 24px 60px;
}

/* Knowledge Network Topology Card */
.topology-card {
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
  align-items: center;
}
.topology-canvas-wrap {
  position: relative;
  width: 100%;
  height: 280px;
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  overflow: hidden;
}
#brainCanvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
}
#brainCanvas:active { cursor: grabbing; }
.topology-hud {
  position: absolute;
  top: 10px; left: 10px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--dm-cyan);
  background: #0a192f;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-dark);
  pointer-events: none;
}
.topology-ticker {
  position: absolute;
  bottom: 10px; left: 10px; right: 10px;
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  padding: 6px 12px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
}
.ticker-indicator {
  width: 8px; height: 8px;
  background: var(--dm-yellow);
  border-radius: 2px;
  flex-shrink: 0;
}
.topology-info {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.topology-info h2 {
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 700;
  margin: 0;
  color: #ffffff;
}
.topology-info p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
}
.topology-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.topology-metric-box {
  background: #0d2247;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  padding: 10px 12px;
}
.topology-metric-val {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}
.topology-metric-lbl {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Metric Cards Grid */
.hero-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 10px;
  padding: 18px 20px;
}
.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.stat-title {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.stat-tag {
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  background: #0d2247;
  color: var(--dm-cyan);
  border: 1px solid var(--border-dark);
}
.stat-value {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 800;
  color: #ffffff;
  margin: 4px 0;
}
.stat-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

/* Navigation Tabs */
.nav-tabs {
  display: flex;
  gap: 6px;
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  padding: 6px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.nav-tab {
  flex: 1 1 160px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  font-family: var(--font);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
}
.nav-tab:hover {
  color: #ffffff;
  background: #0d2247;
}
.nav-tab.active {
  background: #0d2247;
  color: #ffffff;
  border-color: var(--dm-cyan);
}
.nav-tab .badge {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  background: #061637;
  color: var(--dm-cyan);
  border: 1px solid var(--border-dark);
}
.nav-tab.active .badge {
  background: var(--dm-cyan);
  color: #061637;
}

/* Tab Panels */
.tab-panel { display: none; }
.tab-panel.active { display: block; }

/* Content Box Cards */
.content-box {
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}
.content-box-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-dark);
  padding-bottom: 14px;
  flex-wrap: wrap;
}
.content-box-header h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}
.content-box-header p {
  margin: 3px 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

/* Search Toolbar */
.search-form {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 16px;
}
.search-input-wrap {
  flex: 1 1 340px;
}
.search-input-wrap input {
  width: 100%;
  min-height: 46px;
  padding: 10px 16px;
  font: inherit;
  font-size: 14px;
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  color: #ffffff;
}
.search-input-wrap input:focus,
select:focus {
  outline: none;
  border-color: var(--dm-cyan);
}
select {
  min-height: 46px;
  padding: 10px 14px;
  font: inherit;
  font-size: 13.5px;
  font-weight: 500;
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  color: #ffffff;
  cursor: pointer;
}
.chips-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 20px;
}
.chips-label {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-right: 4px;
}
.chip {
  min-height: 32px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  background: #0d2247;
  border: 1px solid var(--border-dark);
  border-radius: 4px;
  color: #93c5fd;
  cursor: pointer;
}
.chip:hover {
  background: var(--dm-cyan);
  color: #061637;
  border-color: var(--dm-cyan);
}

/* Results Cards */
.results-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.result-card {
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  padding: 18px 20px;
}
.result-card:hover {
  border-color: var(--dm-cyan);
}
.result-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}
.result-card-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 3px;
}
.result-card-path {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}
.result-meta-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 12px;
}
.pill {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-dark);
  background: #0d2247;
}
.pill.project { color: #93c5fd; }
.pill.authority { color: #a5f3fc; }
.pill.score { color: #cbd5e1; }
.result-snippet {
  font-size: 13px;
  line-height: 1.6;
  color: #e2e8f0;
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  padding: 12px 14px;
  margin-bottom: 12px;
}
.result-snippet mark, .result-snippet b {
  background: #854d0e;
  font-weight: 700;
  color: #fef08a;
  padding: 1px 3px;
  border-radius: 2px;
}

/* Candidate Inbox */
.inbox-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}
.filter-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.filter-tab-btn {
  min-height: 36px;
  padding: 6px 14px;
  font-family: var(--font);
  font-size: 12px;
  font-weight: 600;
  background: #061637;
  color: var(--text-muted);
  border: 1px solid var(--border-dark);
  border-radius: 4px;
  cursor: pointer;
}
.filter-tab-btn.active {
  background: var(--dm-cyan);
  color: #061637;
  border-color: var(--dm-cyan);
}
.candidates-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.candidate-card {
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  padding: 18px 20px;
}
.candidate-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.candidate-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}
.candidate-desc {
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--text-muted);
  margin: 4px 0 10px;
}
.candidate-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 14px;
  justify-content: flex-end;
}

/* Status Badges */
.tag {
  display: inline-block;
  padding: 3px 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border-radius: 4px;
  border: 1px solid var(--border-dark);
}
.tag.candidate { background: #1e3a6d; color: #93c5fd; }
.tag.verified { background: #064e3b; color: #6ee7b7; border-color: #059669; }
.tag.quarantined { background: #78350f; color: #fde68a; border-color: #d97706; }
.tag.canonical { background: #581c87; color: #e9d5ff; border-color: #7e22ce; }
.tag.rejected { background: #7f1d1d; color: #fca5a5; border-color: #dc2626; }

/* Project Explorer */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.project-card {
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.project-card:hover {
  border-color: var(--dm-cyan);
}
.project-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.project-card-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-transform: uppercase;
}
.project-stats-list {
  list-style: none;
  padding: 0;
  margin: 10px 0 18px;
  font-size: 13px;
  color: var(--text-muted);
}
.project-stats-list li {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid var(--border-subtle);
}

/* Guide */
.guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.guide-card {
  background: #061637;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  padding: 20px;
}
.guide-card-icon {
  width: 36px; height: 36px;
  border-radius: 6px;
  background: #0d2247;
  border: 1px solid var(--border-dark);
  color: var(--dm-cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}
.guide-card h3 {
  font-family: var(--font-display);
  font-size: 16px;
  color: #ffffff;
  margin: 0 0 8px;
}
.guide-card p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 0 12px;
}
.code-snippet {
  font-family: var(--font-mono);
  font-size: 11.5px;
  background: #030a1c;
  border: 1px solid var(--border-dark);
  border-radius: 4px;
  padding: 10px 12px;
  color: #7dd3fc;
  overflow-x: auto;
}

/* System & Diagnostics */
.system-table {
  width: 100%;
  border-collapse: collapse;
}
.system-table td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-dark);
  font-size: 13.5px;
}
.system-table td:first-child {
  font-weight: 700;
  color: #ffffff;
  width: 240px;
  text-transform: uppercase;
  font-size: 11.5px;
  letter-spacing: 0.04em;
}
.system-table td:last-child {
  font-family: var(--font-mono);
  color: #cbd5e1;
  word-break: break-all;
}

/* Modal Window */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 10, 26, 0.85);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 24px;
}
.modal-backdrop.open { display: flex; }
.modal {
  background: #0a192f;
  border: 1px solid var(--border-dark);
  border-radius: 12px;
  max-width: 980px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-header {
  padding: 16px 20px;
  background: #061637;
  border-bottom: 1px solid var(--border-dark);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.modal-header h3 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  color: #ffffff;
}
.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
.modal-footer {
  padding: 14px 20px;
  background: #061637;
  border-top: 1px solid var(--border-dark);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}
.code-viewer {
  font-family: var(--font-mono);
  font-size: 12px;
  background: #030a1c;
  color: #e2e8f0;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  padding: 14px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 500px;
  overflow: auto;
  line-height: 1.6;
}

/* Toast Notifications */
#flash {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 250;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.toast {
  min-height: 44px;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}
.toast.ok { background: #064e3b; color: #6ee7b7; border: 1px solid #059669; }
.toast.error { background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }

.empty-state {
  text-align: center;
  padding: 36px 20px;
  color: var(--text-muted);
  border: 1px dashed var(--border-dark);
  border-radius: 8px;
  background: #061637;
}
.empty-state p { margin: 6px 0 0; font-size: 13px; }

/* Institutional Footer */
.main-footer {
  margin-top: 40px;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.6;
}
.main-footer a {
  color: var(--dm-cyan);
  text-decoration: none;
  font-weight: 600;
}
.main-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .topology-card { grid-template-columns: 1fr; }
  header { padding: 12px 16px; }
  main { padding: 0 16px 40px; }
  .header-container { flex-direction: column; align-items: stretch; }
  .header-actions { justify-content: space-between; }
  .hero-grid { grid-template-columns: 1fr 1fr; }
}
</style>
</head>
<body>

<header>
  <div class="header-container">
    <div class="brand-group">
      <div class="brand-icon-box">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-label="Dev Maniac's Mark" shape-rendering="crispEdges">
          <g fill="none" stroke="#061637" stroke-width="12" stroke-linejoin="round">
            <path fill="#061637" d="M20 28h142v132H20z"/>
            <path fill="#ff4c4c" stroke="none" d="M34 42h57v48H34z"/>
            <path fill="#ffc529" stroke="none" d="M91 42h57v48H91z"/>
            <path fill="#8b35d1" stroke="none" d="M34 90h57v54H34z"/>
            <path fill="#08b9ca" stroke="none" d="M91 90h57v54H91z"/>
            <path stroke="none" fill="#ffffff" d="M48 58h28v10H60v50h16v10H48zm28 10h10v50H76zM94 58h12v70H94zm40 0h12v70h-12zM106 68h10v20h-10zm18 0h10v20h-10zm-8 10h8v20h-8z"/>
            <path fill="#061637" stroke="none" d="M67 160h48v18h18v14H49v-14h18z"/>
            <path d="M162 78h18v30h18"/>
            <path fill="#061637" d="M176 102h48l14 22v49h-25l-12-14h-18l-12 14h-24v-49z"/>
          </g>
          <g fill="#ffffff"><path d="M169 124h10v-10h10v10h10v10h-10v10h-10v-10h-10z"/></g>
          <rect x="209" y="119" width="9" height="9" fill="#ff4c4c"/>
          <rect x="220" y="130" width="9" height="9" fill="#ffc529"/>
          <rect x="198" y="130" width="9" height="9" fill="#8b35d1"/>
          <rect x="209" y="141" width="9" height="9" fill="#08b9ca"/>
        </svg>
      </div>
      <div class="brand-text">
        <h1>Dev Maniac's <span class="live-pill"><span class="live-dot"></span> CERBERUS LIVE</span></h1>
        <p>Central de Mem&oacute;ria Corporativa &middot; Orquestra&ccedil;&atilde;o Multi-Agente</p>
      </div>
    </div>
    <div class="header-actions">
      <button id="reindex-btn" class="btn-dm sm secondary" type="button">Reindexar Mem&oacute;ria</button>
      <button id="setup-2fa-btn" class="btn-dm sm secondary" type="button">2FA Ativo</button>
      <button id="logout-btn" class="btn-dm sm danger" type="button">Sair</button>
    </div>
  </div>
</header>

<main>
  <div id="flash"></div>

  <!-- Knowledge Topology Card -->
  <section class="topology-card">
    <div class="topology-canvas-wrap">
      <canvas id="brainCanvas"></canvas>
      <div class="topology-hud">TOPOLOGIA DE MEMÓRIA &middot; NÓS E SINAPSES</div>
      <div class="topology-ticker">
        <span class="ticker-indicator"></span>
        <span id="thought-stream-text">Conectado à malha de projetos e chunks do Cerberus.</span>
      </div>
    </div>
    <div class="topology-info">
      <div>
        <h2>Base de Conhecimento Ativa</h2>
        <p>O Cerberus indexa e cruza regras de negócio, ADRs, arquitetura e aprendizados de todos os projetos da Dev Maniac's.</p>
      </div>
      <div class="topology-metrics">
        <div class="topology-metric-box">
          <div class="topology-metric-val" id="mini-stat-nodes">12</div>
          <div class="topology-metric-lbl">Projetos</div>
        </div>
        <div class="topology-metric-box">
          <div class="topology-metric-val" id="mini-stat-synapses">1.254</div>
          <div class="topology-metric-lbl">Chunks &amp; Sinapses</div>
        </div>
      </div>
      <button class="btn-dm sm" id="hero-explore-btn" type="button">Pesquisar Mem&oacute;ria &rarr;</button>
    </div>
  </section>

  <!-- Metric Cards Grid -->
  <section class="hero-grid">
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-title">Arquivos Monitorados</span>
        <span class="stat-tag" id="stat-projects-count">0 PROJETOS</span>
      </div>
      <div class="stat-value" id="m-files">&mdash;</div>
      <p class="stat-desc">Arquivos no reposit&oacute;rio can&ocirc;nico</p>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-title">Documentos &amp; Chunks</span>
        <span class="stat-tag">FTS5 + VETORES</span>
      </div>
      <div class="stat-value" id="m-docs">&mdash;</div>
      <p class="stat-desc">Fragmentos indexados em banco SQLite</p>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-title">Candidatos Inbox</span>
        <span class="stat-tag">AUTO-CAPTURE</span>
      </div>
      <div class="stat-value" id="m-inbox">&mdash;</div>
      <p class="stat-desc">Aprendizados pendentes de aprova&ccedil;&atilde;o</p>
    </div>
    <div class="stat-card">
      <div class="stat-header">
        <span class="stat-title">Motor de Busca</span>
        <span class="stat-tag" id="m-fts">ONLINE</span>
      </div>
      <div class="stat-value">RRF k=60</div>
      <p class="stat-desc" id="status-pill">Fus&atilde;o H&iacute;brida BM25 + Vetores</p>
    </div>
  </section>

  <!-- Nav Tabs -->
  <nav class="nav-tabs" aria-label="Navega&ccedil;&atilde;o principal">
    <button class="nav-tab active" data-tab="tab-search" type="button">
      <span>Busca &amp; Intelig&ecirc;ncia</span>
    </button>
    <button class="nav-tab" data-tab="tab-inbox" type="button">
      <span>Caixa de Entrada</span>
      <span class="badge" id="nav-inbox-badge">0</span>
    </button>
    <button class="nav-tab" data-tab="tab-projects" type="button">
      <span>Projetos &amp; Estrutura</span>
    </button>
    <button class="nav-tab" data-tab="tab-guide" type="button">
      <span>Como Usar o C&eacute;rebro</span>
    </button>
    <button class="nav-tab" data-tab="tab-system" type="button">
      <span>Diagn&oacute;stico</span>
    </button>
  </nav>

  <!-- Tab 1: Busca -->
  <section id="tab-search" class="tab-panel active">
    <div class="content-box">
      <div class="content-box-header">
        <div>
          <h2>Busca H&iacute;brida de Mem&oacute;ria</h2>
          <p>Consulte regras de neg&oacute;cio, arquitetura, ADRs e li&ccedil;&otilde;es corporativas.</p>
        </div>
      </div>

      <div class="search-form">
        <div class="search-input-wrap">
          <input type="search" id="search-q" placeholder="Pesquisar regras, arquitetura, ADRs, banco de dados ou lições..." aria-label="Consulta de busca">
        </div>
        <select id="search-project" aria-label="Filtro de projeto">
          <option value="">(todos os projetos)</option>
        </select>
        <select id="search-mode" aria-label="Modo de busca">
          <option value="hybrid">H&iacute;brido (BM25 + Vetores RRF)</option>
          <option value="lexical">L&eacute;xico (SQLite FTS5 BM25)</option>
          <option value="semantic">Sem&acirc;ntico (Dense Vectors)</option>
        </select>
        <button id="search-btn" class="btn-dm" type="button">Buscar &rarr;</button>
      </div>

      <div class="chips-bar">
        <span class="chips-label">Atalhos:</span>
        <button class="chip" data-query="arquitetura" type="button">#arquitetura</button>
        <button class="chip" data-query="regras de negócio" type="button">#regras-de-negocio</button>
        <button class="chip" data-query="multi-tenant" type="button">#multi-tenant</button>
        <button class="chip" data-query="banco de dados" type="button">#database</button>
        <button class="chip" data-query="seguranca" type="button">#seguranca</button>
        <button class="chip" data-query="protocolo ai" type="button">#protocolo-ai</button>
      </div>

      <div id="search-results">
        <div class="empty-state">
          <strong>Pronto para pesquisar</strong>
          <p>Digite uma pergunta ou clique em um atalho acima para consultar a base.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Tab 2: Caixa de Entrada -->
  <section id="tab-inbox" class="tab-panel">
    <div class="content-box">
      <div class="content-box-header">
        <div>
          <h2>Caixa de Entrada &amp; Candidatos (Inbox)</h2>
          <p>Aprendizados e decisões capturados automaticamente pelos agentes de IA.</p>
        </div>
        <button id="refresh-btn" class="btn-dm sm secondary" type="button">Atualizar Inbox</button>
      </div>

      <div class="inbox-toolbar">
        <div class="filter-tabs">
          <button class="filter-tab-btn active" data-status="" type="button">TODOS</button>
          <button class="filter-tab-btn" data-status="CANDIDATE" type="button">CANDIDATE</button>
          <button class="filter-tab-btn" data-status="VERIFIED" type="button">VERIFIED</button>
          <button class="filter-tab-btn" data-status="QUARANTINED" type="button">QUARANTINED</button>
          <button class="filter-tab-btn" data-status="CANONICAL" type="button">CANONICAL</button>
          <button class="filter-tab-btn" data-status="REJECTED" type="button">REJECTED</button>
        </div>
      </div>

      <div id="inbox-table">
        <div class="empty-state">
          <strong>Inbox vazia</strong>
          <p>Nenhum candidato pendente de revis&atilde;o no momento.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Tab 3: Projetos -->
  <section id="tab-projects" class="tab-panel">
    <div class="content-box">
      <div class="content-box-header">
        <div>
          <h2>Projetos &amp; Base de Conhecimento</h2>
          <p>Mapeamento de isolamento e dom&iacute;nios corporativos da Dev Maniac's.</p>
        </div>
      </div>
      <div class="projects-grid" id="projects-container">
        <!-- Rendered via JS -->
      </div>
    </div>
  </section>

  <!-- Tab 4: Como Usar o Cérebro -->
  <section id="tab-guide" class="tab-panel">
    <div class="content-box">
      <div class="content-box-header">
        <div>
          <h2>Como Usar o C&eacute;rebro (Cerberus Intelligence)</h2>
          <p>Entenda como humanos e agentes de IA consultam e promovem memória.</p>
        </div>
      </div>

      <div class="guide-grid">
        <div class="guide-card">
          <div class="guide-card-icon">1</div>
          <h3>Como a IA Consulta a Mem&oacute;ria</h3>
          <p>Agentes aut&ocirc;nomos (Gemini Maestro, Codex, MiniMax M3, GLM) acessam o Cerberus via MCP ou REST antes de programar.</p>
          <div class="code-snippet">
            cerberus_get_context_pack({<br>
            &nbsp;&nbsp;project: "dm-erp",<br>
            &nbsp;&nbsp;task_type: "backend_feature"<br>
            })
          </div>
        </div>

        <div class="guide-card">
          <div class="guide-card-icon">2</div>
          <h3>Como o Humano Consulta &amp; Audita</h3>
          <p>Faça pesquisas na aba <strong>Busca &amp; Inteligência</strong> ou audite novos aprendizados na aba <strong>Caixa de Entrada</strong>.</p>
          <div class="code-snippet">
            Busca: "Como funciona o isolamento multi-tenant?"<br>
            Modo: Híbrido (FTS5 BM25 + Vetores RRF)
          </div>
        </div>

        <div class="guide-card">
          <div class="guide-card-icon">3</div>
          <h3>Ciclo de Aprendizado</h3>
          <p>O agente envia como <code>CANDIDATE</code>, o QA verifica (<code>VERIFIED</code>) e o PO Helbert promove para <code>CANONICAL</code>.</p>
          <div class="code-snippet">
            CANDIDATE &rarr; VERIFIED &rarr; CANONICAL (Promovido)
          </div>
        </div>

        <div class="guide-card">
          <div class="guide-card-icon">4</div>
          <h3>Comandos no Terminal (CLI)</h3>
          <p>Consulte diretamente da linha de comando na raiz do projeto:</p>
          <div class="code-snippet">
            python bin/cerberus search "multi-tenant"<br>
            python bin/cerberus status<br>
            python bin/cerberus session-context dm-erp
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Tab 5: Diagnóstico -->
  <section id="tab-system" class="tab-panel">
    <div class="content-box">
      <div class="content-box-header">
        <div>
          <h2>Diagn&oacute;stico do Sistema Cerberus</h2>
          <p>Informa&ccedil;&otilde;es de infraestrutura, armazenamento e seguran&ccedil;a operacional.</p>
        </div>
      </div>
      <table class="system-table">
        <tbody>
          <tr><td>Ambiente &middot; Rede</td><td id="sys-bind">&mdash;</td></tr>
          <tr><td>Diret&oacute;rio Can&ocirc;nico</td><td id="sys-root">&mdash;</td></tr>
          <tr><td>Motor SQLite FTS5</td><td id="sys-fts">&mdash;</td></tr>
          <tr><td>Embeddings &amp; Vetores</td><td>HashingDenseEmbeddingProvider (256-dim feature hashing, L2 normalized)</td></tr>
          <tr><td>Rank Fusion</td><td>Reciprocal Rank Fusion (RRF k=60, determin&iacute;stico)</td></tr>
          <tr><td>Seguran&ccedil;a &amp; Autentica&ccedil;&atilde;o</td><td>Cookie de Sess&atilde;o HMAC-SHA256 &middot; 2FA TOTP RFC 6238 &middot; Rate Limiting</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <footer class="main-footer">
    <div>
      <a href="https://devmaniacs.com.br" target="_blank" rel="noopener noreferrer">devmaniacs.com.br</a>
      <span>&middot;</span>
      <a href="https://suporte.devmaniacs.com.br" target="_blank" rel="noopener noreferrer">Suporte</a>
      <span>&middot;</span>
      <a href="https://radierhub.com.br" target="_blank" rel="noopener noreferrer">RadierHUB</a>
    </div>
    <div style="margin-top:4px;">&copy; 2026 Dev Maniac's &middot; Game &amp; Systems Development. Todos os direitos reservados. &middot; Tecnologia feita de perto.</div>
  </footer>
</main>

<!-- Inspector Modal -->
<div class="modal-backdrop" id="modal" role="dialog" aria-modal="true">
  <div class="modal">
    <div class="modal-header">
      <h3 id="modal-title">Detalhes do Documento</h3>
      <button class="btn-dm sm secondary" id="modal-close-x" type="button">&times;</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
    <div class="modal-footer">
      <button class="btn-dm sm secondary" id="modal-close" type="button">Fechar</button>
      <button class="btn-dm sm" id="modal-promote" type="button" style="display:none;">Promover para Can&ocirc;nico</button>
      <button class="btn-dm sm danger" id="modal-reject" type="button" style="display:none;">Rejeitar</button>
    </div>
  </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function () {
  "use strict";
  const flash = document.getElementById("flash");
  function notice(kind, msg) {
    if (!msg || !flash) return;
    const div = document.createElement("div");
    div.className = "toast " + (kind === "ok" ? "ok" : "error");
    div.textContent = (kind === "ok" ? "[OK] " : "[AVISO] ") + msg;
    flash.appendChild(div);
    setTimeout(() => { div.remove(); }, 4000);
  }

  async function getJSON(url) {
    const r = await fetch(url, { headers: { "Accept": "application/json" } });
    const text = await r.text();
    if (!r.ok) { throw new Error(text || (r.status + " " + r.statusText)); }
    return JSON.parse(text);
  }

  async function postJSON(url, body) {
    const r = await fetch(url, {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body || {})
    });
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

  // ------- 1. Tab Switching (Isolated & Fail-Safe) -------
  try {
    const tabs = document.querySelectorAll(".nav-tab");
    tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        const targetId = tab.dataset.tab;
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
        const activePanel = document.getElementById(targetId);
        if (activePanel) activePanel.classList.add("active");
      });
    });
    const exploreBtn = document.getElementById("hero-explore-btn");
    if (exploreBtn) {
      exploreBtn.addEventListener("click", () => {
        const searchTab = document.querySelector('.nav-tab[data-tab="tab-search"]');
        if (searchTab) searchTab.click();
      });
    }
  } catch (err) {
    console.error("Tab setup error:", err);
  }

  // ------- 2. Knowledge Topology Canvas (Solid & Interactive) -------
  function initTopologyCanvas() {
    try {
      const canvas = document.getElementById("brainCanvas");
      if (!canvas || !canvas.parentElement) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      let width = (canvas.width = canvas.parentElement.clientWidth || 600);
      let height = (canvas.height = canvas.parentElement.clientHeight || 280);

      window.addEventListener("resize", () => {
        if (!canvas.parentElement) return;
        width = canvas.width = canvas.parentElement.clientWidth || 600;
        height = canvas.height = canvas.parentElement.clientHeight || 280;
      });

      const projectLabels = ["DM-ERP", "BIOLAR", "HELPDEV", "TEENUS", "_GLOBAL", "_SHARED", "DMPDV", "APAE", "DESK", "ORCH", "VECTORS", "FTS5"];
      const nodes = [];
      const nodeCount = projectLabels.length;

      for (let i = 0; i < nodeCount; i++) {
        const phi = Math.acos(1 - 2 * (i + 0.5) / nodeCount);
        const theta = Math.PI * (1 + Math.sqrt(5)) * i;
        const radius = 90;
        nodes.push({
          x: radius * Math.sin(phi) * Math.cos(theta),
          y: radius * Math.sin(phi) * Math.sin(theta),
          z: radius * Math.cos(phi),
          label: projectLabels[i],
          color: i % 4 === 0 ? "#08b9ca" : (i % 4 === 1 ? "#ff4c4c" : (i % 4 === 2 ? "#ffc529" : "#1e40af")),
          size: 6
        });
      }

      let rotX = 0.2;
      let rotY = 0.3;
      let isDragging = false;
      let lastMouseX = 0;
      let lastMouseY = 0;

      canvas.addEventListener("mousedown", e => {
        isDragging = true;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
      });
      window.addEventListener("mouseup", () => isDragging = false);
      window.addEventListener("mousemove", e => {
        if (!isDragging) return;
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        rotY += dx * 0.008;
        rotX += dy * 0.008;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
      });

      let pulseTime = 0;
      function renderLoop() {
        try {
          ctx.fillStyle = "#061637";
          ctx.fillRect(0, 0, width, height);

          if (!isDragging) {
            rotY += 0.004;
            rotX += 0.001;
          }
          pulseTime += 0.03;

          const cosX = Math.cos(rotX), sinX = Math.sin(rotX);
          const cosY = Math.cos(rotY), sinY = Math.sin(rotY);

          function project(p3) {
            let x1 = p3.x * cosY + p3.z * sinY;
            let z1 = -p3.x * sinY + p3.z * cosY;
            let y2 = p3.y * cosX - z1 * sinX;
            let z2 = p3.y * sinX + z1 * cosX;

            const fov = 260;
            const scale = fov / (fov + z2 + 130);
            return {
              x: width / 2 + x1 * scale,
              y: height / 2 + y2 * scale,
              scale: scale,
              z: z2
            };
          }

          // Connections
          for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
              const dist = Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y, nodes[i].z - nodes[j].z);
              if (dist < 150) {
                const p1 = project(nodes[i]);
                const p2 = project(nodes[j]);
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.strokeStyle = "rgba(30, 58, 109, 0.7)";
                ctx.lineWidth = 1.2;
                ctx.stroke();

                const pulsePos = (Math.sin(pulseTime + i + j) + 1) / 2;
                const px = p1.x + (p2.x - p1.x) * pulsePos;
                const py = p1.y + (p2.y - p1.y) * pulsePos;
                ctx.beginPath();
                ctx.arc(px, py, 2, 0, Math.PI * 2);
                ctx.fillStyle = "#08b9ca";
                ctx.fill();
              }
            }
          }

          // Nodes
          const projectedNodes = nodes.map(n => ({ ...n, pr: project(n) }));
          projectedNodes.sort((a, b) => b.pr.z - a.pr.z);

          projectedNodes.forEach(n => {
            const pr = n.pr;
            ctx.beginPath();
            ctx.arc(pr.x, pr.y, n.size * pr.scale, 0, Math.PI * 2);
            ctx.fillStyle = n.color;
            ctx.fill();

            if (pr.scale > 0.7) {
              ctx.font = "bold 11px 'Space Grotesk', sans-serif";
              ctx.fillStyle = "#ffffff";
              ctx.fillText(n.label, pr.x + 8, pr.y + 4);
            }
          });

          requestAnimationFrame(renderLoop);
        } catch (e) {
          console.error("Render loop error:", e);
        }
      }
      renderLoop();

      // Thought stream ticker
      const streamMessages = [
        "[Cerberus] 822 chunks indexados em SQLite FTS5 + Vetores RRF...",
        "[Gemini Maestro] Orquestrando governança e pipelines multi-agente...",
        "[MiniMax M3] Consultando regras de negócio do RadierHUB e Teenus...",
        "[Codex GPT-5.6] Validando integridade relacional e embeddings...",
        "[Auto-Capture] Monitorando novas decisões de arquitetura (ADRs)..."
      ];
      let msgIdx = 0;
      setInterval(() => {
        msgIdx = (msgIdx + 1) % streamMessages.length;
        const ticker = document.getElementById("thought-stream-text");
        if (ticker) ticker.textContent = streamMessages[msgIdx];
      }, 4000);
    } catch (err) {
      console.error("Topology init error:", err);
    }
  }

  // ------- 3. Status & Metrics Engine -------
  async function refreshStatus() {
    try {
      const s = await getJSON("/api/status");
      const elFiles = document.getElementById("m-files");
      if (elFiles) elFiles.textContent = s.files;
      const elDocs = document.getElementById("m-docs");
      if (elDocs) elDocs.textContent = s.documents;
      const elInbox = document.getElementById("m-inbox");
      if (elInbox) elInbox.textContent = s.inbox_count;
      const elNavBadge = document.getElementById("nav-inbox-badge");
      if (elNavBadge) elNavBadge.textContent = s.inbox_count;
      const elFts = document.getElementById("m-fts");
      if (elFts) elFts.textContent = s.fts5 ? "ONLINE" : "OFFLINE";
      const elCount = document.getElementById("stat-projects-count");
      if (elCount) elCount.textContent = (s.projects ? s.projects.length : 0) + " PROJETOS";

      const miniSynapses = document.getElementById("mini-stat-synapses");
      if (miniSynapses) miniSynapses.textContent = s.documents;
      const miniNodes = document.getElementById("mini-stat-nodes");
      if (miniNodes) miniNodes.textContent = s.projects ? s.projects.length : 12;

      const sysBind = document.getElementById("sys-bind");
      if (sysBind) sysBind.textContent = esc(s.bind_host) + ":" + s.bind_port + " (Cloudflare Argo Tunnel)";
      const sysRoot = document.getElementById("sys-root");
      if (sysRoot) sysRoot.textContent = esc(s.canonical_root);
      const sysFts = document.getElementById("sys-fts");
      if (sysFts) sysFts.textContent = s.fts5 ? "SQLite FTS5 Ativo (Tokenize: porter unicode61)" : "FTS5 Indisponível";

      const sel = document.getElementById("search-project");
      if (sel) {
        sel.innerHTML = '<option value="">(todos os projetos)</option>';
        (s.projects || []).forEach(p => {
          const opt = document.createElement("option");
          opt.value = p;
          opt.textContent = p;
          sel.appendChild(opt);
        });
      }

      renderProjectsGrid(s);
    } catch (e) {
      console.error("Status error:", e);
      notice("error", "Erro ao carregar status: " + e.message);
    }
  }

  function renderProjectsGrid(stats) {
    const container = document.getElementById("projects-container");
    if (!container) return;
    const projects = stats.projects || ["dm-erp", "biolar", "helpdev", "teenus", "_global", "_shared"];
    const indexed = stats.indexed_projects || [];

    container.innerHTML = projects.map(p => {
      const isIndexed = indexed.includes(p);
      return `
        <div class="project-card">
          <div>
            <div class="project-card-header">
              <h3 class="project-card-name">${esc(p)}</h3>
              <span class="pill project">${isIndexed ? 'INDEXADO' : 'MONITORADO'}</span>
            </div>
            <ul class="project-stats-list">
              <li><span>Status</span><strong>${isIndexed ? 'Pronto para busca' : 'Ativo'}</strong></li>
              <li><span>Isolamento</span><strong>Multi-Tenant Blindado</strong></li>
            </ul>
          </div>
          <button class="btn-dm sm secondary filter-project-btn" data-project="${esc(p)}" type="button">
            Filtrar Mem&oacute;ria &rarr;
          </button>
        </div>
      `;
    }).join("");

    container.querySelectorAll(".filter-project-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const proj = btn.dataset.project;
        const selProj = document.getElementById("search-project");
        if (selProj) selProj.value = proj;
        const tabBtn = document.querySelector('.nav-tab[data-tab="tab-search"]');
        if (tabBtn) tabBtn.click();
        runSearch();
      });
    });
  }

  // ------- 4. Search Execution Engine -------
  async function runSearch() {
    const inputQ = document.getElementById("search-q");
    const selectProj = document.getElementById("search-project");
    const selectMode = document.getElementById("search-mode");
    const out = document.getElementById("search-results");
    if (!out) return;

    const q = inputQ ? inputQ.value.trim() : "";
    const project = selectProj ? selectProj.value : "";
    const mode = selectMode ? selectMode.value : "hybrid";

    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (project) params.set("project", project);
    params.set("mode", mode);

    out.innerHTML = '<div class="empty-state"><strong>Buscando...</strong><p>Consultando base vetorial e léxica.</p></div>';

    try {
      const r = await getJSON("/api/search?" + params.toString());
      if (!r.results || !r.results.length) {
        out.innerHTML = '<div class="empty-state"><strong>Nenhum resultado encontrado</strong><p>Tente outros termos ou remova o filtro de projeto.</p></div>';
        return;
      }

      const cards = r.results.map(item => `
        <div class="result-card">
          <div class="result-card-header">
            <div>
              <h3 class="result-card-title">${esc(item.title)}</h3>
              <div class="result-card-path">${esc(item.source_path)}</div>
            </div>
            <button class="btn-dm sm secondary view-doc-btn" data-id="${esc(item.memory_id || item.chunk_id)}" type="button">
              Ver Documento &rarr;
            </button>
          </div>
          <div class="result-meta-pills">
            <span class="pill project">${esc(item.project_id || '_global')}</span>
            <span class="pill authority">Auth: ${esc(item.authority_level || 50)}</span>
            <span class="pill score">${esc(item.search_mode)} &middot; Score ${esc(Number(item.final_score).toFixed(2))}</span>
          </div>
          <div class="result-snippet">${item.snippet || '(sem snippet)'}</div>
        </div>
      `).join("");

      out.innerHTML = `<div class="results-grid">${cards}</div>`;
      out.querySelectorAll(".view-doc-btn").forEach(btn => {
        btn.addEventListener("click", () => openDocument(btn.dataset.id));
      });
    } catch (e) {
      out.innerHTML = '<div class="toast error" style="position:static;">Erro na busca: ' + esc(e.message) + '</div>';
    }
  }

  // Quick Chips
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const inputQ = document.getElementById("search-q");
      if (inputQ) inputQ.value = chip.dataset.query;
      runSearch();
    });
  });

  const searchBtn = document.getElementById("search-btn");
  if (searchBtn) searchBtn.addEventListener("click", runSearch);
  const searchInput = document.getElementById("search-q");
  if (searchInput) {
    searchInput.addEventListener("keydown", e => {
      if (e.key === "Enter") runSearch();
    });
  }

  // ------- 5. Candidate Inbox Engine -------
  let activeInboxFilter = "";
  async function refreshInbox() {
    const out = document.getElementById("inbox-table");
    if (!out) return;
    const url = "/api/inbox" + (activeInboxFilter ? "?status=" + encodeURIComponent(activeInboxFilter) : "");

    try {
      const r = await getJSON(url);
      const list = r.candidates || [];
      const badge = document.getElementById("nav-inbox-badge");
      if (badge) badge.textContent = list.length;
      const mInbox = document.getElementById("m-inbox");
      if (mInbox) mInbox.textContent = list.length;

      if (!list.length) {
        out.innerHTML = '<div class="empty-state"><strong>Inbox vazia</strong><p>Nenhum candidato com o status selecionado.</p></div>';
        return;
      }

      const rows = list.map(c => `
        <div class="candidate-card">
          <div class="candidate-card-top">
            <div>
              <h3 class="candidate-title">${esc(c.title)}</h3>
              <div class="candidate-desc">ID: ${esc(c.candidate_id)} &middot; Task: ${esc(c.task_id)} &middot; Agente: ${esc(c.agent)} &middot; ${esc(c.created_at)}</div>
            </div>
            <div style="display:flex;gap:6px;align-items:center;">
              <span class="pill project">${esc(c.project_id)}</span>
              ${statusTag(c.status)}
            </div>
          </div>
          <div class="result-snippet" style="max-height:80px;overflow:hidden;">${esc(c.content.slice(0, 300))}&hellip;</div>
          <div class="candidate-actions">
            <button class="btn-dm sm secondary open-candidate-btn" data-id="${esc(c.candidate_id)}" type="button">Inspecionar &amp; Diff</button>
            ${c.status === 'VERIFIED' ? `<button class="btn-dm sm promote-candidate-btn" data-id="${esc(c.candidate_id)}" type="button">Promover para Canônico</button>` : ''}
            ${c.status !== 'CANONICAL' ? `<button class="btn-dm sm danger reject-candidate-btn" data-id="${esc(c.candidate_id)}" type="button">Rejeitar</button>` : ''}
          </div>
        </div>
      `).join("");

      out.innerHTML = `<div class="candidates-grid">${rows}</div>`;
      out.querySelectorAll(".open-candidate-btn").forEach(b => b.addEventListener("click", () => openCandidate(b.dataset.id)));
      out.querySelectorAll(".promote-candidate-btn").forEach(b => b.addEventListener("click", () => promoteCandidateDirect(b.dataset.id)));
      out.querySelectorAll(".reject-candidate-btn").forEach(b => b.addEventListener("click", () => rejectCandidateDirect(b.dataset.id)));
    } catch (e) {
      out.innerHTML = '<div class="toast error" style="position:static;">Erro no inbox: ' + esc(e.message) + '</div>';
    }
  }

  document.querySelectorAll(".filter-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeInboxFilter = btn.dataset.status;
      refreshInbox();
    });
  });

  async function promoteCandidateDirect(id) {
    try {
      await postJSON("/api/inbox/" + encodeURIComponent(id) + "/promote");
      notice("ok", "Item promovido para a memória canônica.");
      refreshInbox();
      refreshStatus();
    } catch (e) { notice("error", "Erro ao promover: " + e.message); }
  }

  async function rejectCandidateDirect(id) {
    try {
      await postJSON("/api/inbox/" + encodeURIComponent(id) + "/reject");
      notice("ok", "Candidato rejeitado.");
      refreshInbox();
      refreshStatus();
    } catch (e) { notice("error", "Erro ao rejeitar: " + e.message); }
  }

  // ------- 6. Modal Windows -------
  let currentCandidate = null;
  async function openCandidate(id) {
    try {
      const c = await getJSON("/api/inbox/" + encodeURIComponent(id));
      currentCandidate = c;
      const title = document.getElementById("modal-title");
      if (title) title.textContent = c.title + " (" + c.candidate_id + ")";
      const body = document.getElementById("modal-body");
      if (body) {
        body.innerHTML = `
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:14px;">
            ${statusTag(c.status)}
            <span class="pill project">${esc(c.project_id)}</span>
            <span class="pill authority">Task: ${esc(c.task_id)}</span>
            <span class="pill score">Agente: ${esc(c.agent)}</span>
          </div>
          <h4 style="margin:16px 0 6px;text-transform:uppercase;font-size:12px;color:#94a3b8;">Conteúdo</h4>
          <div class="code-viewer">${esc(c.content)}</div>
          <h4 style="margin:16px 0 6px;text-transform:uppercase;font-size:12px;color:#94a3b8;">Diff Canônico</h4>
          <div class="code-viewer">${esc(c.diff || '(nenhum diff registrado)')}</div>
        `;
      }
      const promoteBtn = document.getElementById("modal-promote");
      const rejectBtn = document.getElementById("modal-reject");
      if (promoteBtn) promoteBtn.style.display = (c.status === "VERIFIED") ? "inline-flex" : "none";
      if (rejectBtn) rejectBtn.style.display = (c.status !== "CANONICAL") ? "inline-flex" : "none";
      const modal = document.getElementById("modal");
      if (modal) modal.classList.add("open");
    } catch (e) { notice("error", "Erro ao abrir candidato: " + e.message); }
  }

  async function openDocument(id) {
    try {
      const doc = await getJSON("/api/document?id=" + encodeURIComponent(id));
      const title = document.getElementById("modal-title");
      if (title) title.textContent = doc.title;
      const body = document.getElementById("modal-body");
      if (body) {
        body.innerHTML = `
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:14px;flex-wrap:wrap;">
            <span class="pill project">${esc(doc.project_id)}</span>
            <span class="pill authority">Autoridade: ${esc(doc.authority_level)}</span>
            <span class="pill score">Tipo: ${esc(doc.source_type)}</span>
            <span class="pill score">${esc(doc.source_path)}</span>
          </div>
          <h4 style="margin:16px 0 6px;text-transform:uppercase;font-size:12px;color:#94a3b8;">Texto Completo</h4>
          <div class="code-viewer">${esc(doc.full_text || doc.snippet || '(sem texto)')}</div>
        `;
      }
      const promoteBtn = document.getElementById("modal-promote");
      const rejectBtn = document.getElementById("modal-reject");
      if (promoteBtn) promoteBtn.style.display = "none";
      if (rejectBtn) rejectBtn.style.display = "none";
      const modal = document.getElementById("modal");
      if (modal) modal.classList.add("open");
    } catch (e) {
      notice("error", "Erro ao carregar documento: " + e.message);
    }
  }

  function closeModal() {
    const modal = document.getElementById("modal");
    if (modal) modal.classList.remove("open");
  }
  const closeBtn = document.getElementById("modal-close");
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  const closeBtnX = document.getElementById("modal-close-x");
  if (closeBtnX) closeBtnX.addEventListener("click", closeModal);
  const modalElem = document.getElementById("modal");
  if (modalElem) {
    modalElem.addEventListener("click", e => {
      if (e.target.id === "modal") closeModal();
    });
  }
  window.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

  const modalPromote = document.getElementById("modal-promote");
  if (modalPromote) {
    modalPromote.addEventListener("click", async () => {
      if (!currentCandidate) return;
      await promoteCandidateDirect(currentCandidate.candidate_id);
      closeModal();
    });
  }
  const modalReject = document.getElementById("modal-reject");
  if (modalReject) {
    modalReject.addEventListener("click", async () => {
      if (!currentCandidate) return;
      await rejectCandidateDirect(currentCandidate.candidate_id);
      closeModal();
    });
  }

  // ------- 7. Re-indexing & Auth Handlers -------
  const reindexBtn = document.getElementById("reindex-btn");
  if (reindexBtn) {
    reindexBtn.addEventListener("click", async () => {
      reindexBtn.disabled = true;
      reindexBtn.textContent = "Reindexando...";
      try {
        const res = await postJSON("/api/reindex");
        notice("ok", "Reindexação concluída: " + (res.stats ? res.stats.indexed_files : 0) + " arquivos processados.");
        await refreshStatus();
        await refreshInbox();
      } catch (e) {
        notice("error", "Erro ao reindexar: " + e.message);
      } finally {
        reindexBtn.disabled = false;
        reindexBtn.textContent = "Reindexar Memória";
      }
    });
  }

  const refreshBtn = document.getElementById("refresh-btn");
  if (refreshBtn) refreshBtn.addEventListener("click", refreshInbox);

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        await postJSON("/auth/logout");
        window.location.href = "/auth/login";
      } catch (e) {
        window.location.href = "/auth/login";
      }
    });
  }

  const setup2faBtn = document.getElementById("setup-2fa-btn");
  if (setup2faBtn) {
    setup2faBtn.addEventListener("click", () => {
      window.location.href = "/auth/setup-2fa";
    });
  }

  if (window.location.search.includes("setup=ok")) {
    notice("ok", "2FA configurado com sucesso.");
  }

  // ------- 8. Boot Sequence -------
  initTopologyCanvas();
  refreshStatus();
  refreshInbox();
  runSearch();
});
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
    <path fill="#8b35d1" stroke="none" d="M34 90h57v54H34z"/>
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
  <rect x="198" y="130" width="9" height="9" fill="#8b35d1"/>
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
    """Render the Dev Maniac's Cerberus Inspector login page in Suporte Dev Maniac's theme."""
    error_block = ""
    if error_message:
        escaped = (error_message.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
        error_block = (
            f'<div class="login-error" role="alert">'
            f'<span class="err-dot"></span><span>{escaped}</span></div>'
        )
    # Step rendering
    creds_class = "step-content active" if step == "credentials" else "step-content"
    totp_class = "step-content active" if step == "totp" else "step-content"
    if step == "credentials":
        creds_block = f'''
<form id="loginForm" method="POST" action="/auth/login" class="step-form" autocomplete="on">
  <label class="field">
    <span>E-mail Corporativo</span>
    <input type="email" name="email" required autofocus autocomplete="username"
           placeholder="helbert.moura@devmaniacs.com.br" value="{target_email}">
  </label>
  <label class="field">
    <span>Senha de Acesso</span>
    <input type="password" name="password" required autocomplete="current-password"
           placeholder="••••••••••••" minlength="8">
  </label>
  <button type="submit" class="btn-dm primary">Acessar Central de Memória &rarr;</button>
</form>'''
        totp_block = ''
    else:
        creds_block = ''
        totp_block = f'''
<form id="totpForm" method="POST" action="/auth/login" class="step-form" autocomplete="off">
  <input type="hidden" name="pending_token" value="{pending_token}">
  <input type="hidden" name="email" value="{target_email}">
  <div class="totp-badge"><span>2FA &middot; AUTENTICAÇÃO EM DUAS ETAPAS</span></div>
  <p class="totp-help">Digite o código de 8 dígitos gerado no seu aplicativo autenticador.</p>
  <label class="field">
    <span>Código de Autenticação</span>
    <input type="text" name="totp" required autofocus inputmode="numeric"
           autocomplete="one-time-code" pattern="\\d{{8}}" maxlength="8"
           placeholder="00000000" class="totp-input">
  </label>
  <button type="submit" class="btn-dm primary">Confirmar &amp; Entrar &rarr;</button>
  <div class="back-link"><a href="/auth/login">&larr; Voltar para o login</a></div>
</form>'''

    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#061637">
<title>Cerberus Inspector &mdash; Dev Maniac's Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-deep: #061637;
  --bg-deep-2: #0a192f;
  --bg-elev: #0d2247;
  --border-dark: #1e3a6d;
  --ink-light: #f8fafc;
  --text-muted: #94a3b8;
  --dm-cyan: #08b9ca;
  --dm-red: #ff4c4c;
  --dm-yellow: #ffc529;
  --dm-purple: #8b35d1;
  --font: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-display: 'Space Grotesk', var(--font);
  --font-mono: 'IBM Plex Mono', ui-monospace, monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: var(--font);
  background: var(--bg-deep);
  color: var(--ink-light);
  font-size: 14.5px;
}}
body {{
  background-image:
    radial-gradient(ellipse at 50% 15%, rgba(8, 185, 202, 0.18), transparent 70%),
    radial-gradient(ellipse at 80% 80%, rgba(139, 53, 209, 0.12), transparent 60%),
    linear-gradient(180deg, #061637 0%, #0a192f 100%);
  background-attachment: fixed;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px 24px;
}}
.auth-wrapper {{
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.card {{
  background: rgba(13, 34, 71, 0.85);
  backdrop-filter: blur(14px);
  border: 1px solid var(--border-dark);
  border-radius: 18px;
  padding: 34px 32px 30px;
  width: 100%;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.45), 0 0 20px rgba(8, 185, 202, 0.1);
  position: relative;
  overflow: hidden;
}}
.card::before {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--dm-cyan), var(--dm-purple));
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
  width: 64px;
  height: 64px;
  background: #0d2247;
  border: 1.5px solid rgba(8, 185, 202, 0.5);
  border-radius: 14px;
  margin-bottom: 14px;
  box-shadow: 0 0 16px rgba(8, 185, 202, 0.25);
}}
.brand-title {{
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: #ffffff;
  margin: 0 0 4px;
}}
.brand-tag {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--dm-cyan);
  background: rgba(8, 185, 202, 0.12);
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid rgba(8, 185, 202, 0.35);
  margin-bottom: 8px;
}}
.card-subtitle {{
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.4;
}}
.field {{
  display: block;
  margin-bottom: 18px;
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
  min-height: 46px;
  padding: 10px 14px;
  font: inherit;
  font-size: 14.5px;
  background: rgba(6, 22, 55, 0.85);
  color: #ffffff;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
  transition: all 0.15s ease;
}}
.field input:focus {{
  outline: none;
  border-color: var(--dm-cyan);
  box-shadow: 0 0 0 3px rgba(8, 185, 202, 0.25);
}}
.totp-input {{
  font-family: var(--font-mono);
  font-size: 22px !important;
  font-weight: 700;
  letter-spacing: 0.25em;
  text-align: center;
}}
.btn-dm {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 20px;
  font-family: var(--font);
  font-weight: 700;
  font-size: 14.5px;
  color: #fff;
  background: var(--dm-cyan);
  border: 1px solid rgba(8, 185, 202, 0.6);
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(8, 185, 202, 0.3);
  transition: all 0.15s ease;
  width: 100%;
  margin-top: 8px;
  text-decoration: none;
}}
.btn-dm:hover {{
  background: #0aa7b7;
  box-shadow: 0 6px 18px rgba(8, 185, 202, 0.45);
  transform: translateY(-1px);
}}
.btn-dm:active {{ transform: translateY(0); }}
.totp-badge {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--dm-cyan);
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
  font-weight: 600;
  color: var(--text-muted);
  text-decoration: none;
}}
.back-link a:hover {{
  color: var(--dm-cyan);
  text-decoration: underline;
}}
.login-error {{
  display: flex;
  gap: 10px;
  align-items: center;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 18px;
}}
.err-dot {{
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  flex-shrink: 0;
}}
.step-content {{ display: none; }}
.step-content.active {{ display: block; }}
.step-fade {{ animation: fade 0.28s ease; }}
@keyframes fade {{ from {{ opacity: 0; transform: translateY(-4px); }}
                   to   {{ opacity: 1; transform: translateY(0); }} }}

/* Footer Institutional (Dev Maniac's standard) */
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
  color: var(--dm-cyan);
  text-decoration: none;
  font-weight: 600;
}}
.auth-footer-links a:hover {{
  text-decoration: underline;
  color: #38bdf8;
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
</style>
</head>
<body>
  <div class="auth-wrapper">
    <main class="card">
      <div class="brand-header">
        <div class="brand-logo-wrap">
          {DEV_MANIACS_LOGO_SVG}
        </div>
        <h1 class="brand-title">Dev Maniac's</h1>
        <span class="brand-tag"><span class="err-dot" style="background:var(--dm-cyan);"></span> CERBERUS INTELLIGENCE</span>
        <p class="card-subtitle">Central de Mem&oacute;ria Corporativa &middot; Acesso Seguro</p>
      </div>
      {error_block}
      <section class="{creds_class}" id="credsStep">
        {creds_block}
      </section>
      <section class="{totp_class} step-fade" id="totpStep">
        {totp_block}
      </section>
    </main>
    <footer class="auth-footer">
      <nav class="auth-footer-links" aria-label="Links institucionais">
        <a href="https://devmaniacs.com.br" target="_blank" rel="noopener noreferrer">devmaniacs.com.br</a>
        <span>&middot;</span>
        <a href="https://suporte.devmaniacs.com.br" target="_blank" rel="noopener noreferrer">Suporte</a>
        <span>&middot;</span>
        <a href="https://radierhub.com.br" target="_blank" rel="noopener noreferrer">RadierHUB</a>
      </nav>
      <div>&copy; 2026 Dev Maniac's &middot; Game &amp; Systems Development. Todos os direitos reservados.</div>
      <div class="auth-security-badge">
        <span>Cloudflare Argo Tunnel Blindado &middot; 2FA TOTP RFC 6238</span>
      </div>
    </footer>
  </div>
</body>
</html>'''


def _render_setup_2fa_html(secret_b32: str, otp_uri: str,
                            svg: str, error_message: str = "") -> str:
    err_block = ""
    if error_message:
        escaped = (error_message.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
        err_block = (
            f'<div class="login-error" role="alert"><span class="err-dot"></span> '
            f'<span>{escaped}</span></div>'
        )
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#061637">
<title>Cerberus Inspector &mdash; Configurar 2FA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg-deep: #061637;
  --bg-deep-2: #0a192f;
  --bg-elev: #0d2247;
  --border-dark: #1e3a6d;
  --ink-light: #f8fafc;
  --text-muted: #94a3b8;
  --dm-cyan: #08b9ca;
  --dm-red: #ff4c4c;
  --dm-yellow: #ffc529;
  --font: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-display: 'Space Grotesk', var(--font);
  --font-mono: 'IBM Plex Mono', ui-monospace, monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  min-height: 100vh;
  font-family: var(--font);
  background: var(--bg-deep);
  color: var(--ink-light);
  font-size: 14.5px;
}}
body {{
  background-image:
    radial-gradient(ellipse at 50% 15%, rgba(8, 185, 202, 0.18), transparent 70%),
    linear-gradient(180deg, #061637 0%, #0a192f 100%);
  background-attachment: fixed;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px 24px;
}}
.auth-wrapper {{
  width: 100%;
  max-width: 540px;
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.card {{
  background: rgba(13, 34, 71, 0.85);
  backdrop-filter: blur(14px);
  border: 1px solid var(--border-dark);
  border-radius: 18px;
  padding: 32px;
  width: 100%;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.45);
  position: relative;
  overflow: hidden;
}}
.card::before {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--dm-cyan), var(--dm-yellow));
}}
.brand-header {{
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-dark);
  padding-bottom: 16px;
}}
.brand-logo-wrap {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  background: #0d2247;
  border: 1.5px solid rgba(8, 185, 202, 0.5);
  border-radius: 12px;
  flex-shrink: 0;
  box-shadow: 0 0 14px rgba(8, 185, 202, 0.25);
}}
.brand-logo-wrap svg {{
  width: 36px;
  height: 36px;
}}
.brand-header h1 {{
  margin: 0 0 2px;
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
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
  background: #fff;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--border-dark);
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
  min-height: 46px;
  padding: 10px 14px;
  font: inherit;
  font-size: 14.5px;
  background: rgba(6, 22, 55, 0.85);
  color: #ffffff;
  border: 1px solid var(--border-dark);
  border-radius: 8px;
}}
.field input:focus {{
  outline: none;
  border-color: var(--dm-cyan);
  box-shadow: 0 0 0 3px rgba(8, 185, 202, 0.25);
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
  background: #040e24;
  color: #7dd3fc;
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  word-break: break-all;
  margin: 4px 0 10px;
}}
.btn-dm {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 12px 20px;
  font-family: var(--font);
  font-weight: 700;
  font-size: 14.5px;
  color: #fff;
  background: var(--dm-cyan);
  border: 1px solid rgba(8, 185, 202, 0.6);
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(8, 185, 202, 0.3);
  width: 100%;
  transition: all 0.15s ease;
  text-decoration: none;
}}
.btn-dm:hover {{
  background: #0aa7b7;
  box-shadow: 0 6px 18px rgba(8, 185, 202, 0.45);
  transform: translateY(-1px);
}}
.btn-dm:active {{ transform: translateY(0); }}
.login-error {{
  display: flex;
  gap: 8px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}}
.err-dot {{
  width: 8px;
  height: 8px;
  background: #ef4444;
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
          <pre class="uri-block">{secret_b32}</pre>
        </div>
      </div>
      <form method="POST" action="/auth/setup-2fa" style="margin-top:14px">
        <label class="field">
          <span>2. Confirme com o c&oacute;digo gerado no app</span>
          <input type="text" name="totp" required autofocus inputmode="numeric"
                 pattern="\\d{{8}}" maxlength="8" placeholder="00000000" class="totp-input">
        </label>
        <button type="submit" class="btn-dm">Ativar 2FA &amp; Continuar &rarr;</button>
      </form>
    </main>
    <footer class="auth-footer">
      <div>&copy; 2026 Dev Maniac's &middot; Game &amp; Systems Development</div>
    </footer>
  </div>
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
        mode = (query.get("mode", ["hybrid"])[0] or "hybrid").strip().casefold()
        if not q:
            return self._error(HTTPStatus.BAD_REQUEST,
                                "Query parameter 'q' is required")
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
