<?php
// =============================================================
// Dev Maniac's Hub — DB connection helper
// SQLite local (zero infra) — 1 arquivo, 1 usuário, sem rede.
//
// Por que SQLite e não Postgres:
// - Você é o único usuário do Hub (allowlist = 1 email)
// - Volume de login = 1-2 por dia
// - Sem Docker/tunnel/senha/auth pra quebrar
// - Backup = cp hub.sqlite backup.db
// - Funciona IMEDIATAMENTE
//
// Path: mockup/data/hub.sqlite (gitignored)
// =============================================================

declare(strict_types=1);

function dm_db_path(): string {
    $dir = __DIR__ . '/data';
    if (!is_dir($dir)) @mkdir($dir, 0777, true);
    return $dir . '/hub.sqlite';
}

function dm_pg_connect(): PDO {
    // SQLite — não tem como confundir
    $path = dm_db_path();
    $pdo = new PDO('sqlite:' . $path, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);

    // PRAGMAs essenciais pro nosso caso
    $pdo->exec('PRAGMA journal_mode = WAL;');        // leitura concorrente com escrita
    $pdo->exec('PRAGMA foreign_keys = ON;');          // respeitar FK
    $pdo->exec('PRAGMA busy_timeout = 5000;');       // espera até 5s se locked

    // Migration on-first-connect (cria schema se não existir)
    dm_migrate($pdo);
    return $pdo;
}

function dm_migrate(PDO $pdo): void {
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password_hash TEXT,
            totp_secret TEXT,
            backup_codes TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            last_login TEXT,
            last_ip TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    ");
    // Migração leve: adicionar coluna `email` se não existir (versão pré-email)
    $cols = $pdo->query("PRAGMA table_info(users)")->fetchAll(PDO::FETCH_COLUMN, 1);
    if (!in_array('email', $cols, true)) {
        $pdo->exec("ALTER TABLE users ADD COLUMN email TEXT");
        $pdo->exec("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)");
    }
    if (!in_array('backup_codes', $cols, true)) {
        $pdo->exec("ALTER TABLE users ADD COLUMN backup_codes TEXT");
    }

    $pdo->exec("
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            user_agent TEXT,
            ip_address TEXT,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)");

    $pdo->exec("
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_email TEXT,
            action TEXT NOT NULL,
            target TEXT,
            ip_address TEXT,
            user_agent TEXT,
            metadata TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    ");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at DESC)");
    $pdo->exec("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)");
}

/** Wrapper de audit_log — mesmo nome do helper antigo pra não mudar auth.php */
if (!function_exists('dm_audit_log')) {
    function dm_audit_log(string $action, ?string $email, string $ip, string $ua, array $metadata = []): void {
    try {
        $pdo = dm_pg_connect();
        $stmt = $pdo->prepare(
            "INSERT INTO audit_log (user_email, action, target, ip_address, user_agent, metadata)
             VALUES (?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([
            $email,
            $action,
            $email,
            $ip !== '' ? $ip : null,
            $ua,
            $metadata ? json_encode($metadata, JSON_UNESCAPED_SLASHES) : null,
        ]);
    } catch (Throwable $e) {
        // Falha de audit não bloqueia login — loga em arquivo local
        $line = json_encode([
            'ts' => gmdate('c'),
            'action' => $action,
            'email' => $email,
            'ip' => $ip,
            'ua' => $ua,
            'metadata' => $metadata,
            'error' => $e->getMessage(),
        ]) . "\n";
        @file_put_contents(__DIR__ . '/logs/audit-fallback.jsonl', $line, FILE_APPEND | LOCK_EX);
    }
    }
}