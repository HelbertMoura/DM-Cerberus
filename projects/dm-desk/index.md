---
titulo: DM-DESK — Índice do Projeto (UNKNOWN — NOT DOCUMENTED)
tags: [dm-desk, project-index, unknown, needs-po]
atualizado: 2026-08-26
status: draft
---

# 🖥️ DM-DESK — Project Index

> **Status:** **`UNKNOWN — NOT DOCUMENTED — NEEDS PO DECISION`**

---

## ⚠️ 1. Por que este projeto está como `UNKNOWN`

A pasta `projects/dm-desk/` foi criada em 26/08/2026 como parte da evolução do DM-CEREBRO para o formato multi-projeto (ver [`ARCHITECTURE-EVOLUTION-2026-08-26.md`](../../ARCHITECTURE-EVOLUTION-2026-08-26.md)).

**Não existe conteúdo técnico** sobre `DM-DESK` no DM-CEREBRO hoje:
- Nenhum `README.md`, `status.md`, `arquitetura.md`, `deploy.md`.
- Nenhuma menção em `HANDOVER.md` (raiz).
- Nenhuma menção em `wiki/`.
- Nenhuma referência em `LEARNINGS.md` ou `DECISIONS.md` (raiz).

A *única* menção indireta está em `wiki/infra-servidor-rocky.md` (registro genérico do servidor) e em `LEARN-006` e `LEARN-011` (que mencionam o **Hub Remoto de IDEs** — projeto **descontinuado** em 23/08/2026; pode ser a origem conceitual do nome `DM-DESK`, mas isso é inferência, não fato documentado).

## 2. Conjecturas (NÃO FATOS)

A *especulação* abaixo é marcada como tal. **Não pode ser usada para implementação** até que o PO confirme.

- **Hipótese A:** DM-DESK é o sucessor / rebranding do `hub-remote-ide` (descontinuado).
- **Hipótese B:** DM-DESK é um **desktop shell / IDE unificada** que agrega Gemini (Antigravity) + MiniMax Code + Z.AI ZCode + VSCode Web sob um único lançador.
- **Hipótese C:** DM-DESK é o **painel NOC/SOC operacional** de monitoramento da infraestrutura (Citrus, Rocky, Cloudflare, integrações).

> Nenhuma das três foi confirmada nem rejeitada pelo PO. O esqueleto `dm-desk/noc-soc.md` e `dm-desk/ai-operations.md` mencionado no **brief** da task `DM-CEREBRO-SECOND-BRAIN-002` é **conjectura projetada**, não conhecimento existente.

## 3. Pendências ao PO (precisa de decisão)

Para preencher este `index.md` com verdade, o PO precisa responder:

1. **DM-DESK existe como produto?** (Yes/No). Se não, deletar esta pasta.
2. Se sim: **escopo real** — desktop shell, NOC/SOC, hub de IDEs, ou outra coisa?
3. **Stack planejada** (linguagem, framework, banco, single/multi-tenant).
4. **Status atual** — produção, em desenvolvimento, planejamento?
5. **Owner** — Helbert diretamente, ou alguém da equipe?
6. **Reposicionamento em relação ao `hub-remote-ide`** (descontinuado em 23/08/2026).

## 4. Esqueleto de rotas (NÃO IMPLEMENTAR até confirmação)

> A *target structure* da task original mencionava `projects/dm-desk/index.md`, `project-state.md`, `architecture.md`, `product.md`, `security.md`, `noc-soc.md`, `ai-operations.md`, `database.md`, `api.md`, `decisions.md`, `roadmap.md`, `handover.md`, `learnings.md`. **Não** criei nenhum desses arquivos além deste `index.md` por respeito à regra **"Only migrate knowledge that actually exists. Do not invent missing technical details."**

## 5. Read Order Provisional (somente após o PO confirmar)

Quando o PO confirmar o escopo, o read order típico será:
- `projects/dm-desk/index.md` (este arquivo, atualizado)
- `projects/dm-desk/project-state.md` (a criar)
- `projects/dm-desk/architecture.md` (a criar)
- `global/ai-governance.md` (para tasks de IA)
- `global/security-baseline.md` (security)

---

**Owner declarado:** Helbert Moura — Dev Maniac's Systems · **Owner efetivo:** `UNKNOWN — NEEDS PO DECISION`
