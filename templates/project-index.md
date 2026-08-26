---
titulo: Template — PROJECT INDEX
tags: [template, project-index, mapa-projeto]
atualizado: 2026-08-26
status: ativo
---

# 🗂️ <Project Name> — Project Index

> **Slug:** `<slug>`
> **Owner:** Helbert Moura — Dev Maniac's Systems
> **Status declarado:** ativo / draft / deprecated / historical

---

## 1. Purpose

<uma frase: o que este produto faz>

## 2. Status

| Item | Valor |
| :--- | :--- |
| <Indicador 1> | <valor> |
| <Indicador 2> | <valor> |
| <Indicador 3> | <valor> |

## 3. Tech Stack

- **Backend:** <...>
- **Frontend:** <...>
- **Banco:** <...>
- **Container/Deploy:** <...>
- **Multi-tenancy:** <SIM/NÃO — regime>

## 4. Canonical Document Map

> Listar **apenas** o que existe. Se não existe, marcar `UNKNOWN — NEEDS PO`.

| Tópico | Arquivo |
| :--- | :--- |
| Visão geral | `projects/<slug>/README.md` |
| Status | `projects/<slug>/status.md` |
| Arquitetura | `projects/<slug>/arquitetura.md` |
| Deploy | `projects/<slug>/deploy.md` |
| Decisões locais | `projects/<slug>/decisions.md` |
| Handover local | `projects/<slug>/handover.md` |
| Lições locais | `projects/<slug>/learnings.md` |
| Roadmap local | `projects/<slug>/roadmap.md` |

## 5. Current Handover

<resumo do estado operacional atual + link para handover detalhado>

## 6. Current Roadmap

- <data> — <entrega>
- <data> — <entrega>

## 7. Important Decisions

<Listar ADRs locais ativos + referência ao ADR global quando aplicável>

## 8. Document Routing Guide

> **NÃO** preload tudo. Ler só o task-relevant. **NÃO** criar arquivos vazios (`project-state.md`, `handover.md`, `security.md`, `database.md`, etc.) só para satisfazer o read order — se ausentes, o `index.md` age como router único.

| Tarefa | Ler (ordem) |
| :--- | :--- |
| Tarefa de produto | `index.md` → `project-state.md` (QUANDO PRESENTE) → `handover.md` (QUANDO PRESENTE) |
| Tarefa de segurança | `global/security-baseline.md` (DM-CEREBRO) + `security.md` local (QUANDO PRESENTE) |
| Tarefa de deploy | `deploy.md` (QUANDO PRESENTE) + `global/deploy-governance.md` |
| Tarefa de IA | `global/ai-governance.md` + `global/model-routing.md` |
| Tarefa de governança | `global/documentation-policy.md` + INDEX.md do DM-CEREBRO |

## 9. Multi-tenancy (quando aplicável)

<Descrever o regime: topologia híbrida / single-tenant / pool compartilhado. Apontar para ADR-001 do dm-erp se for híbrido.>

## 10. UNKNOWN — Pedidos ao PO

<Listar o que **não** está documentado e precisa de decisão>

---

**Owner:** Helbert Moura — Dev Maniac's Systems · **Última atualização:** AAAA-MM-DD
