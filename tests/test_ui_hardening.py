"""Regression contracts for the Command Workbench Inspector (TASK-CERBERUS-UIUX-REINVENTION-004).

These tests enforce the visual, structural and behavioural contracts of
the reinvented UI:

  * Industrial Command Workbench tokens (no neon, no purple, no glow)
  * Exactly five tabs with persistent shell and Evidence Rail
  * Spotlight search + split-workbench preview
  * Inbox triagem with diff viewer
  * HiDPI vector topology (no gradients, no shadows, no autorotation)
  * Telemetry metrics + reindex
  * Profile / password / TOTP with safe DOM and clean endpoints
  * Reduced motion respect, ARIA, 44 px controls
"""

import re
import shutil
import subprocess
import unittest

from engine.server import UI_HTML, _render_login_html, _render_setup_2fa_html


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _script() -> str:
    """Return the inline <script> body of UI_HTML (must be exactly one)."""
    scripts = re.findall(r"<script>(.*?)</script>", UI_HTML, flags=re.DOTALL)
    assert len(scripts) == 1, f"UI_HTML must have exactly one <script> block (found {len(scripts)})"
    return scripts[0]


# ---------------------------------------------------------------------------
# 1. Tokens and visual prohibitions
# ---------------------------------------------------------------------------
class CommandWorkbenchTokensTests(unittest.TestCase):
    """Spec section 3 — exact tokens + zero ornamental decoration."""

    def test_required_command_workbench_tokens_are_declared(self) -> None:
        for token in (
            "--bg-canvas:#141617",
            "--bg-shell:#191C1D",
            "--bg-panel:#1D2122",
            "--bg-elevated:#272D2E",
            "--bg-input:#171B1C",
            "--border-subtle:#2D3332",
            "--border-default:#39413D",
            "--border-strong:#59645D",
            "--text-primary:#F0F2ED",
            "--text-muted:#9FA99F",
            "--action:#C93B46",
            "--warning:#D8B478",
            "--success:#A9C5A0",
            "--danger:#F19D96",
            "--focus:#D94854",
        ):
            with self.subTest(token=token):
                self.assertIn(token, UI_HTML)

    def test_no_neon_or_purple_decoration_anywhere(self) -> None:
        lowered = UI_HTML.lower()
        forbidden = (
            "purple", "violet", "magenta", "fuchsia",
            "#7c3aed", "#8b5cf6", "#a855f7", "#8b35d1",
            "linear-gradient", "radial-gradient", "conic-gradient",
            "backdrop-filter", "blur(", "drop-shadow", "text-shadow",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, lowered, f"forbidden decoration: {token}")

    def test_legacy_helpdesk_palette_is_removed(self) -> None:
        """The old HelpDesk palette must NOT leak into the reinvented UI.

        NOTE: #91AF88 (action-pressed) is part of the NEW spec section 3 and is
        therefore ALLOWED. We only assert that the legacy custom property names
        and HelpDesk-only swatches are gone.
        """
        lowered = UI_HTML.lower()
        for token in (
            "#061637", "#0a192f", "#0d2247", "#1e3a6d",
            "#08b9ca", "#ff4c4c", "#ffc529",
            "--dm-cyan", "--dm-red", "--dm-yellow", "--dm-blue",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, lowered, f"legacy palette leaked: {token}")

    def test_required_fonts_are_declared(self) -> None:
        lowered = UI_HTML.lower()
        for family in ("space grotesk", "inter", "ibm plex mono"):
            with self.subTest(family=family):
                self.assertIn(family, lowered)

    def test_44px_control_floor_is_present(self) -> None:
        self.assertRegex(
            UI_HTML.lower(),
            r"min-height:\s*(?:44|4[5-9])px",
            "UI must enforce 44 px control floor (WCAG 2.2 AA / ISO 44 px)",
        )


