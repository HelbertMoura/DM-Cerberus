---
titulo: Deploy Status — Hub Remoto (Fase 1 ativa)
tags: [deploy, status, urls, credenciais, hub, code-server]
atualizado: 2026-08-22
status: ativo
---

# 🌐 Deploy Status — Hub Remoto

> **Status:** ✅ Fase 1 deployada e funcionando · 22/08/2026 21:45 · watchdogs Windows+Rocky ativos em 23/08/2026

---

## 🔗 URLs de acesso

| Serviço | URL | Backend |
|---|---|---|
| **Hub Login (mockup)** | https://hub.devmaniacs.com.br/login.html | PHP built-in server local :8766 |
| **Hub Dashboard** | https://hub.devmaniacs.com.br/dashboard.html | Mesmo |
| **Code-server (VSCode web)** | https://code.devmaniacs.com.br/login | Rocky Linux :8766 (Caddy + code-server) |
| **Code-server direto** | https://code.devmaniacs.com.br/ | Redireciona pra /login |

---

## 🔐 Credenciais

### Code-server (https://code.devmaniacs.com.br)

```
Usuário: (não tem usuário — só senha)
Senha:   stnkPHjZIi9A@RSB
```

### PostgreSQL (Hub audit log)

```
Host:     192.168.226.103:5432 (interno — só network)
Database: hub_dm
User:     hub_admin
Password: Y4M2zimX34f1NNUigkPgoVVt
```

⚠️ **Senhas só no `.env` do Rocky** (chmod 600). NUNCA commitadas.

---

## �️ Containers Docker no Rocky

```bash
ssh -p 2222 root@127.0.0.1 'cd /opt/sistemas/hub-remote && docker compose ps'
```

| Container | Imagem | Porta interna | Status |
|---|---|---|---|
| `hub-postgres` | postgres:16-alpine | 5432 | ✅ healthy |
| `hub-code-server` | linuxserver/code-server:latest | 8443 | ✅ running |
| `hub-caddy` | caddy:2-alpine | 8080 → 8766 host | ✅ running |

---

## 🌐 Tunnels Cloudflare ativos

| Tunnel | ID | Hostname | Service |
|---|---|---|---|
| `dm-hub` | `2aa6cd77-13a6-42d4-ab7f-390f5bde7e86` | hub.devmaniacs.com.br | http://127.0.0.1:8766 (Windows local) |
| `dm-code` | `09d80a67-711d-4546-a54c-99f9bb7c911b` | code.devmaniacs.com.br | http://192.168.226.103:8766 (Rocky) |

**Por que 2 tunnels separados?**
- `dm-hub` roda no Windows (mockup + login UI)
- `dm-code` roda no Windows mas roteia pro Rocky
- Separados facilita gerenciar e isolar problemas

---

## 📱 Como testar no celular

### 1. Hub (mockup com brand)
1. Abre **https://hub.devmaniacs.com.br/login.html** no celular
2. Vê a tela de login com mascote Dev Maniac's à esquerda
3. Botão **🔵 Entrar com Google** (mockup — não funciona ainda)
4. Form e-mail/senha abaixo do divider
5. **(iPhone Safari)** Compartilhar → "Adicionar à Tela de Início" → instala como app
6. **(Android Chrome)** Menu (⋮) → "Instalar app"

### 2. Code-server (VSCode real)
1. Abre **https://code.devmaniacs.com.br/login**
2. Cola a senha: `stnkPHjZIi9A@RSB`
3. VSCode abre com workspace padrão
4. Pode navegar pra `/opt/sistemas/<seu-projeto>` direto pelo terminal integrado

---

## 🧪 Validação realizada

| Teste | Status |
|---|---|
| `curl https://hub.devmaniacs.com.br/login.html` | ✅ HTML com brand oficial |
| `curl https://hub.devmaniacs.com.br/dashboard.html` | ✅ Hub 3 IDEs |
| `curl https://hub.devmaniacs.com.br/manifest.webmanifest` | ✅ PWA válido |
| `curl https://hub.devmaniacs.com.br/sw.js` | ✅ Service Worker |
| `curl https://code.devmaniacs.com.br/` | ✅ 302 → /login |
| `curl https://code.devmaniacs.com.br/login` | ✅ 200 (VSCode login) |
| Docker compose up (Rocky) | ✅ 3 containers healthy |
| Tunnel dm-hub conectado | ✅ 4 QUIC connections |
| Tunnel dm-code conectado | ✅ 4 QUIC connections |

---

## 📋 Próximos passos

### Quando você validar visualmente:

- ✅ Login mockup bonito? → OK, segue
- 🔧 Algo ajustar? → me fala
- 🟑 Google OAuth real → **código deployado 23/08** (PHP puro, `mockup/router.php`); colar Client ID/Secret no `mockup/config.php` pra ligar
- 🎨 PWA instalável no celular → testar "Adicionar à tela inicial"
- 📱 Login no code-server funciona? → testar VSCode real

### Backlog

- [ ] Criar projeto OAuth no Google Cloud Console
- [ ] Trocar `127.0.0.1:8766` no tunnel `dm-hub` pra Rocky direto
- [ ] Subir Fase 2 (Guacamole RDP/VNC web)
- [ ] Bridge Antigravity 2.0 via CDP (Fase 3)
- [ ] Backup automático do `/opt/sistemas/hub-remote/`

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026 21:45
