---
titulo: Evolução do DM-CEREBRO para Second Brain multi-projeto (26/08/2026)
tags: [arquitetura, second-brain, evolucao, adr-proposto, multi-projeto]
atualizado: 2026-08-26
status: ativo
prioridade: maxima
---

# 🏛️ ADR Proposto — Evolução do DM-CEREBRO para Second Brain multi-projeto v1

> **Status:** **PROPOSTA** — aguardando integração pelo PO ao `DECISIONS.md` (raiz).
> **Por que este arquivo está separado:** o `DECISIONS.md` (raiz) tem mudanças não-commitadas do PO em 26/08/2026. Para não conflitar, esta ADR fica em arquivo próprio. O PO pode (a) integrar ao `DECISIONS.md`, (b) renumerar ADRs existentes, (c) descartar esta proposta.
> **Cross-reference:** arquivo `docs/DECISIONS.md` dentro do repositório `dm-erp`, ADR-014 (`AI-GOV-STACK-HIERARCHY-008`) — a governança AI canônica que governa esta evolução. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../migra/dm-erp/docs/DECISIONS.md#adr-014`; ajuste conforme seu layout local. O **texto** é o que é canônico, não o link.

---

## Contexto

Em 22/08/2026 o DM-CEREBRO foi estruturado com a Tríade (Gemini + MiniMax M3 + Z.AI Hermes) e 5 pastas de projetos (`canteirohub`, `biolar`, `helpdev`, `dmpdv`, `apae-juatuba`) + `hub-remote-ide` (descontinuado em 23/08/2026). Cada projeto tem `README.md` + `status.md`; alguns têm `arquitetura.md` e `deploy.md`. A wiki é compartilhada.

A partir de 25/08/2026 a operação evidenciou três pontos:

1. **Falta de governança global formalizada.** Não havia `AGENTS.md`, `INDEX.md`, `global/` ou `templates/`. Regras estavam espalhadas em `BRAIN.md` + `TRIADE_PROTOCOLO.md` + `CONTRATO_AGENTES.md` + prompts copy-paste. O `BRAIN.md` age como índice mestre, mas mistura **mapa**, **regras** e **histórico** no mesmo arquivo.

2. **Inconsistência entre projetos quanto à estrutura de arquivos.** `canteirohub` tem `arquitetura.md`, `biolar` tem `arquitetura.md` + `deploy.md`, `helpdev`/`dmpdv` têm só `README.md` + `status.md`. Não há um "formato canônico" por projeto.

3. **A governança AI do dm-erp (TASK-GOV-AI-008 / ADR-014) precisa ser referenciada** pelo DM-CEREBRO corporativo. Sem link explícito, novos agentes podem descobrir a hierarquia AI tarde demais.

## Decisão

DM-CEREBRO evolui para um **Second Brain multi-projeto** baseado em **plain Markdown files**, **semantic folders**, **one topic = one file**, **one root map/index**, **selective reading**, **minimal duplication**, **human-readable + AI-readable**.

### Estrutura Target (alvo, sem migração destrutiva automática)

```text
DM-CEREBRO/
├── AGENTS.md             ← ponto de entrada universal (NOVO)
├── INDEX.md              ← mapa mestre (NOVO)
├── MEMORY.md             ← já existe, mantido
├── DECISIONS.md          ← já existe, mantido; ADR desta evolução pendente integração
├── LEARNINGS.md          ← já existe, mantido
├── HANDOVER.md           ← já existe, mantido
├── ROADMAP.md            ← já existe, mantido
├── BRAIN.md              ← mantido como legacy redirect → INDEX.md
│
├── ARCHITECTURE-EVOLUTION-2026-08-26.md   ← este arquivo (NOVO)
├── proposed-migration.md                  ← plano aguardando gate do PO (NOVO)
│
├── global/                              ← governança cross-produto (NOVO)
│   ├── ai-governance.md
│   ├── model-routing.md
│   ├── qa-policy.md
│   ├── deploy-governance.md
│   ├── security-baseline.md
│   ├── parallel-agents.md
│   └── documentation-policy.md
│
├── projects/                             ← já existe, complementado
│   ├── canteirohub/
│   │   ├── README.md                     ← já existe (legado)
│   │   ├── status.md                     ← já existe (legado)
│   │   ├── arquitetura.md                ← já existe (legado)
│   │   ├── modulos-16-roadmap.md         ← já existe (legado)
│   │   ├── auditoria-360-usabilidade.md  ← já existe (legado)
│   │   ├── relatorio-auditoria-final.md  ← já existe (legado)
│   │   └── index.md                      ← NOVO (mapa de roteamento do projeto)
│   ├── biolar/                           ← complementado com index.md
│   ├── helpdev/                          ← complementado com index.md
│   ├── dmpdv/                            ← complementado com index.md
│   ├── apae-juatuba/                     ← complementado com index.md
│   ├── dm-desk/                          ← NOVA pasta, com index.md flag UNKNOWN
│   ├── dev-maniacs-site/                 ← NOVA pasta, com index.md flag UNKNOWN
│   └── _shared/                          ← mantido (legado, em migração futura)
│
├── templates/                            ← NOVO (templates oficiais)
│   ├── task.md
│   ├── handover.md
│   ├── decision.md
│   ├── audit.md
│   └── project-index.md
│
├── archive/                              ← NOVA pasta marker
│   └── historical/
│       └── README.md                     ← política de arquivo
│
├── wiki/                                 ← já existe, mantido (cross-produto destilado)
├── prompts/                              ← já existe, mantido (legado)
└── raw/                                  ← já existe, mantido (gaveta de ingestão)
```

