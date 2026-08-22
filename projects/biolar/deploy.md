---
titulo: Deploy do Biolar Dedetizadora
tags: [biolar, deploy, docker]
atualizado: 2026-08-22
status: ativo
---

# 🚀 Deploy — Biolar Dedetizadora

## Procedimento Padrão

```bash
# Via SSH no servidor 192.168.226.103:
cd /opt/sistemas/biolar
git pull origin main
docker compose build biolar-app
docker compose up -d biolar-app
```

## Rollback de Emergência

```bash
cd /opt/sistemas/biolar
git log --oneline -5                    # identificar commit bom
git checkout <commit-hash>
docker compose up -d --build biolar-app
```

## Variáveis de Ambiente (.env)

```env
DATABASE_URL=postgres://biolar_app:***@biolar-db:5432/biolar_db
SECRET_KEY=***
DEBUG=False
ALLOWED_HOSTS=sistema.dedetizadorabiolar.com.br,dedetizadorabiolar.com.br
```

## URLs

- **Produção:** https://sistema.dedetizadorabiolar.com.br
- **Domínio secundário:** https://dedetizadorabiolar.com.br
- **Porta interna:** :8000

---

**Última atualização:** 22/08/2026 · Migrado de wiki/projeto-biolar.md
