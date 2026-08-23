---
titulo: Setup Fase 1 — Code-server no Rocky Linux
tags: [setup, fase-1, code-server, rocky, docker, deploy, hub]
atualizado: 2026-08-22
status: ativo
servidor: 192.168.226.103 (Rocky Linux 10.2)
---

# 🚀 Setup Fase 1 — Code-server no Rocky Linux

> **Objetivo:** Subir `code-server` (VSCode web) no Rocky + conectar ao tunnel `hub.devmaniacs.com.br/code` → substituir mockup por IDE real.

---

## ✅ Pré-requisitos validados

- ✅ Rocky Linux 10.2 (Red Quartz) — `192.168.226.103`
- ✅ Docker 29.7.2 + Compose v5.4.0 instalados
- ✅ Diretório `/opt/sistemas/` já existe
- ✅ Acesso SSH via tunnel: `ssh -p 2222 root@127.0.0.1`

---

## 📋 Stack da Fase 1

| Serviço | Porta interna | Função | Imagem Docker |
|---|---|---|---|
| **code-server** | 8080 | VSCode web (substitui mockup) | `linuxserver/code-server:latest` |
| **postgres** | 5432 | Audit log + sessão + 2FA secrets | `postgres:16-alpine` |
| **caddy** | 80/443 | Reverse proxy + TLS (opcional, tunnel já faz) | `caddy:2-alpine` |

**Não precisa mais de mockup** — o code-server serve VSCode real no `/code`.

---

## 🔧 Setup (você executa via SSH no Rocky)

### 1. Criar estrutura

```bash
ssh -p 2222 root@127.0.0.1
mkdir -p /opt/sistemas/hub-remote/{code-server,postgres,caddy,config}
cd /opt/sistemas/hub-remote
```

### 2. Criar `docker-compose.yml`

```yaml
# /opt/sistemas/hub-remote/docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    container_name: hub-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: hub_dm
      POSTGRES_USER: hub_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-MUDE_ESSA_SENHA_FORTE}
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - hub-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hub_admin -d hub_dm"]
      interval: 30s
      timeout: 10s
      retries: 5

  code-server:
    image: linuxserver/code-server:latest
    container_name: hub-code-server
    restart: unless-stopped
    environment:
      PUID: 1000
      PGID: 1000
      TZ: America/Sao_Paulo
      DEFAULT_WORKSPACE: /config/workspace
    volumes:
      - ./code-server/config:/config
      - ./code-server/workspace:/config/workspace
      - /opt/sistemas:/opt/sistemas:rw  # acesso aos projetos
    networks:
      - hub-net
    depends_on:
      postgres:
        condition: service_healthy

  caddy:
    image: caddy:2-alpine
    container_name: hub-caddy
    restart: unless-stopped
    ports:
      - "8766:8080"  # tunnel Cloudflare aponta pra cá
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - hub-net
    depends_on:
      - code-server

networks:
  hub-net:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
```

### 3. Criar Caddyfile (opcional — se não usar tunnel direto)

```caddyfile
# /opt/sistemas/hub-remote/caddy/Caddyfile
:8080 {
  reverse_proxy code-server:8443
}

:8081 {
  reverse_proxy postgres:5432
}
```

### 4. Criar init.sql (audit log + tabelas)

```sql
-- /opt/sistemas/hub-remote/postgres/init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255),
    action VARCHAR(50) NOT NULL,  -- login, logout, open_ide, etc
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_email);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at DESC);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    totp_secret VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5. Subir a stack

```bash
cd /opt/sistemas/hub-remote
docker compose up -d
docker compose ps  # verificar que subiu
docker compose logs code-server  # ver logs
```

---

## 🌐 Conectar ao tunnel Cloudflare

### Atualizar config do tunnel `dm-hub` pra apontar pro Rocky

**Na sua máquina Windows:**

```bash
# Editar o config do tunnel
notepad "C:\Users\Helbert\.cloudflared\config.dm-hub.yml"
```

**Conteúdo novo:**

```yaml
tunnel: dm-hub
credentials-file: C:\Users\Helbert\.cloudflared\2aa6cd77-13a6-42d4-ab7f-390f5bde7e86.json

