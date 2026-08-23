---
titulo: Auditoria UI/UX + Mobile + PWA — Hub Remoto
tags: [auditoria, ui, ux, mobile, pwa, hub-remote-ide]
atualizado: 2026-08-23
status: ativo
---

# 🔍 Auditoria UI/UX · Mobile · PWA — Hub Remoto (23/08/2026)

> **Escopo:** todas as telas do mockup (login, hub, status, dashboard), CSS, JS, PWA
> (manifest + service worker) e rotas do router. **Foco:** mobile e PWA, conforme pedido
> do Helbert. Achados seguidos de correção aplicada no mesmo dia.

---

## 🔴 P0 — Críticos (corrigidos)

| # | Achado | Impacto | Correção |
|---|---|---|---|
| 1 | **Assets de marca 404 no ar** — docroot é `mockup/`, mas logos/ícones moram em `assets/` na raiz do projeto | Logo, mascote, favicon e ícones PWA quebrados desde o deploy inicial; PWA não instalável com ícone correto | Rota `/assets/*` no `router.php` mapeando pra `../assets` com MIME + cache 24h |
| 2 | **Manifest mentia sobre tamanhos** — mesmo PNG declarado como 192/512/180 | Install prompt do Android exige ícone 512 real; Lighthouse reprova | Ícones gerados de verdade com Pillow (nearest p/ pixel art): 512, 180 e maskable-512 (fundo navy, safe zone 80%) |
| 3 | **Tipografia oficial nunca carregou** — nenhum HTML linkava Inter/JetBrains Mono | Site inteiro em Arial/Consolas (fallback), fora da identidade | `<link>` Google Fonts com `preconnect` em login, hub, dashboard (perf mobile) |
| 4 | **Parse error silencioso no router** durante a auditoria (typo de concatenação) | `php -S` serve 200 vazio sem logar erro — site mudo por minutos | Corrigido na hora; LEARN-006 registrado (lint obrigatório pós-edit) |

## 🟠 P1 — Mobile (corrigidos)

| # | Achado | Correção |
|---|---|---|
| 5 | Toolbar do `hub.html` estourava em tela pequena (brand + título + 4 IDEs + fullscreen + chip + Entrar numa linha) | Toolbar com `flex-wrap`, título some ≤768px, IDE-switch rola horizontal, botões com `min-height: 44px` (ergonomia canteiro) |
| 6 | iframe com `calc(100vh - 80px)` — barra do iOS corrompe a altura | Layout flex: body `100dvh` (dynamic viewport), main `flex:1` + `min-height:0` |
| 7 | Sem safe-areas (notch/home indicator iOS em standalone) | `env(safe-area-inset-top/bottom)` no toolbar e no wrap do iframe |
| 8 | Inputs 15px → iOS Safari dava zoom ao focar | `font-size: 16px` nos inputs e botão Google mobile |
| 9 | `alert()` nativo pros IDEs da Fase 2 (feio no celular) | Toast Dev Maniac's (navy, borda cyan, auto-hide 2,8s) |
| 10 | Manifest travava `orientation: portrait` — péssimo pra ler código | Removido (qualquer orientação) |

## 🟡 P2 — PWA (corrigidos)

| # | Achado | Correção |
|---|---|---|
| 11 | `start_url: /dashboard.html` (tela legado) | `start_url: /hub.html`; atalhos atualizados (Code + Status) |
| 12 | SW v1 não cacheara `hub.html`/`status.html`; sem página offline | SW **v2**: cache `dm-hub-v2` com hub/status/offline/ícones; fallback `/offline.html` |
| 13 | SW podia cachear rotas dinâmicas | Exclusão explícita: `/auth/`, `/api/`, `/health.php` sempre na rede |
| 14 | Sem página offline | `offline.html` com marca (stripe DM, spinner, botão retry, auto-recarga quando a rede volta) |

## 🟢 P3 — UX geral (corrigidos)

| # | Achado | Correção |
|---|---|---|
| 15 | "Esqueci a senha" — link morto `href="#"` | Removido (senha real chega na Fase 2) |
| 16 | Login mock redirecionava pro dashboard legado | Agora vai pra `/hub.html` |
| 17 | `status.html`: check de "tema" não testava nada real; check do code apontava `/login` (quebrado pós-SSO) | Check 4 agora testa o **SSO de verdade** (sem cookie → espera 302 pro login do Hub via `health.php?target=sso`); emojis de UI removidos (regra da marca), spinner CSS no lugar de ⏳ |
| 18 | Ícones/manifest com caminhos relativos `../assets` | Caminhos absolutos `/assets/...` |

## O que NÃO mudou (decisão)

- **dashboard.html** (legado) — só ganhou fontes/ícones; sem redesign (será aposentado).
- **Form e-mail/senha + TOTP** do login segue mock (Fase 2 implementa real).
- **Offline do code-server**: iframe depende de rede por natureza — offline.html cobre o shell.

---

**Resultado:** local + Cloudflare 100% 200 com conteúdo real; ícones `image/png` corretos;
watchdogs Windows/Rocky OK. Validação visual no celular fica com o Helbert (PWA install +
safe-areas são melhor vistas no aparelho).

**Owner:** Helbert Moura · executado por Z.AI ZCode (GLM 5.3) · 23/08/2026
