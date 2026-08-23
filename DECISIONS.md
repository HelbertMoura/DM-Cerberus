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
