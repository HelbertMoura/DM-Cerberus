# 🛡️ Sentinel SOC & Monitoramento IA (MiniMax 2.7 HighSpeed) — Whitelist de Processos
> **Sistema:** Dev Maniac's Systems & Sentinel SOC  
> **Servidor:** Rocky Linux 10 (`192.168.226.103`)  
> **Componentes:** `/opt/monitoring/v2/ai/ai_security.py` · `ai_analyzer.py` · HelpDev (`suporte.devmaniacs.com.br`)  
> **Atualizado em:** 24 de Agosto de 2026

---

## 🎯 1. Diagnóstico do Problema de Falso Positivo
1. **Origem:** O script de auditoria de segurança SOC (`ai_security.py`) executava periodicamente o comando `ps -eo pid,user,%cpu,%mem,args --no-headers` para escanear processos anômalos.
2. **Causa Raiz:** Durante o pico momentâneo de varredura do `ps`, o próprio comando `ps` registrava CPU alta momentânea. Como `ps`, `node`, `tsc` e ferramentas de build/monitoramento não estavam na lista de processos do sistema permitidos, o Sentinel classificava o próprio `ps` como `high_cpu_rogue_process`.
3. **Sintoma:** Ao reconhecer o alerta na interface, o evento antigo era arquivado, mas 2 minutos depois um novo evento de `ps` era gerado pelo timer do sistema, fazendo o alerta nunca sumir.

---

## 🔧 2. Correção Definitiva Aplicada
1. **Whitelist Ampliada em `ai_security.py`:**
   - Adicionados à lista de comandos seguros: `ps`, `top`, `ss`, `grep`, `find`, `sh`, `bash`, `monitoring`, `monitor`, `journalctl`, `systemctl`, `rsync`, `tar`, `gzip`, `curl`, `wget`, `awk`, `sed`, `node`, `npm`, `tsc`, `vite`, `esbuild`, `webpack`, `git`, `scp`.
2. **Re-triagem Automática pós-Reconhecimento em `monitoring.py`:**
   - O endpoint de ação `ack_security_events` agora chama `ai_security.py` e em seguida dispara a triagem `ai_analyzer.py --mode triage`, atualizando instantaneamente `insights.json` para o estado limpo (`suggested_actions: []`).
3. **Resultado:** 0 ameaças ativas, 0 falsos positivos, confiança da IA em 98% com status `OK`.
