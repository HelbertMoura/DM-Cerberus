---
titulo: Registro de Decisões de Arquitetura (pré-finalize 2026-08-26)
tags: [archive, historical, decisoes, adr, pre-finalize]
atualizado: 2026-08-26
status: historical
fonte: git show HEAD:DECISIONS.md (estado commitado em 0a1770b)
---

> ## ⚠️ HISTORICAL — PRESERVED BEFORE CONSOLIDATION
>
> **This is historical content.** Preserved before the DM-CEREBRO-PENDING-CLEANUP-008 consolidation.
>
> **NOT an active operational source.** O canônico para ADRs do RadierHUB é:
> - repo: `dm-erp`
> - arquivo: `docs/DECISIONS.md`
> - numeração canônica: **pós-consolidação r161** (ADR-001 … ADR-014)
>
> **Legacy IDs (presentes neste snapshot) podem diferir dos IDs canônicos pós-r161.** Use a tabela de mapeamento em `../proposed-migration.md` §5 ou em `../../DECISIONS.md` (raiz, pós-reparo) para traduzir.
>
> **Do not edit or rewrite this historical body.** It is a faithful preservation of the working tree at the moment the consolidation was applied (commit `0a1770b`).
>
> **Active operational source:** raiz `DECISIONS.md` (reparado em 2026-08-26) + `dm-erp/docs/DECISIONS.md`.

---

# ⚖️ DECISIONS.md (HISTORICAL — pre-finalize 2026-08-26)

> **Nota:** O conteúdo abaixo é uma preservação literal do estado commitado em `git show HEAD:DECISIONS.md` (HEAD = `0a1770b`, commitado na task `DM-CEREBRO-SECOND-BRAIN-FINALIZE-006`). Foi preservado **antes** da reparação aplicada em `DM-CEREBRO-PENDING-CLEANUP-008` (PHASE 2). O conteúdo não foi reescrito; apenas embrulhado com o banner acima.

---

---
titulo: Registro de Decis├Áes de Arquitetura (ADRs)
tags: [decisoes, adr, arquitetura]
atualizado: 2026-08-22
status: ativo
---

# ÔÜû´©Å DECISIONS.md ÔÇö Registro de Decis├Áes de Arquitetura (ADRs)

---

### [ADR-008] Google OAuth em PHP puro no Hub (sem NextAuth/Node) (Rodada 23/08 ┬À Z.AI ZCode)
- **Decis├úo:** O login Google do `hub-remote-ide` roda em PHP puro (`mockup/router.php`, authorization code flow com state anti-CSRF e allowlist de e-mails), usando o PHP built-in server com router ÔÇö mesma stack do mockup, sem build step.
- **Motivo:** NextAuth/Next.js exigiria um daemon Node permanente; o `serve.js` desta m├íquina tem hist├│rico de crash (CSPNG assertion). PHP j├í ├® o runtime do mockup e do watchdog. Testado com credenciais fake: redirect, state, troca de token e tratamento de erro validados.

---

### [ADR-010] Login do Hub sob o princ├¡pio "Hub, apenas." (Rodada 23/08 ┬À Hermes/M3 DM Agent ÔÇö v2.1)
- **Decis├úo:** A tela de login do `hub-remote-ide` foi reconstru├¡da **duas vezes** do zero ÔÇö primeiro v1.4 (ainda no `styles.css` compartilhado), depois **v2.1 com CSS totalmente isolado** (`mockup/login.css`) ÔÇö sob o conceito "Hub, apenas.": **mobile-first**, sem reaproveitar estrutura da v1.3. Foco #1 ├® o uso via celular (o Helbert acessa pelo bolso).
- **Arquitetura (v2.1):**
  - Mobile-first: shell vertical com `padding: 24px 16px`, max-width 480px, `min-height: 100dvh`
  - Tablet (ÔëÑ640px): padding generoso, t├¡tulo 32px, CTA 60px altura
  - Desktop (ÔëÑ1024px): grid 2 colunas (`280px 1fr`), avatar circular 220px ├á esquerda, CTA 64px ├á direita
  - Avatar **sempre circular** (`border-radius: 50%` em todos viewports) com `object-fit: cover` + `object-position: center 18%` (rosto do mascote fica no topo do asset 700├ù1400)
  - CTA "Entrar com Google" paper (fundo navy-2) com sombra cyan brutalista (`box-shadow: 8px 8px 0 0 var(--dm-cyan)`)
  - Status em chips arredondados (`border: 1.5px solid`, estado `is-ok`/`is-warn`/`is-pending`)
  - Warn "login google pendente" sutil (fonte 11px, dot 6px, background amarelo 6% opacity)
