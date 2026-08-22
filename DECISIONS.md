---
titulo: Registro de Decisões de Arquitetura (ADRs)
tags: [decisoes, adr, arquitetura]
atualizado: 2026-08-22
status: ativo
---

# ⚖️ DECISIONS.md — Registro de Decisões de Arquitetura (ADRs)

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
