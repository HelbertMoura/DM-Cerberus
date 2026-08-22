---
titulo: Procedimento de Backup do DM-Cerebro
tags: [backup, cron, devops, shared]
atualizado: 2026-08-22
status: ativo
---

# 💾 Backup do Segundo Cérebro

## 🎯 Objetivo

Garantir que o DM-Cerebro tenha backup automático diário, mesmo que você perca o servidor Rocky Linux.

---

## 📋 Procedimento de Instalação

### 1. Clonar o repo no servidor

```bash
# No servidor Rocky (192.168.226.103)
mkdir -p /opt/devmaniacs
cd /opt/devmaniacs
git clone git@github.com:DevManiacs/dm-cerebro.git
cd dm-cerebro
```

### 2. Instalar o script de backup

```bash
# Copiar para /usr/local/bin e dar permissão
sudo cp projects/_shared/backup-dm-cerebro.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup-dm-cerebro.sh

# Criar diretório de backup
sudo mkdir -p /opt/backups/dm-cerebro
sudo chown $USER:$USER /opt/backups/dm-cerebro
```

### 3. Configurar variáveis (editar o script)

Edite `/usr/local/bin/backup-dm-cerebro.sh` e ajuste:
- `CEREBRO_DIR` → onde o clone está (já sugerido: `/opt/devmaniacs/dm-cerebro`)
- `BACKUP_DIR` → onde salvar os tarballs
- `RETENTION_DAYS` → quantos dias manter (sugestão: 30)

### 4. Agendar no cron

```bash
crontab -e
```

Adicionar a linha (todo dia às 03:00):
```cron
0 3 * * * /usr/local/bin/backup-dm-cerebro.sh >> /var/log/dm-cerebro-backup.log 2>&1
```

### 5. Testar manualmente

```bash
sudo /usr/local/bin/backup-dm-cerebro.sh
ls -lh /opt/backups/dm-cerebro/
```

---

## � Restore (em caso de desastre)

```bash
# Localizar backup mais recente
ls -lt /opt/backups/dm-cerebro/ | head

# Extrair
tar -xzf /opt/backups/dm-cerebro/dm-cerebro_AAAAMMDD_HHMMSS.tar.gz -C /opt/devmaniacs/

# Pronto! Cérebro restaurado em /opt/devmaniacs/dm-cerebro/
```

---

## ☁️ Upload para B2 (opcional, recomendado)

Para backup off-site (Backblaze B2 é mais barato que AWS):

1. Instalar `b2` CLI: https://github.com/Backblaze/B2_Command_Line_Tool
2. Criar bucket: `dm-cerebro-backups`
3. Descomentar bloco B2 no script
4. Preencher `B2_APPLICATION_KEY_ID` e `B2_APPLICATION_KEY`
5. Custo estimado: ~$0.005/GB/mês (centavos)

---

## 📊 Verificação de Saúde

Para verificar se os backups estão funcionando:

```bash
# Tamanho médio dos últimos 7 backups
ls -lh /opt/backups/dm-cerebro/*.tar.gz | tail -7 | awk '{print $5}'

# Idade do backup mais recente
find /opt/backups/dm-cerebro -name "*.tar.gz" -mtime -1 | wc -l
# Deve retornar >=1 se rodou nas últimas 24h
```

---

**Última atualização:** 22/08/2026
