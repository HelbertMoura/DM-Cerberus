---
titulo: Hub Remoto de IDEs — Documentação Técnica Completa
tags: [hub-remote-ide, documentacao, arquitetura, devmaniacs, code-server, oauth, pwa, tunnels, fase-1]
atualizado: 2026-08-23
status: ativo
versao: 1.0.0
autor: Hermes Agent (DM-Cerebro)
---

# 🏛 Hub Remoto de IDEs — Documentação Técnica Completa

> **Projeto:** `hub-remote-ide` — Hub web unificado pra acessar Gemini, MiniMax M3, Z.AI e Antigravity 2.0 remotamente, com SSO, PWA, tema Dev Maniac's e 2FA.
>
> **Empresa:** Dev Maniac's Systems · **Owner:** Helbert Moura
>
> **Data:** 22/08/2026 (criação) → 23/08/2026 (Fase 1 deployada)
>
> **Localização:** `C:\Users\Helbert\Desktop\DM-Cerebro\projects\hub-remote-ide\`

---

## 📑 Índice

1. [Visão geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Estrutura de pastas (cada arquivo)](#3-estrutura-de-pastas)
4. [Stack técnica](#4-stack-técnica)
5. [URLs e domínios](#5-urls-e-domínios)
6. [Tunnels Cloudflare](#6-tunnels-cloudflare)
7. [Infraestrutura Docker no Rocky](#7-infraestrutura-docker-no-rocky)
8. [Identidade visual Dev Maniac's](#8-identidade-visual-dev-maniacs)
9. [Tema VSCode (Dev Maniac's Dark/Light)](#9-tema-vscode)
10. [PWA — Instalação mobile](#10-pwa)
11. [Autenticação](#11-autenticação)
12. [Status do projeto por fase](#12-status-do-projeto-por-fase)
13. [Comandos úteis](#13-comandos-úteis)
14. [Erros conhecidos e como resolver](#14-erros-conhecidos)
15. [Backlog e próximos passos](#15-backlog)
16. [Glossário](#16-glossário)

---

## 1. Visão geral

### O que é
Hub web único (em `hub.devmaniacs.com.br`) que serve como ponto central pra acessar 3 IDEs locais da Helbert (Antigravity 2.0, MiniMax Code, Z.AI) e um VSCode remoto (code-server), de qualquer lugar — PC, celular, tablet.

### Por que existe
- Helbert trabalha em canteiro de obras, longe da máquina Windows
- Precisa ver/controlar os 3 IDEs que rodam no Windows + Rocky
- Quer **1 URL só** pra tudo (não 4 URLs separadas)
- Quer **login único** (Google OAuth) e **SSO** entre Hub e code-server
- Quer instalar como **PWA** no celular (ícone na tela inicial)

### Princípios
- **Mobile-first** — toda tela é projetada pra celular antes do desktop
- **Identidade oficial** — usa cores e tipografia extraídas de `devmaniacs.com.br`
- **Sem lock-in** — open-source (Apache 2.0 / MIT), self-hosted
- **Zero custo** — todas ferramentas usadas são gratuitas
- **Audit completo** — PostgreSQL registra toda ação

---

## 2. Arquitetura

### Diagrama (3 camadas)

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA 1 — CLIENTE                       │
│  📱 iOS Safari  📱 Android Chrome  💻 Chrome/Edge           │
│                                                             │
│  Abre: https://hub.devmaniacs.com.br                       │
│  Vê: login mockup → Google OAuth → Hub com iframe          │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTPS (TLS 1.3)
┌─────────────────────────────────────────────────────────────┐
│               CAMADA 2 — CLOUDFLARE EDGE                    │
│                                                             │
│  DNS: hub.devmaniacs.com.br + code.devmaniacs.com.br        │
│  Proxy: WAF + DDoS protection + Cache                      │
│  Tunnel: 2 tunnels named (dm-hub, dm-code)                │
└─────────────────────────────────────────────────────────────┘
                ↓                          ↓
    ┌───────────────────┐        ┌───────────────────────┐
    │   dm-hub tunnel   │        │    dm-code tunnel     │
    │   (Windows local) │        │    (Rocky 192.168     │
    │                   │        │     .226.103:8766)    │
    └────────┬──────────┘        └──────────┬────────────┘
             ↓                              ↓
    ┌─────────────────┐         ┌──────────────────────┐
    │  PHP -S :8766    │         │   Docker Compose     │
    │  (mockup HTML)  │         │   no Rocky           │
    │                 │         │                      │
    │  /login.html    │         │  ┌────────────────┐  │
    │  /hub.html      │         │  │ hub-caddy:8080 │  │
    │  /status.html   │         │  │   ↓            │  │
    │  /manifest.*    │         │  │ hub-code-srv   │  │
    │  /sw.js         │         │  │   :8443        │  │
    │  /health.php    │         │  └────────────────┘  │
    │  /styles.css    │         │  ┌────────────────┐  │
    │  /app.js        │         │  │ hub-postgres   │  │
    │  /assets/brand/ │         │  │   :5432        │  │
    └─────────────────┘         │  └────────────────┘  │
                                └──────────────────────┘
```

### Fluxo de login (Fase 1, com mockup)

```
Usuário acessa hub.devmaniacs.com.br/login.html
        ↓
Vê: mascote Dev Maniac's + botão Google (único método — form e-mail/senha removido 23/08)
        ↓
Botão Google → /auth/google → Google consent → /api/auth/callback/google
(🟡 implementado; liga de vez ao preencher mockup/config.php)
        ↓
Só helbertcurcio@gmail.com passa (allowlist do config.php — demais contas: página de acesso negado + audit)
        ↓
hub.html abre iframe do code.devmaniacs.com.br SEM senha (cookie SSO dm_sso)
        ↓
iframe carrega VSCode com tema Dev Maniac's Dark
```

