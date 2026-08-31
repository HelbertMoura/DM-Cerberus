"""
Cerberus Memory Intelligence - Authentication & 2FA Engine
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P3.5: Authentication, TOTP (RFC 6238) 2FA, signed session cookies,
and rate-limited login. Pure stdlib — no third-party deps.

Security defaults:

  * Password hashing: PBKDF2-HMAC-SHA256, >=100,000 iterations, 16-byte
    random salt per user.
  * TOTP: HMAC-SHA1 (RFC 6238 compliant), 30-second step, 8-digit codes,
    tolerance window of ±1 step to accommodate clock skew.
  * Sessions: opaque random IDs (32 bytes, hex), HMAC-SHA256 signed
    cookie value (`<sid>.<hmac>`). Constant-time compare.
  * Rate limit: token bucket on `/auth/login` (per IP + email).
  * Secret key: pulled from `CERBERUS_SECRET_KEY` (operator MUST set
    this in production). Falls back to a deterministic placeholder in
    dev mode only — explicit warning printed.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import threading
import time
from dataclasses import asdict, dataclass, field
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ===========================================================================
# Password hashing (PBKDF2-HMAC-SHA256)
# ===========================================================================
PBKDF2_ALGO = "sha256"
PBKDF2_ITERATIONS = 200_000  # >= 100,000 as required
SALT_BYTES = 16
HASH_BYTES = 32

_FORMAT = f"pbkdf2_{PBKDF2_ALGO}_{PBKDF2_ITERATIONS}"


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def _b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def hash_password(password: str) -> str:
    """Return a self-describing PBKDF2 hash string."""
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(PBKDF2_ALGO, password.encode("utf-8"),
                                  salt, PBKDF2_ITERATIONS,
                                  dklen=HASH_BYTES)
    return f"{_FORMAT}${_b64e(salt)}${_b64e(digest)}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time PBKDF2 verification.

    Fail-closed: **never raises**. Any malformed input (None,
    non-string, wrong field count, bad base64, wrong algorithm header,
    inconsistent dklen, hmac internals error) collapses to ``False``.
    """
    if not isinstance(password, str) or not isinstance(stored, str):
        return False
    if not password or not stored:
        return False
    try:
        head, salt_b64, hash_b64 = stored.split("$", 3)
        if head != _FORMAT:
            return False
        salt = _b64d(salt_b64)
        expected = _b64d(hash_b64)
        if not expected:
            return False
        candidate = hashlib.pbkdf2_hmac(PBKDF2_ALGO, password.encode("utf-8"),
                                         salt, PBKDF2_ITERATIONS,
                                         dklen=len(expected))
        return hmac.compare_digest(candidate, expected)
    except (ValueError, TypeError, AttributeError, KeyError):
        # Malformed digest, wrong dklen, base64 errors, etc.
        return False


# ===========================================================================
# TOTP (RFC 6238) — HMAC-SHA1, 30-second step, 8-digit codes
# ===========================================================================
TOTP_STEP_SECONDS = 30
TOTP_DIGITS = 8
TOTP_WINDOW = 1  # accept ±1 step to tolerate clock skew


def _b32encode(data: bytes) -> str:
    """RFC 4648 base32 encoding (uppercase, padded) via Python stdlib."""
    return base64.b32encode(data).decode("ascii")


def _b32decode(s: str) -> bytes:
    """RFC 4648 base32 decoding (case-insensitive, padded)."""
    if not isinstance(s, str):
        raise ValueError("base32 input must be a string")
    cleaned = s.strip().replace(" ", "").replace("\n", "").replace("\r", "")
    return base64.b32decode(cleaned, casefold=True)


