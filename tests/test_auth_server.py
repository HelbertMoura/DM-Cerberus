"""
Cerberus Memory Intelligence - Authentication & Server Protection Tests
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P3.5: PBKDF2 hashing, TOTP verification, signed session cookies,
rate limiting, and protected REST API endpoints.
"""

import json
import contextlib
import io
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

from engine.auth import (
    DEFAULT_DEV_ADMIN_EMAIL,
    DEFAULT_DEV_ADMIN_PASSWORD,
    PBKDF2_ITERATIONS,
    SESSION_COOKIE_NAME,
    SESSION_TTL_SECONDS,
    RateLimiter,
    SessionStore,
    TOTP,
    UserStore,
    build_set_cookie_header,
    get_secret_key,
    hash_password,
    parse_cookie_header,
    resolve_client_ip,
    should_use_secure_cookie,
    sign_cookie,
    totp_qr_svg,
    verify_cookie,
    verify_password,
)
# Backward-compat aliases (re-export the new dev-fallback names under the
# historic names that the rest of the file references).
DEFAULT_ADMIN_EMAIL = DEFAULT_DEV_ADMIN_EMAIL
DEFAULT_ADMIN_PASSWORD = DEFAULT_DEV_ADMIN_PASSWORD
from engine.capture import AutoCaptureEngine
from engine.index import SQLiteMemoryIndex
from engine.retrieval import CerberusMemoryService
from engine.server import DEFAULT_HOST, AuthState, make_server


# ============================================================================
# TestPBKDF2PasswordHashing
# ============================================================================
class TestPBKDF2PasswordHashing(unittest.TestCase):
    def test_hash_format_uses_pbkdf2_sha256_with_high_iterations(self) -> None:
        h = hash_password("super-secret")
        # Format: pbkdf2_sha256_<iter>$<salt_b64>$<hash_b64>
        parts = h.split("$")
        self.assertEqual(len(parts), 3, f"unexpected hash shape: {h!r}")
        head, salt_b64, hash_b64 = parts
        algo, iter_str = head.rsplit("_", 1)
        self.assertEqual(algo, "pbkdf2_sha256")
        self.assertEqual(int(iter_str), PBKDF2_ITERATIONS)
        self.assertGreaterEqual(int(iter_str), 100_000)
        self.assertTrue(len(salt_b64) > 0)
        self.assertTrue(len(hash_b64) > 0)

    def test_verify_password_accepts_correct_password(self) -> None:
        h = hash_password("hunter2")
        self.assertTrue(verify_password("hunter2", h))

    def test_verify_password_rejects_wrong_password(self) -> None:
        h = hash_password("hunter2")
        self.assertFalse(verify_password("hunter3", h))

    def test_hash_uses_random_salt_per_password(self) -> None:
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        # Same password + different salts => different hashes
        self.assertNotEqual(h1, h2)

    def test_verify_rejects_malformed_hash(self) -> None:
        self.assertFalse(verify_password("anything", "not-a-hash"))
        self.assertFalse(verify_password("anything", ""))
        self.assertFalse(verify_password("", "any-hash"))

    def test_verify_rejects_empty_password(self) -> None:
        h = hash_password("anything")
        self.assertFalse(verify_password("", h))


# ============================================================================
# TestTOTP
# ============================================================================
class TestTOTP(unittest.TestCase):
    def test_generate_produces_8_digit_code(self) -> None:
        t = TOTP.generate()
        code = t.now()
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isdigit())

    def test_verify_accepts_current_code(self) -> None:
        t = TOTP.generate()
        self.assertTrue(t.verify(t.now()))

    def test_verify_rejects_wrong_code(self) -> None:
        t = TOTP.generate()
        self.assertFalse(t.verify("00000000"))

    def test_verify_rejects_short_code(self) -> None:
        t = TOTP.generate()
        self.assertFalse(t.verify("123"))
        self.assertFalse(t.verify(""))

    def test_verify_rejects_non_digit_code(self) -> None:
        t = TOTP.generate()
        self.assertFalse(t.verify("abcdefgh"))

    def test_verify_handles_clock_skew_within_window(self) -> None:
        t = TOTP.generate()
        # Verify with a timestamp from the future
        future_code = t.now()
        # Subtract 30 seconds (one step)
        self.assertTrue(t.verify(future_code, at=time.time() - 30))

    def test_base32_roundtrip(self) -> None:
        t = TOTP.generate()
        b = t.to_base32()
        t2 = TOTP.from_base32(b)
        self.assertEqual(t.secret, t2.secret)
        self.assertTrue(t2.verify(t.now()))

    def test_provisioning_uri_format(self) -> None:
        t = TOTP.generate()
        uri = t.provisioning_uri("user@example.com", issuer="Cerberus")
        self.assertTrue(uri.startswith("otpauth://totp/"))
        self.assertIn("secret=", uri)
        self.assertIn("issuer=Cerberus", uri)
        self.assertIn("digits=8", uri)
        self.assertIn("period=30", uri)

    def test_secret_must_be_at_least_10_bytes(self) -> None:
        with self.assertRaises(ValueError):
            TOTP(secret=b"short")