---

## 3. Estrutura de pastas

```
C:\Users\Helbert\Desktop\DM-Cerebro\projects\hub-remote-ide\
│
├── README.md                          ← visão geral do projeto
├── identidade-visual.md               ← paleta + tipografia + mascote
├── arquitetura.md                     ← diagrama detalhado + ADRs
├── config-modelos.md                  ← modelo padrão MiniMax M3 + GLM manual
├── invocacao-manual-glm.md            ← como usar GLM 5.3 on-demand
├── auth-seguranca.md                  ← Google OAuth + TOTP + 2FA docs
├── setup-fase-1.md                    ← comandos SSH pro Rocky (8 KB)
├── watchdog-hub.md                    ← docs do script de monitoramento
├── DEPLOY-STATUS.md                   ← status atual + URLs + credenciais
├── docker-compose.yml                 ← stack completa Fase 1
├── .env.example                       ← template de env vars
├── .env.fase1.example                 ← template específico Fase 1
├── .gitignore                         ← ignora .env, node_modules, etc
│
├── caddy/
│   └── Caddyfile                      ← reverse proxy + CORS headers
│
├── scripts/
│   └── rocky/                         ← watchdog do Rocky (versionado)
│       ├── watchdog-rocky.sh          ← check healthz + recupera stack
│       ├── dm-hub-watchdog.service    ← systemd unit (oneshot)
│       └── dm-hub-watchdog.timer      ← systemd timer (5 min)
│
├── postgres/
│   └── init.sql                       ← schema (users, sessions, audit_log)
│
├── dev-maniacs-theme/                 ← tema VSCode oficial
│   ├── package.json                   ← manifesto da extensão
│   └── themes/
│       ├── dev-maniacs-light.json     ← tema claro (paper background)
│       └── dev-maniacs-dark.json      ← tema escuro (navy background)
│
├── assets/brand/                      ← logos extraídos do site oficial
│   ├── dev-maniacs-mark.png           ← logo principal
│   ├── dev-maniacs-mascot.webp        ← mascote Helbert
│   ├── dev-maniacs-social-card.png    ← social card
│   └── devmaniacs-styles.css          ← CSS fonte (55 KB, baixado via curl)
│
└── mockup/                            ← interface web atual (PWA)
    ├── login.html                     ← tela de login (brand + Google OAuth btn)
    ├── dashboard.html                 ← hub antigo com cards IDE (legado)
    ├── hub.html                       ← hub novo unificado com iframe (atual)
    ├── status.html                    ← página de diagnóstico (5 checks)
    ├── styles.css                     ← identidade visual completa (22 KB)
    ├── app.js                         ← interações JS (toggle, login fake)
    ├── manifest.webmanifest           ← PWA manifest v2 (ícones reais, atalhos)
    ├── sw.js                          ← service worker v2 (offline + cache)
    ├── offline.html                   ← página offline da marca (auto-retry)
    ├── health.php                     ← proxy CORS pra checks (+target sso)
    └── serve.js                       ← servidor Node backup (não usado)
```

### Resumo por categoria

| Categoria | Arquivos | Tamanho total | Função |
|---|---|---|---|
| **Documentação** | 9 arquivos `.md` | ~50 KB | Decisões, arquitetura, runbooks |
| **Infraestrutura** | `docker-compose.yml`, `caddy/Caddyfile`, `postgres/init.sql`, `.gitignore`, `.env*` | ~12 KB | Stack Docker + config |
| **Identidade** | `assets/brand/*` + `mockup/styles.css` | ~100 KB | Logo, mascote, paleta |
| **Tema VSCode** | `dev-maniacs-theme/*` | ~7 KB | Tema oficial pro code-server |
| **Frontend** | `mockup/*.html` + `mockup/*.js` + `manifest.webmanifest` + `sw.js` | ~30 KB | UI completa + PWA |
| **Backend PHP** | `mockup/health.php` | ~1.4 KB | Proxy CORS pra status checks |
| **Backend Node** | `mockup/serve.js` | ~1 KB | Servidor estático alternativo |

---

## 4. Stack técnica

### Frontend (mockup atual)

| Item | Tecnologia | Versão | Por quê |
|---|---|---|---|
| HTML | HTML5 | — | Padrão web |
| CSS | CSS3 custom properties | — | Variáveis `--navy`, `--cyan`, etc |
| Fontes | Inter + JetBrains Mono | via Google Fonts + system fallback | Tipografia oficial Dev Maniac's |
| JavaScript | Vanilla ES6+ | — | Sem build step, sem framework |
| Service Worker | Web Workers API | — | PWA offline |
| Manifest | W3C Web App Manifest | — | PWA instalável |

### Backend (mockup)

| Item | Tecnologia | Versão | Por quê |
|---|---|---|---|
| Servidor estático | PHP built-in server | PHP 8.3 | Lida melhor com HEAD que Python |
| Proxy CORS | PHP + cURL | PHP 8.3 | Evita CORS no `status.html` |
| Server alternativo | Node.js + `serve.js` | Node 22 | Backup (CSPNG assertion failure em subprocess) |

### Backend (Fase 1 — code-server no Rocky)

| Item | Tecnologia | Versão | Por quê |
|---|---|---|---|
| Container runtime | Docker | 29.7.2 | Já instalado no Rocky |
| Compose | Docker Compose | v5.4.0 | Stack multi-container |
| VSCode Web | linuxserver/code-server | latest | VSCode completo no browser |
| Database | PostgreSQL | 16-alpine | Audit log + sessões |
| Reverse proxy | Caddy | 2-alpine | TLS automático + CORS |

