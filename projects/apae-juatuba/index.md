---
titulo: APAE Juatuba — Portais & Drive — Índice do Projeto
tags: [apae, project-index, nextcloud, portal, filantropia]
atualizado: 2026-08-26
status: ativo
---

# 🏥 APAE Juatuba — Portais & Drive

> **Slug:** `apae-juatuba`
> **Cliente:** APAE Juatuba (entidade filantrópica)
> **Status:** Em produção, manutenção + migração Collabora 24.04

---

## 1. Purpose

Hospeda os sistemas da APAE Juatuba:
- Portal institucional público.
- Painel de monitoramento interno.
- Drive corporativo (Nextcloud + Collabora).

## 2. Status

| # | Componente | Status | Notas |
| :--- | :--- | :--- | :--- |
| 01 | Portal institucional (React) | ✅ Produção | `apaejuatubamg.com.br` (:3001) |
| 02 | Nextcloud Drive | ✅ Produção | `drive.apaejuatubamg.com.br` (:8181) |
| 03 | Collabora Online | ✅ Produção | Edição Office |
| 04 | Painel de monitoramento | ✅ Produção | `monitoramento.apaejuatubamg.com.br` (:8765) |
| 05 | Migração Collabora 24.04 | 🟡 Planejado | Q4/2026 (30/11/2026) |

## 3. Tech Stack

- **Nextcloud 31** (Hub 8).
- **Collabora Online** (edição Office).
- **React** para portal institucional.
- **Multi-tenancy:** NÃO (entidade única).

## 4. URLs Canônicas

| Função | URL | Porta |
| :--- | :--- | :---: |
| Portal institucional | `https://apaejuatubamg.com.br` | :3001 |
| Monitoramento | `https://monitoramento.apaejuatubamg.com.br` | :8765 |
| Nextcloud Drive | `https://drive.apaejuatubamg.com.br` | :8181 (office proxy) |

## 5. Canonical Document Map

| Tópico | Arquivo |
| :--- | :--- |
| Visão geral | `projects/apae-juatuba/README.md` |
| Status | `projects/apae-juatuba/status.md` |

## 6. Current Handover

Sem handover local dedicado. Acompanhar `HANDOVER.md` global.

## 7. Current Roadmap

- **30/11/2026** — Migração Collabora 24.04 (Z.AI Hermes owner).

## 8. Important Decisions

Nenhuma ADR local registrada no DM-CEREBRO. Projeto de baixo risco; mudanças seguem governança global padrão.

## 9. Document Routing Guide

| Tarefa | Ler (ordem) |
| :--- | :--- |
| Tarefa de produto | `projects/apae-juatuba/README.md` → `status.md` |
| Tarefa de infra | `wiki/infra-servidor-rocky.md` |
| Tarefa de segurança | `global/security-baseline.md` |

## 10. UNKNOWN — Pedidos ao PO

- ADR local? (provavelmente não — projeto simples).
- Handover local dedicado? (talvez não necessário pelo baixo volume).
- Stack do painel de monitoramento? (não documentado em detalhe).

---

**Owner:** Helbert Moura — Dev Maniac's Systems
