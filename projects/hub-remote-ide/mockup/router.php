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
// Rotas de autenticação
// =============================================================

if ($uri === '/auth/google' && $method === 'GET') {
    dm_session_start();

    if (!dm_creds_ok($config)) {
        dm_page(503, 'DM//AUTH · SETUP PENDENTE', 'Google OAuth ainda não configurado',
            '<p>As credenciais do Google Cloud Console não foram preenchidas.</p>'
            . '<p>1. Copie <code>mockup/config.example.php</code> para <code>mockup/config.php</code> (se ainda não existir).<br>'
            . '2. Preencha <code>google_client_id</code> e <code>google_client_secret</code>.</p>'
            . '<p>Redirect URI que deve estar cadastrado no Google:<br>'
            . '<code>https://hub.devmaniacs.com.br/api/auth/callback/google</code></p>'
            . '<p><a href="/login.html">← Voltar ao login</a></p>');
    }

    // state anti-CSRF
    $_SESSION['oauth_state'] = bin2hex(random_bytes(16));
    dm_audit('oauth_start');

    $params = [
        'client_id'     => $config['google_client_id'],
        'redirect_uri'  => $config['redirect_uri'],
        'response_type' => 'code',
        'scope'         => 'openid email profile',
        'state'         => $_SESSION['oauth_state'],
        'prompt'        => 'select_account',
    ];
    header('Location: https://accounts.google.com/o/oauth2/v2/auth?' . http_build_query($params));
    exit;
}

