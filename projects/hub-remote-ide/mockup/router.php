<?php
// =============================================================
// Dev Maniac's Hub — Router (PHP built-in server)
// Uso: php -S 127.0.0.1:8766 router.php
//
// Rotas:
//   /auth/google                  → inicia login Google (302 p/ Google)
//   /api/auth/callback/google     → recebe o code, troca por token, cria sessão
//   /auth/logout                  → encerra sessão
//   /auth/me                      → JSON com o usuário logado (ou 401)
//   demais caminhos               → arquivos estáticos do mockup
//
// Stack: PHP 8.3 puro, sem framework. Sessão = cookie DMHUBSESSID.
// Audit: logs/auth-audit.jsonl (JSONL append)
// =============================================================

declare(strict_types=1);

$configFile = __DIR__ . '/config.php';
$config = is_file($configFile) ? (array) require $configFile : null;

$uri  = rawurldecode((string) parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH));
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

// ------------------------------------------------------------
// Helpers
// ------------------------------------------------------------

function dm_session_start(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) return;
    // php.ini global aponta save_path pra um drive E:\ que nem sempre existe
    // (APAE-DRIVE-REMOTO) — usa diretório local do projeto (gitignored).
    $sp = __DIR__ . '/logs/sessions';
    if (!is_dir($sp)) @mkdir($sp, 0777, true);
    session_save_path($sp);
    session_name('DMHUBSESSID');
    session_set_cookie_params([
        'lifetime' => 0,
        'path'     => '/',
        'httponly' => true,
        'samesite' => 'Lax',
        'secure'   => true, // o hub é servido via HTTPS (Cloudflare Tunnel)
    ]);
    session_start();
}

