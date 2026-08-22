---
titulo: Arquitetura — Hub Remoto IDEs
tags: [arquitetura, hub, ide, pwa, devmaniacs, code-server, guacamole, cdp]
atualizado: 2026-08-22
status: ativo
---

# 🏗️ Arquitetura — Hub Remoto de IDEs

> Diagrama, componentes e decisões técnicas.

---

## 📐 Diagrama Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                        📱 / 💻 / 🖥️ CLIENTE                         │
│              (Celular, Tablet, Notebook, PC do escritório)         │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │         🌐 PWA: hub.devmaniacs.com.br (Next.js)           │     │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐  │     │
│   │  │ Login + │→ │  Hub    │→ │ Dashboard 3 IDEs        │  │     │
│   │  │ 2FA     │  │ Principal│ │ ┌──────┬──────┬──────┐  │  │     │
│   │  └─────────┘  └─────────┘ │ │Gemini│ │ M3  │ │Z.AI │  │  │     │
│   │                              │ │ 🖥️  │ │ 🖥️  │ │ 🖥️  │  │  │     │
│   │                              │ └──────�──────┴──────┘  │  │     │
│   │                              └─────────────────────────┘  │     │
│   └──────────────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTPS (Cloudflare)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│               ☁️ CLOUDFLARE TUNNEL (já ativo)                       │
│         hub.devmaniacs.com.br → 192.168.226.103:3000                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│            🖥️ ROCKY LINUX 10 (192.168.226.103)                      │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  🐳 Docker Compose: hub-stack                            │     │
│   │                                                           │     │
│   │  ┌─────────────────┐  ┌──────────────────────────────┐  │     │
│   │  │ 🔐 Auth Service │  │ � PWA Frontend (Next.js)    │  │     │
│   │  │ (Node.js 22)    │  │ :3000                        │  │     │
│   │  │ :3001           │  │ Hub + iframe dos IDEs        │  │     │
│   │  └────────┬────────┘  └──────────────────────────────┘  │     │
│   │           │                                              │     │
│   │  ┌────────▼────────────────────────────────────────┐    │     │
│   │  │ 🐘 PostgreSQL 16 (já existe)                    │    │     │
│   │  │ db: dm_hub (sessões, audit, users)               │    │     │
│   │  └─────────────────────────────────────────────────┘    │     │
│   │                                                           │     │
│   │  ┌─────────────────────────────────────────────────┐    │     │
│   │  │ 🖥️ IDEs (cada um em container próprio)           │    │     │
│   │  │                                                   │    │     │
│   │  │  ┌────────────────�  ┌────────────────┐         │    │     │
│   │  │  │ ♊️ Antigravity  │  │ 🚀 MiniMax Code│         │    │     │
│   │  │  │    2.0          │  │    (Mavis)     │         │    │     │
│   │  │  │ :8443           │  │ :8444          │         │    │     │
│   │  │  │ CDP bridge      │  │ headless       │         │    │     │
│   │  │  └────────────────┘  └────────────────┘         │    │     │
│   │  │                                                   │    │     │
│   │  │  ┌────────────────┐  ┌────────────────┐         │    │     │
│   │  │  │ 🧠 Z.AI Code    │  │ � code-server │         │    │     │
│   │  │  │   (web oficial) │  │  (VSCode web)  │         │    │     │
│   │  │  │ :8445           │  │ :8446          │         │    │     │
│   │  │  │ iframe direto   │  │ Microsoft      │         │    │     │
│   │  │  └────────────────┘  └────────────────┘         │    │     │
│   │  └───────────────────────────────────────────────────┘    │     │
│   └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│            🏠 DESKTOP HELBERT (Windows)                             │
│                                                                     │
│   Antigravity 2.0 ──┐                                               │
│   MiniMax Code ─────┼──→ Cloudflared SSH Tunnel                     │
│   Z.AI Code ────────┘    (ssh.devmaniacs.com.br)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## � Fluxo de Acesso (celular → IDE)

```
1. 📱 Usuário abre hub.devmaniacs.com.br
   ↓
2. 🔐 Login (email + senha)
   ↓
3. 📱 Escaneia QR (2FA TOTP) no Google Authenticator
   ↓
4. 🎫 JWT salvo em cookie httpOnly (8h)
   ↓
5. �️ Dashboard mostra 3 cards (Gemini, M3, Z.AI)
   - Status online/offline (heartbeat a cada 30s)
   - Sessão ativa (se alguma)
   - Última atividade
   ↓
6. 👆 Toque em "Conectar"
   ↓
7. 🔌 Backend valida JWT + cria sessão
   ↓
8. 🪟 Abre iframe/WebSocket com IDE remoto
   - code-server: WebSocket direto
   - Antigravity: CDP via WebSocket proxy
   - Outros: noVNC
   ↓
9. ⌨️ Teclado/touch enviado via WebSocket
   ↓
10. 🖥️ Resposta renderizada no iframe
```

---

