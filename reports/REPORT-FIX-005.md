# REPORT-FIX-005 — Codex QA Findings Closure

TASK-ID: `CERBERUS-P2-FIX-005`  
ACTIVE ROLE: SENIOR DEVELOPER / IMPLEMENTATION ENGINE  
Data: 2026-08-30  
Escopo: 4 correções de precisão endereçando os findings do Codex QA sobre a Fase P2.

---

## 1. Resultado

- **Suíte completa**: `Ran 75 tests in 7.996s` — **OK** (32 originais + 31 P2 + 12 FIX-005).
- **100% green** — 75 ok, 0 errors, 0 failures.
- **Sem regressões** nos 63 testes pré-existentes.
- **Sem commit, sem push** (autorização explícita do TASK).

---

## 2. Mapeamento Finding → Fix → Teste

| # | Finding do Codex QA | Fix implementado | Teste de regressão |
|---|---|---|---|
| **#1** | `on_qa_approved` por `task_id` não distingue mesmo TASK em projetos diferentes | Novo parâmetro `project_id` em `on_qa_approved` (orchestrator.py:267-322) | `test_qa_approval_by_task_with_project_id_only_verifies_target`<br>`test_qa_approval_by_task_without_project_id_verifies_all`<br>`test_qa_approval_by_candidate_id_with_wrong_project_is_skipped` |
| **#2** | `ensure_indexed` hardcoded `C:/DevManiacs/migra/dm-erp/docs` mesmo em root isolado | Removido hardcoded path; novo helper `_select_index_roots()` honra `CERBERUS_ROOT` + `CERBERUS_ALLOWED_ROOTS` + `CERBERUS_EXTRA_ROOTS` (orchestrator.py:75-138, 209-216) | `test_ensure_indexed_ignores_hardcoded_dm_erp_when_isolated`<br>`test_ensure_indexed_rejects_extra_roots_outside_allowlist`<br>`test_ensure_indexed_returns_empty_when_root_disallowed` |
| **#3** | `on_report_accepted` chama `ingest_report(allow_file=True)` → leitura arbitrária de FS | Novo `_resolve_report_payload()` (orchestrator.py:266-313) só lê arquivo se: (a) string for path-like de uma linha, (b) path resolvido cair dentro do allowlist. Multi-line strings sempre inline. `ingest_report(allow_file=...)` agora respeita essa decisão. | `test_report_accepted_refuses_to_read_path_outside_root`<br>`test_report_accepted_reads_path_inside_root`<br>`test_report_accepted_treats_multiline_string_as_inline` |
| **#4** | Path detection: `projects/biolar/global/report.md` → `_global` (errado). Aliases `site`/`desk`/`apae` aceitos como substring | Nova ordem de prioridade em `detect_project_from_path` (maestri.py:53-99):<br>1. `projects/<slug>` (vence global/shared)<br>2. `_global`/`_shared`<br>3. **Match exato de segmento** contra `STRICT_PATH_ALIASES` (maestri.py:81-86)<br>4. Pasta mais próxima | `test_detect_project_path_projects_subdir_beats_global`<br>`test_detect_project_path_strict_alias_exact_segment_only`<br>`test_detect_project_path_global_and_shared_still_work_when_no_projects` |

---

## 3. Arquivos Alterados

| Arquivo | Tipo | Δ Linhas | Mudança |
|---|---|---:|---|
| `engine/integrations/orchestrator.py` | modificado | +180 | Adicionado `STRICT_PATH_ALIASES`, helpers `_configured_allowed_roots` / `_select_index_roots`, `_resolve_report_payload`, novo parâmetro `project_id` em `on_qa_approved`, refatoração de `ensure_indexed` e `on_report_accepted` |
| `engine/integrations/maestri.py` | modificado | ~+15/-10 | Reordenação das regras de detecção; substituição de `PROJECT_ALIASES` por `STRICT_PATH_ALIASES` no loop de alias match; docstring atualizada |
| `tests/test_orchestrator_integration.py` | modificado | +210 | Nova classe `TestFix005Regression` com 12 testes cobrindo os 4 findings |
| `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` | modificado | +60 | Versão bumped para 1.1.0; tabela de testes corrigida (32 + 31 + 12 = **75**); nova seção de segurança com 4 entradas de FIX-005; nova seção Changelog com diff resumido; exemplos de path detection na tabela de aliases |
| `reports/TEST-OUTPUT-FIX-005.log` | novo | — | Log verbose da suíte completa |

---

## 4. Conformidade com os Requisitos

### 4.1 Project-Scoped QA Approval
- ✅ `on_qa_approved(candidate_id=None, task_id=None, project_id=None)` — assinatura estendida (orchestrator.py:267).
- ✅ Quando `task_id` + `project_id`: filtra candidatos por `candidate.project_id == target_slug`; demais são adicionados a `skipped` com reason `project mismatch` (orchestrator.py:303-307).
- ✅ Quando `candidate_id` + `project_id`: o candidato de outro projeto gera `ValueError` antes da transição de status (orchestrator.py:283-287 + `_verify_within_project` em 314-322).
- ✅ Backward-compat: sem `project_id`, comportamento legado preservado (orchestrator.py:283 + testes).

