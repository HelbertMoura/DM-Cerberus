---
titulo: Biolar Dedetizadora — Índice do Projeto
tags: [biolar, project-index, erp-dedetizacao]
atualizado: 2026-08-26
status: ativo
---

# 🐛 Biolar Dedetizadora — Project Index

> **Slug:** `biolar`
> **Servidor:** `/opt/sistemas/biolar` em `192.168.226.103`
> **Domínio:** `sistema.dedetizadorabiolar.com.br` (:8000) — secundário: `dedetizadorabiolar.com.br`
> **Status:** Em produção, sprint de migração Django 5.2 + módulo fiscal

---

## 1. Purpose

ERP operacional e financeiro de **dedetização** para a Biolar Dedetizadora. Cadastros, agendamento, OS, controle de produtos químicos, faturamento, e em breve módulo fiscal SEFAZ.

## 2. Status (resumo)

- **6/7 componentes** ativos ou em homologação.
- **Uptime produção:** 99.7% (últimos 30 dias).
- **OSs processadas/mês:** ~120.
- **Bugs críticos:** 0.
- **Sprint atual (Q3/2026):** Migração Django 5.2 + preparação módulo fiscal.

| # | Componente | Status |
| :--- | :--- | :--- |
| 01 | Cadastros básicos | ✅ Produção |
| 02 | Agendamento de visitas | ✅ Produção |
| 03 | Ordem de serviço (OS) | ✅ Produção |
| 04 | Controle de produtos químicos | ✅ Produção |
| 05 | Faturamento | 🟡 Homologação (testes finais com 2 clientes) |
| 06 | SEFAZ DF-e | 🔵 Planejamento (início 01/09) |
| 07 | WhatsApp bot | ⏸ Backlog (Q1/2027) |

## 3. Tech Stack

- **Backend:** Django 5 + Gunicorn.
- **Banco:** PostgreSQL 18 (`biolar-db`).
- **Container:** Docker Compose.
- **Proxy:** Cloudflare Tunnel.
- **SSL:** Automático.
- **Multi-tenancy:** **NÃO** — Biolar é single-tenant (instância dedicada).

## 4. Canonical Document Map

| Tópico | Arquivo |
| :--- | :--- |
| Visão geral | `projects/biolar/README.md` |
| Status | `projects/biolar/status.md` |
| Arquitetura | `projects/biolar/arquitetura.md` |
| Deploy | `projects/biolar/deploy.md` |
| Wiki técnica (cross-projeto) | `wiki/fiscal-sefaz-a1.md` (quando SEFAZ entrar) |

## 5. Current Handover

Último handover registrado em `HANDOVER.md` (raiz). Biolar não tem handover local dedicado — apontar para o global até que tenha volume próprio.

## 6. Current Roadmap

- **30/09/2026** — Migração Django 5.2 (owner: MiniMax M3).
- **15/10/2026** — Módulo fiscal SEFAZ (owner: Z.AI Hermes / GLM-5.3 Max se envolver cripto A1).
- **30/11/2026** — WhatsApp bot de agendamento.
- Q1/2027 — Demais melhorias.

## 7. Important Decisions

- ADR-003 do `dm-erp` (Topologia Híbrida de Bancos PostgreSQL 16 — canônico pós-r161) **NÃO** se aplica a Biolar — Biolar usa **um único banco dedicado** (`biolar-db`). Não importar a regra de multi-tenant do dm-erp.
- Certificado A1 vence em **Outubro/2026** — renovação urgente. Coordenação com equipe SEFAZ do dm-erp (cross-pollination) é desejável.

## 8. Document Routing Guide

| Tarefa | Ler (ordem) |
| :--- | :--- |
| Tarefa de produto | `projects/biolar/README.md` → `status.md` → `arquitetura.md` → `deploy.md` |
| Tarefa SEFAZ | `wiki/fiscal-sefaz-a1.md` + `dm-erp/docs/DECISIONS.md` (ADR-012) — compartilhar decisões |
| Tarefa de deploy | `projects/biolar/deploy.md` + `global/deploy-governance.md` (DM-CEREBRO) |
| Tarefa de segurança | `global/security-baseline.md` (DM-CEREBRO) — não herdar regras multi-tenant do dm-erp |
| Renovação A1 | `global/security-baseline.md` §2.3 + coordenação com dm-erp |

## 9. Bloqueios Conhecidos

- ⚠️ **Certificado A1 vence Out/2026** — ação de infra do PO (renovar + atualizar `vault` quando aplicável).

---

**Owner:** Helbert Moura — Dev Maniac's Systems
