#!/bin/bash
# =============================================================
# Dev Maniac's Hub — Watchdog Rocky (systemd timer)
# Mantém a stack docker hub-remote respondendo em :8766/healthz.
# Roda a cada 5 min via dm-hub-watchdog.timer.
# Deploy: /opt/scripts/watchdog-rocky.sh (chmod +x)
# =============================================================

COMPOSE_DIR="/opt/sistemas/hub-remote"
LOG="/var/log/dm-hub-watchdog.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

# rotação simples: > 500 KB mantém as últimas 300 linhas
if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 512000 ]; then
    tail -300 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

# healthz responde 200 mesmo com status "expired" (erro conhecido #8 do
# README — não é falha). curl -f só falha em 4xx/5xx/timeout.
if curl -sf -m 10 http://127.0.0.1:8766/healthz > /dev/null 2>&1; then
    exit 0
fi

log "AVISO: healthz falhou — recuperando stack..."
cd "$COMPOSE_DIR" || { log "ERRO: $COMPOSE_DIR nao existe"; exit 1; }

docker compose up -d >> "$LOG" 2>&1
sleep 10
if curl -sf -m 10 http://127.0.0.1:8766/healthz > /dev/null 2>&1; then
    log "OK: recuperado com docker compose up -d"
    exit 0
fi

log "ERRO: up -d nao resolveu — reiniciando stack..."
docker compose restart >> "$LOG" 2>&1
sleep 15
if curl -sf -m 10 http://127.0.0.1:8766/healthz > /dev/null 2>&1; then
    log "OK: recuperado com docker compose restart"
    exit 0
fi

log "CRITICO: stack continua fora do ar — intervencao manual necessaria"
exit 1
