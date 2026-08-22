---
titulo: Arquitetura Técnica do CanteiroHUB
tags: [canteirohub, arquitetura, django, react]
atualizado: 2026-08-22
status: ativo
---

# 🏗️ Arquitetura — CanteiroHUB / DM-ERP

## Stack Atual

### Backend
- **Django 5.0** + Django REST Framework
- **PostgreSQL 16** (topologia híbrida — ver ADR-001)
- **Celery** + Redis (filas assíncronas)
- **Python 3.11**

### Frontend
- **React 18** + Vite
- **Tailwind CSS** (paleta Industrial Solid-State)
- **Lucide-React** (vetores, sem emojis no UI)
- **Dexie.js** (IndexedDB para offline-first)
- **PWA** habilitado (instalável mobile)

### Infraestrutura
- **Container:** Docker + Docker Compose
- **Servidor:** Rocky Linux 10.2 (192.168.226.103)
- **Túnel:** Cloudflare (`a0c5bea6-1a4b-4ffe-a041-da8cb18f419a`)
- **SSL:** Automático via Cloudflare
- **Backup:** Pendente (planejado para Q3)

## Topologia Multi-Tenant (ADR-001)

```
┌─────────────────────────────────────────────────┐
│         Master Admin (SaaS Hub)                 │
│         /opt/sistemas/dm-erp/master/            │
└──────────┬──────────────────────┬────────────────�
           │                      │
   ┌───────▼────────┐    ┌────────▼──────────┐
   │  Tenant ENTERPRISE │    │ Tenant STANDARD   │
   │  Banco dedicado    │    │ Banco compartilhado│
   │  tenant_<slug>     │    │ default + tenant_id│
   │  (ex: teenus)      │    │                   │
   └────────────────────┘    └───────────────────┘
```

## Padrões Arquiteturais

1. **Multi-tenant estrito:** Todo model herda de `TenantAwareModel`
2. **Esteira atômica:** Transições multi-step com `select_for_update` (ADR-002)
3. **SPA com hash routing:** Sem React Router, usa `window.location.hash` (ADR-003)
4. **Offline-first:** Dexie + service worker para uso em canteiro
5. **API REST versionada:** `/api/v1/...` com Django REST Framework

## Estrutura de Diretórios

```
/opt/sistemas/teenus-erp/
├── prod/
│   ├── backend/          ← Django
│   ├── frontend/         ← React
│   ├── docker-compose.yml
│   └── .env
└── dev/
    └── (mesma estrutura)
```

## ADRs Relacionadas
- [[DECISIONS#adr-001]] — Topologia híbrida de bancos
- [[DECISIONS#adr-002]] — Esteira atômica de formalização
- [[DECISIONS#adr-003]] — SPA com hash routing

---

**Owner:** Helbert Moura · **Última atualização:** 22/08/2026