# ============================================================================
# TestSessionCookies
# ============================================================================
class TestSessionCookies(unittest.TestCase):
    def test_sign_and_verify_roundtrip(self) -> None:
        key = "test-secret-key-for-cookie-signing"
        cookie_value = sign_cookie("session-id-12345", key)
        self.assertEqual(verify_cookie(cookie_value, key), "session-id-12345")

    def test_verify_rejects_tampered_signature(self) -> None:
        key = "test-secret"
        cookie_value = sign_cookie("abc", key)
        tampered = cookie_value[:-4] + "XXXX"
        self.assertIsNone(verify_cookie(tampered, key))

    def test_verify_rejects_wrong_key(self) -> None:
        cookie_value = sign_cookie("abc", "key-one")
        self.assertIsNone(verify_cookie(cookie_value, "key-two"))

    def test_verify_rejects_malformed_value(self) -> None:
        self.assertIsNone(verify_cookie("", "any"))
        self.assertIsNone(verify_cookie("no-dot-here", "any"))
        self.assertIsNone(verify_cookie(".just-dot", "any"))


# ============================================================================
# TestRateLimiter
# ============================================================================
class TestRateLimiter(unittest.TestCase):
    def test_allows_under_burst(self) -> None:
        rl = RateLimiter(rate_per_minute=60, burst=5)
        for _ in range(5):
            self.assertTrue(rl.allow("test"))

    def test_blocks_after_burst(self) -> None:
        rl = RateLimiter(rate_per_minute=1, burst=3)
        self.assertTrue(rl.allow("test"))
        self.assertTrue(rl.allow("test"))
        self.assertTrue(rl.allow("test"))
        self.assertFalse(rl.allow("test"))

    def test_separate_keys_have_separate_buckets(self) -> None:
        rl = RateLimiter(rate_per_minute=1, burst=1)
        self.assertTrue(rl.allow("ip-1"))
        self.assertFalse(rl.allow("ip-1"))
        self.assertTrue(rl.allow("ip-2"))

    def test_refills_over_time(self) -> None:
        rl = RateLimiter(rate_per_minute=600, burst=1)  # 10/sec
        self.assertTrue(rl.allow("test"))
        self.assertFalse(rl.allow("test"))
        time.sleep(0.15)
        # ~1.5 tokens added in 150ms at 10/sec
        self.assertTrue(rl.allow("test"))

    def test_reset_clears_buckets(self) -> None:
        rl = RateLimiter(rate_per_minute=1, burst=1)
        rl.allow("test")
        self.assertFalse(rl.allow("test"))
        rl.reset("test")
        self.assertTrue(rl.allow("test"))


# ============================================================================
# TestUserStore
# ============================================================================
class TestUserStore(unittest.TestCase):
    def test_seeds_default_admin_on_first_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = UserStore(Path(tmp) / "users.json")
            admin = store.get(DEFAULT_ADMIN_EMAIL)
            self.assertIsNotNone(admin)
            self.assertTrue(admin.is_admin)
            self.assertTrue(admin.is_active)
            self.assertTrue(verify_password(DEFAULT_ADMIN_PASSWORD,
                                            admin.password_hash))

    def test_persistence_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "users.json"
            store1 = UserStore(path)
            admin = store1.get(DEFAULT_ADMIN_EMAIL)
            admin.totp_secret = TOTP.generate().to_base32()
            store1.upsert(admin)
            store2 = UserStore(path)
            admin2 = store2.get(DEFAULT_ADMIN_EMAIL)
            self.assertEqual(admin2.totp_secret, admin.totp_secret)

    def test_set_totp_secret_updates_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = UserStore(Path(tmp) / "users.json")
            secret = TOTP.generate().to_base32()
            store.set_totp_secret(DEFAULT_ADMIN_EMAIL, secret)
            self.assertEqual(store.get(DEFAULT_ADMIN_EMAIL).totp_secret, secret)


# ============================================================================
# TestAuthStatePendingTokens
# ============================================================================
class TestAuthStatePendingTokens(unittest.TestCase):
    def setUp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.tmp = Path(tmp)
        self.auth = AuthState(self.tmp, auth_disabled=True)

    def test_create_and_consume_pending_token(self) -> None:
        token = self.auth.create_pending("user@example.com")
        self.assertEqual(self.auth.consume_pending(token), "user@example.com")

    def test_consume_returns_none_for_unknown_token(self) -> None:
        self.assertIsNone(self.auth.consume_pending("unknown-token"))

    def test_consume_is_one_time_use(self) -> None:
        token = self.auth.create_pending("user@example.com")
        self.auth.consume_pending(token)
        self.assertIsNone(self.auth.consume_pending(token))

    def test_expired_pending_token_is_removed_by_check_and_consume(self) -> None:
        token = self.auth.create_pending("user@example.com")
        self.auth._pending[token]["created_at"] = time.time() - 301
        self.assertIsNone(self.auth.check_pending(token))
        self.assertIsNone(self.auth.consume_pending(token))