### Infraestrutura externa

| Item | Tecnologia | Função |
|---|---|---|
| Cloudflare DNS | Free tier | DNS proxy + WAF |
| Cloudflare Tunnel | Named tunnels | Conexão HTTPS sem expor IP |
| SSH (alternativo) | cloudflared access tcp | Backup pra Rocky |

### Por que essas escolhas

- **PHP em vez de Python:** Python `http.server` retorna 400 em alguns HEAD requests (descobrimos), PHP é mais robusto
- **Caddy em vez de Nginx:** config mais legível, CORS + TLS em 1 lugar
- **PostgreSQL 16:** mesmo padrão dos outros projetos Dev Maniac's (dm-erp, biolar)
- **Cloudflare Tunnel:** zero custo, zero exposição de IP, WAF grátis

---

## 5. URLs e domínios

| URL | Tipo | Backend | Quem usa |
|---|---|---|---|
| `https://hub.devmaniacs.com.br/login.html` | PWA | PHP :8766 (Windows) | Login (fase 1: fake; fase 2: Google OAuth) |
| `https://hub.devmaniacs.com.br/dashboard.html` | PWA | PHP :8766 | Hub legado com cards (substituído por hub.html) |
| `https://hub.devmaniacs.com.br/hub.html` | PWA | PHP :8766 | Hub novo unificado com iframe |
| `https://hub.devmaniacs.com.br/status.html` | PWA | PHP :8766 | Diagnóstico (5 checks) |
| `https://hub.devmaniacs.com.br/manifest.webmanifest` | PWA | PHP :8766 | Manifesto PWA (instalação) |
| `https://hub.devmaniacs.com.br/sw.js` | PWA | PHP :8766 | Service worker (offline) |
| `https://hub.devmaniacs.com.br/health.php` | PWA | PHP :8766 | Proxy CORS pra checks |
| `https://code.devmaniacs.com.br/login` | Code-server | Rocky :8766 (Caddy) | VSCode Web (senha) |
| `https://code.devmaniacs.com.br/healthz` | Code-server | Rocky :8766 | Health check JSON |

### DNS records no Cloudflare

| Tipo | Nome | Conteúdo | Proxy |
|---|---|---|---|
| CNAME | `hub.devmaniacs.com.br` | `2aa6cd77-13a6-42d4-ab7f-390f5bde7e86.cfargotunnel.com` | ✅ Proxied |
| CNAME | `code.devmaniacs.com.br` | `09d80a67-711d-4546-a54c-99f9bb7c911b.cfargotunnel.com` | ✅ Proxied |

---

## 6. Tunnels Cloudflare

### dm-hub (tunnel principal)

- **ID:** `2aa6cd77-13a6-42d4-ab7f-390f5bde7e86`
- **Credenciais:** `C:\Users\Helbert\.cloudflared\2aa6cd77-13a6-42d4-ab7f-390f5bde7e86.json`
- **Config:** `C:\Users\Helbert\.cloudflared\config.dm-hub.yml`
- **Origem:** `http://127.0.0.1:8766` (PHP -S no Windows)
- **Rota:** `hub.devmaniacs.com.br/*`
- **Status atual:** ✅ Rodando (PID 52136, sessão `proc_ce5500de8172`)

### dm-code (tunnel code-server)

- **ID:** `09d80a67-711d-4546-a54c-99f9bb7c911b`
- **Credenciais:** `C:\Users\Helbert\.cloudflared\09d80a67-711d-4546-a54c-99f9bb7c911b.json`
- **Config:** `C:\Users\Helbert\.cloudflared\config.dm-code.yml`
- **Origem:** `http://192.168.226.103:8766` (Caddy + code-server no Rocky)
- **Rota:** `code.devmaniacs.com.br/*`
- **Status atual:** ✅ Rodando (PID 21672, sessão `proc_08be9599c536`)

### Config YAML exemplo (dm-hub.yml)

```yaml
tunnel: dm-hub
credentials-file: C:\Users\Helbert\.cloudflared\2aa6cd77-13a6-42d4-ab7f-390f5bde7e86.json

ingress:
  - hostname: hub.devmaniacs.com.br
    service: http://127.0.0.1:8766
  - service: http_status:404
```

### Comando pra subir cada tunnel

```bash
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-hub.yml" run dm-hub
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-code.yml" run dm-code
```

### Comandos úteis Cloudflare

```bash
# Listar tunnels
cloudflared tunnel list

# Ver info de um tunnel específico
cloudflared tunnel info dm-hub

# Validar config antes de subir
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-hub.yml" ingress validate

# Ver rota DNS
cloudflared tunnel route dns dm-hub hub.devmaniacs.com.br
```

---

## 7. Infraestrutura Docker no Rocky

### Servidor: 192.168.226.103 (Rocky Linux 10.2)

Acesso SSH via Cloudflare Tunnel: `ssh -p 2222 root@127.0.0.1` (precisa do tunnel local ativo).

### Estrutura de pastas no Rocky

```
/opt/sistemas/hub-remote/
├── docker-compose.yml                 ← stack Fase 1
├── .env                               ← senhas (chmod 600, NÃO commitado)
├── .env.fase1.example                 ← template
├── caddy/
│   └── Caddyfile                      ← reverse proxy + CORS
├── postgres/
│   ├── data/                          ← volume persistente (gitignored)
│   └── init.sql                       ← schema inicial
└── code-server/
    ├── config/
    │   ├── data/User/settings.json    ← tema Dev Maniac's Dark + JetBrains Mono
    │   └── extensions/dev-maniacs-theme/  ← tema custom instalado
    └── workspace/                     ← workspace padrão do VSCode
```

