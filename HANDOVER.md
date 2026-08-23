---
titulo: Handover Log — Passagem de Bastão Entre Agentes & Sessões
tags: [handover, log, sessoes, agentes, trilho, shared, gemini, m3, zai]
atualizado: 2026-08-22
status: ativo
prioridade: alta
---

# 🤝 Handover Log — Passagem de Bastão da Tríade

> **Objetivo:** Registrar toda passagem de bastão entre agentes (Gemini ↔ M3 � Z.AI) e entre sessões (hoje → amanhã) para que **nenhuma memória se perca**.

---

## 📐 Formato Padrão de Entrada

Toda vez que um agente terminar uma tarefa e passar pro próximo, ele **adiciona uma entrada** neste arquivo:

```markdown
## [AAAA-MM-DD HH:MM] <AGENTE_ORIGEM> → <AGENTE_DESTINO>

**Sessão:** <breve descrição do que estava rolando>
**Tarefa executada:** <o que foi feito>
**Arquivos criados/alterados:**
- <caminho/arquivo1.md>
- <caminho/arquivo2.md>

**Decisão técnica (ADR-XXX):** <link ou resumo>
**Aprendizado (LEARN-XXX):** <link ou resumo>
**Status:** ✅ concluído | 🟡 parcial | 🔴 bloqueado

**Próximo passo:** <o que o próximo agente ou sessão deve fazer>
**Commit:** <sha do commit>
---
```

---

## 📜 Histórico de Handoffs

<!-- NOVA ENTRADA MAIS RECENTE PRIMEIRO -->

## [2026-08-23 17:50] Gemini (Orquestrador & Arquiteto Sênior) → Helbert

**Sessão:** Encerramento e descomissionamento total do projeto Hub Remoto de IDEs (`hub-remote-ide`), com remoção de recursos de infraestrutura (Cloudflare Tunnels, DNS, rotinas agendadas e diretório de projeto), mantendo todos os demais sistemas intactos e operacionais.

**Ações Executadas:**
1. **Exclusão de Túneis Cloudflare:** Túneis `dm-hub` e `dm-code` excluídos do Cloudflare com sucesso (`cloudflared tunnel delete -f`). Túnel principal corporativo (`devmaniacs-tunnel` / `a0c5bea6-1a4b-4ffe-a041-da8cb18f419a`), SSH (`devmaniacs-vm-ssh`), Biolar, Teenus e HelpDev continuam 100% ativos e intocados.
2. **Finalização de Processos Locais:** Processos `php.exe` (:8766) e executáveis `cloudflared` associados ao Hub encerrados.
3. **Remoção de Agendamento Windows:** Tarefa `DM Hub Watchdog` desregistrada do Agendador de Tarefas do Windows e scripts (`watchdog-hub*.{vbs,cmd,sh}`, `config.dm-*.yml`) removidos de `~/.cloudflared/`.
4. **Limpeza de Diretórios:** Pasta `projects/hub-remote-ide` removida.
5. **Atualização Documental:** `MEMORY.md` e `DECISIONS.md` (ADR-013) atualizados para refletir o status de projeto descontinuado.

**Status:** ✅ Descomissionamento 100% finalizado e seguro.

---

## [2026-08-23 17:45] Gemini (Orquestrador & Arquiteto Sênior) → Helbert

**Sessão:** Refinamento arquitetural da Central de Orquestração de IA Dev Maniac's (Tríade Desktop: Antigravity 2.0, MiniMax Code Desktop, Z.AI ZCode Desktop + VSCode Web), harmonização do rodapé oficial no login, avatar oficial e eliminação do CMD piscando no Windows.

**Entregas Realizadas:**
1. **Conceito Real do Hub Alinhado (AI Orchestration Hub Multi-Projetos):**
   - O Hub é a central operacional de orquestração das 3 Desktop IDEs de IA do Helbert para **qualquer projeto** (`dm-erp / CanteiroHUB`, `Biolar`, `HelpDev`, `DM-PDV`, `hub-remote-ide`, etc.).
   - **Antigravity 2.0 (Gemini 3.7 Flash High)** como workspace principal com **Dispatcher da Tríade** (seletor de projeto + geração instantânea de prompts para MiniMax M3 e Z.AI Hermes com 1-clique).
   - **MiniMax Code (M3)** como Construtor Pesado de Código (Backend Django & Frontend React).
   - **Z.AI ZCode (Hermes GLM-5.3)** como Especialista em Raciocínio Profundo, Cálculos Matemáticos e Criptografia.
   - **VSCode Web** com SSO via `dm_sso` para edição remota.
   - Aba "Infra Rocky" removida da barra de navegação conforme solicitado.
