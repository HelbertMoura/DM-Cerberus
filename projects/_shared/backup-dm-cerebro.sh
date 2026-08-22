#!/usr/bin/env bash
# ============================================================
# Script: backup-dm-cerebro.sh
# Descrição: Backup automático do Segundo Cérebro Dev Maniac's
# Agendamento: cron diário (03:00 AM)
# Owner: Helbert Moura · Dev Maniac's Systems
# Versão: 1.0 · 22/08/2026
# ============================================================

set -euo pipefail

# ─────────────────────────────────────────────
# CONFIGURAÇÕES — AJUSTAR ANTES DE USAR
# ─────────────────────────────────────────────

# Origem: onde está o clone do DM-Cerebro no servidor Linux
CEREBRO_DIR="/opt/devmaniacs/dm-cerebro"

# Destino local do tarball
BACKUP_DIR="/opt/backups/dm-cerebro"

# Dias para manter backups localmente
RETENTION_DAYS=30

# Backblaze B2 (opcional — descomentar para ativar)
# B2_BUCKET="dm-cerebro-backups"
# B2_APPLICATION_KEY_ID="xxx"
# B2_APPLICATION_KEY="xxx"

# ─────────────────────────────────────────────
# VALIDAÇÕES
# ─────────────────────────────────────────────

if [[ ! -d "$CEREBRO_DIR" ]]; then
  echo "❌ ERRO: Diretório $CEREBRO_DIR não existe."
  echo "   Execute: cd /opt/devmaniacs && git clone <repo> dm-cerebro"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

# ─────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/dm-cerebro_${TIMESTAMP}.tar.gz"

echo "🧠 Iniciando backup do DM-Cerebro..."
echo "   Origem: $CEREBRO_DIR"
echo "   Destino: $BACKUP_FILE"

# 1. Pull das últimas alterações (se for repo Git)
if [[ -d "$CEREBRO_DIR/.git" ]]; then
  echo "📥 Sincronizando com Git remoto..."
  cd "$CEREBRO_DIR"
  git pull --quiet origin main || echo "�️  Git pull falhou (offline?) — usando versão local"
fi

# 2. Criar tarball excluindo .git (economiza espaço)
echo "📦 Criando tarball..."
tar -czf "$BACKUP_FILE" \
  --exclude='.git' \
  --exclude='raw/processed' \
  -C "$(dirname "$CEREBRO_DIR")" \
  "$(basename "$CEREBRO_DIR")"

# 3. Verificar integridade
echo "🔍 Verificando integridade..."
if tar -tzf "$BACKUP_FILE" > /dev/null; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "✅ Backup criado com sucesso: $BACKUP_FILE ($SIZE)"
else
  echo "❌ ERRO: tarball corrompido!"
  exit 1
fi

# 4. Limpar backups antigos (manter últimos RETENTION_DAYS)
echo "🧹 Limpando backups > ${RETENTION_DAYS} dias..."
find "$BACKUP_DIR" -name "dm-cerebro_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 5. Upload para Backblaze B2 (opcional — descomentar para ativar)
# if command -v b2 &> /dev/null; then
#   echo "☁️  Enviando para B2..."
#   export B2_APPLICATION_KEY_ID="$B2_APPLICATION_KEY_ID"
#   export B2_APPLICATION_KEY="$B2_APPLICATION_KEY"
#   b2 authorize-account
#   b2 upload-file "$B2_BUCKET" "$BACKUP_FILE" "$(basename $BACKUP_FILE)"
# fi

echo "🎯 Backup concluído!"
