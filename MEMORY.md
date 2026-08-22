---
titulo: Memória Central Permanente da Dev Maniac's
tags: [memory, contexto, permanente]
atualizado: 2026-08-22
status: ativo
---

# 🧠 MEMORY.md — Memória Central Permanente da Dev Maniac's
> **Fundador:** Helbert Moura (Engenheiro Sênior & Arquiteto Chefe)
> **Empresa:** Dev Maniac's Systems  
> **Diretriz de Design:** Industrial Solid-State (Azul Aço #1E40AF, Chumbo #0F172A, Fundo Sólido #F1F5F9, sem neon/gradientes).  
> **Proibição:** BANIMENTO TOTAL DE EMOJIS no UI de botões e tabelas — usar Lucide-React vetorial.  
> **Multi-Tenant Estrito:** Todo modelo novo deve herdar de `TenantAwareModel`.

---

## 🖥️ Topologia de Infraestrutura Real
- **Servidor Dedicado:** Rocky Linux 10.2 Red Quartz (`192.168.226.103`)
- **Acesso SSH:** `ssh root@192.168.226.103` (chave direta)
- **Hardware:** 1 TB NVMe SSD (12% uso), 32 GB RAM (29% uso), 16 vCPUs Dedicated Intel Xeon Silver.
- **Túnel Cloudflare:** `tunnel a0c5bea6-1a4b-4ffe-a041-da8cb18f419a` gerenciando domínios corporativos seguros HTTPS com SSL automático.

---

## 📦 Ecossistema de Produtos Ativos da Dev Maniac's
1. **CanteiroHUB / DM-ERP:** SaaS de gestão de obras e engenharia (instância piloto Teenus Gestão).
2. **Biolar Dedetizadora:** ERP operacional e financeiro de dedetização (`/opt/sistemas/biolar`).
3. **HelpDev:** Central de suporte técnico e chamados (`/opt/sistemas/helpdev`).
4. **DM-PDV:** Sistema de ponto de venda comercial rápido (`/opt/sistemas/dm-pdv`).
5. **Nextcloud Teenus & APAE:** Armazenamento seguro e suíte de escritório Collabora.
