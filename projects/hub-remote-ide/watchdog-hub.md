---
titulo: Watchdog — manter Hub sempre no ar
tags: [watchdog, tunnel, cloudflared, monitor, restart, devmaniacs]
atualizado: 2026-08-23
status: ativo
---

# 🛡️ Watchdog — Manter Hub sempre no ar

> **Problema:** Se o Windows reiniciar ou o `cloudflared.exe` crashar, os tunnels caem e `hub.devmaniacs.com.br` retorna 502.

---

## 🎯 Solução

Script Bash que verifica o health check a cada 60 segundos e reinicia automaticamente.

**Arquivo:** `C:\Users\Helbert\.cloudflared\watchdog-hub.sh`

---

## 🚀 Uso

### Modo one-shot (subir tudo de novo)

```bash
bash /c/Users/Helbert/.cloudflared/watchdog-hub.sh
```

### Modo watch (monitor infinito)

```bash
bash /c/Users/Helbert/.cloudflared/watchdog-hub.sh --watch
```

---

## 🪟 Tornar persistente no Windows (Task Scheduler)

1. Abre **Task Scheduler** (`taskschd.msc`)
2. **Create Task** (não "Basic Task")
3. Aba **General**:
   - Name: `DM Hub Watchdog`
   - Run whether user is logged on or not ✅
   - Run with highest privileges ✅
4. Aba **Triggers**:
   - New → At startup
   - Delay: 30 seconds (deixa o Windows estabilizar)
5. Aba **Actions**:
   - New → Start a program
   - Program: `C:\Program Files\Git\bin\bash.exe`
   - Arguments: `--watch /c/Users/Helbert/.cloudflared/watchdog-hub.sh`
6. Aba **Conditions**:
   - ❌ "Start only if on AC power" (se for notebook)
7. Aba **Settings**:
   - Allow task to be run on demand ✅
   - If task fails, restart every: 1 minute

---

## 📊 Logs

```
~/.cloudflared/logs/
├── watchdog.log       # log principal (health checks)
├── dm-hub.log         # output do tunnel dm-hub
├── dm-code.log        # output do tunnel dm-code
└── python-mockup.log  # output do servidor mockup
```

**Ver logs em tempo real:**

```bash
tail -f /c/Users/Helbert/.cloudflared/logs/watchdog.log
```

---

## 🧪 Testar

```bash
# Matar tunnel manualmente
taskkill /F /IM cloudflared.exe

# Esperar 60 segundos
sleep 60

# Verificar log
tail -30 /c/Users/Helbert/.cloudflared/logs/watchdog.log

# Verificar health
curl -I https://hub.devmaniacs.com.br/login.html
curl -I https://code.devmaniacs.com.br/login
```

**Resultado esperado:** Watchdog detecta falha → reinicia tudo → health check volta a 200.

---

## ⚠️ Limitações conhecidas

| Limitação | Workaround |
|---|---|
| Watchdog só funciona se Windows estiver ligado | Adicionar UPS (nobreak) |
| Se o Docker do Rocky cair, code-server cai | Watchdog separado no Rocky via systemd |
| Se Cloudflare tiver outage global | Aguardar (raro) |
| Watchdog em Bash roda via Git Bash | Alternativa: Python script + Task Scheduler |

---

## 🐧 Versão Linux (pro Rocky)

Quando você quiser monitorar o Rocky também, cria `/opt/scripts/watchdog-hub-rocky.sh`:

```bash
#!/bin/bash
# Roda como systemd service
while true; do
    if ! curl -sf http://127.0.0.1:8766/healthz > /dev/null; then
        cd /opt/sistemas/hub-remote && docker compose restart code-server
        systemctl restart docker  # fallback extremo
    fi
    sleep 30
done
```

E registra como systemd timer.

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 23/08/2026