# ============================================================================
# TestProtectedEndpointsIntegration
# ============================================================================
def _pick_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((DEFAULT_HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


class _AuthServerHandle:
    """Server with auth ENABLED for tests."""

    def __init__(self, application_root: Path,
                 secret_key: str = "test-secret-32-bytes-or-more!!") -> None:
        self.port = _pick_free_port()
        self.host = DEFAULT_HOST
        self.application_root = application_root
        self.secret_key = secret_key
        self.server = make_server(
            host=self.host, port=self.port,
            application_root=application_root,
            auth_disabled=False,
        )
        # Override the default insecure key with our explicit one
        self.server.RequestHandlerClass.auth.secret_key = secret_key
        self.server.RequestHandlerClass.auth.is_secure = True
        # Reset user_store so each test gets a fresh default admin
        self.server.RequestHandlerClass.auth.user_store = UserStore(
            application_root / ".cerberus" / "users.json"
        )
        self.server.RequestHandlerClass.auth.session_store = SessionStore()
        self.server.RequestHandlerClass.auth.rate_limiter = RateLimiter(
            rate_per_minute=1000, burst=100
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            name=f"cerberus-auth-{self.port}", daemon=True,
        )

    def __enter__(self):
        self.thread.start()
        for _ in range(50):
            try:
                with socket.create_connection((self.host, self.port), timeout=0.5):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            raise RuntimeError("Server did not become ready")
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.server.shutdown()
            self.server.server_close()
        finally:
            self.thread.join(timeout=2.0)

    def url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"

    def request(self, method: str, path: str, *,
                form: dict = None, json_body: dict = None,
                cookies: dict = None, headers: dict = None,
                follow_redirects: bool = False):
        """Build a urllib Request, send it, return (status, body, headers)."""
        url = self.url(path)
        data = None
        req_headers = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)
        if cookies:
            cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
            req_headers["Cookie"] = cookie_str
        if form is not None:
            data = urllib.parse.urlencode(form).encode("utf-8")
            req_headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method,
                                     headers=req_headers)
        # Use a custom opener that does NOT follow 3xx redirects so we
        # can observe the redirect status directly.
        if not follow_redirects:
            opener = urllib.request.build_opener(NoRedirectHandler)
        else:
            opener = urllib.request.build_opener()
        try:
            resp = opener.open(req, timeout=10)
            return resp.status, resp.read().decode("utf-8"), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8"), dict(e.headers or {})


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Disable automatic redirect following so tests see 30x directly."""

    def http_error_301(self, req, fp, code, msg, headers):  # noqa: ARG002
        return fp
    http_error_302 = http_error_303 = http_error_307 = http_error_308 = http_error_301


class TestProtectedEndpointsIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.tmp.mkdir(parents=True, exist_ok=True)
        (self.tmp / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
        (self.tmp / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
        self.srv = _AuthServerHandle(self.tmp)

    def tearDown(self) -> None:
        self.srv.__exit__(None, None, None)
        self._tmp.cleanup()

    def test_root_redirects_to_login_when_unauthenticated(self) -> None:
        with self.srv as s:
            status, body, headers = s.request(
                "GET", "/", headers={"Accept": "text/html"}
            )
        self.assertEqual(status, 303)
        self.assertEqual(headers.get("Location"), "/auth/login")

    def test_api_endpoints_return_401_when_unauthenticated(self) -> None:
        with self.srv as s:
            for path in ("/api/status", "/api/inbox", "/api/inbox/abc"):
                status, _, _ = s.request("GET", path)
                self.assertEqual(status, 401, f"{path} should be 401")

    def test_login_get_returns_login_page(self) -> None:
        with self.srv as s:
            status, body, _ = s.request(
                "GET", "/auth/login", headers={"Accept": "text/html"}
            )
        self.assertEqual(status, 200)
        self.assertIn("Cerberus Inspector", body)
        self.assertIn("E-mail", body)
        self.assertIn("Senha", body)

    def test_login_with_valid_credentials_no_totp_sets_session(self) -> None:
        """First-run admin (no TOTP yet) gets a session immediately."""
        with self.srv as s:
            status, body, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
        self.assertEqual(status, 303)
        self.assertEqual(headers.get("Location"), "/")
        set_cookie = headers.get("Set-Cookie", "")
        self.assertIn(SESSION_COOKIE_NAME + "=", set_cookie)
        # Cookie should be a signed value
        cookie_value = set_cookie.split(";", 1)[0].split("=", 1)[1]
        self.assertIn(".", cookie_value)

    def test_session_cookie_grants_dashboard_access(self) -> None:
        with self.srv as s:
            # First login (no TOTP enrolled yet)
            status, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            self.assertEqual(status, 303)
            cookie = headers.get("Set-Cookie", "")
            # Extract cookie value
            sid_cookie = cookie.split(";", 1)[0]
            # Use the cookie for subsequent requests
            cookies = {SESSION_COOKIE_NAME: sid_cookie.split("=", 1)[1]}
            status, body, _ = s.request(
                "GET", "/api/status", cookies=cookies,
                headers={"Accept": "application/json"},
            )
        self.assertEqual(status, 200)

    def test_login_with_wrong_password_returns_error(self) -> None:
        with self.srv as s:
            status, body, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": "wrong-password"},
            )
        self.assertEqual(status, 303)
        self.assertIn("err=", headers.get("Location", ""))
        self.assertIn("/auth/login", headers.get("Location", ""))

    def test_logout_clears_session_cookie(self) -> None:
        with self.srv as s:
            status, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            sid_cookie = headers.get("Set-Cookie", "").split(";", 1)[0]
            cookies = {SESSION_COOKIE_NAME: sid_cookie.split("=", 1)[1]}
            # Logout
            status, _, headers = s.request(
                "POST", "/auth/logout", cookies=cookies
            )
            self.assertEqual(status, 303)
            self.assertIn("Max-Age=0", headers.get("Set-Cookie", ""))

    def test_logged_out_session_cannot_access_api(self) -> None:
        with self.srv as s:
            # Login
            _, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            sid_cookie = headers.get("Set-Cookie", "").split(";", 1)[0]
            cookies = {SESSION_COOKIE_NAME: sid_cookie.split("=", 1)[1]}
            # Logout
            s.request("POST", "/auth/logout", cookies=cookies)
            # Now try to access API
            status, _, _ = s.request(
                "GET", "/api/status", cookies=cookies
            )
        self.assertEqual(status, 401)

    def test_two_step_login_with_totp_required(self) -> None:
        """Admin with TOTP enrolled -> step 1 returns pending token,
        step 2 with valid code issues session."""
        with self.srv as s:
            auth = s.server.RequestHandlerClass.auth
            # Enroll TOTP for the admin
            secret_b32 = TOTP.generate().to_base32()
            auth.user_store.set_totp_secret(DEFAULT_ADMIN_EMAIL, secret_b32)
            totp_obj = TOTP.from_base32(secret_b32)
            valid_code = totp_obj.now()

            # Step 1: email + password -> 303 to login?step=totp
            status, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            self.assertEqual(status, 303)
            location = headers.get("Location", "")
            self.assertIn("step=totp", location)

            # Extract pending token from Location
            from urllib.parse import parse_qs, urlparse
            qs = parse_qs(urlparse(location).query)
            pending_token = qs.get("pending", [""])[0]
            self.assertTrue(pending_token)

            # Step 2: pending + totp code -> session
            status, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "pending_token": pending_token,
                      "totp": valid_code},
            )
            self.assertEqual(status, 303)
            self.assertIn(SESSION_COOKIE_NAME + "=",
                          headers.get("Set-Cookie", ""))

    def test_two_step_login_with_wrong_totp_redirects_back(self) -> None:
        with self.srv as s:
            auth = s.server.RequestHandlerClass.auth
            secret_b32 = TOTP.generate().to_base32()
            auth.user_store.set_totp_secret(DEFAULT_ADMIN_EMAIL, secret_b32)

            # Step 1
            status, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            from urllib.parse import parse_qs, urlparse
            location = headers.get("Location", "")
            qs = parse_qs(urlparse(location).query)
            pending_token = qs.get("pending", [""])[0]

            # Step 2 with wrong TOTP
            status, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "pending_token": pending_token,
                      "totp": "00000000"},
            )
            self.assertEqual(status, 303)
            self.assertIn("err=", headers.get("Location", ""))

    def test_rate_limiting_blocks_after_burst(self) -> None:
        with self.srv as s:
            # Override rate limiter to tiny burst for the test
            auth = s.server.RequestHandlerClass.auth
            auth.rate_limiter = RateLimiter(rate_per_minute=1, burst=3)
            # Make 5 attempts; after 3, should be rate-limited
            for i in range(5):
                status, _, _ = s.request(
                    "POST", "/auth/login",
                    form={"email": "wrong@example.com",
                          "password": "bad"},
                )
                self.assertEqual(status, 303)
            # The last attempt must include "Muitas" in the error
            # (rate-limit message is in Portuguese to match the QA spec)
            _, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": "wrong@example.com",
                      "password": "bad"},
            )
            self.assertIn("err=", headers.get("Location", ""))
            self.assertIn("Muitas", headers.get("Location", ""))

    def test_setup_2fa_requires_auth(self) -> None:
        with self.srv as s:
            status, _, _ = s.request(
                "GET", "/auth/setup-2fa",
                headers={"Accept": "text/html"},
            )
        self.assertEqual(status, 303)
        # (redirect to login)

    def test_setup_2fa_get_with_session_returns_qr_card(self) -> None:
        with self.srv as s:
            # Login
            _, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            sid_cookie = headers.get("Set-Cookie", "").split(";", 1)[0]
            cookies = {SESSION_COOKIE_NAME: sid_cookie.split("=", 1)[1]}

            # Fetch setup page
            status, body, _ = s.request(
                "GET", "/auth/setup-2fa",
                cookies=cookies,
                headers={"Accept": "text/html"},
            )
        self.assertEqual(status, 200)
        self.assertIn("Habilitar 2FA", body)
        self.assertIn("otpauth", body)

    def test_setup_2fa_post_with_valid_code_activates(self) -> None:
        with self.srv as s:
            # Login
            _, _, headers = s.request(
                "POST", "/auth/login",
                form={"email": DEFAULT_ADMIN_EMAIL,
                      "password": DEFAULT_ADMIN_PASSWORD},
            )
            sid_cookie = headers.get("Set-Cookie", "").split(";", 1)[0]
            cookies = {SESSION_COOKIE_NAME: sid_cookie.split("=", 1)[1]}
            auth = s.server.RequestHandlerClass.auth

            # Fetch setup to seed pending_setup
            s.request("GET", "/auth/setup-2fa", cookies=cookies,
                      headers={"Accept": "text/html"})
            pending_secret = next(iter(auth._pending_setup_sessions.values()))
            totp_obj = TOTP.from_base32(pending_secret)
            code = totp_obj.now()

            # Submit valid code
            status, _, headers = s.request(
                "POST", "/auth/setup-2fa",
                cookies=cookies,
                form={"totp": code},
            )
            self.assertEqual(status, 303)
            self.assertIn("setup=ok", headers.get("Location", ""))
            # Admin now has TOTP enrolled
            self.assertIsNotNone(auth.user_store.get(DEFAULT_ADMIN_EMAIL).totp_secret)


# ============================================================================
# TestEndToEndAuthFlow
# ============================================================================
class TestEndToEndAuthFlow(unittest.TestCase):
    """Full E2E: login -> access dashboard -> setup 2FA -> logout."""

    def test_full_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            srv = _AuthServerHandle(tmp_path)
            with srv as s:
                # 1. Unauthenticated -> 401
                status, _, _ = s.request("GET", "/api/status")
                self.assertEqual(status, 401)

                # 2. Login (no TOTP yet)
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_ADMIN_EMAIL,
                          "password": DEFAULT_ADMIN_PASSWORD},
                )
                self.assertEqual(status, 303)
                cookies = {SESSION_COOKIE_NAME:
                           headers.get("Set-Cookie", "").split(";", 1)[0]
                           .split("=", 1)[1]}

                # 3. Authenticated -> dashboard renders
                status, body, _ = s.request(
                    "GET", "/api/status", cookies=cookies
                )
                self.assertEqual(status, 200)
                payload = json.loads(body)
                self.assertIn("files", payload)
                self.assertIn("inbox_count", payload)

                # 4. Setup 2FA
                s.request("GET", "/auth/setup-2fa", cookies=cookies,
                          headers={"Accept": "text/html"})
                auth = s.server.RequestHandlerClass.auth
                pending = next(iter(auth._pending_setup_sessions.values()))
                totp_obj = TOTP.from_base32(pending)
                status, _, _ = s.request(
                    "POST", "/auth/setup-2fa",
                    cookies=cookies,
                    form={"totp": totp_obj.now()},
                )
                self.assertEqual(status, 303)
                self.assertTrue(auth.user_store.get(DEFAULT_ADMIN_EMAIL).totp_secret)

                # 5. Now login requires TOTP
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_ADMIN_EMAIL,
                          "password": DEFAULT_ADMIN_PASSWORD},
                )
                from urllib.parse import parse_qs, urlparse
                loc = headers.get("Location", "")
                self.assertIn("step=totp", loc)

                # 6. Logout
                status, _, _ = s.request(
                    "POST", "/auth/logout", cookies=cookies
                )
                self.assertEqual(status, 303)

                # 7. Cannot access again
                status, _, _ = s.request("GET", "/api/status",
                                          cookies=cookies)
                self.assertEqual(status, 401)


# ============================================================================
# FIX-007 — Precision refinements reported by Codex QA
# ============================================================================
import base64 as _base64
import secrets


class TestFix007AdminCredentials(unittest.TestCase):
    """Fix #1: admin email/password strictly from env, no weak hardcoded."""

    def test_missing_env_uses_random_ephemeral_password_and_logs_it(self) -> None:
        for key in ("CERBERUS_ADMIN_EMAIL", "CERBERUS_ADMIN_PASSWORD"):
            os.environ.pop(key, None)
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(output):
                store = UserStore(Path(tmp) / "users.json")
        admin = store.get(DEFAULT_DEV_ADMIN_EMAIL)
        self.assertIsNotNone(admin)
        self.assertTrue(verify_password(DEFAULT_DEV_ADMIN_PASSWORD,
                                        admin.password_hash))
        self.assertGreaterEqual(len(DEFAULT_DEV_ADMIN_PASSWORD), 16)
        self.assertIn(DEFAULT_DEV_ADMIN_PASSWORD, output.getvalue())

    def test_env_admin_email_overrides_default(self) -> None:
        custom = "custom.admin@example.com"
        os.environ["CERBERUS_ADMIN_EMAIL"] = custom
        os.environ["CERBERUS_ADMIN_PASSWORD"] = "EnvOnlySecret!1"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                store = UserStore(Path(tmp) / "users.json")
            admin = store.get(custom)
            self.assertIsNotNone(admin)
            self.assertFalse(store.get(DEFAULT_DEV_ADMIN_EMAIL))
            self.assertTrue(verify_password("EnvOnlySecret!1",
                                            admin.password_hash))
            # first-run echo must be None when env supplies a password
            self.assertIsNone(store.first_run_default_password)
        finally:
            os.environ.pop("CERBERUS_ADMIN_EMAIL", None)
            os.environ.pop("CERBERUS_ADMIN_PASSWORD", None)

    def test_weak_static_password_does_not_appear_as_default(self) -> None:
        # Sanity: the old "Admin@123456" must not be the default.
        self.assertNotEqual(DEFAULT_DEV_ADMIN_PASSWORD, "Admin@123456")
        self.assertNotEqual(DEFAULT_DEV_ADMIN_PASSWORD, "admin")
        self.assertNotEqual(DEFAULT_DEV_ADMIN_PASSWORD, "password")