ingress:
  # Hub mockup (atual)
  - hostname: hub.devmaniacs.com.br
    path: /
    service: http://127.0.0.1:8766  # mockup local
  
  # Code-server no Rocky (NOVO)
  - hostname: code.devmaniacs.com.br
    service: http://192.168.226.103:8766
  
  - service: http_status:404
```

### Criar DNS pra code.devmaniacs.com.br

```bash
# Via API (que já funciona)
curl -X POST "https://api.cloudflare.com/client/v4/zones/77c99fbc1e785fd393551b5d771b4c59/dns_records" \
  -H "X-Auth-Email: helbertcurcio@gmail.com" \
  -H "X-Auth-Key: cfk_JxWo6pWWUiM2gF0JP7zvKhMaAGjgIh96YcO7hM2w4b9630c5" \
  -H "Content-Type: application/json" \
  --data '{"type":"CNAME","name":"code.devmaniacs.com.br","content":"2aa6cd77-13a6-42d4-ab7f-390f5bde7e86.cfargotunnel.com","proxied":true}'
```

**Resultado:**
- `https://hub.devmaniacs.com.br/` → mockup (login)
- `https://code.devmaniacs.com.br/` → VSCode web real (code-server)

---

## 🔐 Segurança

### Senha do code-server

```bash
# Gerar senha forte
openssl rand -hex 32
```

### Variáveis de ambiente

```bash
# /opt/sistemas/hub-remote/.env
POSTGRES_PASSWORD=cole-senha-forte-aqui
CODE_PASSWORD=$(openssl rand -hex 32)  # senha inicial do VSCode
```

### HTTPS

Já temos via Cloudflare Tunnel (TLS 1.3).

---

## 📱 Mobile UX

Quando você abre `https://code.devmaniacs.com.br/` no celular:

- ✅ VSCode adaptado pra mobile (touch-friendly)
- ✅ Touch keyboard funciona
- ✅ File explorer otimizado
- ✅ Terminal integrado funciona
- ✅ Extensions funcionam (vou pré-instalar as úteis)

### Extensions pré-instaladas (lista inicial)

```bash
# Dentro do code-server (terminal)
code-server --install-extension dbaeumer.vscode-eslint
code-server --install-extension esbenp.prettier-vscode
code-server --install-extension ms-python.python
code-server --install-extension rust-lang.rust-analyzer
code-server --install-extension vue.volar
code-server --install-extension bradlc.vscode-tailwindcss
code-server --install-extension ms-toolsai.datawrangler
```

---

## 🧪 Validação pós-deploy

```bash
# 1. Containers rodando?
docker compose ps

# 2. Code-server responde?
curl -I http://192.168.226.103:8766

# 3. Tunnel propaga?
curl -I https://code.devmaniacs.com.br

# 4. PostgreSQL ok?
docker exec hub-postgres pg_isready -U hub_admin
```

---

## 📊 Resumo da Fase 1

| Antes | Depois |
|---|---|
| Mockup HTML estático | VSCode web real |
| Sem terminal | Terminal integrado |
| Sem extensões | ESLint, Prettier, Python, Rust, etc |
| Sem acesso aos projetos | Acesso direto a `/opt/sistemas/` |
| Sem persistência | Audit log no PostgreSQL |

**Tempo total de deploy:** ~20 min (você executa os comandos acima).

---

## ⏭️ Próximas fases

- **Fase 2:** Adicionar Guacamole (RDP/VNC web) pra controlar os 3 IDEs
- **Fase 3:** Bridge Antigravity 2.0 via CDP (Chrome DevTools Protocol)

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
