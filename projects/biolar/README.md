---
titulo: Biolar Dedetizadora — Visão Geral
tags: [biolar, erp, django]
atualizado: 2026-08-22
status: ativo
---

# 🧪 Biolar Dedetizadora — ERP Operacional

> **Servidor:** `/opt/sistemas/biolar` no `192.168.226.103`
> **Git:** `https://github.com/HelbertMoura/PRD-BIOLAR.git`
> **Stack:** Django, PostgreSQL 18 (`biolar-db`), Docker Compose.
> **URL:** `https://sistema.dedetizadorabiolar.com.br` (:8000)

---

## 🎯 Visão Geral

ERP operacional e financeiro para Dedetizadora Biolar — empresa real em operação.
Foco em: agendamento, ordens de serviço, controle de produtos químicos, faturamento e
emissão fiscal (SEFAZ DF-e em desenvolvimento).

## Status Atual

| Componente | Status |
|---|---|
| Cadastros básicos | ✅ Produção |
| Agendamento de visitas | ✅ Produção |
| Ordem de serviço | ✅ Produção |
| Faturamento | � Em homologação |
| SEFAZ DF-e | 🔴 Em planejamento (Q4/2026) |
| WhatsApp bot | ⚪ Backlog |

## Próximas Entregas (ver [[ROADMAP]])

- **30/09/2026** — Migração Django 5.2 (MiniMax M3)
- **15/10/2026** — Módulo fiscal SEFAZ (Z.AI Hermes)

## Links Internos

- `status.md` — status detalhado por sprint
- `arquitetura.md` — stack e padrões técnicos
- `decisoes.md` — ADRs específicas do Biolar

---

**Owner:** Helbert Moura · **Última atualização:** 22/08/2026
