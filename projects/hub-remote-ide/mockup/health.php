<?php
// =============================================================
// Dev Maniac's Hub — proxy de health check
// Evita problemas de CORS testando endpoints cross-origin
// Uso: /health.php?target=code|theme|...
// =============================================================

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate');
header('Access-Control-Allow-Origin: *');

$target = $_GET['target'] ?? 'code';

switch ($target) {
    case 'code':
        $url = 'https://code.devmaniacs.com.br/healthz';
        break;
    case 'code-login':
        $url = 'https://code.devmaniacs.com.br/login';
        break;
    default:
        echo json_encode(['error' => 'unknown target']);
        exit;
}

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_NOBODY, false);

$body = curl_exec($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$time = curl_getinfo($ch, CURLINFO_TOTAL_TIME);
$error = curl_error($ch);
curl_close($ch);

echo json_encode([
    'target' => $target,
    'url' => $url,
    'status' => $status ?: 0,
    'time_ms' => round($time * 1000),
    'error' => $error ?: null,
    'body_preview' => substr($body, 0, 100),
], JSON_UNESCAPED_SLASHES);