2. **Avatar Oficial & Identidade Visual:**
   - Avatar real do Helbert Moura (`/assets/brand/dev-maniacs-icon-180.png`) integrado no topo e modal de perfil (substituindo o placeholder `HM`).
   - Logo aprimorada com badge oficial `DEV MANIAC'S` e `AI ORCHESTRATION HUB`.
3. **Harmonização do Rodapé Oficial na Tela de Login:**
   - Login Astro v2 (`login.astro` / `login-built/`) e fallback `login.html` atualizados com o rodapé oficial: `© Dev Maniac’s Systems · 2026` + `Desenvolvido à base de ☕ e ⚡ por Dev Maniac's` (link ativo).
4. **Causa Raiz & Solução do "CMD piscando na tela":**
   - O Task Scheduler executava `watchdog-hub.cmd` a cada 5 min, abrindo um console `cmd.exe` interativo visível no desktop.
   - Criado `C:\Users\Helbert\.cloudflared\watchdog-hub-silent.vbs` executado via `wscript.exe` em segundo plano 100% invisível (zero janelas popup).
5. **Limpeza do Projeto:**
   - Removido arquivo de rascunho `qr-test.svg` (284 KB) e bump de Service Worker para `dm-hub-v14`.

**Decisão técnica:** ADR-013 refinada.
**Status:** ✅ 100% concluído, testado e validado.

---

## [2026-08-23 17:30] Gemini (Orquestrador & Arquiteto Sênior) → Helbert / Próximos Agentes

**Sessão:** Reconstrução 100% completa do Hub Remoto de IDEs (`hub.html`, `hub.css`, `hub.js`) para resolver quebras no desktop/mobile pós-login, unificando a Tríade de IA e o monitoramento de infraestrutura da Dev Maniac's.

**Problemas identificados:**
- `hub.html` anterior era legado, sem CSS isolado, com sidebar do VSCode distorcendo o viewport, botões sem estilo consistente e sem suporte mobile.
- Falta de integração com os outros motores (Gemini, MiniMax M3, Z.AI Hermes) e sem visualização de status do servidor Rocky Linux (`192.168.226.103`).
- Ausência do rodapé oficial exigido.

**Tarefa executada:** Hub Remoto v3.0 completo, industrial e multi-workspace:
1. **`mockup/hub.html`** reconstruído do zero com 5 workspaces integrados:
   - **Workspace 1: VSCode Web / Code-Server** (`code.devmaniacs.com.br`) em iframe responsivo com toolbar, reload assíncrono, fullscreen, abertura externa e feedback de SSO.
   - **Workspace 2: Gemini 3.7 Flash High (Orquestrador & Arquiteto)** com atalhos de repositórios e gerador de prompts estruturados para arquitetura e QA.
   - **Workspace 3: MiniMax M3 (Heavy Builder Engine)** com construtor rápido de tarefas injetando o contrato de agentes (`SYSTEM_PROMPT_PADRAO_M3.md`) e templates para Django REST e React.
   - **Workspace 4: Z.AI Hermes (Deep Reasoning & Math)** com templates cirúrgicos de BDI TCU, Criptografia SEFAZ A1 (XMLDSig), Curva S e Rateio Matricial.
   - **Workspace 5: Monitor de Infraestrutura Rocky Linux (`192.168.226.103`)** exibindo KPIs de hardware reais (16 vCPUs, 32GB RAM, 1TB NVMe) e tabela de serviços com healthchecks em tempo real (CanteiroHUB Dev/Prod, Biolar, HelpDev, SQLite, Postgres).
2. **`mockup/hub.css`** (folha isolada sob a ADR-011): tokens oficiais Navy `#061637`, Cyan `#08B9CA`, Purple `#6B4C9A`, Paper `#FAF6ED`, layout `100dvh`, alvos de toque mínimos de 44px (`min-h-[44px]`), safe-areas iOS e banimento total de emojis (Lucide SVG vetorial).
3. **`mockup/hub.js`** com checagem automática de auth (`/auth/me`), switcher de abas com persistência no `localStorage`, geradores de prompts com cópia em 1-clique, monitor de health checks assíncronos e modal de alteração de senha (`/auth/change-password`).
4. **`mockup/health.php`** atualizado para suportar múltiplos targets (`code`, `sso`, `teenus_dev`, `teenus_prod`, `helpdev`).
5. **`mockup/router.php`** atualizado com rotas para `/hub.css`, `/hub.js` e redirect amigável `/hub` → `/hub.html`.
6. **`mockup/sw.js`** bump de versão para `dm-hub-v12` incluindo `/hub.css` e `/hub.js` no cache estático.
7. **Rodapé Oficial:** `© 2026 Dev Maniac's · Game & Systems Development` + `Desenvolvido à base de ☕️ e ⚡️ por Dev Maniac's` + chip de ping e SSL TLS 1.3.

