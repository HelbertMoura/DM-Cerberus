<?php
// =============================================================
// Dev Maniac's Hub — configuração do Google OAuth
// Copie para config.php e preencha com os valores do Google Cloud
// Console → APIs & Services → Credentials → OAuth 2.0 Client IDs
// (tipo "Web application"). config.php é gitignored.
// =============================================================

return [
    // OAuth Client ID (termina em .apps.googleusercontent.com)
    'google_client_id'     => 'PASTE-CLIENT-ID-HERE',

    // OAuth Client Secret (criado junto com o Client ID)
    'google_client_secret' => 'PASTE-CLIENT-SECRET-HERE',

    // Redirect URI EXATAMENTE igual ao cadastrado no Google Cloud:
    'redirect_uri'         => 'https://hub.devmaniacs.com.br/api/auth/callback/google',

    // Secret compartilhado do SSO Hub → Code-server.
    // Gere com: openssl rand -hex 32
    // Use o MESMO valor no SSO_SECRET do .env do Rocky.
    'sso_secret'           => 'PASTE-SSO-SECRET-HERE',

    // Allowlist — só estas contas Google podem entrar.
    // Hub é público na internet: NÃO remover.
    'allowed_emails'       => [
        'helbertcurcio@gmail.com',
    ],
];