### Containers ativos

| Container | Imagem | Porta interna | Porta exposta | Status |
|---|---|---|---|---|
| `hub-postgres` | `postgres:16-alpine` | 5432 | nenhuma (só network interna) | ✅ Healthy |
| `hub-code-server` | `linuxserver/code-server:latest` | 8443 | nenhuma (via Caddy) | ✅ Running |
| `hub-caddy` | `caddy:2-alpine` | 8080 | **8766:8080** (host) | ✅ Running |

### docker-compose.yml (resumo)

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: hub_dm
      POSTGRES_USER: hub_admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

  code-server:
    image: linuxserver/code-server:latest
    environment:
      PUID: 1000
      PGID: 1000
      TZ: America/Sao_Paulo
      DEFAULT_WORKSPACE: /config/workspace
      PASSWORD: ${CODE_PASSWORD}
      SUDO_PASSWORD: ${CODE_PASSWORD}
      CS_DISABLE_PROXY_DOMAIN_AUTH: "true"
    volumes:
      - ./code-server/config:/config
      - ./code-server/workspace:/config/workspace
      - /opt/sistemas:/opt/sistemas:rw   # acesso aos projetos

  caddy:
    image: caddy:2-alpine
    ports:
      - "8766:8080"
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
```

### Schema PostgreSQL (init.sql)

3 tabelas:
- **`users`** — e-mail, password_hash (bcrypt), google_id, totp_secret, role
- **`sessions`** — user_id, token_hash, expires_at (JWT cookies)
- **`audit_log`** — user_id, action, target, ip, user_agent, metadata (JSONB)

Admin padrão criado: `helbertcurcio@gmail.com`

### Senhas (.env)

```
POSTGRES_PASSWORD=Y4M2zimX34f1NNUigkPgoVVt
CODE_PASSWORD=stnkPHjZIi9A@RSB
```

⚠️ Senhas geradas via `secrets.choice` (32 chars, alfanum + especiais). NÃO commitadas.

### Comandos úteis no Rocky

```bash
# Entrar no Rocky
ssh -p 2222 root@127.0.0.1

# Ver status dos containers
cd /opt/sistemas/hub-remote && docker compose ps

# Logs
docker logs hub-code-server --tail 30
docker logs hub-caddy --tail 30

# Reiniciar tudo (NÃO executar sem autorização)
docker compose restart

# Validar Caddyfile antes de aplicar
docker exec hub-caddy caddy validate --config /etc/caddy/Caddyfile

# Acessar PostgreSQL
docker exec -it hub-postgres psql -U hub_admin -d hub_dm
```

---

## 8. Identidade visual Dev Maniac's

### Paleta oficial (extraída via curl de `devmaniacs.com.br`, 22/08/2026)

```css
/* CORES PRIMÁRIAS */
--navy:   #061637;  /* Background principal */
--paper:  #faf6ed;  /* Texto claro / fundo claro */
--white:  #ffffff;  /* Texto puro */

/* CORES DE ACCENT */
--purple: #6b4c9a;  /* Eyebrows, links, badges */
--cyan:   #08b9ca;  /* CTAs, hovers, links ativos */
--coral:  #ff4c4c;  /* Alertas, badges de status */
--yellow: #ffd166;  /* Highlights, notificações */

/* CORES NEUTRAS */
--gray-100: #faf6ed;
--gray-500: #5c5c5c;
--gray-700: #2a3850;
```

### Tipografia

| Família | Uso | Fallback |
|---|---|---|
| **Inter** (sans-serif) | UI, títulos, parágrafos | system-ui, -apple-system, Arial |
| **JetBrains Mono** (monospace) | Código, labels, eyebrows | Menlo, Monaco, Consolas |

### Estilo visual

- **Sombras brutalistas:** `8px 8px 0 var(--navy)` (sólida, não blur)
- **Bordas pesadas:** `3px solid var(--navy)` em cards
- **Stripe colorida:** coral → yellow → cyan → purple (bandeira Dev Maniac's)
- **Prefixos industriais:** `DM//` antes de labels
- **Numeração:** `01/02/03/04` estilo tipográfico
- **Eyebrows:** barra roxa + texto roxo uppercase

### Arquivos de marca baixados

- `assets/brand/dev-maniacs-mark.png` — logo pixel art oficial (192x192)
- `assets/brand/dev-maniacs-mascot.webp` — Helbert cartoon 3D estilo Pixar
- `assets/brand/dev-maniacs-social-card.png` — card de redes sociais
- `assets/brand/devmaniacs-styles.css` — CSS fonte (55 KB, baixado via curl)

---

## 9. Tema VSCode

### Arquivos do tema

- `dev-maniacs-theme/package.json` — manifesto da extensão
- `dev-maniacs-theme/themes/dev-maniacs-light.json` — tema claro
- `dev-maniacs-theme/themes/dev-maniacs-dark.json` — tema escuro

### Cores aplicadas (Dark — padrão)

| Elemento | Cor |
|---|---|
| `editor.background` | `#061637` (navy) |
| `editor.foreground` | `#faf6ed` (paper) |
| `editorCursor.foreground` | `#08b9ca` (cyan) |
| `editor.lineHighlightBackground` | `#0f2046` |
| `sideBar.background` | `#061637` |
| `activityBar.background` | `#030b22` |
| `titleBar.activeBackground` | `#030b22` |
| `statusBar.background` | `#030b22` |
| `statusBar.foreground` | `#08b9ca` |
| `terminal.background` | `#030b22` |
| `button.background` | `#6b4c9a` (purple) |
| `focusBorder` | `#08b9ca` (cyan) |

