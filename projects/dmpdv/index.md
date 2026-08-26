---
titulo: DM-PDV — Ponto de Venda — Índice do Projeto
tags: [dmpdv, project-index, pdv, comercial]
atualizado: 2026-08-26
status: ativo
---

# 🛒 DM-PDV — Ponto de Venda Dev Maniac's

> **Slug:** `dmpdv`
> **Servidor:** `/opt/sistemas/dm-pdv` em `192.168.226.103`
> **Domínio:** `pdv.devmaniacs.com.br` (:3000)
> **Status:** Backlog (depende de A1 do Biolar)

---

## 1. Purpose

Sistema de ponto de venda comercial rápido. Pretende ser a frente de vendas (NFC-e, SAT) que depende da esteira fiscal/SEFAZ do Biolar.

## 2. Status (resumo)

- **Status:** Backlog. Primeira venda real prevista para Dez/2026 (ver `ROADMAP.md`).
- Dependência crítica: Certificado A1 do Biolar (que vence Out/2026 e precisa ser renovado).

## 3. Tech Stack

> **UNKNOWN — NEEDS PO DECISION.** Não há `arquitetura.md` no DM-CEREBRO para DM-PDV. Apenas referências de domínio/porta.

- **Domínio:** `pdv.devmaniacs.com.br` (:3000).
- **Container:** `dm-pdv-frontend` (referência no `wiki/infra-servidor-rocky.md`).
- **Stack detalhada:** não documentada.

## 4. Canonical Document Map

| Tópico | Arquivo |
| :--- | :--- |
| Visão geral | `projects/dmpdv/README.md` |
| Status | `projects/dmpdv/status.md` |
| Wiki infra (cross) | `wiki/infra-servidor-rocky.md` |

## 5. Current Handover

Sem handover local dedicado. Acompanhar `HANDOVER.md` global.

## 6. Current Roadmap

- **Out/2026** — Renovar A1 do Biolar (pré-condição).
- **Dez/2026** — DM-PDV com NFC-e validado, primeira venda real processada.
- Q1/2027 — SAT (depende de A1).

## 7. Important Decisions

- **NÃO** comece DM-PDV sem resolver o A1 do Biolar. Coordenação obrigatória.

## 8. Document Routing Guide

| Tarefa | Ler (ordem) |
| :--- | :--- |
| Tarefa de produto | `projects/dmpdv/README.md` → `status.md` |
| Tarefa de infra | `wiki/infra-servidor-rocky.md` |
| Tarefa SEFAZ (preparação) | `wiki/fiscal-sefaz-a1.md` + ADR-012 do dm-erp |
| Renovação A1 | `global/security-baseline.md` + acompanhar Biolar |

## 9. UNKNOWN — Pedidos ao PO

- Stack detalhado (linguagem, framework, banco, integração com impressora fiscal).
- Multi-tenancy ou single-tenant?
- Handover local?
- ADR local?
- Quem é o owner do A1 compartilhado (Biolar ou DM-PDV)?

---

**Owner:** Helbert Moura — Dev Maniac's Systems
