---
titulo: Registro de Decisões de Arquitetura (ADRs)
tags: [decisoes, adr, arquitetura]
atualizado: 2026-08-22
status: ativo
---

# ⚖️ DECISIONS.md — Registro de Decisões de Arquitetura (ADRs)

---

### [ADR-008] Google OAuth em PHP puro no Hub (sem NextAuth/Node) (Rodada 23/08 · Z.AI ZCode)
- **Decisão:** O login Google do `hub-remote-ide` roda em PHP puro (`mockup/router.php`, authorization code flow com state anti-CSRF e allowlist de e-mails), usando o PHP built-in server com router — mesma stack do mockup, sem build step.
- **Motivo:** NextAuth/Next.js exigiria um daemon Node permanente; o `serve.js` desta máquina tem histórico de crash (CSPNG assertion). PHP já é o runtime do mockup e do watchdog. Testado com credenciais fake: redirect, state, troca de token e tratamento de erro validados.

---

### [ADR-010] Login do Hub sob o princípio "Hub, apenas." (Rodada 23/08 · Hermes/M3 DM Agent — v2.1)
- **Decisão:** A tela de login do `hub-remote-ide` foi reconstruída **duas vezes** do zero — primeiro v1.4 (ainda no `styles.css` compartilhado), depois **v2.1 com CSS totalmente isolado** (`mockup/login.css`) — sob o conceito "Hub, apenas.": **mobile-first**, sem reaproveitar estrutura da v1.3. Foco #1 é o uso via celular (o Helbert acessa pelo bolso).
- **Arquitetura (v2.1):**
  - Mobile-first: shell vertical com `padding: 24px 16px`, max-width 480px, `min-height: 100dvh`
  - Tablet (≥640px): padding generoso, título 32px, CTA 60px altura
  - Desktop (≥1024px): grid 2 colunas (`280px 1fr`), avatar circular 220px à esquerda, CTA 64px à direita
  - Avatar **sempre circular** (`border-radius: 50%` em todos viewports) com `object-fit: cover` + `object-position: center 18%` (rosto do mascote fica no topo do asset 700×1400)
  - CTA "Entrar com Google" paper (fundo navy-2) com sombra cyan brutalista (`box-shadow: 8px 8px 0 0 var(--dm-cyan)`)
  - Status em chips arredondados (`border: 1.5px solid`, estado `is-ok`/`is-warn`/`is-pending`)
  - Warn "login google pendente" sutil (fonte 11px, dot 6px, background amarelo 6% opacity)
- **O que FORA removido da v1.3:**
  - Stripe colorido `coral/yellow/cyan/purple` no topo (decorativo, distraía)
  - Barra `DM//ACESSO` imitando janela de SO (gimmick desnecessário)
  - Mascote "espiando" o cartão com margin negativo (envelhece mal)
  - Grade técnica 32×32 + 4 pixels coloridos no fundo (ruído visual)
  - Animação `mascot-bob` (chamativa demais pra primeira impressão)
  - 3 bolinhas coloridas de "controle de janela" (referência a macOS gratuita)
  - Linha de status no rodapé do console (telemetria competindo com CTA)
  - **`styles.css` compartilhado** (vazava regras de dashboard/hub pra dentro do login)