function dm_audit(string $event, array $extra = []): void
{
    $dir = __DIR__ . '/logs';
    if (!is_dir($dir)) @mkdir($dir, 0777, true);
    $line = json_encode([
        'ts'    => gmdate('c'),
        'event' => $event,
        'ip'    => $_SERVER['HTTP_CF_CONNECTING_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? null,
        'ua'    => $_SERVER['HTTP_USER_AGENT'] ?? null,
    ] + $extra, JSON_UNESCAPED_SLASHES) . "\n";
    @file_put_contents($dir . '/auth-audit.jsonl', $line, FILE_APPEND | LOCK_EX);
}

/** Página de erro/setup com a cara da marca (navy/paper/cyan) */
function dm_page(int $status, string $eyebrow, string $title, string $bodyHtml): never
{
    http_response_code($status);
    header('Content-Type: text/html; charset=utf-8');
    echo '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">'
       . '<meta name="viewport" content="width=device-width, initial-scale=1">'
       . '<title>' . htmlspecialchars($title) . ' · Hub DM</title><style>'
       . 'body{margin:0;min-height:100vh;display:grid;place-items:center;background:#061637;color:#faf6ed;'
       . 'font-family:system-ui,-apple-system,Arial,sans-serif;padding:24px;box-sizing:border-box}'
       . '.card{max-width:520px;border:3px solid #08b9ca;box-shadow:8px 8px 0 rgba(0,0,0,.45);padding:32px;background:#0b1f4b}'
       . '.eyebrow{font-family:Consolas,monospace;font-size:12px;letter-spacing:.18em;color:#6b4c9a;text-transform:uppercase}'
       . 'h1{margin:8px 0 12px;font-size:22px}p{margin:8px 0;line-height:1.55;color:#c9d4ef}'
       . 'code{font-family:Consolas,monospace;color:#08b9ca;word-break:break-all}'
       . 'a{color:#08b9ca;text-decoration:none;font-weight:600}a:hover{text-decoration:underline}'
       . 'footer{margin-top:20px;font-family:Consolas,monospace;font-size:11px;color:#5c7090}'
       . '</style></head><body><div class="card">'
       . '<p class="eyebrow">' . htmlspecialchars($eyebrow) . '</p>'
       . '<h1>' . htmlspecialchars($title) . '</h1>'
       . $bodyHtml
       . '<footer>DM//HUB · ' . date('d/m/Y H:i') . '</footer>'
       . '</div></body></html>';
    exit;
}

/** Decodifica o payload do id_token (JWT parte 2, base64url) */
function dm_jwt_payload(string $jwt): ?array
{
    $parts = explode('.', $jwt);
    if (count($parts) !== 3) return null;
    $json = base64_decode(strtr($parts[1], '-_', '+/'), true);
    if ($json === false) return null;
    $payload = json_decode($json, true);
    return is_array($payload) ? $payload : null;
}

function dm_creds_ok(?array $cfg): bool
{
    return $cfg !== null
        && !str_starts_with((string) ($cfg['google_client_id'] ?? ''), 'PASTE-')
        && !str_starts_with((string) ($cfg['google_client_secret'] ?? ''), 'PASTE-')
        && !empty($cfg['google_client_id'])
        && !empty($cfg['google_client_secret']);
}

// =============================================================
// Rotas de autenticação (delegam pro auth.php que implementa
// email + senha + 2FA TOTP — sem Google OAuth)
// =============================================================

if (in_array($uri, ['/auth/login', '/auth/2fa', '/auth/2fa/setup', '/auth/change-password', '/auth/regen-backup'], true)) {
    require __DIR__ . '/auth.php';
    exit;
}

/** GET /auth/status — estado público do auth (sem expor valores) */
if ($uri === '/auth/status') {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    // Auth local (Postgres) — não precisa checar credenciais Google.
    // Retorna true pra manter compat com frontend.
    echo json_encode([
        'auth_method'   => 'password_totp',
        'user_db_ready' => true,
        'sso_secret_set'=> !str_starts_with((string) ($config['sso_secret'] ?? 'PASTE'), 'PASTE-')
                            && (string) ($config['sso_secret'] ?? '') !== '',
    ]);
    exit;
}

if ($uri === '/auth/logout') {
    dm_session_start();
    $email = $_SESSION['user']['email'] ?? null;
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();

    // Derruba também o cookie SSO do code-server (*.devmaniacs.com.br)
    setcookie('dm_sso', '', [
        'expires'  => time() - 3600,
        'path'     => '/',
        'domain'   => '.devmaniacs.com.br',
        'secure'   => true,
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    dm_audit('logout', ['email' => $email]);
    header('Location: /login.html');
    exit;
}

if ($uri === '/auth/status') {
    // Estado público do auth (sem expor valores) — a tela de login usa
    // pra avisar se as credenciais Google ainda não foram coladas.
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode([
        'google_configured' => dm_creds_ok($config),
        'sso_secret_set'    => !str_starts_with((string) ($config['sso_secret'] ?? 'PASTE'), 'PASTE-')
                                && (string) ($config['sso_secret'] ?? '') !== '',
    ]);
    exit;
}

if ($uri === '/auth/me') {
    dm_session_start();
    header('Content-Type: application/json; charset=utf-8');
    if (empty($_SESSION['user'])) {
        http_response_code(401);
        echo json_encode(['authenticated' => false]);
    } else {
        // sso_code: indica se o cookie assinado pro code-server está ativo
        $ssoActive = false;
        $ssoSecret = (string) (($config['sso_secret'] ?? ''));
        $cookie    = (string) ($_COOKIE['dm_sso'] ?? '');
        if ($ssoSecret !== '' && substr_count($cookie, '.') === 1) {
            [$payload, $sig] = explode('.', $cookie, 2);
            $expect = hash_hmac('sha256', $payload, $ssoSecret, true);
            if (hash_equals($expect, base64_decode(strtr($sig, '-_', '+/')))) {
                $d = json_decode(base64_decode(strtr($payload, '-_', '+/')), true);
                $ssoActive = is_array($d) && ($d['exp'] ?? 0) > time();
            }
        }
        echo json_encode(['authenticated' => true, 'user' => $_SESSION['user'], 'sso_code' => $ssoActive]);
    }
    exit;
}

// =============================================================
// Estáticos
// =============================================================

if ($uri === '/') {
    header('Location: /login.html');
    exit;
}

// /assets/* mapeia pra pasta assets/ DO PROJETO (um nível acima do
// docroot mockup/). Sem isso, logo/mascote/ícones PWA davam 404 —
// bug encontrado na auditoria de 23/08/2026.
if (str_starts_with($uri, '/assets/')) {
    $root = realpath(__DIR__ . '/../assets');
    $file = realpath(__DIR__ . '/../' . ltrim($uri, '/'));
    $types = ['png' => 'image/png', 'webp' => 'image/webp', 'svg' => 'image/svg+xml', 'css' => 'text/css'];
    $ext   = strtolower(pathinfo((string) $file, PATHINFO_EXTENSION));
    if ($file !== false && $root !== false && str_starts_with($file, $root)
        && is_file($file) && isset($types[$ext])) {
        header('Content-Type: ' . $types[$ext]);
        header('Cache-Control: public, max-age=86400');
        header('Content-Length: ' . (string) filesize($file));
        readfile($file);
        exit;
    }
    dm_page(404, 'DM//404', 'Asset não encontrado', '<p><code>' . htmlspecialchars($uri) . '</code></p>');
}

// sw.js NUNCA pode ser cacheado (nem pela Cloudflare): o service worker
// precisa ver bytes novos pra se atualizar. Cache de CDN no sw.js = PWA
// travado na versão velha pra sempre.
if ($uri === '/sw.js') {
    $f = __DIR__ . '/sw.js';
    if (is_file($f)) {
        header('Content-Type: application/javascript; charset=utf-8');
        header('Cache-Control: no-cache, no-store, must-revalidate');
        header('Content-Length: ' . (string) filesize($f));
        readfile($f);
        exit;
    }
}

// login.css — folha isolada do login (v2.0+). Carregada APENAS pelo
// login.html. Cache curto pra iterar rápido sem purgar Cloudflare.
if ($uri === '/login.css') {
    $f = __DIR__ . '/login.css';
    if (is_file($f)) {
        header('Content-Type: text/css; charset=utf-8');
        header('Cache-Control: public, max-age=300');
        header('Content-Length: ' . (string) filesize($f));
        readfile($f);
        exit;
    }
}

if ($uri !== '' && $uri !== '/') {
    $file = realpath(__DIR__ . $uri);
    $root = realpath(__DIR__);
    if ($file !== false && str_starts_with($file, $root) && is_file($file)) {
        return false; // deixa o built-in server servir/executar o arquivo
    }
}

// Qualquer outro caminho: 404 do próprio PHP built-in server
return false;
