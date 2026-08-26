---
titulo: CanteiroHUB / DM-ERP (RadierHUB) — Índice do Projeto
tags: [canteirohub, radierhub, dm-erp, project-index]
atualizado: 2026-08-26
status: ativo
---

# 🏗️ CanteiroHUB / DM-ERP (RadierHUB) — Project Index

> **Slug:** `canteirohub` · **Nome oficial atual:** **RadierHUB** (rebranding ADR-008 canônico pós-r161)
> **Cliente fundador:** Construtora Teenus Ltda (instância `Teenus Gestão`)
> **Servidor:** `/opt/sistemas/teenus-erp/` em `192.168.226.103`
> **Domínio oficial:** `radierhub.com.br`
> **Cérebro específico (canônico):** `dm-erp/docs/brain/BRAIN.md` (no repositório `dm-erp`)
> **Status:** 6/16 módulos homologados (sprint Q3/2026)

---

## 1. Purpose

SaaS white-label multi-tenant para construtoras. ERP-âncora da Dev Maniac's. Cliente fundador é a Construtora Teenus (instância Teenus Gestão).

## 2. Status

| Item | Valor |
| :--- | :--- |
| Módulos homologados | 6 de 16 (Master Admin, Auth/Perfil, Dashboard, Obras, Orçamentos, Contratos) |
| Uptime DEV | 99.8% (últimos 30 dias) |
| Uptime PROD | 99.95% (últimos 30 dias) |
| Bugs críticos | 0 |
| Próxima entrega | Módulo 07 (Compras) — sprint atual (Z.AI Hermes) |

## 3. Tech Stack (declarado)

- **Backend:** Django 5.0 + DRF, Python 3.11, PostgreSQL 16 (topologia híbrida), Celery + Redis.
- **Frontend:** React 18 + Vite, Tailwind CSS, Lucide-React, Dexie.js (IndexedDB offline-first), PWA.
- **Infra:** Docker Compose, Rocky Linux 10.2, Cloudflare Tunnel (`a0c5bea6-…`), SSL automático.
- **Multi-tenancy:** Topologia híbrida (banco dedicado para Enterprise / pool compartilhado para Standard) — ver ADR-003 (canônico pós-r161).

## 4. Canonical Document Map (apenas o que existe no DM-CEREBRO)

> **Fonte canônica de verdade:** `dm-erp/docs/` (no repositório `dm-erp`). Os arquivos aqui no DM-CEREBRO são cópias de referência. Em caso de divergência, vence o `dm-erp/docs/`.

| Tópico | Arquivo no DM-CEREBRO | Fonte canônica dm-erp |
| :--- | :--- | :--- |
| Status | `projects/canteirohub/status.md` | `dm-erp/docs/PROJECT_STATE.md` |
| Arquitetura | `projects/canteirohub/arquitetura.md` | `dm-erp/docs/ARCHITECTURE.md` |
| Módulos roadmap | `projects/canteirohub/modulos-16-roadmap.md` | `dm-erp/docs/ROADMAP.md` |
| Auditoria 360 | `projects/canteirohub/auditoria-360-usabilidade.md` | (interno ao projeto) |
| Relatório final | `projects/canteirohub/relatorio-auditoria-final.md` | (interno) |
| Visão geral | `projects/canteirohub/README.md` | `dm-erp/AGENTS.md` |
| Wiki técnica | `wiki/projeto-radierhub-dmerp.md`, `wiki/engenharia-bdi-tcu.md`, `wiki/engenharia-eap-curvas.md`, `wiki/engenharia-rdo-digital.md`, `wiki/fiscal-sefaz-a1.md` | `dm-erp/docs/brain/wiki/*` |
| Decisões globais | `DECISIONS.md` (raiz) | `dm-erp/docs/DECISIONS.md` (canônico) |
| Handover global | `HANDOVER.md` (raiz) | (legado; substitui por sessões do `dm-erp`) |

## 5. Current Handover

Estado operacional detalhado em `dm-erp/HANDOVER.md` (no repositório). Resumo:
- v1.0.0-ALPHA em DEV e PROD.
- TASK-SEFAZ-002 (Ciclo 2 · Frente 3) concluída em 26/08/2026 (cofre A1, RBAC estrito, smoke 8/8 PASS).
- Próximas: TASK-SEFAZ-005 (Manifestação) → 006 (Integração Financeira) → 007 (Frontend).