- **O que ENTROU (v2.1):**
  - Arquivo `mockup/login.css` **isolado**, carregado SÓ pelo login.html (ver [ADR-011](#adr-011-css-isolado-por-página-crítica))
  - Wrappers semânticos `.login-left` (marca + avatar) e `.login-right` (copy + CTA + status)
  - Avatar circular 80px (mobile) → 220px (desktop), sempre circular, crop agressivo no topo
  - Eyebrow `HUB · ACESSO` com barra cyan de 24px (sutil, elegante)
  - Restrição `acesso exclusivo · helbertcurcio@gmail.com` em mono 10px (transparente)
- **Motivo:** Helbert disse explicitamente "a tela de login do HUB de IA da DevManiac's não tá legal, quero refazer ela do zero antes de seguir com esse projeto". A v1.3 tinha o problema clássico de **decoração competindo com o CTA**. Princípio seguido: **uma tela, uma decisão**. A marca está no logo + avatar + tagline. O CTA está sozinho. O status está em chips.
- **Cuidado:** o `styles.css` compartilhado vazava regras de dashboard/hub (toolbar `.app-header`, classes de status) pra dentro do login — gerava conflito de classes. Por isso a v2.1 migrou pra folha isolada. Detalhes em ADR-011.
- **Validação:** Playwright headless em 3 viewports (390×844 mobile, 768×1024 tablet, 1280×800 desktop). Screenshots em `C:\Users\Helbert\AppData\Local\Temp\login2-{mobile,tablet,desktop}.png`. Hierarquia confirmada: olho vai pro CTA depois do avatar.
- **Status:** ✅ v2.1 validada e aprovada pelo Helbert (Telegram); deploy + commit pendentes na próxima rodada.

### [ADR-011] CSS isolado por página crítica (Rodada 23/08 · Hermes/M3 DM Agent)
- **Decisão:** Páginas com identidade visual forte e fluxo próprio (login, offline, error pages) ganham **folha CSS própria** + **breakpoint próprio**, carregada exclusivamente por aquela página. Outras páginas continuam compartilhando o `styles.css` global.
- **Contexto:** Na v1.4 do login, ao editar a seção `.login-page` do `styles.css` compartilhado, **regras do dashboard/hub vazaram pro login** — classes como `.app-header` (toolbar do hub interno) interferiam na cascata do login. O sintoma mais óbvio: o login no celular parecia "toda quebrada" porque o Helbert abriu `hub.html` pensando ser login. Mesmo sem o bug de confundimento, o CSS compartilhado cria **acoplamento implícito**: editar login pode quebrar dashboard, e vice-versa.
- **Princípio:** páginas críticas = isolamento; páginas utilitárias = compartilhamento. Lista inicial:
  - `login.html` → `login.css` (isolado, já migrado)
  - `offline.html` → `offline.css` (a migrar)
  - `error.html` / `404.html` → `error.css` (a migrar)
  - `dashboard.html` / `hub.html` / `status.html` → continuam usando `styles.css` global (são páginas "operacionais" sem identidade de marca forte)
- **Mecânica técnica:** o `mockup/router.php` precisa ter rota explícita pra cada folha isolada (ex: `/login.css` → `__DIR__ . '/login.css'`) com `Content-Type: text/css` e `Cache-Control: public, max-age=300` (cache curto pra iterar). A folha global `styles.css` continua servida pelo fallback estático do built-in PHP server.
- **Motivo:** desacoplar risco de regressão visual entre páginas; permitir iteração visual do login sem medo de quebrar o hub. **Custo:** +1 arquivo CSS por página crítica + 5 linhas de router por folha. **Benefício:** zero vazamento de regras, validação visual isolada, rollback seguro.
- **Status:** ✅ aplicado no login (v2.1). Próximas páginas críticas a migrar quando forem retrabalhadas.

---

### [ADR-009] SSO Hub → Code-server via cookie HMAC + Caddy forward_auth (Rodada 23/08 · Z.AI ZCode)
- **Decisão:** Login único Hub→code-server implementado com cookie `dm_sso` assinado (HMAC-SHA256, payload `{email,exp}`, Domain `.devmaniacs.com.br`, 8h) emitido pelo Hub no login Google e validado no Rocky pelo container `hub-auth` (php:8.3-alpine) via `forward_auth` do Caddy. code-server com `auth: none` atrás do gate; `/healthz` livre pra watchdogs; `CODE_PASSWORD` fica só pro sudo do terminal.
- **Motivo:** code-server não suporta OAuth nativo; JWT-plugin do Caddy exigiria build custom. Cookie compartilhado entre subdomínios do mesmo eTLD+1 funciona até dentro de iframe (SameSite=Lax) com zero dependências novas. Cuidado registrado: `config.yaml` do code-server persiste `auth: password` — remover o env não basta (erro conhecido #9 do README do hub).

---

### [ADR-001] Topologia Híbrida de Bancos PostgreSQL 16 (Rodada 133 · Z.AI)
- **Decisão:** Tenants Enterprise (ex: Teenus) possuem banco PostgreSQL dedicado (`tenant_<slug>`), enquanto tenants Standard compartilham o banco `default` com segregação por `tenant_id`.
- **Motivo:** Máximo isolamento de dados de clientes grandes sem sobrecarregar o servidor com centenas de bancos para contas menores.

---

### [ADR-002] Esteira Atômica de Formalização 1-Clique (Rodada 134/140 · Z.AI)
- **Decisão:** A conversão de Orçamento ➔ Contrato ➔ Obra roda em transação única com `select_for_update` e método de maior resíduo (Largest-Remainder) normalizando a EAP para 100.00% exato.
- **Motivo:** Evita concorrência duplicada e garante que se houver erro em tag de minuta jurídica, todo o ciclo sofre rollback sem deixar dados órfãos.

---

### [ADR-003] Roteamento SPA Universal por Hash & Histórico Nativo (Rodada 143 · Gemini)
- **Decisão:** Sincronização de telas do frontend via `window.location.hash` e escuta aos eventos `popstate`/`hashchange`.
- **Motivo:** Permite links diretos, persistência total no F5 e navegação nativa com os botões Voltar/Avançar do navegador.

---

### [ADR-004] RDO Digital Offline-First & Sincronização Dexie IndexedDB (Rodada 150 · Tríade)
- **Decisão:** O Diário de Obra (RDO) armazena registros e fotos comprimidas via Canvas API no IndexedDB local do celular, sincronizando automaticamente com o backend Django em transação atômica quando o sinal 4G é restabelecido. Clima registrado nos 3 turnos (Manhã/Tarde/Noite) para respaldo jurídico de dias impraticáveis.
- **Motivo:** Canteiros de obra têm conexão intermitente. O mestre nunca pode perder o relatório diário ou ficar travado sem sinal.

---

### [ADR-005] Compliance Trabalhista NR-06/NR-07 e Blindagem LGPD no RH (Rodada 152 · Tríade)
- **Decisão:** O status de aptidão do ASO é sempre calculado dinamicamente em 4 bandas (30/15/5 dias e vencido). Colaboradores com ASO vencido são automaticamente bloqueados na ingestão de RDOs com rollback total. Fichas de EPI exigem CA válido e termo assinado digitalmente com SHA-256. CPFs são mascarados por padrão (fail-closed).
- **Motivo:** Evita passivos trabalhistas graves em fiscalizações do MTE e garante conformidade estrita com a LGPD.

---

### [ADR-006] Dashboard Modular Adaptativa & Telemetria em Lote (Rodada 153 · Tríade)
- **Decisão:** A Dashboard foi refatorada para arquitetura de widgets desacoplados. Widgets são renderizados apenas se o módulo correspondente estiver ativo no Tenant (`TenantConfig`). O usuário pode reordenar, ocultar/exibir e aplicar presets (Engenharia vs Financeiro). O backend agrega toda a telemetria em um único endpoint anti N+1 (`/api/v1/dashboard/telemetria/`).
- **Motivo:** Elimina poluição visual de módulos inativos, acelera a velocidade de renderização para 0ms e atende perfeitamente perfis distintos de usuários (Mestre vs Diretor).

---

### [ADR-007] Painel de Configurações da Empresa e Padronização Formal v1.0.0-ALPHA (Rodada 153 · Tríade)
- **Decisão:** Criado o módulo oficial de 'Configurações da Empresa' para o cliente gerenciar sua própria equipe, identidade visual, SMTP próprio e políticas de 2FA. A versão de release em toda a aplicação (login, footer, topbar e changelog) foi unificada formalmente como 'v1.0.0-ALPHA (Build 2026.08)'.
- **Motivo:** Dá total autonomia de gestão para o cliente fundador (Teenus) e alinha governança e transparência técnica durante a fase de homologação.

---

## ADR-012 — Auth local email+senha+2FA (sem Google OAuth) · SQLite · dm_sso HMAC mantido

> **Status:** Aceita · **Data:** 2026-08-23 · **Decisor:** Helbert Moura (input) + Hermes/M3 (DM Agent)

### Contexto
Login era via Google OAuth (Client ID/Secret no `config.php`). Helbert precisava de: email `helbert.moura@devmaniacs.com.br`, senha pessoal, 2FA TOTP, sem depender do Google Cloud Console.

### Decisão
Substituir Google OAuth por auth local:
- **Stack:** PHP 8.3 (nativo) + SQLite (pdo_sqlite nativo) + bcrypt nativo (`password_hash`/`password_verify`) + TOTP RFC 6238 (custom PHP, validado contra pyotp)
- **Schema:** 3 tabelas no SQLite (`users`, `sessions`, `audit_log`) — mesmo modelo do Postgres do Rocky, mas em arquivo local
- **Cookie SSO:** `dm_sso` HMAC-SHA256 (mantido 100% — `hub-auth` no Rocky continua validando sem mudança)
- **2FA:** TOTP 6 dígitos, janela ±1 (3 codes válidos), QR code provisioning via otpauth:// URI (futuro)
- **Anti-brute-force:** bloqueio após 5 tentativas erradas em 15 min
- **Remember me:** opcional 30 dias, só com 2FA ativo
- **Audit:** `audit_log` table + fallback JSONL (`logs/audit-fallback.jsonl`) se DB cair

### Trade-offs
- ✅ Zero infra (não precisa container Postgres nem network)
- ✅ Funciona offline
- ✅ Compatível com Rocky (cookie SSO mesmo formato)
- ✅ Backup trivial (`cp hub.sqlite backup.db`)
- ❌ SQLite = 1 writer (não escala pra >100 usuários)
- ❌ Sem replicação (1 servidor só)
- ❌ `function_exists` guards necessários em PHP multi-arquivo (LEARN-011)

### Por que NÃO Postgres do Rocky
- Postgres só acessível dentro da rede Docker (`172.29.0.2:5432`), sem `ports:` mapping no docker-compose
- SSH tunnel funciona mas **autenticação scram-sha-256 rejeita a senha** quando vem via Windows (LEARN-009 tentativa)
- 3 instâncias Postgres locais conflitando na porta 5432 da2222
- 1 usuário (Helbert) não justifica overhead de Postgres

### Por que NÃO Go
- gcc não disponível nativamente no Windows (WinLibs winget instalou parcialmente, false positive)
- Pure-Go SQLite (`modernc.org/sqlite`) precisa Go 1.21+ (temos 1.20)
- `mattn/go-sqlite3` (gold standard) precisa CGO+gcc
- PHP+SQLite já validado em produção em <1 iteração

### Reversibilidade
Trocar `dm_pg_connect()` em `db.php` por versão Postgres é trivial (interface idêntica). Se um dia Helbert adicionar mais usuários ou quiser HA, migrar de SQLite pra Postgres é trocar 1 arquivo.

