---
titulo: INDEX.md — Mapa Mestre do Segundo Cérebro Dev Maniac's
tags: [index, mapa, indice, second-brain, master]
atualizado: 2026-08-26
status: ativo
---

# 🗺️ INDEX.md — DM-CEREBRO Master Map

> **Localização:** `C:\Users\Helbert\Desktop\DM-Cerebro\`
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)
> **Versão do schema:** Second Brain multi-projeto v1 (26/08/2026)
> **Autoridade canônica AI:** arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp` (cérebro do dm-erp / RadierHUB), registrado como `TASK-GOV-AI-008` · **ADR-014 (dm-erp)**. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. O **texto** é o que é canônico, não o link.
> **Ponto de entrada para qualquer agente:** [`AGENTS.md`](./AGENTS.md)

---

## 1. O que é o DM-CEREBRO

O **DM-CEREBRO** é o **Segundo Cérebro corporativo** da Dev Maniac's Systems. É um diretório de arquivos **Markdown simples** que serve como:

- Memória institucional de longo prazo (escrita por humanos e IAs);
- Mapa de conhecimento para onboarding de novos agentes e sessões;
- Registro de decisões, aprendizados, status e handoffs;
- Fonte canônica de regras globais que valem para **todos** os produtos.

**Não é:**
- Um CMS, wiki com build, ou sistema com dependências;
- Um substituto de documentação de produto (cada produto tem a sua, dentro de `projects/<slug>/`);
- Um clone de Notion/Obsidian/Logseq (é mais simples — é plain Markdown).

**Filosofia:** *plain Markdown files, semantic folders, one topic = one file, one root map/index, selective reading, minimal duplication, human-readable + AI-readable.*

---

## 2. Governança Global

Regras que valem para **TODOS** os produtos Dev Maniac's. Ficam em `global/`:

| Doc | Propósito |
| :--- | :--- |
| [`global/ai-governance.md`](./global/ai-governance.md) | Quem é o quê na equipe de IA. Referência ao `AI-GOV-STACK-HIERARCHY-008` (dm-erp) como fonte da verdade multimodelo. |
| [`global/model-routing.md`](./global/model-routing.md) | Bloco `MODEL ROUTING` canônico + decision tree + modos da GLM-5.3-Flash (MEDIUM/HIGH/MAX). |
| [`global/qa-policy.md`](./global/qa-policy.md) | Política de QA independente. Quem faz QA. Como separar PM de QA. |
| [`global/deploy-governance.md`](./global/deploy-governance.md) | State machine `IMPLEMENTED → VALIDATED → QA APPROVED → PO GATE → DEPLOYED → PRODUCTION VERIFIED → CLOSED`. |
| [`global/security-baseline.md`](./global/security-baseline.md) | Baseline de segurança que todo produto deve atender. |
| [`global/parallel-agents.md`](./global/parallel-agents.md) | Regra de paralelismo entre agentes (sem shared worktree, sem shared prod, etc.). |
| [`global/documentation-policy.md`](./global/documentation-policy.md) | Política de documentação: frontmatter, nomenclatura, one-topic-one-file, ADR, learnings. |
| [`global/langflow-rag-mcp-guide.md`](./global/langflow-rag-mcp-guide.md) | Padrão arquitetural de RAG visual com Langflow e exportação de servidores MCP para produtos. |
| [`global/skills-catalog.md`](./global/skills-catalog.md) | Catálogo canônico de skills externas adotadas (Ponytail, Osmani cherry-pick, Graphify), licenças e guardrails. |
| [`global/taxonomy.md`](./global/taxonomy.md) | Taxonomia canônica V2: distinção entre Knowledge, Skill, Task, Memory, Tool, Library, Pattern, Reference e Model + regra anti-bloat. |

---

## 2.1 Padrões de Interface (UI Pattern Library)