## 🔌 Componentes Detalhados

### 1. Auth Service (Node.js + Fastify)

```typescript
// Endpoints
POST /auth/login          { email, password } → { requires2FA: true, tempToken }
POST /auth/2fa            { tempToken, totpCode } → { jwt, expiresIn: 28800 }
POST /auth/logout         (revoga JWT)
GET  /auth/me             (dados do user logado)
POST /auth/refresh        (renova JWT)

// Stack
- Argon2id pra hash de senha
- jsonwebtoken + jose pra JWT
- otplib pra TOTP (compatível Google Authenticator)
- Cookie httpOnly + SameSite=Strict
```

### 2. PWA Frontend (Next.js 15)

```typescript
// Páginas
/                    → Login
/dashboard           → Hub com 3 cards
/ide/[name]          → Iframe do IDE específico
/settings            → 2FA setup, devices, audit

// Componentes principais
<IdeCard status="online|offline|working" />
<ClipboardSync />    // copia celular → PC
<NotificationPush /> // service worker
<AuditLog />         // histórico de acessos
```

### 3. code-server (VSCode web)

```yaml
# docker-compose.yml (trecho)
code-server:
  image: linuxserver/code-server:4.96
  container_name: dm-codeserver
  ports:
    - "8446:8443"
  environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Sao_Paulo
  volumes:
    - ~/projetos:/config/projects
    - ~/.config/code-server:/config
  restart: unless-stopped
```

### 4. Antigravity 2.0 (CDP Bridge)

```bash
# Iniciar com debug remoto
antigravity.exe --remote-debugging-port=9222 --user-data-dir=/tmp/ag-profile

# Bridge Node.js
const CDP = require('chrome-remote-interface');
const client = await CDP({ port: 9222 });
// captura screenshots, envia input, lê console
```

### 5. Apache Guacamole (Z.AI + MiniMax Code)

```yaml
guacamole:
  image: guacamole/guacamole:1.5.5
  container_name: dm-guac
  ports:
    - "8447:8080"
  environment:
    - GUACD_HOSTNAME=guacd
  depends_on:
    - guacd
    - postgres

guacd:
  image: guacamole/guacd:1.5.5
  container_name: dm-guacd
```

---

## 💾 Banco de Dados

```sql
-- Schema: dm_hub

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,        -- Argon2id
  totp_secret TEXT,                   -- 2FA
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,
  enabled BOOLEAN DEFAULT true
);

CREATE TABLE sessions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  jwt_jti VARCHAR(255) UNIQUE,        -- JWT ID
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT false
);

CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  action VARCHAR(50) NOT NULL,        -- login, logout, ide_connect, ide_disconnect, etc
  ide_name VARCHAR(50),               -- gemini, m3, zai, codeserver
  ip_address INET,
  user_agent TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_sessions_user ON sessions(user_id, expires_at DESC);
```

---

## 🔐 Segurança — Camadas

| Camada | Implementação |
|---|---|
| **Transport** | HTTPS obrigatório (Cloudflare Tunnel) |
| **Auth** | Email + senha (Argon2id) + 2FA TOTP |
| **JWT** | RS256, expira 8h, rotação por sessão |
| **Cookie** | httpOnly, Secure, SameSite=Strict |
| **Rate limit** | 5 tentativas/min por IP (fail2ban) |
| **Audit** | Tudo em PostgreSQL com retention 90 dias |
| **IP allowlist** | Opcional (se Helbert quiser) |
| **CSP** | strict-dynamic, no unsafe-inline |

---

## 📊 Decisões (ADRs)

### ADR-005: code-server como IDE padrão na Fase 1
- **Contexto:** 3 IDEs diferentes, todos exigem bridge complexo
- **Decisão:** Fase 1 usa só code-server (VSCode web) — 10 min setup
- **Consequência:** MVP rápido, depois expande pra Z.AI + M3 + Antigravity

### ADR-006: PostgreSQL 16 (já existe) pra sessões + audit
- **Contexto:** Não criar dependência nova
- **Decisão:** Usar schema `dm_hub` no PostgreSQL existente
- **Consequência:** Zero infra nova, backup automático incluso

### ADR-007: Docker Compose pra stack completa
- **Contexto:** Portabilidade entre Rocky dev e prod
- **Decisão:** 1 docker-compose.yml com todos os serviços
- **Consequência:** `docker compose up -d` sobe tudo

### ADR-008: Auth.js + TOTP (não SMS)
- **Contexto:** Canteiro de obra, sem rede celular confiável
- **Decisão:** TOTP via Google Authenticator (offline-first)
- **Consequência:** 2FA funciona sem SMS

---

## 🔗 Links Externos

- code-server: https://github.com/coder/code-server
- Apache Guacamole: https://guacamole.apache.org/
- CDP: https://chromedevtools.github.io/devtools-protocol/
- Auth.js: https://authjs.dev/
- otplib: https://github.com/yeojz/otplib

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