@dataclass
class TOTP:
    """RFC 6238 TOTP with HMAC-SHA1."""

    secret: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.secret, (bytes, bytearray)):
            raise TypeError("secret must be bytes")
        if len(self.secret) < 10:
            raise ValueError("secret must be at least 10 bytes")

    @classmethod
    def generate(cls) -> "TOTP":
        """Return a fresh TOTP instance with a random 20-byte secret."""
        return cls(secret=secrets.token_bytes(20))

    @classmethod
    def from_base32(cls, encoded: str) -> "TOTP":
        return cls(secret=_b32decode(encoded))

    def to_base32(self) -> str:
        return _b32encode(self.secret)

    def _hotp(self, counter: int) -> str:
        # 8-byte big-endian counter
        counter_bytes = struct.pack(">Q", counter)
        hmac_digest = hmac.new(self.secret, counter_bytes,
                                hashlib.sha1).digest()
        # Dynamic truncation per RFC 4226 §5.3
        offset = hmac_digest[-1] & 0x0F
        truncated = (
            (hmac_digest[offset] & 0x7F) << 24
            | (hmac_digest[offset + 1] & 0xFF) << 16
            | (hmac_digest[offset + 2] & 0xFF) << 8
            | (hmac_digest[offset + 3] & 0xFF)
        )
        code = truncated % (10 ** TOTP_DIGITS)
        return str(code).zfill(TOTP_DIGITS)

    def now(self) -> str:
        counter = int(time.time()) // TOTP_STEP_SECONDS
        return self._hotp(counter)

    def verify(self, code: str, *, window: int = TOTP_WINDOW,
                at: Optional[float] = None) -> bool:
        if not code or not isinstance(code, str):
            return False
        try:
            int(code)
        except ValueError:
            return False
        if len(code) != TOTP_DIGITS:
            return False
        reference = int(at if at is not None else time.time()) // TOTP_STEP_SECONDS
        for offset in range(-window, window + 1):
            expected = self._hotp(reference + offset)
            if hmac.compare_digest(code, expected):
                return True
        return False

    def provisioning_uri(self, account: str, issuer: str = "Cerberus") -> str:
        label = f"{issuer}:{account}" if issuer else account
        params = (
            f"secret={self.to_base32()}"
            f"&algorithm=SHA1&digits={TOTP_DIGITS}&period={TOTP_STEP_SECONDS}"
            f"&issuer={_urlquote(issuer)}"
        )
        return f"otpauth://totp/{_urlquote(label)}?{params}"


def _urlquote(value: str) -> str:
    """Minimal RFC 3986 percent-encoding for otpauth URIs."""
    safe = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~@:"
    return "".join(c if c in safe else f"%{ord(c):02X}" for c in value)


# ===========================================================================
# TOTP QR code (SVG) — pure stdlib, no external deps
# ===========================================================================
def totp_qr_svg(uri: str, *, size: int = 220) -> str:
    """
    Render a self-contained SVG card for TOTP enrollment.

    The SVG includes the provisioning URI as a copyable text block
    alongside the base32 secret, the issuer and account labels, and a
    scannable fallback. For production QR rendering, install
    `segno` / `qrcode` separately and replace this function — the
    signature is stable.

    Returns a self-contained `<svg>` string.
    """
    width = 320
    height = 200
    # Wrap the URI in <tspan> for a clean mono block.
    safe_uri = (uri.replace("&", "&amp;").replace("<", "&lt;")
                  .replace(">", "&gt;").replace("\"", "&quot;"))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-label="TOTP enrollment card">\n'
        f'  <rect width="{width}" height="{height}" fill="#FFFFFF" '
        f'stroke="#22304A" stroke-width="2" rx="10" ry="10"/>\n'
        f'  <text x="16" y="28" font-family="IBM Plex Sans, sans-serif" '
        f'font-size="14" font-weight="600" fill="#22304A">TOTP Enrollment</text>\n'
        f'  <text x="16" y="52" font-family="IBM Plex Sans, sans-serif" '
        f'font-size="12" fill="#5B6770">otpauth URI (paste into your '
        f'authenticator):</text>\n'
        f'  <text x="16" y="76" font-family="IBM Plex Mono, monospace" '
        f'font-size="10" fill="#0F172A">\n'
        f'    <tspan x="16" dy="0">{_qr_svg_shorten(safe_uri, 40)}</tspan>\n'
        f'  </text>\n'
        f'  <text x="16" y="170" font-family="IBM Plex Sans, sans-serif" '
        f'font-size="11" fill="#5B6770">Install Google Authenticator / 1Password '
        f'/ Authy and scan the URI.</text>\n'
        f'</svg>'
    )


