---
titulo: Infraestrutura & Topologia do Servidor Dev Maniac's
tags: [infra, rocky-linux, docker, cloudflare]
atualizado: 2026-08-22
status: ativo
---

# 🖥️ Infraestrutura & Topologia do Servidor Dev Maniac's
> **IP Interno:** `192.168.226.103`
> **Sistema Operacional:** Rocky Linux 10.2 (Red Quartz) · Kernel 6.12  
> **SSH:** `ssh root@192.168.226.103` (chave direta configurada)  
> **Diretório Mestre:** `/opt/sistemas/`

---

## 🌐 Roteamento de Portas e Túneis Cloudflare

| Subdomínio / Domínio | Porta Local | Container / Serviço | Descrição |
| :--- | :---: | :--- | :--- |
| `erp.construtorateenus.com.br` | `:3100` | `teenus_prod_frontend` | CanteiroHUB Instância Teenus (PROD) |
| `canteirohub.devmaniacs.com.br` | `:3101` | `teenus_dev_frontend` | CanteiroHUB Master Lab (DEV) |
| `sistema.dedetizadorabiolar.com.br` | `:8000` | `biolar-app` | Dedetizadora Biolar (Django + Postgres 18) |
| `suporte.devmaniacs.com.br` | `:7070` | `helpdev-frontend` | Central de Suporte HelpDev |
| `pdv.devmaniacs.com.br` | `:3000` | `dm-pdv-frontend` | Ponto de Venda Dev Maniac's |
| `devmaniacs.com.br` | `:2543` | `portifoliodev` | Site Institucional Dev Maniac's |
| `drive.construtorateenus.com.br` | `:8281` | `teenus-drive-office-proxy` | Nextcloud 31 + Collabora Office Teenus |
| `drive.apaejuatubamg.com.br` | `:8181` | `apae-drive-office-proxy-1` | Nextcloud APAE Juatuba |
| `apaejuatubamg.com.br` | `:3001` | `apae-juatuba` | Portal Institucional APAE Juatuba |
| `monitoramento.apaejuatubamg.com.br`| `:8765` | `apae-juatuba-monitoramento` | Painel de Câmeras/Monitoramento APAE |
| `construtorateenus.com.br` | `:6969` | `teenus-construtora` | Site Institucional Construtora Teenus |
| `wec.ctsft.com.br` | `:5050` | `wec-sft` | Portal Corporativo WEC-SFT |

---

## 🗄️ Bancos de Dados PostgreSQL Ativos

- `teenus_prod_db`: PostgreSQL 16 (:5432 interno)
- `teenus_dev_db`: PostgreSQL 16 (:5435 mapeado para 127.0.0.1)
- `biolar-db`: PostgreSQL 18 (:5432 interno)
- `helpdev-db`: PostgreSQL (:5432 interno)
- `teenus-drive-postgres`: PostgreSQL (:5432 interno)
- `apae-drive-postgres-1`: PostgreSQL (:5432 interno)
