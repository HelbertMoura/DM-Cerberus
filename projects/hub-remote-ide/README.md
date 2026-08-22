---
titulo: Hub Remoto de IDEs — Dev Maniac's
tags: [hub, remote, ide, pwa, devmaniacs, antigravity, minimax, zai, code-server]
atualizado: 2026-08-22
status: ativo
fase: 1-de-3
prioridade: alta
---

# 🌐 Hub Remoto de IDEs — Dev Maniac's

> **O que é:** Uma página web (`hub.devmaniacs.com.br`) com login + 2FA que dá acesso aos 3 IDEs (Antigravity 2.0, MiniMax Code, Z.AI Code) de qualquer lugar — celular, tablet, PC.

---

## 🎯 Objetivo

Acessar e controlar remotamente os 3 IDEs que rodam no seu desktop, com:

- ✅ Login + senha + 2FA (Google Authenticator)
- ✅ PWA instalável no celular (funciona como app nativo)
- ✅ Mobile-first (canteiro de obras com luva + sol)
- ✅ Clipboard compartilhado (copia celular → cola PC)
- ✅ Voice input (fala em vez de digitar)
- ✅ Audit log (PostgreSQL)
- ✅ HTTPS via Cloudflare (já tem)
- ✅ Identidade visual **Dev Maniac's** (cores, logo, tipografia)

---

## 🖥️ Os 3 IDEs

| IDE | Como virar web | Esforço | Status |
|---|---|---|---|
| 🧠 **Z.AI Code** | Já tem versão web oficial (`z.ai/code`) | 5 min | ⏳ Fase 2 |
| 🚀 **MiniMax Code** | Servidor headless experimental + versão web | 30 min | ⏳ Fase 2 |
| ♊️ **Antigravity 2.0** | Electron + CDP (Chrome DevTools Protocol) | 2h | ⏳ Fase 3 |

**Caminho pragmático:** na Fase 1, usar **VSCode via code-server** como padrão pra acelerar — é 10 min de setup e 100% remoto. Os outros IDEs entram nas Fases 2 e 3.

---

## 🏗️ Stack

| Camada | Tecnologia | Por quê |
|---|---|---|
| **Frontend PWA** | Next.js 15 + TypeScript | PWA nativo, mobile-first |
| **Streaming IDE** | code-server (VSCode web) | Padrão industrial da Microsoft |
| **Streaming outros IDEs** | Apache Guacamole + noVNC | Clientless, ultra-leve |
| **Bridge Antigravity** | CDP (Chrome DevTools Protocol) | Controle nativo Electron |
| **Auth** | Auth.js v5 + TOTP (2FA) | Senha + Google Authenticator |
| **Backend** | Node.js 22 (Fastify) | Leve, rápido, TypeScript |
| **Banco** | PostgreSQL 16 (já tem) | Sessões + audit log |
| **HTTPS** | Cloudflare Tunnel (já tem) | Zero cert pra configurar |
| **Container** | Docker Compose | 1 stack, portável |

---

## �️ Estrutura

```
hub-remote-ide/
├── README.md                 ← este arquivo
├── arquitetura.md            ← diagrama + decisões técnicas
├── identidade-visual.md      ← cores, logo, tipografia Dev Maniac's
├── setup-fase-1.md           ← MVP em 1 sessão (code-server)
├── setup-fase-2.md           ← Z.AI + M3 web (Guacamole)
├── setup-fase-3.md           ← Antigravity 2.0 (CDP bridge)
├── docker-compose.yml        ← stack completo
├── cloudflare-tunnel.md      ← config subdomínio
├── auth-seguranca.md         ← login + 2FA + fail2ban
├── pwa/                      ← frontend Next.js
│   ├── package.json
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx          ← login
│   │   ├── dashboard/        ← 3 abas (Gemini, M3, Z.AI)
│   │   └── api/
│   ├── public/
│   │   ├── manifest.json     ← PWA
│   │   ├── icon-192.png      ← ícone Dev Maniac's
│   │   └── icon-512.png
│   └── tailwind.config.ts    ← tema Dev Maniac's
├── assets/                   ← logo, ícones, fontes
├── docs/                     ← prints, diagramas
└── scripts/                  ← deploy, backup, monitor
```

---

## 📅 Roadmap (3 fases)

### ✅ Fase 1 — MVP (1 dia)
- [x] Estrutura criada no DM-Cerebro
- [ ] code-server (VSCode web) no Rocky na porta `:8443`
- [ ] Cloudflare Tunnel → `code.devmaniacs.com.br`
- [ ] Login básico (sem 2FA ainda)
- [ ] PWA shell com identidade Dev Maniac's

### ⏳ Fase 2 — Multi-IDE (1 semana)
- [ ] Apache Guacamole pro Z.AI Code
- [ ] MiniMax Code headless
- [ ] Hub unificado `hub.devmaniacs.com.br` com iframe dos 3
- [ ] 2FA (TOTP) obrigatório
- [ ] Clipboard compartilhado

### ⏳ Fase 3 — Polish (1 mês)
- [ ] Bridge Antigravity 2.0 via CDP
- [ ] Voice input (Web Speech API)
- [ ] Audit log completo no PostgreSQL
- [ ] Notificações push (PWA + Service Worker)
- [ ] Mobile-first UI refinado

---

## 🔐 Segurança

| Camada | Proteção |
|---|---|
| **HTTPS** | Cloudflare Tunnel + cert automático |
| **Login** | Email + senha forte (Argon2id) |
| **2FA** | TOTP via Google Authenticator |
| **Sessão** | Cookie httpOnly + SameSite=Strict, expira 8h |
| **Audit** | Tudo gravado em `dm_hub_audit` (PostgreSQL) |
| **Fail2ban** | Bloqueia IP após 5 tentativas erradas |
| **Backup** | Diário (já tem rotina) |

---

## 💰 Custo

| Item | Valor |
|---|---|
| Domínio `hub.devmaniacs.com.br` | R$ 0 (já tem) |
| Servidor Rocky | R$ 0 (já tem) |
| Cloudflare Tunnel | R$ 0 (free tier) |
| PostgreSQL | R$ 0 (já tem) |
| Stack open-source | R$ 0 |
| **Total** | **R$ 0** |

---

## 🔗 Links

- Site institucional: https://devmaniacs.com.br/
- Servidor: `192.168.226.103` (Rocky Linux 10)
- Túnel SSH: `ssh.devmaniacs.com.br` (já ativo)
- DM-Cerebro: `C:\Users\Helbert\Desktop\DM-Cerebro\`
- HANDOVER: ver `HANDOVER.md` no DM-Cerebro

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