### Token colors (syntax highlighting)

| Scope | Cor | Style |
|---|---|---|
| `keyword` | `#a07ad9` (roxo claro) | bold |
| `string` | `#4dd6e7` (ciano claro) | normal |
| `constant.numeric` | `#ff7a7a` (coral claro) | normal |
| `entity.name.function` | `#ffd97a` (amarelo claro) | bold |
| `entity.name.class` | `#a07ad9` (roxo claro) | bold |
| `comment` | `#5c7090` (azul acinzentado) | italic |
| `variable` | `#faf6ed` (paper) | normal |
| `tag` | `#a07ad9` (roxo claro) | normal |

### Instalação manual (já feito no Rocky)

```bash
# 1. Copiar arquivos
scp -P 2222 package.json root@127.0.0.1:/opt/sistemas/hub-remote/code-server/config/extensions/dev-maniacs-theme/
scp -P 2222 -r themes/ root@127.0.0.1:/opt/sistemas/hub-remote/code-server/config/extensions/dev-maniacs-theme/

# 2. Settings.json já configurado em:
# /opt/sistemas/hub-remote/code-server/config/data/User/settings.json
# {
#   "workbench.colorTheme": "Dev Maniac's Dark",
#   "editor.fontFamily": "JetBrains Mono, Menlo, Monaco, Consolas, monospace",
#   ...
# }
```

⚠️ **Problema conhecido:** code-server pode precisar de restart do container pra detectar a extensão. Verificar com:
```bash
ssh -p 2222 root@127.0.0.1 'docker logs hub-code-server --tail 20'
```

---

## 10. PWA — Instalação mobile

### Manifest.webmanifest (v2 — auditoria 23/08/2026)

```json
{
  "name": "Dev Maniac's Hub",
  "short_name": "DM Hub",
  "start_url": "/hub.html",
  "display": "standalone",
  "background_color": "#061637",
  "theme_color": "#061637",
  "icons": [
    { "src": "/assets/brand/dev-maniacs-mark-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/assets/brand/dev-maniacs-mark-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" },
    { "src": "/assets/brand/dev-maniacs-mark-180.png", "sizes": "180x180", "type": "image/png", "purpose": "any" }
  ],
  "shortcuts": [
    { "name": "VSCode Web (Code-server)", "url": "/hub.html?ide=code" },
    { "name": "Diagnóstico do Hub", "url": "/status.html" }
  ]
}
```

> Ícones reais gerados com Pillow (nearest-neighbor, pixel art preservado).
> Sem `orientation` travada — landscape é essencial pra ler código no celular.

### Service Worker (sw.js v2)

- **Versão do cache:** `dm-hub-v2` (trocar a cada deploy de assets)
- **Estratégia:** network-first pra HTML, cache-first pra assets estáticos
- **Cache estático:** `/`, `/login.html`, `/hub.html`, `/status.html`, `/offline.html`, `/styles.css`, `/app.js`, `/manifest.webmanifest`, ícones da marca
- **Nunca cacheia:** `/auth/*`, `/api/*`, `/health.php` (dinâmicos/sessão)
- **Offline:** sem rede, HTML cai no `/offline.html` (marca DM + botão retry + auto-recarga quando a rede volta)

### Como instalar no celular

**iOS Safari:**
1. Abre `https://hub.devmaniacs.com.br/login.html`
2. Botão compartilhar (⬆️)
3. "Adicionar à Tela de Início"
4. Confirma nome "DM Hub"
5. Ícone aparece na home

**Android Chrome:**
1. Abre `https://hub.devmaniacs.com.br/login.html`
2. Menu (⋮)
3. "Instalar app" ou "Adicionar à tela inicial"
4. Confirma

---

## 11. Autenticação

### Fase 1 (atual — mockup)

**Login fake:** submit do form redireciona pra `/hub.html` sem validar nada.

Botão Google OAuth é **visual apenas** — link aponta pra `/auth/google` (rota que não existe).

### Fase 2 — Google OAuth real (🟡 IMPLEMENTADO, aguardando credenciais — 23/08/2026)

Implementado **em PHP puro** (sem NextAuth/Node — a stack do mockup é PHP, sem build step):
o servidor agora sobe com roteador (`php -S 127.0.0.1:8766 router.php`).

| Rota | Função |
|---|---|
| `/auth/google` | Inicia o fluxo: 302 pro Google com `state` anti-CSRF |
| `/api/auth/callback/google` | Troca `code` → token (backchannel TLS), valida iss/aud/exp do `id_token`, checa allowlist, cria sessão |
| `/auth/logout` | Encerra a sessão |
| `/auth/me` | JSON com usuário logado (401 se não autenticado) |

**Segurança:** allowlist de e-mails (`config.php` — só `helbertcurcio@gmail.com`), cookie
`DMHUBSESSID` HttpOnly/Secure/SameSite=Lax, `session_regenerate_id` no login, audit log em
`mockup/logs/auth-audit.jsonl` (login, negadas, erros de troca).

**O que falta pra ligar:** colar Client ID/Secret no `mockup/config.php` (template em
`config.example.php`; arquivo gitignored). Redirect URI já validado no Google Cloud:
`https://hub.devmaniacs.com.br/api/auth/callback/google`. Testado com creds fake em 23/08:
redirect, state, troca de token e tratamento de erro (`invalid_client`) todos OK.

### SSO Hub → Code-server (✅ IMPLEMENTADO — 23/08/2026)