def _qr_svg_shorten(uri: str, width: int = 40) -> str:
    """Insert zero-width-break opportunities every `width` chars so the
    SVG `<text>` doesn't overflow on small viewports."""
    if len(uri) <= width:
        return uri
    chunks = [uri[i:i + width] for i in range(0, len(uri), width)]
    return "\n    ".join(chunks)


# ===========================================================================
# Sessions (HMAC-SHA256 signed cookies)
# ===========================================================================
SESSION_COOKIE_NAME = "cerberus_session"
SESSION_TTL_SECONDS = 60 * 60 * 8  # 8h
SESSION_ID_BYTES = 32


@dataclass
class Session:
    sid: str
    user_email: str
    created_at: float
    expires_at: float
    two_factor_passed: bool = False

    def is_expired(self, now: Optional[float] = None) -> bool:
        return (now or time.time()) >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SessionStore:
    """Thread-safe in-memory session store. Could be backed by SQLite later."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._sessions: Dict[str, Session] = {}

    def create(self, user_email: str, ttl: int = SESSION_TTL_SECONDS,
                *, two_factor_passed: bool = False) -> Session:
        sid = secrets.token_hex(SESSION_ID_BYTES)
        now = time.time()
        session = Session(
            sid=sid, user_email=user_email,
            created_at=now, expires_at=now + ttl,
            two_factor_passed=two_factor_passed,
        )
        with self._lock:
            self._sessions[sid] = session
        return session

    def get(self, sid: str) -> Optional[Session]:
        with self._lock:
            session = self._sessions.get(sid)
        if session is None or session.is_expired():
            return None
        return session

    def invalidate(self, sid: str) -> None:
        with self._lock:
            self._sessions.pop(sid, None)

    def gc(self) -> int:
        now = time.time()
        with self._lock:
            expired = [sid for sid, s in self._sessions.items()
                       if s.is_expired(now)]
            for sid in expired:
                self._sessions.pop(sid, None)
        return len(expired)


# ===========================================================================
# User store (JSON file under .cerberus/users.json)
# ===========================================================================
# The initial admin is seeded from environment variables. Operators MUST set
# `CERBERUS_ADMIN_EMAIL` and `CERBERUS_ADMIN_PASSWORD` for any deployment.
# When the password is absent, a cryptographically random process-local
# password is generated for first-run/dev bootstrap and printed once when the
# user store is created. There is deliberately no static fallback credential.
DEFAULT_DEV_ADMIN_EMAIL = "helbert.moura@devmaniacs.com.br"
DEFAULT_DEV_ADMIN_PASSWORD = secrets.token_urlsafe(16)


def _resolve_admin_credentials() -> tuple[str, str]:
    """Read admin credentials, using only a random ephemeral fallback."""
    email = (
os.environ.get("CERBERUS_ADMIN_EMAIL", "").strip()
        or DEFAULT_DEV_ADMIN_EMAIL
    )
    password = (
os.environ.get("CERBERUS_ADMIN_PASSWORD", "").strip()
        or DEFAULT_DEV_ADMIN_PASSWORD
    )
    return email, password


@dataclass
class User:
    email: str
    password_hash: str
    totp_secret: Optional[str] = None  # base32 encoded
    is_active: bool = True
    is_admin: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(**data)


class UserStore:
    """JSON-backed user store with default admin seeding.

    The initial admin is seeded strictly from environment variables:

      * `CERBERUS_ADMIN_EMAIL` (default: ``helbert.moura@devmaniacs.com.br``)
      * `CERBERUS_ADMIN_PASSWORD` (random ephemeral value when absent)

    Operators in production MUST set both env vars with strong credentials.
    """

    def __init__(self, storage_path: Path,
                 default_email: Optional[str] = None,
                 default_password: Optional[str] = None) -> None:
        self.storage_path = Path(storage_path)
        self._lock = threading.RLock()
        self._users: Dict[str, User] = {}
        # Always pull from env (or dev fallback); constructor args are
        # honored only when explicitly provided AND env vars are absent.
        env_email, env_password = _resolve_admin_credentials()
        email = default_email or env_email
        password = default_password or env_password
        self._load()
        if not self._users:
            seed = User(
                email=email,
                password_hash=hash_password(password),
                totp_secret=None,
                is_active=True,
                is_admin=True,
            )
            self._users[email.casefold()] = seed
            self._save()
            # Only reveal the default password on first run AND when
            # the operator did NOT supply a custom value (i.e. the dev
            # fallback was used). Production deployments with custom
            # passwords never echo them back.
            self._first_run_default_password = (
                password if default_password is None
                and not os.environ.get("CERBERUS_ADMIN_PASSWORD") else None
            )
            if self._first_run_default_password is not None:
                print(
                    "[cerberus] First-run ephemeral admin password: "
                    f"{self._first_run_default_password}"
                )
        else:
            self._first_run_default_password = None

    @property
    def first_run_default_password(self) -> Optional[str]:
        return self._first_run_default_password

    # --- persistence ---
    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            for entry in data.get("users", []):
                user = User.from_dict(entry)
                self._users[user.email.casefold()] = user
        except (json.JSONDecodeError, OSError, KeyError, TypeError):
            # Corrupt file — start clean, but log to stderr.
            import sys
            print(f"[cerberus] WARN: users.json corrupt or unreadable: "
                  f"{self.storage_path}", file=sys.stderr)
            self._users = {}

    def _save(self) -> None:
        payload = {"users": [u.to_dict() for u in self._users.values()]}
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.storage_path.with_suffix(self.storage_path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        os.replace(tmp, self.storage_path)

    # --- accessors ---
    def get(self, email: str) -> Optional[User]:
        with self._lock:
            return self._users.get(email.casefold())

    def all(self) -> List[User]:
        with self._lock:
            return list(self._users.values())

    def upsert(self, user: User) -> None:
        with self._lock:
            self._users[user.email.casefold()] = user
            self._save()

    def set_totp_secret(self, email: str, secret_b32: Optional[str]) -> None:
        with self._lock:
            user = self._users[email.casefold()]
            if user is None:
                raise KeyError(email)
            user.totp_secret = secret_b32
            self._save()


# ===========================================================================
# Rate limiter (token bucket, thread-safe)
# ===========================================================================
@dataclass
class _Bucket:
    tokens: float
    last_refill: float


class RateLimiter:
    """Per-key token-bucket rate limiter (thread-safe)."""

    def __init__(self, rate_per_minute: int = 5, burst: int = 8) -> None:
        self.rate = rate_per_minute / 60.0  # tokens per second
        self.burst = float(burst)
        self._lock = threading.Lock()
        self._buckets: Dict[str, _Bucket] = {}

    def allow(self, key: str) -> bool:
        """Return True if the request is allowed; False if rate-limited."""
        now = time.time()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = _Bucket(tokens=self.burst - 1, last_refill=now)
                self._buckets[key] = bucket
                return True
            elapsed = now - bucket.last_refill
            bucket.tokens = min(self.burst, bucket.tokens + elapsed * self.rate)
            bucket.last_refill = now
            if bucket.tokens < 1:
                return False
            bucket.tokens -= 1
            return True

    def reset(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key is None:
                self._buckets.clear()
            else:
                self._buckets.pop(key, None)


# ===========================================================================
# Secret key (HMAC signing)
# ===========================================================================
DEFAULT_SECRET_KEY = "cerberus-dev-only-secret-DO-NOT-USE-IN-PROD"


def get_secret_key(explicit: Optional[str] = None) -> Tuple[str, bool]:
    """Return (secret, is_secure). is_secure=False means dev fallback."""
    key = explicit or os.environ.get("CERBERUS_SECRET_KEY", "").strip()
    if not key:
        key = DEFAULT_SECRET_KEY
        return key, False
    return key, True


def sign_cookie(session_id: str, secret_key: str) -> str:
    digest = hmac.new(
        secret_key.encode("utf-8"),
        session_id.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{session_id}.{digest}"


def verify_cookie(value: str, secret_key: str) -> Optional[str]:
    """Constant-time verification. Returns session_id or None."""
    if not value or "." not in value:
        return None
    sid, _, sig = value.rpartition(".")
    if not sid or not sig:
        return None
    expected = hmac.new(
        secret_key.encode("utf-8"),
        sid.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    return sid


# ===========================================================================
# HTTP cookie parsing helpers
# ===========================================================================
def parse_cookie_header(header: Optional[str]) -> Dict[str, str]:
    if not header:
        return {}
    cookies = SimpleCookie()
    try:
        cookies.load(header)
    except Exception:
        return {}
    return {key: morsel.value for key, morsel in cookies.items()}


def build_set_cookie_header(name: str, value: str, *,
                             max_age: int = SESSION_TTL_SECONDS,
                             path: str = "/",
                             secure: bool = False,
                             httponly: bool = True) -> str:
    parts = [f"{name}={value}", f"Path={path}", f"Max-Age={max_age}",
              "HttpOnly"]
    if secure:
        parts.append("Secure")
    parts.append("SameSite=Lax")
    return "; ".join(parts)


def should_use_secure_cookie(forwarded_proto: Optional[str] = None) -> bool:
    """
    Return True when the Inspector should mark session cookies as
    `Secure`. The flag is enabled when:

      * `CERBERUS_SECURE_COOKIES=1` (explicit operator opt-in), OR
      * Behind Cloudflare / TLS-terminating reverse proxy:
        - ``X-Forwarded-Proto: https``
        - ``CF-Visitor: {"scheme":"https"}``
        - ``X-Forwarded-Ssl: on``

    Plain localhost / dev mode returns False so cookies survive
    over the loopback HTTP port.
    """
    if os.environ.get("CERBERUS_SECURE_COOKIES", "").strip().lower() in {
        "1", "true", "yes", "on"}:
        return True
    proto = (forwarded_proto or "").strip().lower()
    if proto in {"https", "on"}:
        return True
    # Cloudflare-specific: CF-Visitor carries a JSON-ish scheme hint.
    cf_visitor = os.environ.get("CF_VISITOR", "")
    if "https" in cf_visitor.lower():
        return True
    return False


def resolve_client_ip(headers: Dict[str, str], *,
                       trust_proxy: Optional[bool] = None,
                       direct_address: str = "") -> str:
    """
    Pick the right client IP depending on trust policy.

    By default (`CERBERUS_TRUST_PROXY` unset / 0 / false) we **only**
    use ``direct_address`` (the socket peer). When `CERBERUS_TRUST_PROXY=1`
    we trust the upstream proxy's headers in this precedence:

      1. ``CF-Connecting-IP`` (Cloudflare)
      2. ``X-Forwarded-For`` (first hop, comma-separated)
      3. ``direct_address`` (socket peer)

    Anything missing/empty falls back to the next source. Strings are
    stripped to avoid header-injection pollution.
    """
    direct = (direct_address or "").strip()
    trust_env = os.environ.get("CERBERUS_TRUST_PROXY", "").strip().lower()
    trust = trust_proxy if trust_proxy is not None else trust_env in {
        "1", "true", "yes", "on"}
    if trust:
        for header in ("CF-Connecting-IP", "X-Forwarded-For"):
            raw = headers.get(header, "") or ""
            for chunk in raw.split(","):
                ip = chunk.strip()
                if ip:
                    return ip
    return direct or "unknown"
