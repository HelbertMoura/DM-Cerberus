# 🔁 Cerberus Handoffs + Captura de Fim de Sessão
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)
> **Versão:** 1.0.0 (GOVERNANCA-CERBERUS-CAPTURE-001) · 08 de Setembro de 2026
> **Status:** Ativo — implementado e testado (263 testes, 100% verdes)
> **Complementa:** [`CERBERUS-MEMORY-ARCHITECTURE.md`](./CERBERUS-MEMORY-ARCHITECTURE.md), [`CERBERUS-ORCHESTRATOR-INTEGRATION.md`](./CERBERUS-ORCHESTRATOR-INTEGRATION.md), [`CERBERUS-AUTO-CAPTURE.md`](./CERBERUS-AUTO-CAPTURE.md)

---

## 🎯 1. Propósito

Absorver, do projeto `ai-memory` (akitaonrails, v2.x), os dois padrões com maior impacto no fluxo do maestri — **handoff tipado com claim único** e **captura automática de fim de sessão por hooks** — sem migrar de engine, sem daemon novo e **sem abrir mão do hardening 002** (entrada automática nunca escreve Markdown canônico; promoção é sempre humana).

O que foi deliberadamente **não** adotado: captura de chat bruto, consolidação automática em wiki sem gate humano, e o binário do ai-memory em si (Windows experimental; filosofia de captura incompatível com a governança local).

---

## 🔁 2. Protocolo de Handoff (claim-exactly-once)

Módulo: `engine/handoffs.py` (`HandoffStore`) · CLI: `cerberus handoff-*`

Um handoff é um registro tipado de delegação, armazenado em `.cerberus/handoffs/`. Estados:

```
OPEN ──claim──▶ CLAIMED ──complete──▶ DONE
  └────────────── cancel ───────────────▶ CANCELLED ◀── cancel (só o dono) ──┘
```

**Atomicidade do claim:** o gate é a criação exclusiva do marker `<id>.claim` (`O_CREAT | O_EXCL`), atômica em POSIX e NTFS. Em corrida de dois workers, exatamente um consegue reivindicar; o segundo recebe erro explícito. Isso elimina a classe de bug de duplo-claim/loops de delegação do canvas.

**Reserva por role:** `--to-role QA` impede que outra role reivindique (comparação case-insensitive; vazio = qualquer agente).

**Regras de Dono:**
- `complete` e `cancel` em estado CLAIMED só são aceitos do agente que reivindicou.
- `cancel` em estado OPEN é permitido a qualquer agente autorizado.

**Isolamento:** handoffs são estado operacional de workflow; nenhum método toca em `LEARNINGS.md`/`DECISIONS.md` (coberto por teste).

### CLI

```bash
cerberus handoff-create --task TASK-X --project biolar --summary "Corrigir template" \
                        --from-agent MAESTRO --to-role QA
cerberus handoff-claim  HDO-<id> --agent M3
cerberus handoff-done   HDO-<id> --agent M3 --result "Suíte verde 51/51"
cerberus handoff-cancel HDO-<id> --agent MAESTRO
cerberus handoff-list   [--status OPEN|CLAIMED|DONE|CANCELLED]
```

---

## 🧷 3. Captura de Fim de Sessão (hooks)

Script: `hooks/claude_session_capture.py`

Ligado como hook de fim de sessão nos harnesses. No encerramento, o script:

1. Lê o payload JSON do hook no stdin (compatível com payload `snake_case` — Claude Code/Qwen/Codex — e `camelCase` — Antigravity: `transcriptPath`, `conversationId`, `workspacePaths`).
2. Lê a cauda do transcript (máx. 256 KB, últimos 12 blocos de texto do assistente).
3. Extrai **apenas seções estruturadas** (`Learnings`/`Lições Aprendidas`/`Gotchas`/`Findings`, bullets ≥ 20 caracteres).
4. Cria **candidatos** na inbox (`.cerberus/inbox/`) com proveniência obrigatória: `task_id` (preferência: `TASK:`/`TASK-ID:` no conteúdo; fallback `SES-<session_id[:8]>`), `agent` = harness (`CLAUDE_CODE`, `CODEX`, `QWEN`, `AGY`), projeto resolvido por `detect_project_from_path(cwd)`.
5. Segredos são redigidos e o candidato vai `QUARANTINED` (herdado do pipeline).

**Garantias de governança (inalteradas):**
- Chat bruto nunca é fonte: sem seções estruturadas, **nada** é capturado (sem candidato "placeholder").
- Entrada automática nunca escreve no canônico — a promoção continua exigindo `cerberus review <id> --verify` + `promote <id> --apply` humanos.
- O script **nunca derruba a sessão**: qualquer falha sai 0 silenciosamente (ou com JSON de erro no stdout quando sem `--quiet`).
- `--quiet` para harnesses que interpretam stdout do hook de Stop (Antigravity pode reabrir o loop; Codex SessionEnd é advisory-only).
- Dedup por fingerprint: a mesma lição capturada por harnesses diferentes vira **um** candidato (`SKIPPED_DUPLICATE`).

