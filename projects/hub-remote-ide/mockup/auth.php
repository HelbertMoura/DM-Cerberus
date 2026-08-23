<?php
// =============================================================
// Dev Maniac's Hub — Auth local (email + senha + 2FA TOTP)
// SQLite. Mantém compat com cookie `dm_sso` HMAC-SHA256.
// TOTP via matemática direta — sem manipulação de bits, sem libs.
// =============================================================

declare(strict_types=1);

require_once __DIR__ . '/db.php';

function dm_totp_now(string $secret_b32): string {
    // RFC 6238 — HMAC-SHA1, 6 digits, step 30s, ±1 step janela
    $key = base32_decode_simple($secret_b32);
    $t = (int) (time() / 30);
    // Para PHP 8.0+ pack 'J' = unsigned 64-bit big-endian
    $bin = pack('J', $t);
    $hash = hash_hmac('sha1', $bin, $key, true);
    $offset = ord($hash[19]) & 0x0f;
    $code =
        ((ord($hash[$offset])     & 0x7f) << 24) |
        ((ord($hash[$offset + 1]) & 0xff) << 16) |
        ((ord($hash[$offset + 2]) & 0xff) <<  8) |
         ord($hash[$offset + 3])         & 0xff;
    return str_pad((string) ($code % 1000000), 6, '0', STR_PAD_LEFT);
}

/**
 * Decodifica base32 RFC 4648 SEM manipulação de string.
 * Usa a função nativa base32_decode se existir, senão fallback manual
 * via unpack de bytes (mais robusto).
 */
function base32_decode_simple(string $b32): string {
    $b32 = strtoupper(rtrim($b32, '='));
    // Mapeamento: cada char vira 5 bits via array lookup
    static $lookup = [
        'A' => 0, 'B' => 1, 'C' => 2, 'D' => 3, 'E' => 4, 'F' => 5, 'G' => 6,
        'H' => 7, 'I' => 8, 'J' => 9, 'K' => 10, 'L' => 11, 'M' => 12, 'N' => 13,
        'O' => 14, 'P' => 15, 'Q' => 16, 'R' => 17, 'S' => 18, 'T' => 19, 'U' => 20,
        'V' => 21, 'W' => 22, 'X' => 23, 'Y' => 24, 'Z' => 25,
        '2' => 26, '3' => 27, '4' => 28, '5' => 29, '6' => 30, '7' => 31,
    ];
    $bits = 0;
    $value = 0;
    $out = '';
    foreach (str_split($b32) as $c) {
        if (!isset($lookup[$c])) return '';
        $value = ($value << 5) | $lookup[$c];
        $bits += 5;
        if ($bits >= 8) {
            $bits -= 8;
            $out .= chr(($value >> $bits) & 0xff);
            $value &= (1 << $bits) - 1;
        }
    }
    return $out;
}

function dm_totp_verify(string $secret_b32, string $code): bool {
    $code = preg_replace('/\s+/', '', $code);
    if (!preg_match('/^\d{6}$/', $code)) return false;
    $t_now = (int) (time() / 30);
    // ±1 step = 90s janela
    for ($i = -1; $i <= 1; $i++) {
        $t = $t_now + $i;
        $bin = pack('J', $t);
        $key = base32_decode_simple($secret_b32);
        $hash = hash_hmac('sha1', $bin, $key, true);
        $offset = ord($hash[19]) & 0x0f;
        $candidate =
            ((ord($hash[$offset])     & 0x7f) << 24) |
            ((ord($hash[$offset + 1]) & 0xff) << 16) |
            ((ord($hash[$offset + 2]) & 0xff) <<  8) |
             ord($hash[$offset + 3])         & 0xff;
        $candidate = str_pad((string) ($candidate % 1000000), 6, '0', STR_PAD_LEFT);
        if (hash_equals($candidate, $code)) return true;
    }
    return false;
}

function dm_brute_check(string $email, string $ip): bool {
    $pdo = dm_pg_connect();
    $since = gmdate('Y-m-d H:i:s', time() - 15 * 60);
    $stmt = $pdo->prepare(
        "SELECT COUNT(*) FROM audit_log
         WHERE action IN ('login_failed_password', 'login_failed_2fa')
           AND created_at >= ?
           AND (user_email = ? OR ip_address = ?)"
    );
    $stmt->execute([$since, $email, $ip]);
    return ((int) $stmt->fetchColumn()) < 5;
}