class TestFix007SecureCookieDecision(unittest.TestCase):
    """Fix #2: secure cookies behind Cloudflare / TLS proxies."""

    def test_plain_loopback_returns_no_secure(self) -> None:
        old = os.environ.get("CERBERUS_SECURE_COOKIES")
        try:
            os.environ.pop("CERBERUS_SECURE_COOKIES", None)
            self.assertFalse(should_use_secure_cookie(forwarded_proto=None))
        finally:
            if old is not None:
                os.environ["CERBERUS_SECURE_COOKIES"] = old

    def test_explicit_opt_in_enables_secure(self) -> None:
        old = os.environ.get("CERBERUS_SECURE_COOKIES")
        try:
            os.environ["CERBERUS_SECURE_COOKIES"] = "1"
            self.assertTrue(should_use_secure_cookie(forwarded_proto=None))
            os.environ["CERBERUS_SECURE_COOKIES"] = "true"
            self.assertTrue(should_use_secure_cookie(forwarded_proto=None))
        finally:
            if old is None:
                os.environ.pop("CERBERUS_SECURE_COOKIES", None)
            else:
                os.environ["CERBERUS_SECURE_COOKIES"] = old

    def test_https_forwarded_proto_enables_secure(self) -> None:
        old = os.environ.get("CERBERUS_SECURE_COOKIES")
        try:
            os.environ.pop("CERBERUS_SECURE_COOKIES", None)
            self.assertTrue(should_use_secure_cookie(forwarded_proto="https"))
            self.assertTrue(should_use_secure_cookie(forwarded_proto="HTTPS"))
        finally:
            if old is not None:
                os.environ["CERBERUS_SECURE_COOKIES"] = old

    def test_cloudflare_visitor_header_enables_secure(self) -> None:
        old = os.environ.pop("CERBERUS_SECURE_COOKIES", None)
        os.environ["CF_VISITOR"] = '{"scheme":"https"}'
        try:
            self.assertTrue(should_use_secure_cookie())
        finally:
            os.environ.pop("CF_VISITOR", None)
            if old is not None:
                os.environ["CERBERUS_SECURE_COOKIES"] = old