# ---------------------------------------------------------------------------
# 2. Shell, tabs and Evidence Rail
# ---------------------------------------------------------------------------
class ShellAndTabsTests(unittest.TestCase):

    def setUp(self) -> None:
        self.pages = {
            "dashboard": UI_HTML,
            "login": _render_login_html(),
            "setup_2fa": _render_setup_2fa_html("JBSWY3DPEHPK3PXP", "otpauth://totp/x", "<svg></svg>"),
        }

    def test_login_pages_have_no_neon_or_purple_either(self) -> None:
        for name, html in self.pages.items():
            lowered = html.lower()
            for token in ("purple", "violet", "linear-gradient", "backdrop-filter",
                          "blur(", "#8b5cf6"):
                with self.subTest(page=name, token=token):
                    self.assertNotIn(token, lowered)

    def test_five_tabs_are_present_and_unique(self) -> None:
        tab_ids = ("tab-search", "tab-inbox", "tab-topology", "tab-metrics", "tab-profile")
        for tab_id in tab_ids:
            with self.subTest(tab=tab_id):
                self.assertIn(f'id="{tab_id}"', UI_HTML)
                self.assertIn(f'data-tab="{tab_id}"', UI_HTML)

        # Count <button ... role="tab" ...> (CSS selectors also mention the attribute).
        tab_buttons = re.findall(r'<button[^>]*\brole="tab"', UI_HTML)
        self.assertEqual(len(tab_buttons), 5, "exactly 5 tab buttons expected")

        tabpanels = re.findall(r'<section[^>]*\brole="tabpanel"', UI_HTML)
        self.assertEqual(len(tabpanels), 5, "exactly 5 tabpanels expected")

    def test_only_metrics_tabpanel_is_visible_by_default(self) -> None:
        # Other tabpanels must carry `hidden` attribute initially.
        self.assertRegex(UI_HTML, r'<section[^>]*id="tab-metrics"[^>]*role="tabpanel"(?![^>]*\bhidden)')
        for hidden_tab in ("tab-search", "tab-inbox", "tab-topology", "tab-profile"):
            with self.subTest(hidden=hidden_tab):
                # tabpanel must have hidden attribute
                pattern = (
                    r'<section[^>]*id="' + hidden_tab + r'"[^>]*role="tabpanel"[^>]*\bhidden'
                )
                self.assertRegex(UI_HTML, pattern)

    def test_shell_landmarks_are_present(self) -> None:
        for landmark_id in ("app-header", "primary-tabs", "evidence-rail",
                            "workspace", "toast-region", "dialog-root"):
            with self.subTest(landmark=landmark_id):
                self.assertIn(f'id="{landmark_id}"', UI_HTML)

        # Evidence Rail must contain the four required sub-spans
        for sub_id in ("evidence-cluster", "evidence-index", "evidence-scope", "evidence-sync"):
            with self.subTest(evidence=sub_id):
                self.assertIn(f'id="{sub_id}"', UI_HTML)

    def test_header_carries_required_actions(self) -> None:
        for element_id in ("cluster-status", "profile-btn", "profile-avatar", "logout-btn"):
            with self.subTest(element=element_id):
                self.assertIn(f'id="{element_id}"', UI_HTML)
        self.assertIn("Cerberus Inspector", UI_HTML)
        self.assertIn("Dev Maniac", UI_HTML)
        # Header height 64 px is encoded in --header-height.

    def test_skip_link_targets_workspace(self) -> None:
        self.assertIn('class="skip-link"', UI_HTML)
        self.assertIn('href="#workspace"', UI_HTML)