if (!function_exists('dm_issue_sso_cookie')) {
    function dm_issue_sso_cookie(string $email, bool $remember = false): void {
    $cfg = (array) (require __DIR__ . '/config.php');
    $ssoSecret = (string) ($cfg['sso_secret'] ?? '');
    if ($ssoSecret === '' || str_starts_with($ssoSecret, 'PASTE-')) return;
    $ttl = $remember ? 30 * 86400 : 8 * 3600;
    $exp = time() + $ttl;
    $payload = rtrim(strtr(base64_encode(json_encode(['email' => $email, 'exp' => $exp])), '+/', '-_'), '=');
    $sig = rtrim(strtr(base64_encode(hash_hmac('sha256', $payload, $ssoSecret, true)), '+/', '-_'), '=');
    setcookie('dm_sso', $payload . '.' . $sig, [
        'expires'  => $exp,
        'path'     => '/',
        'domain'   => '.devmaniacs.com.br',
        'secure'   => true,
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    }
}

if (!function_exists('dm_session_start')) {
    function dm_session_start(): void {
        if (session_status() === PHP_SESSION_ACTIVE) return;
        $sp = __DIR__ . '/logs/sessions';
        if (!is_dir($sp)) @mkdir($sp, 0777, true);
        session_save_path($sp);
        session_name('DMHUBSESSID');
        session_set_cookie_params([
            'lifetime' => 0,
            'path'     => '/',
            'httponly' => true,
            'samesite' => 'Lax',
            'secure'   => true,
        ]);
        @session_start();
    }
}

/** ============================================================
 * ROTEAMENTO
 * ============================================================ */

$uri = rawurldecode((string) parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH));
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$ip = (string) ($_SERVER['HTTP_CF_CONNECTING_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? '');
$ua = (string) ($_SERVER['HTTP_USER_AGENT'] ?? '');

/** POST /auth/login — passo 1 (senha) */
if ($uri === '/auth/login' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');

    $input = json_decode((string) file_get_contents('php://input'), true) ?: $_POST;
    $email = strtolower(trim((string) ($input['email'] ?? '')));
    $password = (string) ($input['password'] ?? '');
    $remember = (bool) ($input['remember'] ?? false);

    if ($email === '' || $password === '') {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'missing_credentials']);
        exit;
    }
    if (!dm_brute_check($email, $ip)) {
        dm_audit_log('login_blocked_bruteforce', $email, $ip, $ua);
        http_response_code(429);
        echo json_encode(['ok' => false, 'error' => 'too_many_attempts']);
        exit;
    }

    $pdo = dm_pg_connect();
    $stmt = $pdo->prepare("SELECT id, email, password_hash, totp_secret, role FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$user || empty($user['password_hash']) || !password_verify($password, $user['password_hash'])) {
        dm_audit_log('login_failed_password', $email, $ip, $ua);
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'invalid_credentials']);
        exit;
    }

    dm_session_start();
    session_regenerate_id(true);
    $_SESSION['pre_2fa'] = [
        'user_id' => $user['id'],
        'email'   => $user['email'],
        'role'    => $user['role'],
        'remember'=> $remember,
        'started_at' => gmdate('c'),
    ];
    dm_audit_log('login_password_ok', $email, $ip, $ua);

    $needs_totp_setup = empty($user['totp_secret']);
    echo json_encode([
        'ok' => true,
        'next' => $needs_totp_setup ? '2fa_setup' : '2fa',
        'email' => $email,
    ]);
    exit;
}

/** POST /auth/2fa — passo 2 (TOTP) */
if ($uri === '/auth/2fa' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');

    dm_session_start();
    if (empty($_SESSION['pre_2fa'])) {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'no_password_session']);
        exit;
    }

    $pre = $_SESSION['pre_2fa'];
    $input = json_decode((string) file_get_contents('php://input'), true) ?: $_POST;
    $code = trim((string) ($input['code'] ?? ''));

    if (!preg_match('/^\d{6}$/', preg_replace('/\s+/', '', $code))) {
        dm_audit_log('login_failed_2fa', $pre['email'], $ip, $ua, ['reason' => 'malformed']);
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'invalid_code_format']);
        exit;
    }

    $pdo = dm_pg_connect();
    $stmt = $pdo->prepare("SELECT totp_secret FROM users WHERE id = ?");
    $stmt->execute([$pre['user_id']]);
    $secret = $stmt->fetchColumn();

    if (!$secret || !dm_totp_verify((string) $secret, $code)) {
        dm_audit_log('login_failed_2fa', $pre['email'], $ip, $ua);
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'invalid_2fa']);
        exit;
    }

    $_SESSION['user'] = [
        'email'    => $pre['email'],
        'role'     => $pre['role'],
        'method'   => 'password+totp',
        'login_at' => gmdate('c'),
    ];
    $remember = (bool) ($pre['remember'] ?? false);

    $pdo->prepare("UPDATE users SET last_login = datetime('now'), last_ip = ? WHERE id = ?")
        ->execute([$ip, $pre['user_id']]);

    $session_id = session_id();
    $token_hash = hash('sha256', $session_id . $ua);
    $expires_at = gmdate('Y-m-d H:i:s', time() + ($remember ? 30 * 86400 : 8 * 3600));
    $pdo->prepare(
        "INSERT INTO sessions (id, user_id, token_hash, user_agent, ip_address, expires_at)
         VALUES (?, ?, ?, ?, ?, ?)
         ON CONFLICT(token_hash) DO UPDATE SET expires_at = excluded.expires_at"
    )->execute([$session_id, $pre['user_id'], $token_hash, $ua, $ip, $expires_at]);

    dm_issue_sso_cookie($pre['email'], $remember);
    dm_audit_log('login_success', $pre['email'], $ip, $ua, ['remember' => $remember]);
    unset($_SESSION['pre_2fa']);

    echo json_encode(['ok' => true, 'redirect' => '/hub.html']);
    exit;
}