class TestFix007ClientIPResolution(unittest.TestCase):
    """Fix #2: default to socket peer; only trust proxy headers when env set."""

    def test_default_uses_direct_address(self) -> None:
        old = os.environ.get("CERBERUS_TRUST_PROXY")
        try:
            os.environ.pop("CERBERUS_TRUST_PROXY", None)
            ip = resolve_client_ip(
                {"CF-Connecting-IP": "203.0.113.5",
                 "X-Forwarded-For": "198.51.100.1, 192.0.2.1"},
                direct_address="127.0.0.1",
            )
            self.assertEqual(ip, "127.0.0.1")
        finally:
            if old is not None:
                os.environ["CERBERUS_TRUST_PROXY"] = old

    def test_trust_proxy_prefers_cf_connecting_ip(self) -> None:
        old = os.environ.get("CERBERUS_TRUST_PROXY")
        try:
            os.environ["CERBERUS_TRUST_PROXY"] = "1"
            ip = resolve_client_ip(
                {"CF-Connecting-IP": "203.0.113.5",
                 "X-Forwarded-For": "198.51.100.1"},
                direct_address="127.0.0.1",
            )
            self.assertEqual(ip, "203.0.113.5")
        finally:
            if old is None:
                os.environ.pop("CERBERUS_TRUST_PROXY", None)
            else:
                os.environ["CERBERUS_TRUST_PROXY"] = old

    def test_trust_proxy_falls_back_to_x_forwarded_for(self) -> None:
        old = os.environ.get("CERBERUS_TRUST_PROXY")
        try:
            os.environ["CERBERUS_TRUST_PROXY"] = "1"
            ip = resolve_client_ip(
                {"CF-Connecting-IP": "",
                 "X-Forwarded-For": "198.51.100.1, 192.0.2.1"},
                direct_address="127.0.0.1",
            )
            self.assertEqual(ip, "198.51.100.1")
        finally:
            if old is None:
                os.environ.pop("CERBERUS_TRUST_PROXY", None)
            else:
                os.environ["CERBERUS_TRUST_PROXY"] = old

    def test_trust_proxy_falls_back_to_direct_when_headers_empty(self) -> None:
        old = os.environ.get("CERBERUS_TRUST_PROXY")
        try:
            os.environ["CERBERUS_TRUST_PROXY"] = "1"
            ip = resolve_client_ip({}, direct_address="127.0.0.1")
            self.assertEqual(ip, "127.0.0.1")
        finally:
            if old is None:
                os.environ.pop("CERBERUS_TRUST_PROXY", None)
            else:
                os.environ["CERBERUS_TRUST_PROXY"] = old