Padrões canônicos reutilizáveis de UX/UI mantidos em [`ui-patterns/`](./ui-patterns/):
- [`ui-patterns/navigation.md`](./ui-patterns/navigation.md) — Tabs, bottom nav, mobile safe areas, drawer.
- [`ui-patterns/forms.md`](./ui-patterns/forms.md) — Progressive forms, inline validation, masked inputs.
- [`ui-patterns/overlays.md`](./ui-patterns/overlays.md) — Dialogs, sheets, popovers, command palettes.
- [`ui-patterns/data-display.md`](./ui-patterns/data-display.md) — Master-detail, data grids densos, interactive cards.
- [`ui-patterns/interaction.md`](./ui-patterns/interaction.md) — Feedback, active indicators, purposeful motion.

---

## 3. Projetos Registrados

Cada projeto da Dev Maniac's tem sua pasta `projects/<slug>/` com **pelo menos** um `index.md` (mapa de roteamento). Demais arquivos são criados sob demanda.

| Slug | Nome | Status declarado | Index |
| :--- | :--- | :--- | :--- |
| `canteirohub` | CanteiroHUB / DM-ERP (RadierHUB) | Ativo, 6/16 módulos | [`projects/canteirohub/index.md`](./projects/canteirohub/index.md) |
| `biolar` | Biolar Dedetizadora | Ativo, em migração Django 5.2 | [`projects/biolar/index.md`](./projects/biolar/index.md) |
| `helpdev` | HelpDev — Central de Suporte | Ativo, help desk operacional | [`projects/helpdev/index.md`](./projects/helpdev/index.md) |
| `dmpdv` | DM-PDV — Ponto de Venda | Backlog (depende de A1 do Biolar) | [`projects/dmpdv/index.md`](./projects/dmpdv/index.md) |
| `apae-juatuba` | APAE Juatuba — Portais & Drive | Ativo, portais institucionais | [`projects/apae-juatuba/index.md`](./projects/apae-juatuba/index.md) |
| `dm-desk` | **UNKNOWN — NEEDS PO DECISION** | Não documentado | [`projects/dm-desk/index.md`](./projects/dm-desk/index.md) |
| `dev-maniacs-site` | **UNKNOWN — NEEDS PO DECISION** | Não documentado | [`projects/dev-maniacs-site/index.md`](./projects/dev-maniacs-site/index.md) |
| `hub-remote-ide` | **HISTORICAL** (descontinuado em 23/08/2026) | Apenas referência histórica | `archive/historical/hub-remote-ide.md` |
| `_shared` | Conhecimento cross-product (legado) | Mantido, em migração para `global/` | [`projects/_shared/`](./projects/_shared/) |

> **DM-DESK** e **DEV-MANIACS-SITE** foram listados como "a registrar" pelo PO, mas não existe conhecimento técnico deles no DM-CEREBRO. Criei o esqueleto com flag `UNKNOWN — NEEDS PO DECISION` em vez de inventar.

---

## 4. Read Order Canônico V2 (Minimal Persistent Context & Progressive Loading)

A leitura do cérebro é **estritamente proporcional ao escopo da tarefa**:

```text
TAREFA TRIVIAL (typo, 1 linha, estilo isolado)
→ Ler apenas o arquivo alvo + teste local imediato. Zero overhead.

TAREFA NORMAL DE COMPONENTE / FEATURE (via Task Contract)
1. Task Contract (recebido do Maestro)
2. Arquivos-alvo do escopo + DESIGN.md (se UI)
3. Referências específicas sob demanda (ex: ui-patterns/ ou skills/<skill>/references/)
4. Testes locais e correlacionados

TAREFA ESTRUTURAL / ARQUITETURA / SEGURANÇA
1. /AGENTS.md + /global/security-baseline.md ou /global/ai-governance.md
2. /projects/<slug>/index.md + architecture.md / decisions.md
3. Gate formal e suíte abrangente
```