/** GET /auth/2fa/qr?uri=... — retorna SVG do QR code
 *  Autenticado em pre_2fa (mesma sessão do /auth/2fa/setup).
 *  Usa lib kazuhikoarase/qrcode-generator (MIT, ~50KB, zero deps). */
if ($uri === '/auth/2fa/qr' && $method === 'GET') {
    require_once __DIR__ . '/qrlib.php';

    dm_session_start();
    if (empty($_SESSION['pre_2fa'])) {
        http_response_code(401);
        header('Content-Type: image/svg+xml');
        echo '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>';
        exit;
    }

    $uri_param = (string) ($_GET['uri'] ?? '');
    if ($uri_param === '' || !str_starts_with($uri_param, 'otpauth://')) {
        http_response_code(400);
        header('Content-Type: image/svg+xml');
        echo '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>';
        exit;
    }

    // Cache curto (30 dias) — o secret é por user e só muda em setup 2FA novo
    header('Content-Type: image/svg+xml; charset=utf-8');
    header('Cache-Control: private, max-age=2592000');

    // Versão fixa 10 (57x57 módulos) — suporta otpauth URI até ~1430 chars.
    // Versão 7 (992 max) overflow com URI encodado (1092 chars).
    // Auto-detect (typeNumber=0) falha em alguns tamanhos com essa lib.
    $qr = new QRCode();
    $qr->setTypeNumber(10);
    $qr->setErrorCorrectLevel(QR_ERROR_CORRECT_LEVEL_M);
    $qr->addData($uri_param);
    $qr->make();

    // Captura o output do printSVG ao invés de imprimir direto
    ob_start();
    $qr->printSVG(8);  // size=8 = cada módulo = 8px
    $svg = ob_get_clean();

    // Injeta cor navy (brand) em vez de preto puro
    $svg = str_replace('fill="#000000"', 'fill="#061637"', $svg);
    echo $svg;
    exit;
}

/** GET /auth/2fa/setup — gera otpauth URL (autenticado em pre_2fa) */
if ($uri === '/auth/2fa/setup' && $method === 'GET') {
    header('Content-Type: application/json; charset=utf-8');

    dm_session_start();
    if (empty($_SESSION['pre_2fa'])) {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'no_password_session']);
        exit;
    }

    $pre = $_SESSION['pre_2fa'];
    $pdo = dm_pg_connect();
    $stmt = $pdo->prepare("SELECT totp_secret FROM users WHERE id = ?");
    $stmt->execute([$pre['user_id']]);
    $secret = $stmt->fetchColumn();

    if (!$secret) {
        $alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        $secret = '';
        for ($i = 0; $i < 32; $i++) {  // 32 chars = 20 bytes base32
            $secret .= $alphabet[random_int(0, 31)];
        }
        $pdo->prepare("UPDATE users SET totp_secret = ? WHERE id = ?")
            ->execute([$secret, $pre['user_id']]);
    }

    $otpauth = sprintf(
        'otpauth://totp/%s:%s?secret=%s&issuer=%s',
        rawurlencode('Dev Maniacs Hub'),
        rawurlencode($pre['email']),
        $secret,
        rawurlencode('Dev Maniacs Hub')
    );

    echo json_encode([
        'ok' => true,
        'secret' => $secret,
        'otpauth_url' => $otpauth,
    ]);
    exit;
}

/** POST /auth/change-password — troca senha (autenticado) */
if ($uri === '/auth/change-password' && $method === 'POST') {
    header('Content-Type: application/json; charset=utf-8');

    dm_session_start();
    if (empty($_SESSION['user'])) {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'not_authenticated']);
        exit;
    }

    $input = json_decode((string) file_get_contents('php://input'), true) ?: $_POST;
    $current = (string) ($input['current'] ?? '');
    $new = (string) ($input['new'] ?? '');

    if (strlen($new) < 12 || !preg_match('/[A-Z]/', $new) || !preg_match('/[a-z]/', $new) || !preg_match('/[0-9!@#$%^&*]/', $new)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'weak_password']);
        exit;
    }

    $pdo = dm_pg_connect();
    $stmt = $pdo->prepare("SELECT password_hash FROM users WHERE email = ?");
    $stmt->execute([$_SESSION['user']['email']]);
    $hash = $stmt->fetchColumn();

    if (!$hash || !password_verify($current, $hash)) {
        http_response_code(401);
        echo json_encode(['ok' => false, 'error' => 'wrong_current_password']);
        exit;
    }

    $new_hash = password_hash($new, PASSWORD_BCRYPT, ['cost' => 12]);
    $pdo->prepare("UPDATE users SET password_hash = ?, updated_at = datetime('now') WHERE email = ?")
        ->execute([$new_hash, $_SESSION['user']['email']]);

    dm_audit_log('password_changed', $_SESSION['user']['email'], $ip, $ua);

    echo json_encode(['ok' => true]);
    exit;
}

http_response_code(404);
header('Content-Type: application/json; charset=utf-8');
echo json_encode(['ok' => false, 'error' => 'not_found']);
exit;