class TestFix007Base32Stdlib(unittest.TestCase):
    """Fix #3: TOTP secrets roundtrip via stdlib base64."""

    def test_base32_roundtrip_via_stdlib(self) -> None:
        secret = secrets.token_bytes(20)
        encoded = _base64.b32encode(secret).decode("ascii")
        decoded = _base64.b32decode(encoded, casefold=True)
        self.assertEqual(decoded, secret)

    def test_totp_roundtrip_uses_stdlib_base32(self) -> None:
        t = TOTP.generate()
        b = t.to_base32()
        t2 = TOTP.from_base32(b)
        self.assertEqual(t.secret, t2.secret)
        self.assertTrue(t2.verify(t.now()))

    def test_unpadded_secret_roundtrip(self) -> None:
        # TOTP secrets are 20 bytes (160 bits) which stdlib base32 encodes
        # to 32 chars + padding. Strip padding and ensure decoder handles.
        t = TOTP.generate()
        encoded = t.to_base32().rstrip("=")
        t3 = TOTP.from_base32(encoded)
        self.assertEqual(t3.secret, t.secret)


class TestFix007TotpRetryGrace(unittest.TestCase):
    """Fix #4: TOTP retries up to 3 attempts per pending_token."""

    def test_single_wrong_attempt_keeps_pending_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            srv = _AuthServerHandle(tmp_path)
            with srv as s:
                auth = s.server.RequestHandlerClass.auth
                secret_b32 = TOTP.generate().to_base32()
                auth.user_store.set_totp_secret(DEFAULT_DEV_ADMIN_EMAIL,
                                                  secret_b32)
                # Step 1
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "password": DEFAULT_DEV_ADMIN_PASSWORD},
                )
                from urllib.parse import parse_qs, urlparse
                loc = headers.get("Location", "")
                qs = parse_qs(urlparse(loc).query)
                pending = qs.get("pending", [""])[0]
                self.assertTrue(pending)

                # Wrong TOTP code attempt 1
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "pending_token": pending,
                          "totp": "00000001"},
                )
                loc = headers.get("Location", "")
                self.assertIn("err=", loc)
                self.assertIn("incorreto", loc)
                # Pending token still alive
                self.assertIsNotNone(auth.check_pending(pending))
                self.assertEqual(auth.check_pending(pending).get("attempts"),
                                  1)

    def test_three_wrong_attempts_invalidate_pending_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            srv = _AuthServerHandle(tmp_path)
            with srv as s:
                auth = s.server.RequestHandlerClass.auth
                secret_b32 = TOTP.generate().to_base32()
                auth.user_store.set_totp_secret(DEFAULT_DEV_ADMIN_EMAIL,
                                                  secret_b32)
                # Step 1
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "password": DEFAULT_DEV_ADMIN_PASSWORD},
                )
                from urllib.parse import parse_qs, urlparse
                loc = headers.get("Location", "")
                qs = parse_qs(urlparse(loc).query)
                pending = qs.get("pending", [""])[0]

                # 3 wrong attempts
                for attempt in range(3):
                    status, _, headers = s.request(
                        "POST", "/auth/login",
                        form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                              "pending_token": pending,
                              "totp": f"0000000{attempt + 1}"},
                    )
                loc = headers.get("Location", "")
                # After 3 failures the user is bounced back to step 1
                # (credentials is the default step, so the query string
                # may omit the `step=` parameter entirely).
                self.assertTrue(loc.startswith("/auth/login"),
                                 f"expected redirect to /auth/login, got {loc!r}")
                self.assertIn("err=", loc)
                self.assertIn("Muitas", loc)
                # Pending token must be invalidated
                self.assertIsNone(auth.check_pending(pending))

    def test_correct_totp_after_two_wrong_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            srv = _AuthServerHandle(tmp_path)
            with srv as s:
                auth = s.server.RequestHandlerClass.auth
                secret_b32 = TOTP.generate().to_base32()
                auth.user_store.set_totp_secret(DEFAULT_DEV_ADMIN_EMAIL,
                                                  secret_b32)
                totp_obj = TOTP.from_base32(secret_b32)

                # Step 1
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "password": DEFAULT_DEV_ADMIN_PASSWORD},
                )
                from urllib.parse import parse_qs, urlparse
                loc = headers.get("Location", "")
                qs = parse_qs(urlparse(loc).query)
                pending = qs.get("pending", [""])[0]

                # Two wrong attempts
                for attempt in range(2):
                    s.request(
                        "POST", "/auth/login",
                        form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                              "pending_token": pending,
                              "totp": f"0000000{attempt + 1}"},
                    )
                # Now the correct code — should succeed
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "pending_token": pending,
                          "totp": totp_obj.now()},
                )
                self.assertEqual(status, 303)
                self.assertEqual(headers.get("Location"), "/")
                self.assertIn(SESSION_COOKIE_NAME + "=",
                              headers.get("Set-Cookie", ""))

    def test_expired_pending_token_cannot_issue_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            with _AuthServerHandle(tmp_path) as s:
                auth = s.server.RequestHandlerClass.auth
                totp_obj = TOTP.generate()
                auth.user_store.set_totp_secret(
                    DEFAULT_DEV_ADMIN_EMAIL, totp_obj.to_base32())
                _, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "password": DEFAULT_DEV_ADMIN_PASSWORD},
                )
                from urllib.parse import parse_qs, urlparse
                pending = parse_qs(
                    urlparse(headers.get("Location", "")).query
                ).get("pending", [""])[0]
                auth._pending[pending]["created_at"] = time.time() - 301

                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "pending_token": pending,
                          "totp": totp_obj.now()},
                )

                self.assertEqual(status, 303)
                self.assertEqual(headers.get("Location"),
                                 "/auth/login?error=session_expired")
                self.assertNotIn(SESSION_COOKIE_NAME + "=",
                                 headers.get("Set-Cookie", ""))