### 4.2 Isolation in ensure_indexed
- ✅ Removido hardcoded `Path("C:/DevManiacs/migra/dm-erp/docs")` (orchestrator.py:211-216 agora usa `_select_index_roots`).
- ✅ Sob `CERBERUS_ROOT` custom, apenas essa raiz é elegível.
- ✅ Sob CERBERUS_ROOT não setado, `application_root` + opcional `CERBERUS_EXTRA_ROOTS` (todos validados contra `CERBERUS_ALLOWED_ROOTS`).
- ✅ Toda raiz precisa (a) existir, (b) cair dentro do allowlist resolvido.
- ✅ Fail-closed: raiz fora do allowlist → 0 arquivos indexados (orchestrator.py:202-205).

### 4.3 Secure Report Ingestion
- ✅ `on_report_accepted` nunca chama `ingest_report(allow_file=True)` cegamente.
- ✅ Heurística de path-like restrita a: 1 linha, ≤4096 chars, começa com `X:`, `/`, `\`, `./`, `../` ou `~`.
- ✅ Path resolvido deve cair dentro do allowlist (`_configured_allowed_roots`).
- ✅ Multi-line strings são SEMPRE tratadas como conteúdo inline (orchestrator.py:283-285).
- ✅ Quando lido, `result["source_path"]` traz o path absoluto resolvido para proveniência (orchestrator.py:251).
- ✅ Fail-closed: erro de I/O → trata como inline.

### 4.4 Maestri Path Detection Priority & Alias Precision
- ✅ Nova ordem: `projects/<slug>` → `_global`/`_shared` → **match exato de segmento** em `STRICT_PATH_ALIASES` → pasta slugificada.
- ✅ `STRICT_PATH_ALIASES` definido em orchestrator.py:69-82; contém apenas nomes completos (`dm-erp`, `dev-maniacs-site`, `dm-desk`, `apae-juatuba`, etc.) — **sem** `site`/`desk`/`apae` soltos.
- ✅ `detect_project_from_path` em maestri.py usa `STRICT_PATH_ALIASES.get(ancestor.casefold())` — match exato only (maestri.py:81-85).

### 4.5 Tests & Doc Consistency
- ✅ 12 regression tests adicionados em `TestFix005Regression` (3 por finding).
- ✅ Doc `CERBERUS-ORCHESTRATOR-INTEGRATION.md` atualizado:
  - Tabela de aliases expandida com exemplos (linhas 80-94)
  - Tabela de testes corrigida para 32+31+12 = **75** (linhas 252-261)
  - Nova seção 8 Changelog com v1.1.0 (linhas 313-330)
- ✅ Suíte completa **100% green** (75/75 PASS).

---

## 5. Resultados dos Testes

```
Ran 75 tests in 7.996s
OK
```

Distribuição:
- `test_candidate_pipeline.py`: 11
- `test_cerberus_engine.py`: 7
- `test_cli_integration.py`: 2
- `test_index_hardening.py`: 8
- `test_installer.py`: 2
- `test_mcp_protocol.py`: 3
- **`test_orchestrator_integration.py`**: **42** (30 P2 + 12 FIX-005)

Log completo em `reports/TEST-OUTPUT-FIX-005.log`.

---

## 6. Segurança — Garantias Endurecidas

| # | Antes do FIX-005 | Depois do FIX-005 |
|---|---|---|
| QA cross-project | `TASK-01` em biolar podia inadvertidamente verificar candidato em helpdev | Filtro explícito por slug; mismatches reportados em `skipped[]` |
| Indexação isolada | Adapter sempre puxava `C:/DevManiacs/migra/dm-erp/docs` mesmo sob root customizado | Apenas roots validados contra `CERBERUS_ALLOWED_ROOTS` |
| Ingestão de relatório | `ingest_report(allow_file=True)` lia qualquer path | Arquivo só aberto se dentro do allowlist; path-like vs inline decidido por heurística segura |
| Detecção de projeto | `projects/biolar/global/x` → `_global` (incorreto) | `projects/<slug>` tem prioridade absoluta; loose aliases removidos |

---

## 7. Decisões de Implementação

1. **Novo dict `STRICT_PATH_ALIASES`** em vez de mexer no `PROJECT_ALIASES` existente, porque `PROJECT_ALIASES` ainda é útil para CLI input explícito (digitar `site` na CLI continua resolvendo para `dev-maniacs-site`). Apenas path detection usa o conjunto estrito.
2. **Backward-compat preservado** — chamadas antigas a `on_qa_approved(task_id=...)` sem `project_id` continuam funcionando idênticamente.
3. **Fail-closed em `_select_index_roots`** — qualquer root inválido é descartado silenciosamente; se nada válido restar, retorna lista vazia e o indexador reporta 0 chunks.
4. **Multi-line strings sempre inline** — heurística de path é restrita a strings de 1 linha para evitar que conteúdo com `\n` acidentalmente seja tratado como path.
5. **`source_path` opcional em `on_report_accepted`** — só presente quando o adapter leu um arquivo (proveniência auditável).

---

## 8. Ready For Commit

- ✅ 75/75 testes passam (100% green).
- ✅ Documentação canônica atualizada (`docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` v1.1.0).
- ✅ Sem regressões.
- ✅ Sem dependências novas (apenas stdlib).
- ✅ Backward-compatible.
- ✅ 4 findings do Codex QA endereçados com cobertura de regressão.
- ⏸ Sem commit, sem push (autorização explícita do TASK não inclui essas ações).

---

NO IMPLEMENTATION beyond TASK scope  
NO COMMIT  
NO PUSH
