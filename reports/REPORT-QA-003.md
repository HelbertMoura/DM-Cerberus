# REPORT-QA-003 — Independent Cerberus Memory Hardening Audit

TASK-ID: `CERBERUS-MEMORY-HARDENING-QA-003`  
ACTIVE ROLE: QA ENGINEER / MEMORY SAFETY AUDITOR / MCP PROTOCOL REVIEWER  
Data: 2026-08-30  
Escopo: auditoria independente e estritamente read-only do HARDENING-002

## Veredito

HARDENING_QA: NEEDS_FIXES  
CANONICAL_WRITE_PROTECTION: FAIL  
CANDIDATE_INBOX: PASS  
PROMOTION_GATE: FAIL  
SECRET_QUARANTINE: FAIL  
ROOT_DEDUP: PASS  
INDEX_DETERMINISM: PASS  
CLI_GLOBAL: PASS  
MCP_PROTOCOL: FAIL  
PROJECT_ISOLATION: FAIL  
FILESYSTEM_SAFETY: FAIL  
TESTS: 23 PASS / 0 FAIL na suíte existente; testes adversariais adicionais reproduziram 5 blockers HIGH/CRITICAL e 5 findings MEDIUM  
BLOCKERS: vazamento cross-project; raiz arbitrária via ambiente; candidato adulterável; filtro de segredos incompleto; diretório sensível indexável  
HIGH: ver seção Findings  
MEDIUM: ver seção Findings  
READY_FOR_COMMIT: NO

NO IMPLEMENTATION  
NO COMMIT  
NO PUSH

## Evidências positivas