class TestFix007VerifyPasswordFailClosed(unittest.TestCase):
    """Fix #5: verify_password never raises."""

    def test_none_password_returns_false(self) -> None:
        self.assertFalse(verify_password(None, "any$hash"))
        self.assertFalse(verify_password("any", None))

    def test_non_string_password_returns_false(self) -> None:
        self.assertFalse(verify_password(123, "any$hash"))
        self.assertFalse(verify_password(b"bytes", "any$hash"))
        self.assertFalse(verify_password("any", 123))
        self.assertFalse(verify_password("any", b"bytes"))

    def test_malformed_digest_returns_false(self) -> None:
        self.assertFalse(verify_password("anything", ""))
        self.assertFalse(verify_password("anything", "no-dollar-here"))
        self.assertFalse(verify_password("anything",
                                          "wrong$base64!!$stuff"))
        self.assertFalse(verify_password("anything",
                                          "wrong_format$short"))

    def test_wrong_algorithm_header_returns_false(self) -> None:
        h = "pbkdf2_wrongalgo_100000$YWFh$YWFh"
        self.assertFalse(verify_password("anything", h))

    def test_corrupted_base64_returns_false(self) -> None:
        h = "pbkdf2_sha256_200000$!!!not-base64!!!$!!!also-bad!!!"
        self.assertFalse(verify_password("anything", h))

    def test_valid_hash_still_verifies_correctly(self) -> None:
        h = hash_password("correct-password")
        self.assertTrue(verify_password("correct-password", h))
        self.assertFalse(verify_password("wrong-password", h))