**Decisão técnica:** ADR-013 (Hub Remoto de IDEs v3.0 Multi-Workspace e Monitor de Infraestrutura).
**Aprendizado:** LEARN-012 (Layout 100dvh + CSS isolado para iframes de IDEs remotas).

**Status:** ✅ 100% concluído, testado e validado localmente (HTTP 200 em todas as rotas e health checks ativos).

---

## [2026-08-23 11:20] Hermes/M3 (DM Agent) → próximo agente (Hub interno)

**Sessão:** Retrabalho 100% do zero da tela de login do `hub-remote-ide`, após o Helbert ver no celular que a v1.4 estava "toda quebrada" (na verdade ele abriu `hub.html`, não `login.html` — diagnóstico confirmado via `curl` em produção).

**Diagnóstico do bug original:**
- `https://hub.devmaniacs.com.br/login.html` em produção retornava a v1.4 corretamente (0 ocorrências de `app-header` ou `ANTIGRAVITY` no HTML retornado).
- O Helbert abriu `hub.html` (página interna do dashboard pós-login) e achou que era o login.
- Mas o pedido de retrabalho foi mantido: ele queria ver o login refeito também.

**Tarefa executada:** Login v2.0 → v2.1 — redesenho completo, mobile-first, arquivo CSS isolado.
1. Criado `mockup/login.css` (446 linhas) — folha **isolada**, carregada SÓ pelo login.html. Tokens próprios, zero dependência do `styles.css` compartilhado. Protege contra regressões visuais em dashboard/hub.
2. Reescrito `mockup/login.html` (172 linhas) — mobile-first com wrappers `.login-left` (marca + avatar) e `.login-right` (copy + CTA + status).
3. Adicionada rota `/login.css` no `mockup/router.php` com `Cache-Control: public, max-age=300`.
4. Avatar circular 80px (mobile) / 220px (desktop) com `border-radius: 50%` em **todos** viewports + `object-fit: cover` + `object-position: center 18%` pra esconder o fundo bege do asset.
5. CTA "Entrar com Google" continua dominante (paper branco + sombra cyan brutalista), 56px altura no mobile / 64px no desktop.
6. Warn de "login google pendente" reduzido (fonte 11px, dot 6px, background sutil).
7. Validação visual: Playwright headless em 3 viewports (390×844 mobile, 768×1024 tablet, 1280×800 desktop) — screenshots em `C:\Users\Helbert\AppData\Local\Temp\login2-{mobile,tablet,desktop}.png`. Hierarquia confirmada: olho vai pro CTA depois do avatar.

**Arquivos criados/alterados:**
- `projects/hub-remote-ide/mockup/login.html` (v2.1, reescrito do zero)
- `projects/hub-remote-ide/mockup/login.css` (v2.1, NOVO, isolado)
- `projects/hub-remote-ide/mockup/router.php` (rota `/login.css` adicionada)
- `DM-Cerebro/HANDOVER.md` (esta entrada)
- `DM-Cerebro/LEARNINGS.md` (LEARN-008 adicionado)
- `DM-Cerebro/DECISIONS.md` (ADR-010 atualizado + ADR-011 adicionado)

**Decisão técnica (ADR-011):** CSS isolado por página crítica. O `styles.css` compartilhado vazava regras (toolbar do dashboard, classes de status) pra dentro do login. Princípio novo: páginas com identidade visual forte (login, offline, error) ganham folha própria + breakpoint próprio. Outras páginas continuam compartilhando o `styles.css`.

**Aprendizado (LEARN-008):** Crop agressivo de asset vertical com fundo bege (`object-position: center 18%`) + `border-radius: 50%` resolve o problema do "mascote esticado num cartão paper". A regra é: asset vertical ≠ crop central; é crop no TOPO onde fica o rosto.

**Status:** ✅ concluído, validado visualmente, **deployado em produção + commit + push** (commits `984006d` + `8610262`).
**Pendente:** Nenhum crítico. Próxima etapa é retomar Fase 2 (refazer `hub.html` do zero, mesma estratégia de CSS isolado) — só quando você quiser.

### Detalhes do deploy (rodada pós "pode fazer oq precisa")

**Como o deploy aconteceu:**
- O Cloudflare tunnel `dm-hub` aponta pra `service: http://127.0.0.1:8766` (config em `~/.cloudflared/config.dm-hub.yml`).
- O `php -S 127.0.0.1:8766 router.php` é mantido no ar pelo `watchdog-hub.sh` (Task Scheduler a cada 5 min), com workdir `mockup/`.
- **Por isso**: editar arquivos em `mockup/` É o deploy. Não tem rsync/scp/build/CI — o PHP lê do disco direto.
- Único passo manual que precisei: **bump do Service Worker** (`dm-hub-v4` → `dm-hub-v5`) + adicionar `/login.css` em `STATIC_ASSETS` no `sw.js`. Força `skipWaiting()` + `clients.claim()` em todos os clients com SW v4 cacheado.

