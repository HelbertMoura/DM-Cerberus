---
titulo: HelpDev — Central de Suporte — Índice do Projeto
tags: [helpdev, project-index, helpdesk]
atualizado: 2026-08-26
status: ativo
---

# 🛟 HelpDev — Central de Suporte Dev Maniac's

> **Slug:** `helpdev`
> **Servidor:** `/opt/sistemas/helpdev` em `192.168.226.103`
> **Domínio:** `suporte.devmaniacs.com.br` (:7070)
> **Status:** Em produção, help desk operacional

---

## 1. Purpose

Central de suporte técnico e chamados para o ecossistema Dev Maniac's. Atende clientes internos (Biolar, dm-erp/Teenus, DM-PDV, devmaniacs.com.br) e externos.

## 2. Status (resumo)

- Em produção como help desk operacional.
- Em monitoramento pelo `Monitor de Infraestrutura` (Hub Remoto v3.0 histórico) — substituído pelo sistema de healthchecks do HelpDev.

## 3. Tech Stack

> **UNKNOWN — NEEDS PO DECISION.** Não há arquivo `arquitetura.md` no DM-CEREBRO para HelpDev. As informações disponíveis vêm apenas do README e do registro de porta/servidor.

- **Domínio:** `suporte.devmaniacs.com.br` (:7070).
- **Container:** `helpdev-frontend` + `helpdev-backend` (referência no `wiki/infra-servidor-rocky.md`).
- **Stack detalhada:** não documentada no DM-CEREBRO.

## 4. Canonical Document Map

| Tópico | Arquivo |
| :--- | :--- |
| Visão geral | `projects/helpdev/README.md` |
| Status | `projects/helpdev/status.md` |
| Wiki infra (cross) | `wiki/infra-servidor-rocky.md` |

## 5. Current Handover

Sem handover local dedicado. Acompanhar `HANDOVER.md` global.

## 6. Current Roadmap

- Q4/2026 — Dashboard executivo + métricas (ver `ROADMAP.md` global).
- v2 com integração WhatsApp Business (backlog).

## 7. Important Decisions

Nenhuma ADR local registrada no DM-CEREBRO.

## 8. Document Routing Guide

| Tarefa | Ler (ordem) |
| :--- | :--- |
| Tarefa de produto | `projects/helpdev/README.md` → `status.md` |
| Tarefa de infra | `wiki/infra-servidor-rocky.md` (mapa do servidor) |
| Tarefa de segurança | `global/security-baseline.md` |

## 9. UNKNOWN — Pedidos ao PO

- Stack detalhado (linguagem, framework, banco).
- Multi-tenancy ou single-tenant?
- Handover local?
- ADR local?

---

**Owner:** Helbert Moura — Dev Maniac's Systems
