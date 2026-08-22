# 🧪 Biolar Dedetizadora — ERP Operacional e Comercial
> **Diretório no Servidor:** `/opt/sistemas/biolar`  
> **Git:** `https://github.com/HelbertMoura/PRD-BIOLAR.git`  
> **URL Produção:** `https://sistema.dedetizadorabiolar.com.br` / `https://dedetizadorabiolar.com.br` (:8000)  
> **Stack:** Django, Gunicorn, PostgreSQL 18 (`biolar-db`), Docker Compose.

---

## 🚀 Como Fazer Deploy
```bash
# Via SSH no servidor:
cd /opt/sistemas/biolar
git pull origin main
docker compose build biolar-app
docker compose up -d biolar-app
```