**Validação em produção:**
- `curl https://hub.devmaniacs.com.br/login.html` → HTTP 200, 7718 bytes, contém `.login-left` e `.login-right` ✓
- `curl https://hub.devmaniacs.com.br/login.css` → HTTP 200, 11458 bytes, contém `border-radius: 50%` ✓
- `curl https://hub.devmaniacs.com.br/sw.js` → contém `CACHE_VERSION = 'dm-hub-v5'` ✓
- Playwright headless em produção, viewport 390×844 → `C:\Users\Helbert\AppData\Local\Temp\login-prod-prod-mobile.png`. Confirma v2.1 visualmente.

**Não precisei purgar Cloudflare manualmente** — não tinha API token do CF na2222 (o `credentials-file.json` em `~/.cloudflared/` é só cred de tunnel, não API). O bump `v4→v5` + `skipWaiting()` resolve sozinho.

### Rodada 23/08 11:55 — privacidade + ícone PWA do mascote

**Helbert levantou 2 pontos sensatos:**
1. Email `helbertcurcio@gmail.com` estava visível no front + mensagens técnicas de diagnóstico operacional ("login google pendente — cole o client id/secret no mockup/config.php", "credenciais ausentes"). Vazava arquitetura interna pra qualquer visitante.
2. O ícone PWA atual (`dev-maniacs-mark-512.png`) era um **caminhão de carga genérico** — parecia ícone de qualquer projeto de logística, sem identidade da Dev Maniac's.

**O que foi feito:**

1. **Privacidade no front (LEARN-009 + ADR-010 atualizado):**
   - Removido `helbertcurcio@gmail.com` do `<p class="login-restrict">">` (allowlist fica SÓ no back, em `config.php`)
   - Removido parágrafo "acesso exclusivo · helbertcurcio@gmail.com"
   - Removido aviso "login google pendente — cole o client id/secret no `mockup/config.php`" (HTML com `hidden=true`, JS nunca força visibilidade)
   - Chip "credenciais ausentes" → "configuração pendente" (texto neutro)
   - **Copy do front agora é genérica:** `"Seu painel unificado — acesso único a partir de qualquer lugar."` (era "Gemini, MiniMax M3, Z.AI e VSCode Web — um login, do canteiro pro bolso.")
   - `<meta description>` + `manifest.webmanifest` description: mesma copy genérica
   - **Páginas internas (dashboard/hub/status) MANTÊM a stack** — são pós-auth, faz sentido ver os IDEs específicos

2. **Ícone PWA novo — rosto do mascote:**
   - 4 tamanhos gerados via PIL: 32, 180, 192, 512px
   - Crop: top 30% do asset 700×1400, fundo bege removido via alpha mask, fundo do canvas = NAVY #061637, borda cyan #08B9CA com 2.5% espessura
   - **Pixel `(256,60)` do ícone 512 validado como `(6,22,55,255)` = NAVY (não transparente, não branco)**
   - Visualmente validado: mascote limpo, sem sliver bege, profissional, distintivo

3. **Substituições em todos HTMLs:**
   - `login.html`, `hub.html`, `dashboard.html`, `offline.html`, `status.html` → `<link rel="icon">` + `<link rel="apple-touch-icon">` apontam pros ícones novos
   - `manifest.webmanifest` → lista os 4 tamanhos novos (any/maskable)

4. **SW v6 → v7:**
   - `CACHE_VERSION = 'dm-hub-v7'`
   - STATIC_ASSETS aponta pros ícones novos (mark.png antigo mantido — é o logo DM interno)
   - Notification icon/badge aponta pros ícones novos

**Commits na ordem:**
- `984006d` — feat(login): v2.1 mobile-first
- `8610262` — chore(sw): bump v4→v5
- `c243d83` — docs(handover): status final
- `a99a136` — fix(login): remove email + msgs técnicas (privacidade)
- `3f3b957` — feat(brand): ícone PWA do mascote + copy segura (este)

**Validação em produção (curl):**
- `curl /login.html` → login-sub "Seu painel unificado — acesso único a partir de qualquer lugar." ✓
- `curl /login.html | grep Gemini` → zero ocorrências ✓
- `curl /sw.js | grep CACHE_VERSION` → `dm-hub-v7` ✓
- `curl /manifest.webmanifest` → descrição atualizada ✓

**Não commitei/pushei LEARN-009 nem atualizei HANDOVER automaticamente** — esses dois arquivos do cérebro ficam pra próxima rodada (LEARN-009 será commitado com o título de "docs(cérebro)" antes da Fase 2).