class TestFix007SetCookie(unittest.TestCase):
    """Fix #2 (delivery): session cookie includes Secure when behind CF."""

    def test_cookie_has_secure_attribute_when_proxy_https(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            srv = _AuthServerHandle(tmp_path)
            with srv as s:
                # Login with X-Forwarded-Proto: https
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "password": DEFAULT_DEV_ADMIN_PASSWORD},
                    headers={"X-Forwarded-Proto": "https"},
                )
                cookie = headers.get("Set-Cookie", "")
                self.assertIn("Secure", cookie)
                self.assertIn("HttpOnly", cookie)
                self.assertIn("SameSite=Lax", cookie)

    def test_cookie_has_no_secure_on_plain_loopback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "LEARNINGS.md").write_text("# L\n", encoding="utf-8")
            (tmp_path / "DECISIONS.md").write_text("# D\n", encoding="utf-8")
            srv = _AuthServerHandle(tmp_path)
            with srv as s:
                # Login without X-Forwarded-Proto
                status, _, headers = s.request(
                    "POST", "/auth/login",
                    form={"email": DEFAULT_DEV_ADMIN_EMAIL,
                          "password": DEFAULT_DEV_ADMIN_PASSWORD},
                )
                cookie = headers.get("Set-Cookie", "")
                self.assertNotIn("Secure", cookie)
                self.assertIn("HttpOnly", cookie)
                self.assertIn("SameSite=Lax", cookie)


class TestFix007DockerCompose(unittest.TestCase):
    """Fix #6: docker-compose.yml has named tunnel + CLOUDFLARE_TUNNEL_TOKEN."""

    def test_compose_declares_cloudflared_named_service(self) -> None:
        compose = Path(__file__).resolve().parents[1] / "docker-compose.yml"
        self.assertTrue(compose.exists())
        text = compose.read_text(encoding="utf-8")
        # Both cloudflared and cerberus services present
        self.assertIn("cloudflared:", text)
        self.assertIn("cerberus:", text)
        # Named-tunnel command
        self.assertIn("tunnel --no-autoupdate run", text)
        # Token env var wired
        self.assertIn("CLOUDFLARE_TUNNEL_TOKEN", text)
        self.assertIn("${CLOUDFLARE_TUNNEL_TOKEN", text)

    def test_env_example_documents_tunnel_token(self) -> None:
        env = Path(__file__).resolve().parents[1] / ".env.example"
        self.assertTrue(env.exists())
        text = env.read_text(encoding="utf-8")
        self.assertIn("CLOUDFLARE_TUNNEL_TOKEN", text)
        self.assertIn("CERBERUS_TRUST_PROXY", text)
        self.assertIn("CERBERUS_SECURE_COOKIES", text)

    def test_compose_yml_parses(self) -> None:
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not available")
        compose = Path(__file__).resolve().parents[1] / "docker-compose.yml"
        doc = yaml.safe_load(compose.read_text(encoding="utf-8"))
        self.assertIn("cerberus", doc["services"])
        self.assertIn("cloudflared", doc["services"])
        self.assertEqual(
            doc["services"]["cloudflared"]["command"],
            "tunnel --no-autoupdate run",
        )


if __name__ == "__main__":
    unittest.main()
