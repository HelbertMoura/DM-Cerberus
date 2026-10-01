"""Regression tests for XSS sinks found in QA audit (items 1-3).

These tests enforce HTML-escaping on three attacker-controllable
interpolation points discovered during the security review of
TASK-CERBERUS-BACKEND-AUTH-PROFILE-001 and
TASK-CERBERUS-FRONTEND-HELPDESK-OVERHAUL-002:

  1. CRIT — search snippet interpolation in UI_HTML (server.py)
  2. HIGH — target_email / pending_token in login HTML f-string
  3. MED  — secret_b32 in setup-2fa HTML f-string (defense-in-depth)
"""

import unittest

from engine.server import UI_HTML, _render_login_html, _render_setup_2fa_html


PAYLOAD = '"><img src=x onerror=alert(1)>'
ESCAPED_FRAGMENT = "&quot;&gt;&lt;img"


class TestSearchSnippetEscaping(unittest.TestCase):
    """QA Item 1 — search results snippet must be esc()'d before innerHTML.

    The Command Workbench UI renders results as <button class='search-result-row'>
    with the snippet inside <div class='snippet'>. We assert that the snippet
    value passes through escapeHTML().
    """

    def test_search_snippet_interpolation_is_escaped(self) -> None:
        # Find the snippet row template and ensure snippet is escaped.
        import re as _re
        m = _re.search(r'<div class="snippet">([^<]+)</div>', UI_HTML)
        self.assertIsNotNone(m, "search-result-row snippet <div> not found")
        self.assertIn("escapeHTML(item.snippet", m.group(1))

    def test_unprotected_interpolation_is_gone(self) -> None:
        # No raw `${item.snippet` interpolation may survive in the dashboard.
        self.assertNotIn("${item.snippet", UI_HTML)


class TestLoginHtmlEscaping(unittest.TestCase):
    """QA Item 2 — login HTML f-string must escape attacker-controlled inputs."""

    def test_target_email_is_escaped_in_value_attr(self) -> None:
        html = _render_login_html(
            error_message="ok",
            pending_token="abc",
            target_email=PAYLOAD,
        )
        self.assertNotIn(PAYLOAD, html)
        self.assertIn(ESCAPED_FRAGMENT, html)

    def test_pending_token_is_escaped_in_hidden_value_attr(self) -> None:
        html = _render_login_html(
            step="totp",
            error_message="ok",
            pending_token=PAYLOAD,
            target_email="user@example.com",
        )
        self.assertNotIn(PAYLOAD, html)
        self.assertIn(ESCAPED_FRAGMENT, html)

    def test_error_message_is_escaped_too(self) -> None:
        html = _render_login_html(
            error_message=PAYLOAD,
            pending_token="",
            target_email="",
        )
        self.assertNotIn(PAYLOAD, html)
        self.assertIn(ESCAPED_FRAGMENT, html)


class TestSetup2faHtmlEscaping(unittest.TestCase):
    """QA Item 3 — setup-2fa HTML f-string must escape secret_b32."""

    def test_secret_b32_is_escaped_in_uri_block(self) -> None:
        html = _render_setup_2fa_html(
            secret_b32=PAYLOAD,
            otp_uri="otpauth://totp/x",
            svg="<svg></svg>",
        )
        self.assertNotIn(PAYLOAD, html)
        self.assertIn(ESCAPED_FRAGMENT, html)


if __name__ == "__main__":
    unittest.main()