> **Regra V2 de Ouro:** NUNCA force o agente a reler o cérebro inteiro para consertar um botão. Carregue apenas o que o Task Contract delimitar.

---

## 5. Source-of-Truth Rule

> **Cada regra/conhecimento tem UM documento canônico. Outros arquivos REFERENCIAM esse documento.**

Exemplos:

- Quem define o modelo AI para o dm-erp? arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp` (registrado como `TASK-GOV-AI-008` · **ADR-014 (dm-erp)**) — `global/ai-governance.md` deste cérebro apenas referencia; o **texto** é o que é canônico.
- Quem define a topologia do servidor? `wiki/infra-servidor-rocky.md` (legado global, mantido) · projetos individuais linkam.
- Quem define regra de UI industrial? `dm-erp/AGENTS.md §11` (canônico) — projetos fora do dm-erp referenciam.

**Não copiar** blocos grandes de política entre arquivos Markdown. Use `@path` ou `[descrição](./path.md)`.

---

## 6. Project Isolation Rule

> **GLOBAL define HOW we work. PROJECT define WHAT we are working on. Nunca aplique silenciosamente as suposições técnicas de um projeto a outro.**

Exemplos práticos:

- Biolar usa Django 5.2 com Postgres 18. HelpDev é Next.js com SQLite. **Não** presuma Postgres no HelpDev.
- dm-erp é multi-tenant. Biolar é single-tenant. **Não** aplique `TenantAwareModel` no Biolar.
- dm-erp tem deploy via systemd timer (sem Celery). Biolar pode usar Celery sem problema. **Não** force a regra do dm-erp no Biolar.

Cada `projects/<slug>/index.md` declara seu **tech stack** e seu **regime de multi-tenancy**. Respeite.

---

## 7. History / Archive Policy

Histórico de decisões é **preservado** (não reescrito):

- `DECISIONS.md` na raiz contém ADRs globais. **Não** reescrever ADRs antigos para refletir a realidade atual — se uma decisão mudou, criar **novo** ADR superseding.
- `LEARNINGS.md` na raiz é **append-only** (nunca apagar, só adicionar).
- `HANDOVER.md` é append-only.
- `ROADMAP.md` é atualizado por sprint (marca de check / etiqueta, não reescrita).
- `MEMORY.md` contém apenas informação durável (convenção organizacional, identidade estável, princípios de longa duração). NÃO colocar: status de tarefa atual, bugs do dia, implementação de hoje, status transitório de quota.

Para arquivos/ADRs **substituídos** por versões mais novas:

- Mover para `archive/historical/` (apenas com aprovação do PO — ver `proposed-migration.md`).
- Marcar com banner `SUPERSEDED — ver <canônico novo>`.
- Preservar a leitura histórica.

---

## 8. Como adicionar um novo projeto

```text
1. Criar pasta /projects/<slug>/
2. Criar /projects/<slug>/index.md usando o template /templates/project-index.md
3. Preencher: nome, propósito, status, tech stack, mapa de docs, handover atual, roadmap, decisões importantes
4. Adicionar linha em §3 deste INDEX.md
5. NÃO pre-criar dezenas de arquivos vazios — só criar conforme a necessidade real
6. NÃO tocar nos arquivos de outros projetos
7. NÃO commitar — o PO revisa
```

**O que NÃO fazer:**

- ❌ Criar README.md gigante com tudo dentro.
- ❌ Replicar governança global no projeto.
- ❌ Inventar decisões técnicas que não foram tomadas.

---

## 9. Política de Memória (MEMORY.md)

`MEMORY.md` (raiz) contém **somente** informação durável e cross-produto:

- ✅ Convenção organizacional da empresa.
- ✅ Identidade estável de longo prazo (fundador, missão, marca-mãe).
- ✅ Princípios operacionais de longa duração.
- ✅ Infraestrutura que não muda (servidor, túnel, cloud account).

**NÃO colocar em MEMORY.md:**

- ❌ Status de tarefa atual, bug aberto, decisão de sprint.
- ❌ Métrica de uso de quota (transitório).
- ❌ Implementação de hoje (vai pra handover).
- ❌ Detalhe de produto específico (vai pra `projects/<slug>/`).

---

## 10. Política de Decisões (DECISIONS.md)

`DECISIONS.md` (raiz) registra **ADRs globais** (decisões que valem para todos os produtos).

- Use formato ADR (Architecture Decision Record) — Contexto · Decisão · Consequências.
- **Nunca** reescrever ADRs antigos.
- Mudança = **novo** ADR superseding (linkando o anterior).
- Decisões **locais** de um produto vão em `projects/<slug>/decisions.md`.

> O registro formal da evolução do DM-CEREBRO para este formato está em [`ARCHITECTURE-EVOLUTION-2026-08-26.md`](./ARCHITECTURE-EVOLUTION-2026-08-26.md) (criado nesta rodada, aguardando integração ao `DECISIONS.md` pelo PO).

---

## 11. Política de Lições (LEARNINGS.md)

`LEARNINGS.md` (raiz) é **append-only**. Lições **locais** de um produto vão em `projects/<slug>/learnings.md`.

**O que entra:**

- Erro de produção com causa raiz e fix.
- Gotcha de biblioteca com workaround.
- Decisão contraintuitiva com ADR relacionado.
- Padrão que funcionou em mais de um lugar.

**O que NÃO entra:**

- Status atual de bug (vai pra handover).
- Conhecimento de uso único (vai pro commit message).
- Tarefa em andamento (vai pra project-state).

---

## 12. Compatibilidade e Migração

A estrutura atual do DM-CEREBRO é parcialmente a target. Migração **proposta** mas **não executada** automaticamente — qualquer movimento destrutivo exige aprovação do PO. Ver [`proposed-migration.md`](./proposed-migration.md) para o plano aguardando gate.

**Status atual:**

- ✅ Criado: `AGENTS.md`, `INDEX.md`, `global/*.md` (sete docs), `templates/*.md` (cinco templates), `projects/*/index.md` (sete índices), `archive/historical/README.md`, `ARCHITECTURE-EVOLUTION-2026-08-26.md`, `proposed-migration.md`.
- 🟡 Legado mantido: `BRAIN.md` (agora redireciona para `INDEX.md`), `HANDOVER.md`, `LEARNINGS.md`, `ROADMAP.md`, `MEMORY.md`, `DECISIONS.md` (estado modificado pelo PO, não tocado nesta rodada), `wiki/`, `prompts/`, `raw/`, `projects/_shared/`, `projects/canteirohub/`, `projects/biolar/`, `projects/helpdev/`, `projects/dmpdv/`, `projects/apae-juatuba/`.
- ❌ NÃO movido: nada foi renomeado, deletado ou movido de pasta nesta rodada. Tudo é aditivo.

---

## 13. Histórico

- **2026-08-22** — Estrutura inicial 10/10 (Tríade Gemini + M3 + Z.AI Hermes), `BRAIN.md` como índice mestre, prompts e _shared definidos.
- **2026-08-23** — `hub-remote-ide` descontinuado (ver `archive/historical/`). SSO Hub ↔ code-server. Auth local email+senha+2FA. CSS isolado por página crítica.
- **2026-08-26** — **Evolução para Second Brain multi-projeto v1** (este documento). `AI-GOV-STACK-HIERARCHY-008` + ADR-014 do dm-erp referenciados como governança AI canônica. Criação de `AGENTS.md` + `INDEX.md` + `global/` + `templates/` + índices de projeto (esqueleto). Migração destrutiva adiada (ver `proposed-migration.md`).

---

**Última atualização:** 26 de Agosto de 2026 · **Owner:** Helbert Moura — Dev Maniac's Systems