Login único de verdade: logou no Hub (Google), o VSCode web abre **sem pedir senha**.

```
1. Login Google OK no Hub (router.php)
2. Hub emite cookie `dm_sso` = base64url({email,exp}) + HMAC-SHA256
   · Domain=.devmaniacs.com.br · HttpOnly/Secure/SameSite=Lax · 8h
3. Browser envia o cookie pro code.devmaniacs.com.br (mesmo site/eTLD+1,
   inclusive dentro do iframe do hub.html)
4. Caddy (Rocky) exige o cookie via forward_auth → container `hub-auth`
   (php:8.3-alpine, auth/auth.php) valida a assinatura com SSO_SECRET
5. Válido → proxy pro code-server (auth: none). Inválido → 302 pro login do Hub
6. /auth/logout derruba sessão E cookie dm_sso
```

- Secret compartilhado: `sso_secret` no `mockup/config.php` = `SSO_SECRET` no `.env` do Rocky
- `healthz` é a única rota livre de auth (watchdogs Windows e Rocky)
- A senha antiga do code-server (`CODE_PASSWORD`) ficou só pro `sudo` do terminal web
- Detalhe: o `config.yaml` do code-server **persiste** `auth: password` no volume —
  remover o env `PASSWORD` não bastou; foi preciso `auth: none` no
  `code-server/config/.config/code-server/config.yaml` (ver erro conhecido #9)

### 2FA com TOTP (futuro)

- `speakeasy.generateSecret()` cria secret único
- QR Code gerado com `qrcode`
- Validado com `speakeasy.totp.verify({ window: 1 })`
- Backup codes (10) salvos criptografados

### Schema PostgreSQL

```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),          -- bcrypt (null se login só Google)
  google_id VARCHAR(255) UNIQUE,
  totp_secret VARCHAR(255),
  backup_codes TEXT[],
  role VARCHAR(20) DEFAULT 'user',
  last_login TIMESTAMPTZ,
  last_ip INET,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)

sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  token_hash VARCHAR(255) UNIQUE,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ
)

audit_log (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  user_email VARCHAR(255),
  action VARCHAR(50),    -- login, logout, open_ide, etc
  target VARCHAR(255),   -- arquivo, IDE acessado
  ip_address INET,
  user_agent TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ
)
```

### SSO Hub → Code-server (planejado)

```
1. Hub valida Google OAuth
2. Hub gera JWT curto (5 min) com user_id + role
3. Hub redireciona pra code-server com JWT no cookie
4. code-server valida JWT (chave compartilhada)
5. code-server cria sessão local
6. Usuário fica logado automaticamente
```

---

## 12. Status do projeto por fase

### Fase 1 — VSCode Web (✅ COMPLETA, 23/08/2026)

| Item | Status |
|---|---|
| Tunnel Cloudflare `dm-hub` | ✅ Funcionando |
| Tunnel Cloudflare `dm-code` | ✅ Funcionando |
| DNS `hub.devmaniacs.com.br` | ✅ Resolvendo |
| DNS `code.devmaniacs.com.br` | ✅ Resolvendo |
| Mockup PHP (login + dashboard + hub + status) | ✅ Servindo 200 OK |
| code-server no Rocky | ✅ Healthy |
| PostgreSQL | ✅ Healthy |
| Caddy reverse proxy | ✅ Rodando |
| Tema Dev Maniac's instalado | ✅ Arquivos copiados, settings.json configurado |
| PWA manifest + service worker | ✅ Funcionando |
| Página de diagnóstico (status.html) | ✅ Funcionando |
| CORS no Caddyfile | ✅ Configurado |
| Docker Compose completo | ✅ Funcionando |
| Schema PostgreSQL | ✅ Criado |
| **Google OAuth real** | 🟡 Código deployado 23/08 (PHP puro, router.php) — falta colar Client ID/Secret no `mockup/config.php` |
| **SSO Hub → Code-server** | ✅ Implementado 23/08 (cookie dm_sso assinado + Caddy forward_auth) |
| **Watchdog automático** | ✅ Agendado (Task Scheduler "DM Hub Watchdog" + systemd timer no Rocky, 23/08) |

### Fase 2 — Controle de IDEs Desktop (📋 PLANEJADA)

| Item | Status |
|---|---|
| Apache Guacamole (RDP/VNC web) | Pendente |
| Bridge p/ Antigravity 2.0 | Pendente |
| Bridge p/ MiniMax Code | Pendente |
| Bridge p/ Z.AI Code | Pendente |
| SSO real entre Hub e 3 IDEs | Pendente |

### Fase 3 — Recursos Avançados (💭 IDEIA)

| Item | Status |
|---|---|
| Push notifications (build complete, deploy done) | Pendente |
| Mobile gesture controls (swipe nos cards IDE) | Pendente |
| Voice input ("abrir Gemini") | Pendente |
| Audit log export (PDF/CSV) | Pendente |
| TOTP 2FA completo | Pendente |
| Backup automático do Rocky → DM-Cerebro | Pendente |

---

## 13. Comandos úteis

### Windows (PowerShell ou Git Bash)

```bash
# Status dos tunnels
tasklist /FI "IMAGENAME eq cloudflared.exe"

# Matar tunnel bugado
taskkill /F /PID <PID>

# Subir tunnel dm-hub
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-hub.yml" run dm-hub

# Subir tunnel dm-code
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-code.yml" run dm-code

# Validar config antes de subir
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-hub.yml" ingress validate

# Iniciar PHP mockup (com roteador de rotas de auth)
cd "/c/Users/Helbert/Desktop/DM-Cerebro/projects/hub-remote-ide/mockup"
php -S 127.0.0.1:8766 router.php

# Testar local
curl -sI http://127.0.0.1:8766/login.html

# Testar via Cloudflare
curl -sI https://hub.devmaniacs.com.br/login.html
curl -sI https://code.devmaniacs.com.br/login
```

### Watchdog (recuperação automática)

```bash
# Rodar o watchdog Windows na mão (só sobe o que faltar)
bash /c/Users/Helbert/.cloudflared/watchdog-hub.sh

# Disparar a tarefa agendada na hora
powershell -NoProfile -Command "Start-ScheduledTask -TaskName 'DM Hub Watchdog'"

# Ver últimos ticks
tail -20 /c/Users/Helbert/.cloudflared/logs/watchdog.log

# Rodar o watchdog do Rocky na hora
ssh devmaniacs-vm "systemctl start dm-hub-watchdog.service"

# Status do timer no Rocky
ssh devmaniacs-vm "systemctl list-timers | grep dm-hub"
```

### Rocky Linux (via SSH)

```bash
# Entrar
ssh -p 2222 root@127.0.0.1

# Status containers
cd /opt/sistemas/hub-remote && docker compose ps

# Logs
docker logs hub-code-server --tail 30 -f
docker logs hub-caddy --tail 30 -f
docker logs hub-postgres --tail 30 -f

# Reiniciar um container
docker compose restart code-server

# Reiniciar tudo
docker compose restart

# Validar Caddyfile
docker exec hub-caddy caddy validate --config /etc/caddy/Caddyfile

# Acessar PostgreSQL
docker exec -it hub-postgres psql -U hub_admin -d hub_dm

# Ver settings.json do code-server
cat /opt/sistemas/hub-remote/code-server/config/data/User/settings.json

# Ver extensão de tema instalada
ls /opt/sistemas/hub-remote/code-server/config/extensions/dev-maniacs-theme/themes/
```

### Cloudflare API (DNS)

```bash
# Listar DNS records
curl "https://api.cloudflare.com/client/v4/zones/77c99fbc1e785fd393551b5d771b4c59/dns_records" \
  -H "X-Auth-Email: helbertcurcio@gmail.com" \
  -H "X-Auth-Key: cfk_JxWo6pWWUiM2gF0JP7zvKhMaAGjgIh96YcO7hM2w4b9630c5"

# Adicionar CNAME
curl -X POST "https://api.cloudflare.com/client/v4/zones/77c99fbc1e785fd393551b5d771b4c59/dns_records" \
  -H "X-Auth-Email: helbertcurcio@gmail.com" \
  -H "X-Auth-Key: cfk_JxWo6pWWUiM2gF0JP7zvKhMaAGjgIh96YcO7hM2w4b9630c5" \
  -H "Content-Type: application/json" \
  --data '{"type":"CNAME","name":"code.devmaniacs.com.br","content":"09d80a67-711d-4546-a54c-99f9bb7c911b.cfargotunnel.com","proxied":true}'
```

---

## 14. Erros conhecidos

### � 1. Tunnel bugado: "dial tcp 127.0.0.1:8766: connectex: No connection could be made"

**Causa:** tunnel Cloudflare com cache de erro interno (mesmo com Python/PHP rodando).

**Sintomas:**
- `curl https://hub.devmaniacs.com.br/login.html` → 502 Bad Gateway
- `curl http://127.0.0.1:8766/login.html` → 200 OK (local funciona)

**Solução:** Matar todos `cloudflared.exe` exceto os serviços SSH, subir novo tunnel.

```bash
# Matar todos
taskkill /F /IM cloudflared.exe

# Subir limpo
cloudflared tunnel --config "C:\Users\Helbert\.cloudflared\config.dm-hub.yml" run dm-hub
```

### ❌ 2. SSH Tunnel local caiu (porta 2222 livre)

**Sintomas:**
- `ssh -p 2222 root@127.0.0.1` → "Connection refused"

**Solução:** o watchdog "DM Hub Watchdog" (Task Scheduler, a cada 5 min) re-sobe o proxy automaticamente. Pra forçar na hora:

```bash
cloudflared access tcp --hostname ssh.devmaniacs.com.br --listener 127.0.0.1:2222
```

**Alternativa (mais robusta):** SSH direto pela LAN, sem Cloudflare no caminho:

```bash
ssh devmaniacs-vm    # alias já em ~/.ssh/config → root@192.168.226.103
```

### � 3. CORS no status.html (Failed to fetch)

**Causa:** navegador bloqueia fetch cross-origin sem headers CORS.

**Solução:** implementado proxy PHP em `/health.php` que busca o `code.devmaniacs.com.br` server-side e retorna JSON pro JS do status.html. Veja `mockup/health.php`.

### ❌ 4. Python http.server retorna 400 em HEAD

**Causa:** Python `SimpleHTTPServer` do Windows lida mal com HEAD requests em alguns casos.

**Solução:** trocado por **PHP built-in server** (`php -S 127.0.0.1:8766 -t .`).

### ❌ 5. Node.js serve.js crash com CSPNG assertion failure

**Causa:** subprocess Node herda crypto seed ruim do Windows.

**Solução:** usar PHP como servidor padrão. `serve.js` fica como backup.

### ❌ 6. Tunnel `cloudflared route dns` cria DNS pro tunnel errado

**Causa:** `cloudflared route dns` usa o tunnel do config global, não do config específico do tunnel.

**Solução:** criar DNS direto via API Cloudflare apontando pro tunnel correto.

### ❌ 7. Tema Dev Maniac's não aparece no code-server

**Causa:** code-server precisa detectar a extensão (pode exigir restart do container).

**Solução:**
```bash
ssh -p 2222 root@127.0.0.1 'docker restart hub-code-server'
```

### ⚠️ 8. Status "expired" no healthz

**Causa:** code-server reporta `{"status":"expired"}` quando está rodando há muito tempo sem atividade.

**Não é erro crítico** — significa que o serviço está rodando mas o "heartbeat" interno expirou. O serviço continua respondendo normalmente.

### ❌ 9. Remover `PASSWORD` do code-server não desativa o login

**Causa:** o `config.yaml` persistido no volume (`code-server/config/.config/code-server/config.yaml`) guarda `auth: password` da primeira subida — o env só vale quando o config ainda não existe.

**Solução:** editar o config na mão e reiniciar:

```bash
ssh devmaniacs-vm "sed -i 's/^auth: password/auth: none/; /^password:/d' \
  /opt/sistemas/hub-remote/code-server/config/.config/code-server/config.yaml && \
  docker restart hub-code-server"
```

⚠️ Com `auth: none`, a única barreira do code-server é o SSO do Caddy — nunca exponha a porta do code-server direto (só via Caddy/tunnel).

### ❌ 10. Assets de marca davam 404 (logo, mascote, ícones PWA)

**Causa:** o docroot do PHP é `mockup/`, mas os arquivos de marca moram em `assets/` na raiz do projeto. Site no ar desde o deploy inicial sem logo/favicon/ícones corretos.

**Solução (aplicada 23/08):** rota `/assets/*` no `router.php` mapeando pra `../assets` + ícones reais gerados (512/180/maskable). Detalhes na `auditoria-ui-ux-2026-08-23.md`.

### ⚠️ 11. Páginas vazias com HTTP 200 (router com parse error)

**Causa:** o PHP built-in server, com router que não compila e `display_errors=0`, responde **200 com body vazio** — sem erro no log, e o watchdog vê "200" e não reclama.

**Solução:** `php -l` obrigatório após QUALQUER edit em PHP servido ao vivo. Diagnóstico definitivo: `php router.php` no CLI mostra o parse error que o `-S` engole (LEARN-006).

---

## 15. Backlog

### 🔴 Alta prioridade (bloqueia uso real)

- [ ] Implementar Google OAuth real no Hub — 🟡 código deployado 23/08, falta colar credenciais no `mockup/config.php`
- [x] SSO Hub → Code-server (token compartilhado) — feito 23/08/2026
- [x] Agendar watchdog automático (Task Scheduler Windows) — feito 23/08/2026
- [x] Watchdog no Rocky (systemd timer) — feito 23/08/2026

### 🟡 Média prioridade (melhora experiência)

- [ ] Tela de loading enquanto iframe carrega (substituir spinner genérico)
- [ ] Notificação quando code-server reiniciar
- [ ] Atalhos de teclado no Hub (Ctrl+K pra abrir paleta)
- [ ] Tema Dev Maniac's Light também no PWA (toggle dark/light)
- [ ] Mobile gestures (swipe pra trocar IDE)

### 🟢 Baixa prioridade (nice-to-have)

- [ ] Push notifications via service worker
- [ ] Voice input ("abrir Gemini")
- [ ] Backup automático do DM-Cerebro → Rocky
- [ ] Audit log exportável (PDF/CSV)
- [ ] Métricas de uso (qual IDE mais usado)

---

## 16. Glossário

| Termo | Significado |
|---|---|
| **PWA** | Progressive Web App — site que pode ser instalado como app nativo |
| **SSO** | Single Sign-On — 1 login vale pra múltiplos serviços |
| **2FA / TOTP** | Autenticador de 2 fatores baseado em tempo (Google Authenticator) |
| **Cloudflare Tunnel** | Conexão HTTPS sem expor IP do servidor |
| **Code-server** | VSCode completo rodando no browser |
| **Docker Compose** | Orquestrador de múltiplos containers Docker |
| **Caddy** | Reverse proxy moderno com TLS automático |
| **JWT** | JSON Web Token — token de sessão |
| **HMAC** | Hash-based Message Authentication Code |
| **bcrypt** | Algoritmo de hash de senhas (12 rounds = ~250ms) |
| **SHA-256** | Função hash criptográfica (256 bits) |
| **CNAME** | DNS record que aponta um domínio pra outro |
| **QUIC** | Protocolo de transporte moderno (Cloudflare usa) |
| **HEAD request** | GET sem body — usado pra checar cache |
| **CSP** | Content Security Policy — header que bloqueia XSS |
| **CORS** | Cross-Origin Resource Sharing — política de acesso entre domínios |

---

## 📊 Commits importantes

| Hash | Descrição |
|---|---|
| `2d6874b` | feat: hub.html unificado + tema Dev Maniac's + SSO switcher |
| `50421d0` | feat: watchdog script + docs |
| `bb49a03` | docs: DEPLOY-STATUS.md |
| `4e3cdf3` | feat: Fase 1 docker-compose + setup + init.sql |
| `76e82c6` | feat: PWA + Google OAuth + auth-seguranca |
| `70730d9` | docs: GLM 5.3 invocação manual |
| `3e365d6` | feat: serve.js + tunnel permanente |
| `68d4c55` | feat: config de modelos + .env.example |

---

**Última atualização:** 23/08/2026 09:10 (auditoria UI/UX+mobile+PWA aplicada — assets 404 corrigidos, ícones reais, SW v2, toolbar mobile)
**Owner:** Helbert Moura · Dev Maniac's Systems
**Mantido por:** Hermes Agent (DM-Cerebro / Z.AI / GLM 5.3 fallback pra MiniMax M3)