---

## 🖥️ 4. Matriz de Harnesses (como ficou em 08/09/2026)

| Harness | MCP `cerberus-memory` | Hook de fim de sessão | Config (backup `.bak-capture-20260908`) |
|---|---|---|---|
| Claude Code (painéis do maestri) | já existia | ✅ `SessionEnd` (timeout 30s) | `~/.claude/settings.json` |
| ZCode CLI (painéis do canvas) | ✅ `mcp.servers` (schema estrito, paths absolutos) | ➖ não existe `SessionEnd`; `Stop` dispararia por turno (quente demais) — ficará MCP-only | `~/.zcode/cli/config.json` |
| Codex CLI | já existia | ✅ `SessionEnd` (timeout 3s, cap do Codex) — **exige trust no `/hooks` do Codex no 1º uso** | `~/.codex/hooks.json` (novo) |
| Qwen Code | ✅ `mcpServers` | ✅ `SessionEnd` (timeout 30000ms) | `~/.qwen/settings.json` |
| Crush | ✅ `mcp` (via wrapper `bin/cerberus-mcp.cmd`, pois não há `cwd`) | ➖ só existe `PreToolUse` — sem evento de fim de sessão | `%LOCALAPPDATA%\crush\crush.json` |
| Antigravity (agy/desktop) | ✅ `mcpServers` em `mcp_config.json` (env `PYTHONPATH`) | ⚠️ `Stop` (o mais próximo de fim de sessão; payload camelCase; `--quiet`) | `~/.gemini/config/mcp_config.json` + `~/.gemini/config/hooks.json` |

Observações:
- ZCode e Antigravity não possuem `SessionEnd` nativo; o `Stop` deles dispara a cada conclusão de resposta/execução — capturar por turno seria ruído e custo. Ficam MCP-only até existir evento de sessão.
- O parser do transcript é tolerante a drift de schema; em caso de formato desconhecido, degrada para "nada capturado" sem erro.
- Os MCPs e hooks entram em vigor nas **próximas sessões** de cada harness (painéis abertos devem ser reiniciados).

---

## 🔎 5. Fluxo Operacional no Maestri

```
Maestro delega          Worker executa                QA / Fecho
─────────────           ──────────────                ───────────
handoff-create          handoff-claim (atômico)       handoff-done --result
(to-role opcional)      → 1º que chegar ganha         QA aprova candidatos:
                                                      cerberus on-qa-approved
                                                      --task T --project P
Fim de sessão de qualquer painel:
hook → inbox (CANDIDATE) → PO revisa:
  cerberus inbox
  cerberus review <id> --verify
  cerberus promote <id> --apply
```

Recomendação de adoção: incluir no Task Contract do maestro a criação do handoff ao delegar e o `handoff-claim` como primeiro ato do executor — o claim vira a prova de quem assumiu o quê.

---

## 🧪 6. Testes e Evidências

- `tests/test_handoffs.py` (12) — ciclo completo, corrida de claim (marker pré-existente barrado com "already claimed"), reserva por role, regras de dono, id inválido, canônico intocado.
- `tests/test_session_capture.py` (5) — seções viram candidatos com proveniência; sem seções = inbox intacta; segredo = `QUARANTINED` redigido; transcript ausente = silêncio; fallback `SES-<id>`.
- E2E como subprocesso real: payload Claude → 2 candidatos; payload agy `--quiet` → saída limpa; dedup entre harnesses provado.
- Suíte completa: **263 testes, 100% verdes** (54–57s).
- `cerberus doctor`: FTS5 ok, inbox gravável, raiz canônica disponível.

---

## 🔙 7. Rollback

- Configs: restaurar os `*.bak-capture-20260908` (7 arquivos; lista na seção 4).
- Desligar captura sem rollback total: remover o bloco `hooks` correspondente no config do harness.
- Handoffs: estado transiente — deletar `.cerberus/handoffs/` não afeta conhecimento canônico.
- O script de wiring idempotente fica em `migra\scratch\wire-cerberus-harnesses-20260908.py`.

---

## 🛣️ 8. Pendências

1. **Codex:** aprovar o hook no `/hooks` (trust gate) na primeira execução.
2. **Installer:** estender `engine/installer.py` com `install_qwen/zcode/crush/agy` + `install_capture_hooks` para reproducibilidade (hoje o wiring foi executado pelo script de scratch).
3. **Maestri:** incluir handoff create/claim na diretriz/roles (decisão do PO).
4. **Vigiar:** `SessionEnd` no ZCode/Antigravity e hooks de fim de sessão no Crush (roadmap deles); se saírem, ativar aqui.