### Princípios (registrados em [`/global/documentation-policy.md`](./global/documentation-policy.md))

1. **One File = One Topic.** Arquivos com ~500+ linhas devem ser fragmentados.
2. **Root Files Are Maps, Not Databases.** `AGENTS.md` e `INDEX.md` devem ser concisos; não acumular conteúdo.
3. **Global ≠ Project.** `GLOBAL` define *como trabalhamos*. `PROJECT` define *em que estamos trabalhando*. Não aplicar suposições técnicas cross-project.
4. **Single Source of Truth.** Cada regra tem um canônico. Outros arquivos **referenciam**, não duplicam.
5. **No Hallucination.** Informação ausente = `UNKNOWN — NOT DOCUMENTED — NEEDS PO DECISION`.
6. **Backward Compatibility.** Paths existentes podem ser referenciados por automação/prompts. **Não** mover/deletar cegamente.
7. **Multi-Modelo.** `AGENTS.md` e `INDEX.md` são canônicos. Entry-points específicos de modelo (`CLAUDE.md`, `QWEN.md`, etc.) devem apenas importar o canônico.

### Cross-Reference com a Governança AI (dm-erp)

Esta evolução **referencia** a governança AI canônica registrada no dm-erp:

- **dm-erp `docs/brain/wiki/protocolo-equipe-ai.md`** (TASK-GOV-AI-008 / **ADR-014**) — organograma, MODEL ROUTING, paralelismo, worktree, deploy state machine, failover. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. O **texto** é o que é canônico.
- **dm-erp ADR-014** — revisão da hierarquia de IA (26/08/2026).

Os arquivos `global/ai-governance.md` e `global/model-routing.md` do DM-CEREBRO **não duplicam** a fonte — apenas contextualizam para o multi-produto e adicionam guidance de aplicação em projetos fora do dm-erp.

## Motivo

- **Separação clara de poderes** (governança global vs. conhecimento de produto).
- **Roteamento explícito** (qualquer agente sabe o que ler para qual tarefa).
- **Contexto seletivo** (não preload o cérebro inteiro).
- **Compatibilidade** (estrutura atual mantida; novos arquivos são aditivos).
- **Cross-pollination** com dm-erp (referência clara à governança AI canônica).
- **Preparação para multi-produto crescente** (novos projetos ficam trivialmente adicionáveis).

## Consequências

- **Documento canônico** da equipe de IA do DM-CEREBRO: `global/ai-governance.md` + link para o canônico dm-erp.
- **Template oficial** de TASK: `templates/task.md` (com header de roteamento obrigatório incluindo `MODE` + 4 campos de paralelismo).
- **Templates de auditoria** do CTO: `templates/audit.md`.
- **Política de nomenclatura** consolidada em `global/documentation-policy.md`.
- **`projects/dm-desk/` e `projects/dev-maniacs-site/`** registrados como `UNKNOWN — NEEDS PO DECISION` (não inventar).
- **Sem migration destrutiva** nesta rodada (ver `proposed-migration.md` para o plano).
- **Sem commit** nesta rodada (o PO revisa e commita).

## Supersede

Esta proposta **não** substitui nenhuma ADR anterior (não havia ADR sobre o formato do DM-CEREBRO; o `BRAIN.md` agia como índice sem ser uma ADR formal).

Esta proposta **referencia**:

- `dm-erp/docs/DECISIONS.md` ADR-014 (AI-GOV-STACK-HIERARCHY-008).
- TASK-GOV-AI-003 (dm-erp, 26/08/2026).
- AI-GOV-MODEL-ROUTING-007 (dm-erp, 26/08/2026).

## Pendências

- [ ] **PO:** revisar este arquivo e integrar ao `DECISIONS.md` (raiz) se aprovado (renumerar como ADR apropriado).
- [ ] **PO:** decidir o status real de `dm-desk` e `dev-maniacs-site`.
- [ ] **PO:** revisar e aprovar `proposed-migration.md` antes de qualquer movimento destrutivo.
- [ ] **PO:** decidir destino de `projects/_shared/` (manter como legado ou migrar para `global/`).
- [ ] **PO:** comitar esta evolução + o restante do working tree (DECISIONS.md + 4 wiki não-commitados).

## Histórico

- **2026-08-22** — Estrutura inicial 10/10 do DM-CEREBRO com Tríade e 5 projetos.
- **2026-08-23** — `hub-remote-ide` descontinuado.
- **2026-08-25/26** — dm-erp TASK-SEFAZ-002 + TASK-GOV-AI-008 / ADR-014 concluídos.
- **2026-08-26** — **Esta proposta** — DM-CEREBRO evoluído para Second Brain multi-projeto v1 (apenas aditiva, sem migration destrutiva).

---

**Autor:** Helbert Moura — Dev Maniac's Systems · **Status:** PROPOSTA aguardando gate do PO