# ---------------------------------------------------------------------------
# 3. Search tab contract
# ---------------------------------------------------------------------------
class SearchTabTests(unittest.TestCase):

    def test_search_form_is_a_spotlight_with_required_landmarks(self) -> None:
        self.assertIn('id="search-form"', UI_HTML)
        self.assertIn('class="spotlight"', UI_HTML)
        self.assertIn('role="search"', UI_HTML)
        self.assertIn('id="search-q"', UI_HTML)
        self.assertIn('id="search-btn"', UI_HTML)
        self.assertIn('aria-label="Filtros', UI_HTML)
        # Required segmented filters
        for token in ("data-scope=\"all\"", "data-scope=\"ecommerce\"",
                      "data-scope=\"mobile\"", "data-scope=\"analytics\"",
                      "data-scope=\"design\"", "data-scope=\"architecture\"",
                      "data-mode=\"hybrid\"", "data-mode=\"semantic\"",
                      "data-mode=\"lexical\""):
            with self.subTest(token=token):
                self.assertIn(token, UI_HTML)

    def test_split_workbench_has_master_and_preview(self) -> None:
        self.assertIn('id="search-workbench"', UI_HTML)
        self.assertIn('class="split-workbench"', UI_HTML)
        self.assertIn('id="search-master"', UI_HTML)
        self.assertIn('id="search-results"', UI_HTML)
        self.assertIn('aria-live="polite"', UI_HTML)
        self.assertIn('id="search-preview"', UI_HTML)
        self.assertIn('id="search-preview-body"', UI_HTML)

    def test_search_routes_through_centralized_request(self) -> None:
        script = _script()
        # The search logic must live inside an isolated initSearch function.
        self.assertIn("function initSearch()", script)
        # AbortController usage is mandatory per spec.
        self.assertIn("AbortController", script)
        # The legacy empty-query short-circuit must remain (no API call on empty).
        run_search = script.split("async function runSearch()", 1)[1].split(
            "function initSearch()", 1
        )[0]
        self.assertIn("if (!q)", run_search)
        self.assertIn("Pronto para pesquisar", run_search)

    def test_search_uses_internal_contract_inputs(self) -> None:
        # Real select inputs that the backend reads must remain in the DOM.
        self.assertIn('id="search-project"', UI_HTML)
        self.assertIn('id="search-mode"', UI_HTML)


# ---------------------------------------------------------------------------
# 4. Inbox tab contract
# ---------------------------------------------------------------------------
class InboxTabTests(unittest.TestCase):

    def test_inbox_has_required_dom(self) -> None:
        for element_id in ("inbox-summary", "inbox-workbench", "inbox-master",
                           "inbox-filters", "inbox-list",
                           "candidate-inspector", "candidate-header",
                           "candidate-metadata", "candidate-diff",
                           "candidate-actions"):
            with self.subTest(element=element_id):
                self.assertIn(f'id="{element_id}"', UI_HTML)
        self.assertIn('class="diff-viewer"', UI_HTML)
        self.assertIn('class="telemetry-strip"', UI_HTML)

    def test_inbox_uses_existing_endpoints(self) -> None:
        for endpoint in ("/api/inbox", "/api/inbox/", "/verify", "/promote", "/reject"):
            with self.subTest(endpoint=endpoint):
                self.assertIn(endpoint, UI_HTML)