**Próximo passo:** Hub interno (`hub.html` redesign) com CSS isolado (mesma estratégia do login v2.1). Aguardando OK visual do Helbert na tela de login AGORA.

## [2026-08-23 10:25] Z.AI GLM 5.3 (DM Agent · Hermes) → Helbert

**Sessão:** Redesign da tela de login do zero (v1.4.0) a pedido do Helbert
**Tarefa executada:**
- Login **reconstruído do zero** sob o conceito "Hub, apenas." — sem reaproveitar a
  estrutura da v1.3 (que Helbert disse "não está legal" no Telegram).
- **Decisão de conceito:** 2 colunas no desktop (marca + mascote | cartão de acesso
  + CTA), 1 coluna no mobile. Mascote em pé, full body, sem sobrepor nada. CTA
  claramente dominante (paper com sombra cyan brutalista). Status como chips
  arredondados discretos, não no rodapé. Zero gimmicks (fora stripe decorativo,
  `DM//ACESSO` imitando janela de SO, mascote espiando, grade de pixels).
- **Bug encontrado e corrigido durante a validação:** o asset do mascote tem
  proporção 700×1400 (1:2, vertical full body) — primeira tentativa deixou
  `width: 100%; height: auto` e o mascote esticou verticalmente dentro do
  `align-items: center` do grid. Corrigido com `height: clamp(280px, 56vh, 460px)`
  + `width: auto` pra preservar a proporção natural do asset. Ver LEARN-007.
- **Validação visual:** Playwright headless capturando PNG em 3 viewports
  (1280×800 desktop, 768×1024 tablet, 390×844 mobile) servindo `php -S` local.
  Confirmado: mascote proporcional em todos os3; CTA dominante; chips de status
  legíveis; nenhum texto cortado; safe-areas mobile respeitadas.
- **Nada do CSS compartilhado foi tocado** — só a seção `.login-page` … `.login-footer`
  do `styles.css` foi substituída (linhas 145-424). Tokens, dashboard, hub, status
  e offline permanecem intactos.

**Arquivos alterados:**
- `projects/hub-remote-ide/mockup/login.html` (reescrito do zero — 174 → 174 linhas,
  mas estrutura HTML completamente nova: `login-shell` + `login-brand-col` + `login-access-col`)
- `projects/hub-remote-ide/mockup/styles.css` (bloco LOGIN substituído: 280 linhas
  removidas, 257 linhas novas, mantendo a sintaxe `#061637`/`#08b9ca` oficial)
- `DM-Cerebro/LEARNINGS.md` (+ LEARN-007 sobre aspect-ratio de mascote vertical)
- `DM-Cerebro/DECISIONS.md` (+ ADR-010: redesign do login sob princípio "Hub, apenas.")
- `DM-Cerebro/HANDOVER.md` (esta entrada)

**Status:** ✅ concluído — aguardando OK visual do Helbert (enviei os3 screenshots)
antes de qualquer deploy no Rocky/Cloudflare. Como o Helbert disse "antes de seguir
com esse projeto", **não fiz deploy** — a versão v1.4 está só no mockup local.

**Próximo passo:**
1. Helbert: validar visual (screenshots em /tmp/login-{desktop,tablet,mobile}.png)
2. Se aprovado: deploy no Rocky (`ssh devmaniacs-vm …`) + bump do SW (`dm-hub-v5`)
3. Depois: retomar Fase 2 (bridges Antigravity/M3/Z.AI no hub)

## [2026-08-23 10:15] Z.AI GLM 5.3 (ZCode CLI) → próxima sessão

