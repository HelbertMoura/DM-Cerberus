---
titulo: Watchdog — manter Hub sempre no ar
tags: [watchdog, tunnel, cloudflared, monitor, restart, devmaniacs, systemd, task-scheduler]
atualizado: 2026-08-23
status: ativo
---

# 🛡️ Watchdog — Manter Hub sempre no ar

> **Problema:** se o `cloudflared.exe` crashar, o PHP morrer ou o proxy SSH cair,
> o hub fica fora do ar ou o Rocky fica inacessível até alguém notar.

> **Estado:** ✅ **DEPLOYADO E TESTADO em 23/08/2026** — Windows (Task Scheduler)
> + Rocky (systemd timer).

---

## 🎯 O que o watchdog cobre

**No Windows (a cada 5 min + no logon):**

| # | Componente | Check | Recuperação |
|---|---|---|---|
| 1 | PHP mockup `127.0.0.1:8766` | porta escutando | sobe `php -S` de novo |
| 2 | Tunnel `dm-hub` | processo com `config.dm-hub.yml` | sobe `cloudflared tunnel run` |
| 3 | Tunnel `dm-code` | processo com `config.dm-code.yml` | sobe `cloudflared tunnel run` |
| 4 | Proxy SSH `127.0.0.1:2222` | porta escutando | sobe `cloudflared access tcp` |

Depois ainda valida ponta a ponta (`hub` e `code` remotos = 200).

**No Rocky (a cada 5 min + 2 min após boot):**

| Componente | Check | Recuperação |
|---|---|---|
| Stack docker hub-remote | `curl 127.0.0.1:8766/healthz` (2xx) | `docker compose up -d` → se falhar, `docker compose restart` |

> `healthz` com `{"status":"expired"}` **não é falha** (erro conhecido #8 do README) — o script só age em 4xx/5xx/timeout.

---

## 📂 Arquivos

**Windows:**

| Arquivo | Função |
|---|---|
| `C:\Users\Helbert\.cloudflared\watchdog-hub.sh` | watchdog v2 (one-shot + `--watch`) |
| `C:\Users\Helbert\.cloudflared\watchdog-hub.cmd` | wrapper pro Task Scheduler |
| `C:\Users\Helbert\.cloudflared\register-watchdog-task.ps1` | registra/reinstala a tarefa |

**Rocky:**

| Arquivo | Função |
|---|---|
| `/opt/scripts/watchdog-rocky.sh` | check + recuperação da stack |
| `/etc/systemd/system/dm-hub-watchdog.service` | unit oneshot |
| `/etc/systemd/system/dm-hub-watchdog.timer` | timer de 5 min |

**Fontes versionadas no projeto:** `scripts/rocky/` (sh + units systemd).

---

## 🚀 Uso

```bash
# Rodar o watchdog Windows na mão (só sobe o que faltar)
bash /c/Users/Helbert/.cloudflared/watchdog-hub.sh

# Disparar a tarefa agendada na hora
powershell -NoProfile -Command "Start-ScheduledTask -TaskName 'DM Hub Watchdog'"

# Rodar o watchdog Rocky na hora
ssh devmaniacs-vm "systemctl start dm-hub-watchdog.service"

# Reinstalar a tarefa Windows (após editar o script)
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\Helbert\.cloudflared\register-watchdog-task.ps1
```

---

## 📊 Logs

```
Windows: ~/.cloudflared/logs/
├── watchdog.log       # cada tick + o que foi recuperado
├── php-mockup.log     # output do PHP
├── dm-hub.log         # output do tunnel dm-hub
├── dm-code.log        # output do tunnel dm-code
└── ssh-proxy.log      # output do proxy SSH 2222

Rocky: /var/log/dm-hub-watchdog.log   # só recebe linha quando ALGO FALHOU
```

---

## 🧪 Teste de recuperação (já executado e aprovado em 23/08/2026)

```bash
# Windows: matar o proxy SSH e deixar o watchdog trazer de volta
# (feito: taskkill do processo da 2222 → Start-ScheduledTask → 2222 recuada + SSH OK)

# Rocky: derrubar o caddy e rodar o watchdog
ssh devmaniacs-vm "docker stop hub-caddy && systemctl start dm-hub-watchdog.service"
# (feito: healthz caiu → up -d re-subiu caddy → healthz OK em ~11s)
```

---

## ⚠️ Limitações e decisões

| Limitação | Detalhe |
|---|---|
| Sessão do usuário | A tarefa Windows roda na sessão do usuário (logon interactive). Tentamos S4U (rodar sem ninguém logado) mas o domínio `T2T3` nega — exige PowerShell elevado. Após reboot, tudo re-sobe no primeiro logon (trigger AtLogOn). |
| Sem duplicatas | O check de túnel é por linha de comando do processo (`config.dm-*.yml`). Se a consulta WMI falhar, trata como "rodando" — duplicar túnel é o bug do 502, pior que adiar um restart. |
| Quirk PowerShell 5.1 | `(Get-CimInstance ... | Where ...).Count` retorna **vazio** quando sobra 1 objeto escalar. Usar wrapper `@(...)`. |
| Processos destacados | **Bug corrigido em 23/08:** processos filhos do console da tarefa (`cmd→bash→nohup`) morriam ~30-60s após a tarefa concluir (fechamento de console = CTRL_CLOSE; o `php.exe` morria, `cloudflared` sobrevive). Todos os starts agora usam `Start-Process -WindowStyle Hidden` (grupo próprio). |
| Cloudflare outage global | Nada a fazer (raro). |
| Windows desligado | Hub cai (PHP + dm-hub estão aqui). code-server continua via dm-code... não — dm-code também roda no Windows. Tudo depende deste Windows ligado. |

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 23/08/2026