## 6. Current Roadmap

- **30/09/2026** — Módulo 07 (Compras).
- **01/09/2026** — Módulo 08 (Medições) — Gemini owner.
- **15/09/2026** — Módulo 09 (Cronograma Físico) — backlog.
- Detalhes: `projects/canteirohub/modulos-16-roadmap.md` e `dm-erp/docs/ROADMAP.md`.

## 7. Important Decisions

ADRs ativos no `dm-erp/docs/DECISIONS.md` (numeração canônica pós-consolidação r161+):
- **ADR-001** Arquitetura Multi-Tenant com `TenantAwareModel` e Bancos Dedicados.
- **ADR-002** RDO Digital Offline-First com IndexedDB (Dexie).
- **ADR-003** Topologia Híbrida de Bancos PostgreSQL 16.
- **ADR-004** Esteira Atômica de Formalização 1-Clique.
- **ADR-005** Módulos Clientes (CRM) e Tarefas (Kanban) com Usabilidade Leiga & Isolamento por Papel.
- **ADR-006** Módulos Documentos (CNDs) e Notificações In-App.
- **ADR-007** Code-Splitting Total com React.lazy() & Suspense.
- **ADR-008** Rebranding Oficial do Produto SaaS para RadierHUB (`radierhub.com.br`).
- **ADR-009** Modal de Termos de Uso & Política de Privacidade LGPD Multi-Tenant.
- **ADR-010** Novo Modelo de Governança e Pipeline Multi-Agente com Gates Estritos.
- **ADR-011** Encerramento do Bootstrap de Governança — Decisões do Product Owner.
- **ADR-012** Automação Periódica do Robô SEFAZ DF-e com Cofre A1 Criptografado e Integração Financeira Atômica.
- **ADR-013** Blindagem Estrutural de Autenticação, Controle de Acesso e Isolamento Multi-Tenant.
- **ADR-014** Revisão da Hierarquia de Roteamento de IA (AI-GOV-STACK-HIERARCHY-008) — fonte de governança AI canônica para todo o DM-CEREBRO.

## 8. Document Routing Guide

| Tarefa | Ler (ordem) |
| :--- | :--- |
| Tarefa geral de produto | `dm-erp/docs/PROJECT_STATE.md` → `dm-erp/AGENTS.md` → `dm-erp/docs/ARCHITECTURE.md` → `dm-erp/HANDOVER.md` |
| Tarefa de segurança | `dm-erp/docs/DECISIONS.md` (ADR-013) + `global/security-baseline.md` (DM-CEREBRO) + `dm-erp/docs/brain/wiki/auditorias-tecnicas-cto.md` |
| Tarefa SEFAZ | `wiki/fiscal-sefaz-a1.md` + `dm-erp/docs/DECISIONS.md` (ADR-012) + `dm-erp/apps/nfe/` (código) |
| Tarefa de UI/UX | `dm-erp/AGENTS.md` §11 (Diretrizes Permanentes) + `dm-erp/docs/brain/wiki/acessibilidade-wcag.md` |
| Tarefa de banco de dados | `dm-erp/docs/DATABASE.md` + ADR-003 (topologia híbrida, canônico pós-r161) |
| Tarefa de IA | `dm-erp/docs/brain/wiki/protocolo-equipe-ai.md` (TASK-GOV-AI-008 / ADR-014) |
| Tarefa de gate de auditoria CTO | `dm-erp/docs/brain/wiki/auditorias-tecnicas-cto.md` |

## 9. Multi-tenancy (crítico)

**Todo** model de negócio herda de `TenantAwareModel`. Toda query filtra por `tenant=request.tenant`. **Não** importar essa regra para projetos single-tenant (Biolar, HelpDev) — cada projeto tem seu próprio regime de isolamento.

## 10. Histórico

- **2026-08-22** — Estrutura inicial 10/10, status e arquitetura registrados.
- **2026-08-25** — TASK-SEFAZ-001 (SEFAZ DF-e arquitetura) aprovada pelo PO.
- **2026-08-26** — TASK-SEFAZ-002 (Cofre A1) e ADR-014 (revisão AI stack) concluídas.
- **2026-08-26** — Índice de projeto criado (esta entrada).

---

**Owner:** Helbert Moura — Dev Maniac's Systems