**Sessão:** Redesign do zero da tela de login (v1.3.0) + hardening de cache
**Tarefa executada:**
- Login reconstruído com conceito único de **console Dev Maniac's**: tela navy imersiva,
  bandeira DM no topo, mascote sobrepondo cartão brutalista estilo terminal (barra
  DM//ACESSO), linha de status mono ao vivo no rodapé ✅
- CSS: seção LOGIN reescrita do zero, blocos legados removidos ✅
- **Fix importante:** Cloudflare cacheava o `sw.js` e travava updates do PWA — o router
  agora serve `/sw.js` com `no-cache` (cf-cache-status: BYPASS confirmado) ✅
- SW bump dm-hub-v4; visão do projeto no README reescrita (Dev Maniac's como um todo) ✅
- QA visual via browser não concluído (webview indisponível) — validação visual fica pro Helbert

**Commits:** `15095de` (login v1.2) · `7806502` (login v1.3 console + fix sw.js cache)

**Status:** ✅ concluído · Única pendência do hub: credenciais Google no `mockup/config.php`

---

## [2026-08-23 09:30] Z.AI GLM 5.3 (ZCode CLI) → próxima sessão

**Sessão:** Follow-up da auditoria — feedback do Helbert
**Tarefa executada:**
- Login agora é **Google-only**: form e-mail/senha + TOTP mock removidos do login.html;
  nota "Acesso exclusivo · helbertcurcio@gmail.com" no lugar ✅
- Imagens de marca com cache-buster `?v=2026-08-23` + **purge total do cache Cloudflare**
  (Helbert ainda via quebrado — servidor/edge estavam OK; era cache) ✅
- Allowlist validada: só o e-mail autorizado entra; outros → "acesso negado" + audit ✅

**Status:** ✅ concluído · Helbert deve fazer hard-refresh (Ctrl+Shift+R) ou reinstalar o PWA

---

## [2026-08-23 09:10] Z.AI GLM 5.3 (ZCode CLI) → próxima sessão

**Sessão:** Auditoria UI/UX + mobile + PWA do hub-remote-ide (pré-Fase 2)
**Tarefa executada:** auditoria completa + correções aplicadas no mesmo dia —
relatório em `projects/hub-remote-ide/auditoria-ui-ux-2026-08-23.md`. Destaques:
- **P0:** assets de marca 404 desde o deploy inicial (docroot ≠ pasta assets) → rota
  `/assets/*` no router + ícones reais 512/180/maskable (Pillow nearest) ✅
- **P0:** tipografia oficial nunca carregou (sem link de fonts) → Inter + JetBrains Mono
  com preconnect ✅
- Mobile: toolbar do hub responsiva (44px, safe-areas iOS, 100dvh, flex-wrap), inputs
  16px (fim do zoom iOS), toast DM no lugar de alert() ✅
- PWA: manifest v2 (start_url hub.html, orientation livre, ícones reais), SW v2
  (cache hub/status/offline, exclusão de /auth/), offline.html com auto-retry ✅
- status.html: check de SSO real (302 pro login = protegido), zero emojis em UI ✅
- Incidente durante a auditoria: parse error no router (typo) = 200 vazio silencioso →
  LEARN-006 (php -l obrigatório pós-edit); site recuperido em minutos ✅

**Arquivos:** mockup/{router,sw,hub,login,status,dashboard,offline,health,manifest,styles,app},
assets/brand/{512,180,maskable}, auditoria-ui-ux-2026-08-23.md, LEARNINGS.md, README.md

**Status:** ✅ concluído · Validação no CELULAR (install PWA + safe-areas) fica pro Helbert

**Próximo passo:**
1. Helbert cola credenciais Google no `mockup/config.php` (última pendência!)
2. Validar PWA no celular → depois Fase 2 (bridges Antigravity/M3/Z.AI)

---

## [2026-08-23 08:45] Z.AI GLM 5.3 (ZCode CLI) → próxima sessão

**Sessão:** SSO Hub → Code-server (continuidade das entregas 3a5acec/24d9605)
**Tarefa executada:**
- SSO completo: login Google no Hub emite cookie `dm_sso` assinado (HMAC); Caddy do
  Rocky valida via `forward_auth` num novo container `hub-auth`; code-server com
  `auth: none` atrás do gate ✅
- `hub.html`: chip do usuário logado (foto Google + e-mail, identidade Dev Maniac's) +
  botão Entrar/Sair dinâmico via `/auth/me` ✅
- `/healthz` livre de auth — watchdogs Windows e Rocky validados pós-deploy ✅
- Testes: sem cookie → 302 pro login; cookie válido → 200 VSCode sem senha; cookie
  adulterado → barrado ✅

**Arquivos criados/alterados:**
- `projects/hub-remote-ide/auth/auth.php` (novo — validador SSO)
- `projects/hub-remote-ide/caddy/Caddyfile` (forward_auth + healthz exempt)
- `projects/hub-remote-ide/docker-compose.yml` (service `auth`; code-server sem PASSWORD)
- `projects/hub-remote-ide/mockup/router.php` (emissão/limpeza do dm_sso; /auth/me com sso_code)
- `projects/hub-remote-ide/mockup/hub.html` (chip de usuário DM)
- `DECISIONS.md` (ADR-008 OAuth PHP + ADR-009 SSO cookie/forward_auth)

**Deploy:** Rocky `/opt/sistemas/hub-remote` (auth/ + compose + Caddyfile + SSO_SECRET no
.env) — code-server config.yaml setado `auth: none` (ver erro conhecido #9 do README).

**Status:** ✅ concluído — SSO no ar. 🟡 OAuth Google ainda aguarda Client ID/Secret do Helbert
(sem isso o fluxo SSO inteiro fica em espera — o botão mostra página de setup).

**Próximo passo:**
1. Helbert cola credenciais Google no `mockup/config.php` → teste real do fluxo completo no navegador
2. Fase 2: bridges pros IDEs desktop (Antigravity/M3/Z.AI via Guacamole ou CDP)

---

## [2026-08-23 08:30] Z.AI GLM 5.3 (ZCode CLI) → próxima sessão (Gemini ou Hermes)

**Sessão:** Suporte direto ao Helbert no hub-remote-ide (continuidade do commit f0419cb do Hermes Agent)
**Tarefa executada:**
- Diagnóstico e correção da queda da porta 2222 + deploy dos 2 watchdogs pendentes ✅
- Bug crítico corrigido: processos filhos do console da tarefa agendada morriam ~60s após o
  Task Scheduler concluir (CTRL_CLOSE) — provável causa raiz histórica das quedas; starts
  agora via `Start-Process -WindowStyle Hidden` ✅
- Google OAuth real implementado em PHP puro (`mockup/router.php`): /auth/google,
  /api/auth/callback/google, /auth/logout, /auth/me — state anti-CSRF, allowlist de e-mail,
  cookie de sessão HttpOnly/Secure, audit JSONL ✅ (🟡 falta colar Client ID/Secret no
  `mockup/config.php` — só o Helbert pode)

**Arquivos criados/alterados:**
- `~/.cloudflared/watchdog-hub.sh` (v2 idempotente) + `watchdog-hub.cmd` + `register-watchdog-task.ps1`
- `projects/hub-remote-ide/mockup/router.php` + `mockup/config.example.php` (config.php é gitignored)
- `projects/hub-remote-ide/scripts/rocky/` (watchdog-rocky.sh + systemd service/timer — deployados no Rocky)
- `projects/hub-remote-ide/README.md`, `DEPLOY-STATUS.md`, `watchdog-hub.md` (atualizados)

**Decisão técnica relevante:**
- OAuth em PHP puro em vez de NextAuth/Node (stack do mockup é PHP sem build step; Node
  `serve.js` tem histórico de crash CSPNG nesta máquina) — candidato a ADR formal
- Quirks de ambiente (PS 5.1 `.Count` escalar, S4U negado no domínio T2T3) registrados em
  `~/Documents/Mgdata-cerebro/infra/ambiente-windows.md` (repo separado, commit de3debc)

**Status:** ✅ concluído (OAuth aguardando credenciais do Helbert — 🟡 único item aberto)

**Próximo passo:**
1. Helbert cola Client ID/Secret no `mockup/config.php` → botão Google funciona de verdade
2. SSO Hub → code-server (token compartilhado) — próximo item de alta prioridade do backlog
3. Fase 2: bridges pros IDEs desktop (Guacamole/CDP)

**Commits desta sessão:**
- `3a5acec` — feat(hub-remote-ide): watchdogs Windows+Rocky deployados e testados
- `24d9605` — feat(hub-remote-ide): Google OAuth real em PHP puro (router.php)

---

## [2026-08-22 20:00] Z.AI Hermes (DM Agent) → Gemini (próxima sessão)

**Sessão:** Finalização da estrutura 10/10 do DM-Cerebro + integração da Tríade
**Tarefa executada:**
- Estrutura base do cérebro: BRAIN, MEMORY, LEARNINGS, DECISIONS, ROADMAP ✅
- Fragmentação de 5 produtos em `projects/` ✅
- Git init + remote + 6 commits no GitHub ✅
- TRIADE_PROTOCOLO.md v3 (alinhado à Panorâmica Oficial) ✅
- CONTRATO_AGENTES.md (obrigação universal ler/atualizar) ✅
- SYSTEM_PROMPT_PADRAO_M3.md (copy-paste pro App M3) ✅

**Arquivos criados/alterados nesta sessão final:**
- `BRAIN.md` (atualizado: tríade + referências ao TRIADE_PROTOCOLO e CONTRATO_AGENTES)
- `projects/_shared/TRIADE_PROTOCOLO.md` (v3 — alinhado à Panorâmica Oficial)
- `projects/_shared/CONTRATO_AGENTES.md` (novo — protocolo obrigatório universal)
- `prompts/SYSTEM_PROMPT_PADRAO_M3.md` (novo — copy-paste pro MiniMax M3)
- `HANDOVER.md` (este arquivo — log de sessões)

**Decisão técnica relevante:**
- ADR-001 a ADR-003 já registradas em DECISIONS.md
- Tríade oficial: Gemini (Eng Chefe + Orquestrador) | M3 (Heavy Builder) | Z.AI GLM 5.3 (Deep Reasoning)

**Status:** ✅ concluído — estrutura 10/10 + contrato ativo

**Próximo passo (Gemini):**
1. Gerar prompts mastigados pro M3 e Z.AI já com o CONTRATO_AGENTES embutido
2. Auditar respostas que voltarem e registrar novas entradas aqui
3. Manter `wiki/`, `DECISIONS.md` e `MEMORY.md` atualizados
4. Continuar deploys no servidor 192.168.226.103

**Commits desta sessão:**
- `5f87eda` — feat shared: CONTRATO_AGENTES + SYSTEM_PROMPT_PADRAO_M3
- `3c9b045` — feat shared: TRIADE_PROTOCOLO alinhado à Panorâmica Oficial
- `bd40fa1` — feat shared: TRIADE_PROTOCOLO atualizado (setup real)
- `d15828d` — feat shared: TRIADE_PROTOCOLO (substitui AGENTS)
- `3e439d4` — feat shared: status.md + deploy + procedimentos
- `f7c70ba` — feat core: estrutura 10/10 base

---

<!-- Entradas mais antigas abaixo (se houver) -->

---

## 🎯 Como Usar (Regras Operacionais)

| Quem | Quando | O que fazer |
|---|---|---|
| **Z.AI (Hermes)** | Ao final de cada task | Adiciona entrada aqui + commita |
| **MiniMax M3** | Ao final de cada task | Adiciona entrada aqui + commita |
| **Gemini (Antigravity)** | Ao auditar resposta de M3/Z.AI | Adiciona entrada aqui + commita |
| **Helbert** | Pode adicionar entradas manuais | Formato livre mas com seções básicas |

---

## 🔗 Arquivos-irmãos (Ler Junto)

- `BRAIN.md` — mapa mestre
- `projects/_shared/TRIADE_PROTOCOLO.md` — quem faz o quê
- `projects/_shared/CONTRATO_AGENTES.md` — obrigação de ler/atualizar
- `DECISIONS.md` — ADRs
- `LEARNINGS.md` — aprendizados
- `MEMORY.md` — contexto executivo permanente

---

**Última atualização:** 22/08/2026 · **Owner:** Helbert Moura · Dev Maniac's Systems

---

## [2026-08-23 17:25] Hermes/M3 (DM Agent) → Helbert

**Sessão:** Substituir Google OAuth por login local email+senha+2FA TOTP (ADR-012).

**Trigger:** Helbert quer login com email da empresa (`helbert.moura@devmaniacs.com.br`), senha pessoal, 2FA TOTP, sem depender do Google Cloud Console.

### Decisões

- **Stack:** PHP 8.3 + SQLite (`pdo_sqlite` nativo, zero infra)
- **Senha:** bcrypt 12 rounds (nativo PHP, validado contra Python `bcrypt`)
- **TOTP:** RFC 6238 custom PHP — validado contra `pyotp` (LEARN-010: bug era no Python de comparação, não no PHP)
- **Cookie:** `dm_sso` HMAC-SHA256 mantido (compatível com `hub-auth` no Rocky)
- **Schema:** 3 tabelas (`users`, `sessions`, `audit_log`) em `mockup/data/hub.sqlite`
- **Brute-force:** bloqueio após 5 tentativas em 15 min
- **Remember me:** opcional 30 dias (só com 2FA ativo)
- **Tela:** form email + senha → form 2FA → redirect hub.html. Sem chips de status, sem link diagnóstico, sem CTA Google

### Entregas (commit `f40b1bd` pushed)

- **Novos:** `mockup/auth.php` (12KB), `mockup/db.php` (5KB SQLite helper + migrations)
- **Modificados:** `router.php` (Google OAuth removido, ~140 linhas), `login.html` (form), `login.css` (estilos), `sw.js` (v8→v9), `.gitignore` (SQLite + .env.db)
- **Validado em produção:** `/auth/login` retorna `{"ok":true,"next":"2fa"}`, `/auth/2fa` retorna `{"ok":true,"redirect":"/hub.html"}`, `/auth/me` retorna `{"authenticated":true}`

### Credenciais iniciais

- Email: `helbert.moura@devmaniacs.com.br`
- Senha: `Acesso.2026#` (trocar via `/auth/change-password` após login)
- TOTP secret: `V7DUS5C5X7DWTP5AJ23CJNNHI4KDOFYI`
- Backup codes: salvos em `C:\Users\Helbert\AppData\Local\Temp\dm-credentials.txt`

### Lições registradas

- **LEARN-010** — TOTP custom: validar contra pyotp ANTES de assumir erro (perdi horas debugando PHP certo)
- **LEARN-011** — PHP `require` em múltiplos arquivos = `Cannot redeclare`. Wrap em `function_exists` ou centralizar em `_common.php`

### ADR registrada

- **ADR-012** — Auth local email+senha+2FA + SQLite + dm_sso HMAC mantido (decisão completa)

### Pendente

- Helbert: testar login no celular (limpar dados do Chrome → reinstalar PWA → email/senha/2FA)
- Próxima: redesign `hub.html` (mesma estratégia de CSS isolado do login) — Fase 2