- A suíte completa passou: `python -B -m unittest discover -s tests -v` → 23/23.
- Captura MCP e CLI normal criou somente candidato em `.cerberus/inbox/`; `LEARNINGS.md` permaneceu byte-idêntico.
- `promote <id>` mostrou diff e não escreveu no canônico.
- `promote <id> --apply` antes de `VERIFIED` falhou; após `review <id> --verify`, aplicou com task, agente, timestamp e fingerprint no texto.
- Token reconhecido foi redigido, entrou em `QUARANTINED` e não pôde ser verificado/promovido.
- `doctor`, `inbox`, `review`, `promote` e `reject` funcionaram pelo wrapper CMD a partir de `C:\`, contra raiz temporária.
- MCP real via `engine.cli mcp` respondeu somente JSON em stdout; stderr ficou vazio; não expôs shell, exec, read/write-file, promote ou rebuild.
- `dm-erp/docs/brain` foi removida como raiz redundante quando `dm-erp/docs` estava presente.
- Dois rebuilds do corpus real, em banco temporário e com ordem inversa de raízes, convergiram em 176 arquivos, 725 chunks e 1 rejeição sensível.
- Arquivo deletado foi removido de `file_meta`, documents e busca no cenário coberto.

## Findings

### CRITICAL-001 — Vazamento cross-project por classificação `_global`

Arquivos de `dm-erp/docs` são indexados usando esse próprio diretório como `root_path`. `resolve_project_and_type()` só vê o caminho relativo e classifica `BUSINESS_RULES.md` como `_global`. A busca de `CerberusMemoryService` inclui `_global` em qualquer projeto.

Reprodução isolada: documento exclusivo de dm-erp foi persistido como `('_global', 'BUSINESS_RULES.md')`; busca pelo marcador com `project_id='biolar'` retornou o documento.

Referências: `engine/parser.py:49-59`, `engine/cli.py:26-34`, `engine/mcp_server.py:17-22`, `engine/retrieval.py:23-29`.

Impacto: quebra direta do isolamento lógico entre projetos e exposição de regras específicas como governança global.

### HIGH-001 — `CERBERUS_ROOT` aceita filesystem arbitrário

CLI e MCP confiam integralmente em `CERBERUS_ROOT`, sem allowlist ou metadata de projeto. Uma raiz temporária arbitrária foi aceita; o MCP criou `.cerberus/index.db` nela e a tornou raiz de indexação/captura.

Referências: `engine/cli.py:26-34`, `engine/mcp_server.py:17-22`.

Impacto: qualquer processo capaz de definir o ambiente pode redirecionar leitura recursiva e escrita da inbox para diretório acessível fora das raízes canônicas aprovadas.

### HIGH-002 — Candidato adulterado ignora fingerprint e quarantine

`CandidateStore.get()` desserializa `content`, `status` e `fingerprint`, mas não recalcula nem valida o fingerprint contra o payload. Em `%TEMP%`, um candidato seguro foi editado para conteúdo arbitrário e status `VERIFIED`; `promote --apply` gravou o payload adulterado em `LEARNINGS.md`.

Referências: `engine/capture.py:66-74`, `engine/capture.py:153-180`.

Impacto: fingerprint e proveniência são decorativos; alteração offline da inbox contorna review, secret filter e lifecycle.

### HIGH-003 — Filtro de segredos incompleto e compartilhado com o índice

Assignments genéricos de token/client-secret e Authorization header fora do início da linha não foram detectados nem redigidos. Como `engine/index.py` reutiliza o mesmo matcher, esses valores podem entrar em `documents.full_text` e FTS.

Referências: `engine/capture.py:15-42`, `engine/index.py:209-216`.

Impacto: candidatos contaminados podem permanecer `CANDIDATE`; documentos com credenciais não reconhecidas podem ser pesquisáveis.

### HIGH-004 — Diretórios sensíveis não são bloqueados por família

O filtro protege alguns nomes de arquivo, mas não diretórios como `secrets/`. Reprodução: `secrets/notes.md` foi indexado e encontrado por busca.

Referências: `engine/index.py:149-180`.

Impacto: a política de exclusão de secrets/credentials/token/private-key é contornável com filename neutro dentro de pasta sensível.

### MEDIUM-001 — Incremental confia somente em mtime

O código consulta `mtime, sha256`, mas pula o arquivo quando o mtime coincide sem comparar o hash. Após alterar conteúdo e restaurar o mtime, a indexação reportou skip; o marcador antigo permaneceu e o novo não apareceu.

Referência: `engine/index.py:194-200`.

### MEDIUM-002 — Validação MCP não aplica tipos nem versão JSON-RPC

Arguments com tipos incompatíveis retornaram `-32603` e detalhes internos (`int has no attribute strip`) em vez de `-32602`. Mensagens com `jsonrpc: '1.0'` ou sem `jsonrpc` foram aceitas como válidas.

Referências: `engine/mcp_server.py:187-252`.

### MEDIUM-003 — Uma entrada corrupta derruba `inbox`

`CandidateStore.list()` não isola erro por item. Um único JSON malformado provocou `ValueError` e impediu listar os demais candidatos.

Referência: `engine/capture.py:86-87`.

### MEDIUM-004 — Promoção não é transacional

Markdown canônico é substituído antes da persistência do estado `CANONICAL`, usando temp path compartilhado. Crash entre as duas escritas permite reaplicação; promoção concorrente pode colidir.

Referências: `engine/capture.py:165-180`.

### MEDIUM-005 — Installer não satisfaz validate/rollback/uninstall

O adapter Codex usa substring e considera até seção comentada como instalada. Adapters JSON sobrescrevem a entrada `cerberus-memory` existente; shape inesperado de `mcpServers` causa `TypeError`. Não existem operações de rollback ou uninstall.

Referências: `engine/installer.py:26-30`, `engine/installer.py:49-53`, `engine/installer.py:74-78`, `engine/installer.py:96-107`, `engine/installer.py:143-149`.

As configurações reais não foram executadas nem alteradas durante este QA; sua integridade foi verificada por SHA-256 antes/depois.

## Observações adicionais

- O wrapper CMD completou os comandos, porém texto PT-BR do diff exibiu caracteres de substituição no subprocesso capturado. Isso não alterou o Markdown gravado, mas merece teste explícito de code page/UTF-8.
- O relatório HARDENING-002 já reconhecia watcher, adapters restantes, auto-detecção e rollback completo como pendências; portanto o rollout multi-agente permanece corretamente bloqueado.
- O working tree já continha alterações alheias antes do QA, incluindo `.gitignore`, `LEARNINGS.md`, `MEMORY.md`, `global/ai-governance.md` e `global/model-routing.md`. Nenhuma foi atribuída ou modificada por esta auditoria.

## Matriz resumida

| Controle | Resultado | Evidência |
|---|---|---|
| Captura automática → inbox | PASS | MCP/CLI em raiz temporária; canônico intacto |
| Lifecycle nominal | PASS | CANDIDATE → VERIFIED → CANONICAL e REJECTED |
| Integridade do lifecycle | FAIL | JSON adulterado promovido |
| Preview sem apply | PASS | Diff gerado; bytes canônicos preservados |
| Quarantine reconhecida | PASS | Redação e bloqueio de verify/promote |
| Cobertura de segredos | FAIL | assignments/header não detectados |
| Root overlap | PASS | 3 raízes → 2 raízes normalizadas |
| Rebuild completo | PASS | duas execuções idênticas: 176/725/1 |
| Incremental/prune | PARTIAL | delete passa; mtime preservado fica stale |
| CLI global | PASS | wrapper CMD desde `C:\` |
| MCP stdout/tools | PASS | somente JSON; zero capability perigosa declarada |
| MCP validação estrita | FAIL | tipos e versão aceitos incorretamente |
| Project isolation | FAIL | dm-erp classificado `_global` e visível a biolar |
| Config integrity durante QA | PASS | hashes reais preservados |

## Comandos reproduzíveis

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -v
```

Os testes adversariais foram executados por scripts efêmeros enviados via stdin ao Python e usaram exclusivamente `%TEMP%` para candidatos, Markdown, configs fake e SQLite.

## Learnings

- Desduplicar roots não preserva isolamento automaticamente: a semântica do projeto precisa sobreviver à normalização da raiz.
- Fingerprint só protege integridade quando é recalculado e comparado antes de qualquer transição/promoção.
- Filtro de segredo baseado apenas em denylist precisa ser testado tanto na captura quanto na indexação, pois ambos compartilham o mesmo boundary.
- `mtime` é uma otimização, não prova de identidade; quando o SHA-256 já está armazenado, ignorá-lo cria stale index silencioso.
- Testes felizes de protocolo não substituem validação de tipos, versão JSON-RPC e inputs estruturalmente inválidos.

## Gate

**NO-GO.** Corrigir CRITICAL/HIGH, adicionar regressões adversariais e repetir QA em sessão limpa antes de qualquer commit ou rollout.

