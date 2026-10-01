"""Integration tests for public health and authenticated profile APIs."""

import json
import socket
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from engine.auth import (
    DEFAULT_DEV_ADMIN_EMAIL,
    DEFAULT_DEV_ADMIN_PASSWORD,
    SESSION_COOKIE_NAME,
    TOTP,
    verify_password,
)
from engine.server import DEFAULT_HOST, make_server


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):  # noqa: ARG002
        return fp

    http_error_302 = http_error_303 = http_error_307 = http_error_308 = http_error_301


def _free_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((DEFAULT_HOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class TestAuthProfileAPI(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
        (self.root / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
        self.port = _free_port()
        self.server = make_server(
            DEFAULT_HOST, self.port, self.root, auth_disabled=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        for _ in range(50):
            try:
                with socket.create_connection((DEFAULT_HOST, self.port), timeout=0.5):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            self.fail("server did not become ready")

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self._tmp.cleanup()

    def request(self, method: str, path: str, *, body=None, cookie=None, accept="application/json"):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Accept": accept}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if cookie:
            headers["Cookie"] = cookie
        req = urllib.request.Request(
            f"http://{DEFAULT_HOST}:{self.port}{path}", data=data,
            method=method, headers=headers,
        )
        try:
            response = urllib.request.build_opener(_NoRedirect).open(req, timeout=10)
            return response.status, response.read().decode(), dict(response.headers)
        except urllib.error.HTTPError as exc:
            try:
                return exc.code, exc.read().decode(), dict(exc.headers or {})
            finally:
                exc.close()

    def form_request(self, path: str, form: dict):
        req = urllib.request.Request(
            f"http://{DEFAULT_HOST}:{self.port}{path}",
            data=urllib.parse.urlencode(form).encode(),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response = urllib.request.build_opener(_NoRedirect).open(req, timeout=10)
        try:
            return response.status, response.read().decode(), dict(response.headers)
        finally:
            response.close()

    def login_cookie(self) -> str:
        form = urllib.parse.urlencode({
            "email": DEFAULT_DEV_ADMIN_EMAIL,
            "password": DEFAULT_DEV_ADMIN_PASSWORD,
        }).encode()
        req = urllib.request.Request(
            f"http://{DEFAULT_HOST}:{self.port}/auth/login", data=form,
            method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response = urllib.request.build_opener(_NoRedirect).open(req, timeout=10)
        value = response.headers["Set-Cookie"].split(";", 1)[0]
        self.assertTrue(value.startswith(SESSION_COOKIE_NAME + "="))
        return value

    def test_health_routes_are_public_and_identical(self) -> None:
        expected = {
            "status": "ok", "service": "cerberus-inspector", "version": "1.0.0"
        }
        for path in ("/api/health", "/healthz"):
            status, body, headers = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body), expected)
            self.assertIn("application/json; charset=utf-8", headers["Content-Type"])

    def test_profile_requires_auth_and_returns_current_user(self) -> None:
        status, _, _ = self.request("GET", "/api/v1/auth/me")
        self.assertEqual(status, 401)
        status, body, _ = self.request(
            "GET", "/api/v1/auth/me", cookie=self.login_cookie()
        )
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertEqual(payload["email"], DEFAULT_DEV_ADMIN_EMAIL)
        self.assertTrue(payload["is_active"])
        self.assertFalse(payload["has_2fa"])
        self.assertIsInstance(payload["created_at"], float)

    def test_change_password_validates_and_persists_hash(self) -> None:
        cookie = self.login_cookie()
        status, body, _ = self.request(
            "POST", "/api/v1/auth/change-password", cookie=cookie,
            body={"current_password": "wrong", "new_password": "new-secret"},
        )
        self.assertEqual((status, json.loads(body)), (400, {"error": "Senha atual incorreta."}))
        status, body, _ = self.request(
            "POST", "/api/v1/auth/change-password", cookie=cookie,
            body={"current_password": DEFAULT_DEV_ADMIN_PASSWORD, "new_password": "short"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(json.loads(body)["error"], "Nova senha deve ter pelo menos 6 caracteres.")
        status, body, _ = self.request(
            "POST", "/api/v1/auth/change-password", cookie=cookie,
            body={"current_password": DEFAULT_DEV_ADMIN_PASSWORD, "new_password": "new-secret"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])
        user = self.server.RequestHandlerClass.auth.user_store.get(DEFAULT_DEV_ADMIN_EMAIL)
        self.assertTrue(verify_password("new-secret", user.password_hash))

    def test_setup_verify_and_disable_six_digit_totp(self) -> None:
        cookie = self.login_cookie()
        status, body, _ = self.request(
            "POST", "/api/v1/auth/2fa/setup", cookie=cookie, body={}
        )
        self.assertEqual(status, 200)
        setup = json.loads(body)
        self.assertIn("DevManiacs-Cerberus", setup["uri"])
        self.assertIn("digits=6", setup["uri"])
        self.assertIn("<svg", setup["qr_svg"])
        totp = TOTP.from_base32(setup["secret"], digits=6)
        status, body, _ = self.request(
            "POST", "/api/v1/auth/2fa/verify-and-enable", cookie=cookie,
            body={"secret": setup["secret"], "code": "000000"},
        )
        self.assertEqual((status, json.loads(body)), (400, {"error": "Codigo TOTP invalido ou expirado."}))
        status, body, _ = self.request(
            "POST", "/api/v1/auth/2fa/verify-and-enable", cookie=cookie,
            body={"secret": setup["secret"], "code": totp.now()},
        )
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])
        self.assertEqual(
            self.server.RequestHandlerClass.auth.user_store.get(DEFAULT_DEV_ADMIN_EMAIL).totp_secret,
            setup["secret"],
        )
        status, _, headers = self.form_request("/auth/login", {
            "email": DEFAULT_DEV_ADMIN_EMAIL,
            "password": DEFAULT_DEV_ADMIN_PASSWORD,
        })
        self.assertEqual(status, 303)
        pending = urllib.parse.parse_qs(
            urllib.parse.urlparse(headers["Location"]).query
        )["pending"][0]
        status, _, headers = self.form_request("/auth/login", {
            "email": DEFAULT_DEV_ADMIN_EMAIL,
            "pending_token": pending,
            "totp": totp.now(),
        })
        self.assertEqual(status, 303)
        self.assertEqual(headers["Location"], "/")
        status, body, _ = self.request(
            "POST", "/api/v1/auth/2fa/disable", cookie=cookie, body={"password": "wrong"}
        )
        self.assertEqual((status, json.loads(body)), (400, {"error": "Senha incorreta."}))
        status, body, _ = self.request(
            "POST", "/api/v1/auth/2fa/disable", cookie=cookie,
            body={"password": DEFAULT_DEV_ADMIN_PASSWORD},
        )
        self.assertEqual(status, 200)
        self.assertFalse(self.server.RequestHandlerClass.auth.user_store.get(DEFAULT_DEV_ADMIN_EMAIL).totp_secret)

    def test_login_alias_and_html_fallback_redirect(self) -> None:
        status, _, headers = self.request("GET", "/login", accept="text/html")
        self.assertEqual(status, 303)
        self.assertEqual(headers["Location"], "/auth/login")
        status, _, headers = self.request("GET", "/unknown", accept="text/html")
        self.assertEqual(status, 303)
        self.assertEqual(headers["Location"], "/auth/login")


if __name__ == "__main__":
    unittest.main()
