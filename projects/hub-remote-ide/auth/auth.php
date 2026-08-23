<?php
// =============================================================
// Dev Maniac's Hub — Validador SSO (lado Rocky)
// Roda dentro do container `auth` (php:8.3-alpine) e é chamado pelo
// Caddy via forward_auth antes de proxyar o code-server.
//
// Valida o cookie `dm_sso` (emitido pelo Hub no login Google):
//   valor = base64url(json{email,exp}) . "." . base64url(hmac_sha256)
//   secret compartilhado: SSO_SECRET (env, mesmo valor do hub config.php)
//
// Respostas:
//   cookie válido   → 200 (Caddy deixa passar)
//   ausente/inválido → 302 pro login do Hub
// =============================================================

$secret = (string) (getenv('SSO_SECRET') ?: '');
$login  = 'https://hub.devmaniacs.com.br/login.html?next=code';

function b64url_decode(string $s): string {
    return base64_decode(strtr($s, '-_', '+/'));
}

$cookie = (string) ($_COOKIE['dm_sso'] ?? '');

if ($secret !== '' && $cookie !== '' && substr_count($cookie, '.') === 1) {
    [$payload, $sig] = explode('.', $cookie, 2);
    $expect = hash_hmac('sha256', $payload, $secret, true);
    if (hash_equals($expect, b64url_decode($sig))) {
        $data = json_decode(b64url_decode($payload), true);
        if (is_array($data) && ($data['exp'] ?? 0) > time()) {
            http_response_code(200);
            header('X-DM-User: ' . rawurlencode((string) ($data['email'] ?? '')));
            exit;
        }
    }
}

// Sem cookie válido → manda pro login do Hub (identidade Dev Maniac's)
http_response_code(302);
header('Location: ' . $login);
exit;
