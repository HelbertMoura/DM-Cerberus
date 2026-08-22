---
titulo: Arquitetura Técnica do Biolar
tags: [biolar, arquitetura, django, postgres]
atualizado: 2026-08-22
status: ativo
---

# 🏗️ Arquitetura — Biolar Dedetizadora

## Stack Atual
- **Backend:** Django 5 + Gunicorn
- **Banco:** PostgreSQL 18 (`biolar-db`)
- **Container:** Docker Compose
- **Proxy:** Cloudflare Tunnel
- **SSL:** Automático

## Diretórios no Servidor
```
/opt/sistemas/biolar/
├── docker-compose.yml
├── backend/
├── frontend/  (se aplicável)
└── .env
```

## Próximas Mudanças (Q4/2026)
- Migração Django 5.2 (30/09)
- Módulo fiscal SEFAZ DF-e (15/10)

---

**Owner:** Helbert Moura · **Última atualização:** 22/08/2026
