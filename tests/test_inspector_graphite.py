"""Focused contracts for the graphite Inspector and local access setup."""
import json
import tempfile
import unittest
from pathlib import Path

from engine.admin_access import configure_access
from engine.auth import UserStore, verify_password
from engine.server import UI_HTML, _render_login_html


class GraphiteInspectorTests(unittest.TestCase):
    def test_navigation_and_metrics_have_real_controls(self):
        for marker in ('aria-orientation="vertical"', 'id="ledger-period"',
                       'id="export-ledger-btn"', 'id="cockpit-sessions-tbody"',
                       'Não conectado', 'não a cota oficial do Codex'):
            self.assertIn(marker, UI_HTML)
        from html.parser import HTMLParser
        ids = []
        class IDs(HTMLParser):
            def handle_starttag(self, tag, attrs):
                ids.extend(value for key, value in attrs if key == 'id')
        IDs().feed(UI_HTML)
        self.assertEqual(len(ids), len(set(ids)), 'DOM IDs must be unique')

    def test_login_has_credentials_help_and_no_false_infrastructure_claim(self):
        page = _render_login_html()
        for marker in ('type="email"', 'autocomplete="current-password"',
                       'Configurar acesso', 'aria-controls="login-password"'):
            self.assertIn(marker, page)
        self.assertNotIn('Cloudflare Argo Tunnel Blindado', page)

    def test_setup_uses_hash_and_reset_preserves_2fa_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            configure_access(root, 'test@example.com', 'test-only-secret-2026')
            path = root / '.cerberus/users.json'
            self.assertNotIn('test-only-secret-2026', path.read_text())
            store = UserStore(path)
            store.set_totp_secret('test@example.com', 'JBSWY3DPEHPK3PXP')
            configure_access(root, 'test@example.com', 'test-only-replacement-2026')
            store = UserStore(path)
            user = store.get('test@example.com')
            self.assertTrue(verify_password('test-only-replacement-2026', user.password_hash))
            self.assertEqual('JBSWY3DPEHPK3PXP', user.totp_secret)
            self.assertEqual(1, len(list((path.parent / 'backups').glob('*.json'))))

    def test_corrupt_or_unknown_user_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / '.cerberus/users.json'
            path.parent.mkdir()
            for raw in ('{broken', json.dumps({'users': []}), json.dumps({'users': [{}]})):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    configure_access(root, 'test@example.com', 'test-only-secret-2026')
                self.assertEqual(raw, path.read_text())


class LedgerHTTPTests(unittest.TestCase):
    def test_invalid_values_and_dedup_reach_http_contract(self):
        from tests.test_server_api import _ServerHandle, _build_state
        with tempfile.TemporaryDirectory() as temp:
            root, service, capture = _build_state(Path(temp))
            with _ServerHandle(application_root=root, service=service, capture_engine=capture) as server:
                for value in (-1, True, '3', 1.5):
                    status, _, _ = server.request('POST', '/api/v1/ledger/record', {'prompt_tokens': value})
                    self.assertEqual(400, status)
                status, _, _ = server.request('POST', '/api/v1/ledger/record', {'loops_prevented': 2, 'total_tokens': 10})
                self.assertEqual(400, status)
                payload = {'session_id':'test', 'event_id':'event-1', 'total_tokens':120}
                for _ in range(2):
                    status, _, _ = server.request('POST', '/api/v1/ledger/record', payload)
                    self.assertEqual(201, status)
                status, raw, _ = server.request('GET', '/api/v1/ledger/stats?days=7')
                stats = json.loads(raw)
                self.assertEqual(200, status)
                self.assertEqual(120, stats['today']['total'])
                self.assertIsNone(stats['today']['prompt'])