- **O que FORA removido da v1.3:**
  - Stripe colorido `coral/yellow/cyan/purple` no topo (decorativo, distra├¡a)
  - Barra `DM//ACESSO` imitando janela de SO (gimmick desnecess├írio)
  - Mascote "espiando" o cart├úo com margin negativo (envelhece mal)
  - Grade t├®cnica 32├ù32 + 4 pixels coloridos no fundo (ru├¡do visual)
  - Anima├º├úo `mascot-bob` (chamativa demais pra primeira impress├úo)
  - 3 bolinhas coloridas de "controle de janela" (refer├¬ncia a macOS gratuita)
  - Linha de status no rodap├® do console (telemetria competindo com CTA)
  - **`styles.css` compartilhado** (vazava regras de dashboard/hub pra dentro do login)
- **O que ENTROU (v2.1):**
  - Arquivo `mockup/login.css` **isolado**, carregado S├ô pelo login.html (ver [ADR-011](#adr-011-css-isolado-por-p├ígina-cr├¡tica))
  - Wrappers sem├ónticos `.login-left` (marca + avatar) e `.login-right` (copy + CTA + status)
  - Avatar circular 80px (mobile) ÔåÆ 220px (desktop), sempre circular, crop agressivo no topo
  - Eyebrow `HUB ┬À ACESSO` com barra cyan de 24px (sutil, elegante)
  - Restri├º├úo `acesso exclusivo ┬À helbertcurcio@gmail.com` em mono 10px (transparente)
- **Motivo:** Helbert disse explicitamente "a tela de login do HUB de IA da DevManiac's n├úo t├í legal, quero refazer ela do zero antes de seguir com esse projeto". A v1.3 tinha o problema cl├íssico de **decora├º├úo competindo com o CTA**. Princ├¡pio seguido: **uma tela, uma decis├úo**. A marca est├í no logo + avatar + tagline. O CTA est├í sozinho. O status est├í em chips.
- **Cuidado:** o `styles.css` compartilhado vazava regras de dashboard/hub (toolbar `.app-header`, classes de status) pra dentro do login ÔÇö gerava conflito de classes. Por isso a v2.1 migrou pra folha isolada. Detalhes em ADR-011.
- **Valida├º├úo:** Playwright headless em 3 viewports (390├ù844 mobile, 768├ù1024 tablet, 1280├ù800 desktop). Screenshots em `C:\Users\Helbert\AppData\Local\Temp\login2-{mobile,tablet,desktop}.png`. Hierarquia confirmada: olho vai pro CTA depois do avatar.
- **Status:** Ô£à v2.1 validada e aprovada pelo Helbert (Telegram); deploy + commit pendentes na pr├│xima rodada.

### [ADR-011] CSS isolado por p├ígina cr├¡tica (Rodada 23/08 ┬À Hermes/M3 DM Agent)
- **Decis├úo:** P├íginas com identidade visual forte e fluxo pr├│prio (login, offline, error pages) ganham **folha CSS pr├│pria** + **breakpoint pr├│prio**, carregada exclusivamente por aquela p├ígina. Outras p├íginas continuam compartilhando o `styles.css` global.
- **Contexto:** Na v1.4 do login, ao editar a se├º├úo `.login-page` do `styles.css` compartilhado, **regras do dashboard/hub vazaram pro login** ÔÇö classes como `.app-header` (toolbar do hub interno) interferiam na cascata do login. O sintoma mais ├│bvio: o login no celular parecia "toda quebrada" porque o Helbert abriu `hub.html` pensando ser login. Mesmo sem o bug de confundimento, o CSS compartilhado cria **acoplamento impl├¡cito**: editar login pode quebrar dashboard, e vice-versa.
- **Princ├¡pio:** p├íginas cr├¡ticas = isolamento; p├íginas utilit├írias = compartilhamento. Lista inicial:
  - `login.html` ÔåÆ `login.css` (isolado, j├í migrado)
  - `offline.html` ÔåÆ `offline.css` (a migrar)
  - `error.html` / `404.html` ÔåÆ `error.css` (a migrar)
  - `dashboard.html` / `hub.html` / `status.html` ÔåÆ continuam usando `styles.css` global (s├úo p├íginas "operacionais" sem identidade de marca forte)
- **Mec├ónica t├®cnica:** o `mockup/router.php` precisa ter rota expl├¡cita pra cada folha isolada (ex: `/login.css` ÔåÆ `__DIR__ . '/login.css'`) com `Content-Type: text/css` e `Cache-Control: public, max-age=300` (cache curto pra iterar). A folha global `styles.css` continua servida pelo fallback est├ítico do built-in PHP server.
- **Motivo:** desacoplar risco de regress├úo visual entre p├íginas; permitir itera├º├úo visual do login sem medo de quebrar o hub. **Custo:** +1 arquivo CSS por p├ígina cr├¡tica + 5 linhas de router por folha. **Benef├¡cio:** zero vazamento de regras, valida├º├úo visual isolada, rollback seguro.
- **Status:** Ô£à aplicado no login (v2.1). Pr├│ximas p├íginas cr├¡ticas a migrar quando forem retrabalhadas.

---

### [ADR-009] SSO Hub ÔåÆ Code-server via cookie HMAC + Caddy forward_auth (Rodada 23/08 ┬À Z.AI ZCode)
- **Decis├úo:** Login ├║nico HubÔåÆcode-server implementado com cookie `dm_sso` assinado (HMAC-SHA256, payload `{email,exp}`, Domain `.devmaniacs.com.br`, 8h) emitido pelo Hub no login Google e validado no Rocky pelo container `hub-auth` (php:8.3-alpine) via `forward_auth` do Caddy. code-server com `auth: none` atr├ís do gate; `/healthz` livre pra watchdogs; `CODE_PASSWORD` fica s├│ pro sudo do terminal.
- **Motivo:** code-server n├úo suporta OAuth nativo; JWT-plugin do Caddy exigiria build custom. Cookie compartilhado entre subdom├¡nios do mesmo eTLD+1 funciona at├® dentro de iframe (SameSite=Lax) com zero depend├¬ncias novas. Cuidado registrado: `config.yaml` do code-server persiste `auth: password` ÔÇö remover o env n├úo basta (erro conhecido #9 do README do hub).

---

### [ADR-001] Topologia H├¡brida de Bancos PostgreSQL 16 (Rodada 133 ┬À Z.AI)
- **Decis├úo:** Tenants Enterprise (ex: Teenus) possuem banco PostgreSQL dedicado (`tenant_<slug>`), enquanto tenants Standard compartilham o banco `default` com segrega├º├úo por `tenant_id`.
- **Motivo:** M├íximo isolamento de dados de clientes grandes sem sobrecarregar o servidor com centenas de bancos para contas menores.

---

### [ADR-002] Esteira At├┤mica de Formaliza├º├úo 1-Clique (Rodada 134/140 ┬À Z.AI)
- **Decis├úo:** A convers├úo de Or├ºamento Ô×ö Contrato Ô×ö Obra roda em transa├º├úo ├║nica com `select_for_update` e m├®todo de maior res├¡duo (Largest-Remainder) normalizando a EAP para 100.00% exato.
- **Motivo:** Evita concorr├¬ncia duplicada e garante que se houver erro em tag de minuta jur├¡dica, todo o ciclo sofre rollback sem deixar dados ├│rf├úos.

---

### [ADR-003] Roteamento SPA Universal por Hash & Hist├│rico Nativo (Rodada 143 ┬À Gemini)
- **Decis├úo:** Sincroniza├º├úo de telas do frontend via `window.location.hash` e escuta aos eventos `popstate`/`hashchange`.
- **Motivo:** Permite links diretos, persist├¬ncia total no F5 e navega├º├úo nativa com os bot├Áes Voltar/Avan├ºar do navegador.

---

### [ADR-004] RDO Digital Offline-First & Sincroniza├º├úo Dexie IndexedDB (Rodada 150 ┬À Tr├¡ade)
- **Decis├úo:** O Di├írio de Obra (RDO) armazena registros e fotos comprimidas via Canvas API no IndexedDB local do celular, sincronizando automaticamente com o backend Django em transa├º├úo at├┤mica quando o sinal 4G ├® restabelecido. Clima registrado nos 3 turnos (Manh├ú/Tarde/Noite) para respaldo jur├¡dico de dias impratic├íveis.
- **Motivo:** Canteiros de obra t├¬m conex├úo intermitente. O mestre nunca pode perder o relat├│rio di├írio ou ficar travado sem sinal.

---

### [ADR-005] Compliance Trabalhista NR-06/NR-07 e Blindagem LGPD no RH (Rodada 152 ┬À Tr├¡ade)
- **Decis├úo:** O status de aptid├úo do ASO ├® sempre calculado dinamicamente em 4 bandas (30/15/5 dias e vencido). Colaboradores com ASO vencido s├úo automaticamente bloqueados na ingest├úo de RDOs com rollback total. Fichas de EPI exigem CA v├ílido e termo assinado digitalmente com SHA-256. CPFs s├úo mascarados por padr├úo (fail-closed).
- **Motivo:** Evita passivos trabalhistas graves em fiscaliza├º├Áes do MTE e garante conformidade estrita com a LGPD.

---

### [ADR-006] Dashboard Modular Adaptativa & Telemetria em Lote (Rodada 153 ┬À Tr├¡ade)
- **Decis├úo:** A Dashboard foi refatorada para arquitetura de widgets desacoplados. Widgets s├úo renderizados apenas se o m├│dulo correspondente estiver ativo no Tenant (`TenantConfig`). O usu├írio pode reordenar, ocultar/exibir e aplicar presets (Engenharia vs Financeiro). O backend agrega toda a telemetria em um ├║nico endpoint anti N+1 (`/api/v1/dashboard/telemetria/`).
- **Motivo:** Elimina polui├º├úo visual de m├│dulos inativos, acelera a velocidade de renderiza├º├úo para 0ms e atende perfeitamente perfis distintos de usu├írios (Mestre vs Diretor).

---

### [ADR-007] Painel de Configura├º├Áes da Empresa e Padroniza├º├úo Formal v1.0.0-ALPHA (Rodada 153 ┬À Tr├¡ade)
- **Decis├úo:** Criado o m├│dulo oficial de 'Configura├º├Áes da Empresa' para o cliente gerenciar sua pr├│pria equipe, identidade visual, SMTP pr├│prio e pol├¡ticas de 2FA. A vers├úo de release em toda a aplica├º├úo (login, footer, topbar e changelog) foi unificada formalmente como 'v1.0.0-ALPHA (Build 2026.08)'.
- **Motivo:** D├í total autonomia de gest├úo para o cliente fundador (Teenus) e alinha governan├ºa e transpar├¬ncia t├®cnica durante a fase de homologa├º├úo.

---

## ADR-012 ÔÇö Auth local email+senha+2FA (sem Google OAuth) ┬À SQLite ┬À dm_sso HMAC mantido

> **Status:** Aceita ┬À **Data:** 2026-08-23 ┬À **Decisor:** Helbert Moura (input) + Hermes/M3 (DM Agent)

### Contexto
Login era via Google OAuth (Client ID/Secret no `config.php`). Helbert precisava de: email `helbert.moura@devmaniacs.com.br`, senha pessoal, 2FA TOTP, sem depender do Google Cloud Console.

### Decis├úo
Substituir Google OAuth por auth local:
- **Stack:** PHP 8.3 (nativo) + SQLite (pdo_sqlite nativo) + bcrypt nativo (`password_hash`/`password_verify`) + TOTP RFC 6238 (custom PHP, validado contra pyotp)
- **Schema:** 3 tabelas no SQLite (`users`, `sessions`, `audit_log`) ÔÇö mesmo modelo do Postgres do Rocky, mas em arquivo local
- **Cookie SSO:** `dm_sso` HMAC-SHA256 (mantido 100% ÔÇö `hub-auth` no Rocky continua validando sem mudan├ºa)
- **2FA:** TOTP 6 d├¡gitos, janela ┬▒1 (3 codes v├ílidos), QR code provisioning via otpauth:// URI (futuro)
- **Anti-brute-force:** bloqueio ap├│s 5 tentativas erradas em 15 min
- **Remember me:** opcional 30 dias, s├│ com 2FA ativo
- **Audit:** `audit_log` table + fallback JSONL (`logs/audit-fallback.jsonl`) se DB cair

### Trade-offs
- Ô£à Zero infra (n├úo precisa container Postgres nem network)
- Ô£à Funciona offline
- Ô£à Compat├¡vel com Rocky (cookie SSO mesmo formato)
- Ô£à Backup trivial (`cp hub.sqlite backup.db`)
- ÔØî SQLite = 1 writer (n├úo escala pra >100 usu├írios)
- ÔØî Sem replica├º├úo (1 servidor s├│)
- ÔØî `function_exists` guards necess├írios em PHP multi-arquivo (LEARN-011)

### Por que N├âO Postgres do Rocky
- Postgres s├│ acess├¡vel dentro da rede Docker (`172.29.0.2:5432`), sem `ports:` mapping no docker-compose
- SSH tunnel funciona mas **autentica├º├úo scram-sha-256 rejeita a senha** quando vem via Windows (LEARN-009 tentativa)
- 3 inst├óncias Postgres locais conflitando na porta 5432 da2222
- 1 usu├írio (Helbert) n├úo justifica overhead de Postgres

### Por que N├âO Go
- gcc n├úo dispon├¡vel nativamente no Windows (WinLibs winget instalou parcialmente, false positive)
- Pure-Go SQLite (`modernc.org/sqlite`) precisa Go 1.21+ (temos 1.20)
- `mattn/go-sqlite3` (gold standard) precisa CGO+gcc
- PHP+SQLite j├í validado em produ├º├úo em <1 itera├º├úo

### Reversibilidade
Trocar `dm_pg_connect()` em `db.php` por vers├úo Postgres ├® trivial (interface id├¬ntica). Se um dia Helbert adicionar mais usu├írios ou quiser HA, migrar de SQLite pra Postgres ├® trocar 1 arquivo.

---

## ADR-013 ÔÇö Hub Remoto de IDEs: Descomissionamento e Remo├º├úo Completa

> **Status:** Descontinuada / Removida ┬À **Data:** 2026-08-23 ┬À **Decisor:** Helbert Moura

### Decis├úo de Descomissionamento
Por decis├úo estrat├®gica do fundador Helbert Moura em 23/08/2026, o projeto do Hub Remoto de IDEs foi **completamente desativado e removido**:
1. **Infraestrutura:** T├║neis Cloudflare `dm-hub` e `dm-code` exclu├¡dos; processos locais de backend e proxy finalizados.
2. **Automa├º├úo:** Tarefa agendada do Windows (`DM Hub Watchdog`) e scripts associados em `~/.cloudflared/` removidos.
3. **C├│digo:** Diret├│rio `projects/hub-remote-ide` removido do reposit├│rio local.
4. **Isolamento:** Nenhum outro projeto (CanteiroHUB, Biolar, HelpDev, DM-PDV, t├║neis corporativos) foi alterado ou impactado.

### Decis├úo
Reconstruir completamente o Hub Remoto como uma esta├º├úo central de comando operacional (Single Page Application com CSS e JS isolados sob a ADR-011):
1. **Workspaces Integrados:**
   - **VSCode Web:** Iframe din├ómico para `https://code.devmaniacs.com.br` com suporte a tela cheia, reload ass├¡ncrono e SSO autom├ítico via `dm_sso`.
   - **Gemini (Orquestrador):** Esta├º├úo de planejamento de rodadas, arquitetura e auditoria com templates de prompt prontos.
   - **MiniMax M3 (Heavy Builder):** Construtor de c├│digo Django REST e React com gerador de prompts integrado ao `SYSTEM_PROMPT_PADRAO_M3.md`.
   - **Z.AI Hermes (Deep Reasoning):** Esta├º├úo matem├ítica e criptogr├ífica (BDI TCU, Curva S, SEFAZ A1 XMLDSig).
   - **Monitor de Infraestrutura:** Monitoramento em tempo real do Servidor Rocky Linux 10.2 (`192.168.226.103`), cont├¬ineres Docker (Biolar, Teenus Dev/Prod, HelpDev) e T├║neis Cloudflare.
2. **Design System Solid-State (Chumbo & Vermelho):**
   - Paleta oficial s├│lida: Chumbo escuro (`#090D16`, `#111827`, `#151F30`), Vermelho Dev Maniac's (`#DC2626`, `#EF4444`).
   - Zero transpar├¬ncia difusa, zero neon, zero halos de brilho ou anima├º├Áes piscantes.
   - ├ìcones oficiais vetoriais de cada ferramenta (VSCode ribbon, Google Gemini 4-pointed star, MiniMax neural M, Z.AI monogram, Rocky Linux geometric mountain).
   - Layout `100dvh` com safe-areas iOS e alvos de toque m├¡nimos de 44px (`min-h-[44px]`).
   - Rodap├® com identifica├º├úo oficial: `┬® Dev ManiacÔÇÖs Systems ┬À 2026` e `Desenvolvido ├á base de Ôÿò e ÔÜí por Dev Maniac's`.
3. **Seguran├ºa & Gest├úo de Acesso:**
   - **Auth Guard Server-Side (Zero Flash):** Redirecionamento HTTP 302 direto no `router.php` para `/login` ao acessar `/hub.html` ou `/hub` sem sess├úo ativa (o browser nunca recebe HTML sem estar autenticado).
   - Valida├º├úo cont├¡nua de sess├úo via `/auth/me`.
   - Modal de Perfil com formul├írio de altera├º├úo de senha segura (`/auth/change-password`).
   - Service Worker bump para `dm-hub-v13`.