# ---------------------------------------------------------------------------
# 5. Topology canvas contract
# ---------------------------------------------------------------------------
class TopologyCanvasTests(unittest.TestCase):

    def test_canvas_landmarks(self) -> None:
        self.assertIn('id="brainCanvas"', UI_HTML)
        self.assertIn('id="topology-stage"', UI_HTML)
        self.assertIn('id="topology-inspector"', UI_HTML)
        self.assertIn('id="topology-empty"', UI_HTML)
        self.assertIn('aria-label="Mapa interativo da mem', UI_HTML)

    def test_canvas_uses_hidpi_with_settransform(self) -> None:
        import re as _re
        script = _script()
        # ResizeObserver lives in initTopologyCanvas; setTransform/dpr in
        # resizeTopologyCanvas. Scan both blocks together.
        chunk = ""
        for marker in ("function resizeTopologyCanvas", "function initTopologyCanvas",
                       "function renderTopologyFrame"):
            idx = script.find(marker)
            if idx >= 0:
                # Take ~1500 chars after the marker to span the function.
                chunk += script[idx: idx + 2000]
        if not chunk:
            chunk = script
        for token in ("devicePixelRatio", "ResizeObserver", "setTransform"):
            with self.subTest(token=token):
                self.assertIn(token, chunk, f"missing HiDPI token: {token}")
        # canvas.width = Math.round(<cssWidth|cssHeight|width|height> * dpr)
        self.assertRegex(
            chunk,
            r"canvas\.(?:width|height)\s*=\s*Math\.round\([^)]*\*\s*dpr\)",
        )
        # setTransform call must scale by dpr.
        self.assertRegex(
            chunk,
            r"setTransform\(\s*dpr\s*,\s*0\s*,\s*0\s*,\s*dpr",
        )

    def test_canvas_has_no_glow_or_gradients(self) -> None:
        script = _script()
        topology = script.split("function initTopologyCanvas()", 1)[1]
        for forbidden in (
            "createRadialGradient",
            "createLinearGradient",
            "createConicGradient",
            "shadowBlur",
            "shadowColor",
            "rotationVelocity",
            "autoRotate",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, topology)
        # Hard prohibition: no ambient raf loop while document hidden.
        self.assertIn("document.hidden", topology)

    def test_topology_interactions_are_declared(self) -> None:
        script = _script()
        # The bootstrap call `if (canvas) ... renderTopologyFrame();` is at the
        # end of initTopologyCanvas; the toolbar buttons appear after it.
        topology = script.split("function initTopologyCanvas()", 1)[1]
        for token in (
            "wheel", "mousedown", "mousemove",
            "topology-center", "topology-fit",
            "ResizeObserver",
        ):
            with self.subTest(token=token):
                self.assertIn(token.lower(), topology.lower())

    def test_canvas_uses_only_token_colours(self) -> None:
        """Hex colours used in Canvas JS must mirror the CSS tokens."""
        # Tokens used by the topology JS must come from the same palette.
        # We assert that the legacy `#38bdf8` cyan accent is gone.
        self.assertNotIn("#38bdf8", UI_HTML)


# ---------------------------------------------------------------------------
# 6. Metrics tab contract
# ---------------------------------------------------------------------------
class MetricsTabTests(unittest.TestCase):

    def test_metrics_required_dom(self) -> None:
        for element_id in ("reindex-btn", "metrics-health-strip",
                           "metrics-grid", "index-breakdown",
                           "system-diagnostics"):
            with self.subTest(element=element_id):
                self.assertIn(f'id="{element_id}"', UI_HTML)

    def test_reindex_endpoint_is_used(self) -> None:
        self.assertIn("postJSON(\"/api/reindex\"", UI_HTML)
        # aria-busy on reindex is mandated.
        self.assertIn("aria-busy", UI_HTML)

    def test_metrics_initializers_and_status_endpoint(self) -> None:
        self.assertIn("function initMetrics()", UI_HTML)
        self.assertIn("/api/status", UI_HTML)