if ($uri === '/api/auth/callback/google' && $method === 'GET') {
    dm_session_start();

    // Google devolve ?error= quando o usuário cancela o consentimento
    if (isset($_GET['error'])) {
        dm_audit('oauth_denied_by_user', ['error' => (string) $_GET['error']]);
        dm_page(400, 'DM//AUTH · CANCELADO', 'Login cancelado no Google',
            '<p>O consentimento foi negado: <code>' . htmlspecialchars((string) $_GET['error']) . '</code></p>'
            . '<p><a href="/login.html">← Tentar de novo</a></p>');
    }

    $code  = (string) ($_GET['code'] ?? '');
    $state = (string) ($_GET['state'] ?? '');
    if ($code === '' || $state === '' || !hash_equals((string) ($_SESSION['oauth_state'] ?? ''), $state)) {
        dm_audit('oauth_state_mismatch');
        dm_page(400, 'DM//AUTH · STATE INVÁLIDO', 'Sessão de login expirada',
            '<p>O parâmetro <code>state</code> não confere (possível CSRF ou aba antiga).</p>'
            . '<p><a href="/login.html">← Recomeçar o login</a></p>');
    }
    unset($_SESSION['oauth_state']);

    if (!dm_creds_ok($config)) {
        dm_page(503, 'DM//AUTH · SETUP PENDENTE', 'Credenciais ausentes no callback',
            '<p>Preencha <code>mockup/config.php</code> e tente novamente.</p>');
    }

    // Troca code → tokens (backchannel server→Google via TLS)
    $ch = curl_init('https://oauth2.googleapis.com/token');
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query([
            'code'          => $code,
            'client_id'     => $config['google_client_id'],
            'client_secret' => $config['google_client_secret'],
            'redirect_uri'  => $config['redirect_uri'],
            'grant_type'    => 'authorization_code',
        ]),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
        CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
    ]);
    $raw  = curl_exec($ch);
    $err  = curl_error($ch);
    $http = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);

    if ($raw === false || $http !== 200) {
        dm_audit('oauth_token_exchange_failed', ['http' => $http, 'curl_err' => $err]);
        dm_page(502, 'DM//AUTH · FALHA NO TOKEN', 'Não foi possível trocar o código pelo token',
            '<p>Google respondeu HTTP <code>' . $http . '</code>' . ($err ? ' · cURL: <code>' . htmlspecialchars($err) . '</code>' : '') . '</p>'
            . '<p>Detalhe: <code>' . htmlspecialchars(mb_substr((string) $raw, 0, 300)) . '</code></p>'
            . '<p><a href="/login.html">← Tentar de novo</a></p>');
    }

    $tokens  = json_decode((string) $raw, true);
    $payload = dm_jwt_payload((string) ($tokens['id_token'] ?? ''));

    // id_token veio direto do endpoint do Google via TLS — validamos campos-chave.
    if (!is_array($payload)) {
        dm_audit('oauth_idtoken_invalid');
        dm_page(502, 'DM//AUTH · TOKEN INVÁLIDO', 'id_token não pôde ser lido', '<p>Tente novamente.</p>');
    }
    $issOk = in_array($payload['iss'] ?? '', ['accounts.google.com', 'https://accounts.google.com'], true);
    $audOk = hash_equals((string) ($payload['aud'] ?? ''), (string) $config['google_client_id']);
    if (!$issOk || !$audOk || ($payload['exp'] ?? 0) < time()) {
        dm_audit('oauth_idtoken_checks_failed', ['iss_ok' => $issOk, 'aud_ok' => $audOk]);
        dm_page(502, 'DM//AUTH · TOKEN REJEITADO', 'id_token falhou na validação (iss/aud/exp)', '<p>Tente novamente.</p>');
    }

    $email = strtolower((string) ($payload['email'] ?? ''));
    if (empty($payload['email_verified']) || $email === '') {
        dm_audit('oauth_email_not_verified', ['email' => $email]);
        dm_page(403, 'DM//AUTH · E-MAIL', 'Conta Google sem e-mail verificado', '<p>Use uma conta com e-mail verificado.</p>');
    }

    // Allowlist — só entra quem está na lista do config.php
    $allowed = array_map('strtolower', (array) ($config['allowed_emails'] ?? []));
    if (!in_array($email, $allowed, true)) {
        dm_audit('login_denied_not_in_allowlist', ['email' => $email]);
        dm_page(403, 'DM//AUTH · ACESSO NEGADO', 'Esta conta não tem acesso ao Hub',
            '<p>E-mail autenticado: <code>' . htmlspecialchars($email) . '</code></p>'
            . '<p>Se deve ter acesso, adicione-o em <code>allowed_emails</code> no <code>mockup/config.php</code>.</p>');
    }

    // Sessão de sucesso
    session_regenerate_id(true);
    $_SESSION['user'] = [
        'email'     => $email,
        'name'      => $payload['name']      ?? $email,
        'picture'   => $payload['picture']   ?? null,
        'google_sub'=> $payload['sub']       ?? null,
        'method'    => 'google',
        'login_at'  => gmdate('c'),
    ];
    dm_audit('login_google', ['email' => $email]);

    // SSO Hub → Code-server: emite cookie assinado (HMAC-SHA256) válido
    // pra *.devmaniacs.com.br — o Caddy do Rocky valida via forward_auth.
    $ssoSecret = (string) ($config['sso_secret'] ?? '');
    if ($ssoSecret !== '' && !str_starts_with($ssoSecret, 'PASTE-')) {
        $exp     = time() + 8 * 3600;
        $payload = rtrim(strtr(base64_encode(json_encode(['email' => $email, 'exp' => $exp])), '+/', '-_'), '=');
        $sig     = rtrim(strtr(base64_encode(hash_hmac('sha256', $payload, $ssoSecret, true)), '+/', '-_'), '=');
        setcookie('dm_sso', $payload . '.' . $sig, [
            'expires'  => $exp,
            'path'     => '/',
            'domain'   => '.devmaniacs.com.br', // vale pro code.devmaniacs.com.br
            'secure'   => true,
            'httponly' => true,
            'samesite' => 'Lax',               // mesmo site (eTLD+1) → enviado no iframe
        ]);
        dm_audit('sso_cookie_issued', ['email' => $email, 'exp' => $exp]);
    }

    header('Location: /hub.html');
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
// Estáticos (com guarda contra path traversal)
// =============================================================

if ($uri === '/') {
    header('Location: /login.html');
    exit;
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
