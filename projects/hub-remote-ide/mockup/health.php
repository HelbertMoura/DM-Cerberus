<?php
// =============================================================
// Dev Maniac's Hub — proxy de health check
// Evita problemas de CORS testando endpoints cross-origin
// Uso: /health.php?target=code|sso|...
// =============================================================

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate');
header('Access-Control-Allow-Origin: *');

$target = $_GET['target'] ?? 'code';
$follow = true;

switch ($target) {
    case 'code':
        $url = 'https://code.devmaniacs.com.br/healthz';
        break;
    case 'sso':
        // Sem cookie dm_sso, o Caddy manda 302 pro login do Hub —
        // esse é exatamente o comportamento ESPERADO do SSO.
        $url = 'https://code.devmaniacs.com.br/';
        $follow = false;
        break;
    default:
        echo json_encode(['error' => 'unknown target']);
        exit;
}

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, $follow);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_NOBODY, false);

$body = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$redirect = curl_getinfo($ch, CURLINFO_REDIRECT_URL);
$time = curl_getinfo($ch, CURLINFO_TOTAL_TIME);
$error = curl_error($ch);
curl_close($ch);

echo json_encode([
    'target' => $target,
    'url' => $url,
    'status' => $status ?: 0,
    'redirect' => $redirect ?: null,
    'time_ms' => round($time * 1000),
    'error' => $error ?: null,
    'body_preview' => substr((string) $body, 0, 100),
], JSON_UNESCAPED_SLASHES);
