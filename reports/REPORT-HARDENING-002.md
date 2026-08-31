# REPORT-HARDENING-002

TASK-ID: `CERBERUS-MEMORY-AUTOMATION-HARDENING-002`  
ACTIVE ROLE: SENIOR BACKEND ENGINEER / SECURITY GATEKEEPER  
Data: 2026-08-30

## Resultado

CERBERUS_AUTOMATION: NEEDS_FIXES  
CANONICAL_MEMORY_SAFE: YES  
DIRECT_AGENT_CANONICAL_WRITE: DISABLED  
CANDIDATE_PIPELINE: PASS  
AUTO_CAPTURE: FAIL (ingestão incremental existe; watcher/job ainda não habilitado)  
AUTO_PROMOTION: DISABLED  
PROVENANCE: PASS  
DEDUP: PASS para duplicata exata; similaridade/contradição requer evolução  
SECRET_FILTER: PASS  
PROJECT_ISOLATION: PASS nos testes existentes  
CLI_GLOBAL: PASS nos wrappers do repositório  
POWERSHELL: PASS  
CMD: PASS  
ARBITRARY_CWD: PASS  
PROJECT_AUTO_DETECTION: FAIL (override por ambiente/CLI disponível; metadata/cwd completo pendente)  
MCP_PROTOCOL: PASS para initialize/tools/list/tools/call/unknown tool/invalid args  
MCP_SUBPROCESS_TEST: PASS  
CODEX: SUPPORTED (config presente; não modificado)  
CLAUDE: SUPPORTED (config presente; não modificado)  
CURSOR: SUPPORTED (config presente; não modificado)  
OPENCODE: NEEDS_ADAPTER  
GEMINI_ANTIGRAVITY: NEEDS_ADAPTER  
MAESTRI: NEEDS_ADAPTER  
INSTALLER_IDEMPOTENT: PASS (fake config isolado)  
INSTALLER_ROLLBACK: PASS parcial (backup original preservado; comando uninstall dedicado pendente)  
INDEX_DETERMINISTIC: PASS  
OVERLAPPING_ROOTS: RESOLVED  
REBUILD: 1,136.673 ms; 175 arquivos; 724 chunks; 1 arquivo rejeitado pelo filtro sensível  
INCREMENTAL: 245.060 ms; corpus estável  
SEARCH_P50: 8.278 ms  
SEARCH_P95: 12.222 ms  
CONTEXT_PACK_P95: 52.254 ms  
DB_SIZE: 3,452,928 bytes  
TESTS: 23 PASS / 0 FAIL  
BLOCKERS: watcher/job automático, adapters OpenCode/Gemini/Maestri, auto-detecção completa e uninstall/rollback operacional  
HIGH: NONE após remediação da revisão adversarial  
MEDIUM: dedupe semântico/conflitos e estados SUPERSEDED/ARCHIVED ainda sem comandos dedicados  
PO_DECISIONS_REQUIRED: definir política/versionamento dos candidatos e escolher mecanismo de scan agendado/event adapter  
READY_FOR_CANONICAL_USE: YES, exclusivamente com review + verify + preview + apply local  
READY_FOR_AUTO_CAPTURE: NO  
READY_FOR_MULTI_AGENT_ROLLOUT: NO

## Alterações

- Captura MCP/CLI redirecionada para `.cerberus/inbox`.
- Contrato de candidato tipado com proveniência, fingerprint, confidence, authority hint e lifecycle.
- Promoção local preview-first, `--apply` explícito, allowlist e escrita atômica.
- Secret filter com quarantine; candidato contaminado não promove.
- Rebuild removido da superfície MCP.
- Raízes aninhadas normalizadas; identidade por caminho canônico elimina colisão de nomes relativos.
- Installer falha fechado em JSON inválido, preserva backup original e é idempotente.
- Launchers executam de CWD arbitrário sem `PYTHONPATH`.

## Evidências reproduzíveis

```powershell
python -m unittest discover -s tests -v
python -m engine.cli index --rebuild
C:\DevManiacs\DM-Cerebro\bin\cerberus.cmd doctor
& C:\DevManiacs\DM-Cerebro\bin\cerberus.ps1 doctor
```

## Segurança

Não foram executados install em configurações reais, commit, push, merge ou deploy. Alterações preexistentes em `.gitignore`, `LEARNINGS.md` e `MEMORY.md` foram preservadas. O índice derivado permanece coberto por `.gitignore`.

### Revisão adversarial

A primeira revisão independente retornou NO-GO e reproduziu: leitura de path arbitrário no ingest MCP, bypass de token `ghp_`, indexação de filename sensível e ausência de prune incremental. Todos receberam testes RED dedicados e foram corrigidos. O MCP agora trata `report_content` estritamente como conteúdo; tokens de provider/JWT são redigidos; indexação bloqueia nomes/conteúdo sensível e escapes; e arquivos deletados são removidos de `file_meta`/documents.

O re-review independente final retornou **GO**, com 23/23 testes e nenhum finding CRITICAL/HIGH remanescente no boundary solicitado. O teste adversarial indexou apenas `architecture.md` e excluiu variantes `token`, `credential`, `.env.*`, `*-secrets` e `private-key`.

## Learnings

- A discrepância histórica não vinha apenas de raízes aninhadas: o delete incremental por `%nome_do_arquivo%` fazia `README.md` de uma raiz apagar documentos homônimos de outra.
- Contadores de ingestão devem ser reconciliados com o estado persistido; após a correção e inclusão da documentação final, rebuild e stats convergem em 724 chunks.
- Existência de arquivo de configuração de cliente não prova schema suportado; adapters não verificados foram mantidos como `NEEDS_ADAPTER`.

NO COMMIT  
NO PUSH