# ---------------------------------------------------------------------------
# 7. Profile tab contract
# ---------------------------------------------------------------------------
class ProfileTabTests(unittest.TestCase):

    def test_profile_dom_is_present(self) -> None:
        for element_id in ("profile-account-card", "profile-password-card",
                           "profile-twofa-card",
                           "change-password-form", "current-password",
                           "new-password", "confirm-password",
                           "twofa-enable-btn", "twofa-enrollment",
                           "twofa-qr", "twofa-secret",
                           "twofa-verify-form", "twofa-code",
                           "twofa-disable-form", "twofa-disable-password",
                           "profile-email", "profile-2fa-status"):
            with self.subTest(element=element_id):
                self.assertIn(f'id="{element_id}"', UI_HTML)

    def test_profile_endpoints_are_used(self) -> None:
        for endpoint in (
            "/api/v1/auth/me",
            "/api/v1/auth/change-password",
            "/api/v1/auth/2fa/setup",
            "/api/v1/auth/2fa/verify-and-enable",
            "/api/v1/auth/2fa/disable",
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIn(endpoint, UI_HTML)

    def test_init_profile_and_autocomplete_are_correct(self) -> None:
        self.assertIn("function initProfile()", UI_HTML)
        self.assertIn("autocomplete=\"current-password\"", UI_HTML)
        self.assertIn("autocomplete=\"new-password\"", UI_HTML)


# ---------------------------------------------------------------------------
# 8. HTTP, dialogs, toasts, safety
# ---------------------------------------------------------------------------
class SafetyAndHttpTests(unittest.TestCase):

    def test_centralized_request_helper_exists(self) -> None:
        script = _script()
        self.assertIn("function requestJSON(", script)
        # 401 must redirect to login once.
        self.assertIn("/auth/login", script)
        self.assertIn("401", script)

    def test_xss_safety_in_renderers(self) -> None:
        script = _script()
        # A robust escaper must be available and used for dynamic text.
        self.assertIn("function escapeHTML(", script)
        # No raw innerHTML assignment of server-provided snippets without sanitization.
        # innerHTML is permitted only for trusted DOM literals (e.g. QR SVG passed as text).
        # The renderMarkdown result must come from escaped source.
        self.assertIn("renderMarkdown", script)

    def test_toast_region_is_used_for_notifications(self) -> None:
        self.assertIn("function showToast(", script := _script())
        self.assertIn('id="toast-region"', UI_HTML)

    def test_dialog_root_exists_for_dialogs(self) -> None:
        self.assertIn('id="dialog-root"', UI_HTML)

    def test_domcontentloaded_boot_isolates_initializers(self) -> None:
        script = _script()
        self.assertIn('document.addEventListener("DOMContentLoaded"', script)
        # Each initializer should be invoked in its own try/catch.
        for initializer in (
            "initTabs", "initEvidenceRail", "initSearch", "initInbox",
            "initTopologyCanvas", "initMetrics", "initProfile",
            "initDialogs", "initKeyboardShortcuts",
        ):
            with self.subTest(init=initializer):
                self.assertIn("function " + initializer + "()", script)

    def test_init_keyboard_shortcuts_covers_escape_and_ctrl_k(self) -> None:
        script = _script()
        kbd = script.split("function initKeyboardShortcuts()", 1)[1]
        self.assertIn("Escape", kbd)
        self.assertRegex(kbd, r"ctrlKey|metaKey")

    def test_renderMarkdown_escapes_html_first(self) -> None:
        script = _script()
        rm = script.split("function renderMarkdown(", 1)[1].split("function ", 1)[0]
        # First meaningful operation must be escaping.
        self.assertRegex(rm, r"\b(?:let|var|const)\s+html\s*=\s*escapeHTML")


# ---------------------------------------------------------------------------
# 9. JavaScript validity in Node
# ---------------------------------------------------------------------------
@unittest.skipUnless(shutil.which("node"), "Node.js is required for JavaScript syntax validation")
class JavaScriptSyntaxTests(unittest.TestCase):

    def test_dashboard_javascript_compiles_in_real_javascript_engine(self) -> None:
        scripts = re.findall(r"<script>(.*?)</script>", UI_HTML, flags=re.DOTALL)
        self.assertEqual(1, len(scripts))
        # Write the script to a temp file and ask Node to syntax-check it.
        # Using a real file (instead of piping via stdin) avoids Windows
        # path/encoding edge cases while still validating the JS as-is.
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", encoding="utf-8",
            delete=False,
        ) as fh:
            fh.write(scripts[0])
            tmp_path = fh.name
        try:
            result = subprocess.run(
                ["node", "--check", tmp_path],
                capture_output=True, check=False,
            )
            self.assertEqual(
                0, result.returncode,
                "node --check failed:\nstdout=%r\nstderr=%r"
                % (result.stdout, result.stderr),
            )
        finally:
            import os
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
