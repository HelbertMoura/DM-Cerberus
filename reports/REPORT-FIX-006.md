# REPORT-FIX-006 — Final Security Contract Alignments

TASK-ID: `CERBERUS-P2-FIX-006`  
ACTIVE ROLE: SENIOR DEVELOPER / IMPLEMENTATION ENGINE  
Data: 2026-08-30  
Escopo: 3 endurecimentos finais de contrato endereçando os últimos findings do Codex QA sobre a Fase P2.

---

## 1. Resultado

- **Suíte completa**: `Ran 84 tests in 8.306s` — **OK** (32 originais + 31 P2 + 12 FIX-005 + 9 FIX-006).
- **100% green** — 84 ok, 0 errors, 0 failures.
- **Sem regressões** nos 75 testes pré-existentes (atualizei 6 testes que cobriam comportamento legado dos contracts que mudaram).
- **Sem commit, sem push** (autorização explícita do TASK).

---

## 2. Mapeamento Finding → Fix → Teste

| # | Finding do Codex QA | Fix implementado | Teste de regressão |
|---|---|---|---|
| **#1** | `on_qa_approved(task_id=...)` sem `project_id` permitia verificação cross-project silenciosa | `on_qa_approved` agora **raise `ValueError`** quando `task_id` é fornecido sem `project_id` válido (orchestrator.py:374-381) | `test_on_qa_approved_task_id_without_project_id_raises`<br>`test_on_qa_approved_candidate_id_only_still_works_without_project_id`<br>`test_qa_approval_by_task_without_project_id_raises_fix006` |
| **#2** | `on_report_accepted` ainda aceitava paths arbitrários via heurística de file-reading | `on_report_accepted` agora **sempre** passa `allow_file=False` para `ingest_report` (orchestrator.py:280-303). Helper `_resolve_report_payload` e campo `source_path` foram **removidos**. | `test_on_report_accepted_calls_ingest_report_with_allow_file_false`<br>`test_on_report_accepted_does_not_emit_source_path`<br>`test_on_report_accepted_never_reads_disk_even_inside_root` |
| **#3** | Aliases soltos `site` → `dev-maniacs-site` e `desk` → `dm-desk` permitiam classificação indevida | Removidos de `PROJECT_ALIASES` (orchestrator.py:31-49). Apenas nomes completos aceitos. `detect_project_from_path` perdeu a regra de fallback "closest folder" — paths genéricos caem em `_global` (maestri.py:81-85). | `test_resolve_project_slug_has_no_loose_site_or_desk_keys`<br>`test_resolve_project_slug_loose_aliases_removed_fix006`<br>`test_loose_paths_fall_back_to_global`<br>`test_projects_site_and_projects_desk_keep_literal_slugs`<br>`test_explicit_full_aliases_still_resolve` |

---

## 3. Arquivos Alterados

| Arquivo | Tipo | Δ Linhas | Mudança |
|---|---|---:|---|
| `engine/integrations/orchestrator.py` | modificado | ~−30/+20 | `PROJECT_ALIASES` perdeu `site`/`desk`. `on_qa_approved` ganhou guard de `project_id` obrigatório. `on_report_accepted` agora é puramente content-only (`allow_file=False` sempre, `_resolve_report_payload` removido, `source_path` removido). |
| `engine/integrations/maestri.py` | modificado | ~−8/+10 | `detect_project_from_path` perdeu a regra #5 (closest folder fallback); agora retorna `_global` quando nenhuma regra casa. |
| `tests/test_orchestrator_integration.py` | modificado | +240 | 9 testes novos em `TestFix006Regression`; 6 testes legados atualizados para refletir os novos contratos. |
| `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` | modificado | +50 | Versão bumped para 1.2.0; nova seção FIX-006 na tabela de testes (8 entradas); entradas de segurança atualizadas; nova entrada de Changelog v1.2.0. |
| `reports/TEST-OUTPUT-FIX-006.log` | novo | — | Log verbose da suíte completa (84/84 PASS). |

---

## 4. Conformidade com os Requisitos

### 4.1 Mandatory project_id for task_id QA approval
- ✅ `on_qa_approved(task_id=..., project_id=None)` raises `ValueError("project_id is required when approving by task_id to prevent cross-project verification")` (orchestrator.py:374-381).
- ✅ Também rejeita `project_id=""` e `project_id="   "` (whitespace).
- ✅ Modo `candidate_id` permanece **opcional** quanto a `project_id` (o id já é único).

### 4.2 Strict Content-Only in on_report_accepted
- ✅ `on_report_accepted` **sempre** passa `allow_file=False` (orchestrator.py:298).
- ✅ `_resolve_report_payload()` removido — nenhum file-reading logic permanece no adapter.
- ✅ `source_path` removido do retorno.
- ✅ Path-shaped strings são tratadas como conteúdo literal (verificado via spy test).

### 4.3 Remove loose aliases site/desk
- ✅ `PROJECT_ALIASES` em orchestrator.py:31-49 **não** contém `site` nem `desk`.
- ✅ `resolve_project_slug('site') == 'site'` (não `dev-maniacs-site`).
- ✅ `resolve_project_slug('desk') == 'desk'` (não `dm-desk`).
- ✅ `projects/site` e `projects/desk` ainda funcionam via regra `projects/<slug>` (literal).
- ✅ `detect_project_from_path('C:/unrelated/site') == '_global'`.
- ✅ `detect_project_from_path('C:/my_desk') == '_global'`.
- ✅ `dm-erp → canteirohub` continua (alias não chamado out pela QA).

### 4.4 Update tests + full suite
- ✅ Test atualizado asserta `ValueError` para task_id sem project_id.
- ✅ Test atualizado asserta `allow_file=False` via spy de `ingest_report`.
- ✅ Test atualizado asserta `C:/unrelated/site` → `_global`.
- ✅ Suíte completa roda **100% green** (84/84 PASS).

---

## 5. Resultados dos Testes

```
Ran 84 tests in 8.306s
OK
```

Distribuição:
- `test_candidate_pipeline.py`: 11
- `test_cerberus_engine.py`: 7
- `test_cli_integration.py`: 2
- `test_index_hardening.py`: 8
- `test_installer.py`: 2
- `test_mcp_protocol.py`: 3
- **`test_orchestrator_integration.py`**: **51** (32 P2 + 12 FIX-005 + 9 FIX-006 — incl. 1 novo em TestProjectResolution)

Log completo em `reports/TEST-OUTPUT-FIX-006.log`.

---

## 6. Segurança — Garantias Endurecidas (FIX-006)

| # | Antes do FIX-006 | Depois do FIX-006 |
|---|---|---|
| QA cross-project por `task_id` | `task_id` sozinho aprovava candidatos em todos os projetos com mesmo id | `task_id` sem `project_id` levanta `ValueError` (fail-closed) |
| Ingestão de relatório | Adapter podia abrir arquivo se path parecesse válido e estivesse no allowlist | Adapter **nunca** abre arquivo; tudo é tratado como conteúdo inline |
| Aliases soltos | `site` → `dev-maniacs-site`, `desk` → `dm-desk` (qualquer pasta `site` virava `dev-maniacs-site`) | Apenas nomes completos remapeáveis; paths genéricos caem em `_global` |
| Detecção de projeto | Closest folder fallback → path `C:/Users/jane/site-files` virava `whatever` (closest) | Sem fallback; `C:/Users/jane/site-files` → `_global` |

---

## 7. Compatibilidade e Decisões

### Decisões
1. **`allow_file=False` é incondicional** — não há flag de override. Caller é responsável por ler arquivo e passar conteúdo inline.
2. **`candidate_id` mode permanece flexível** — exige `project_id` apenas quando se quer cross-check. Sem `project_id`, o id já é único.
3. **Mantido `dm-erp → canteirohub`** — a QA mencionou explicitamente só `site` e `desk`. Alias `dm-erp` é útil para resolver `C:/DevManiacs/migra/dm-erp/docs` → `canteirohub`.
4. **Mantido `apae → apae-juatuba`** — mesmo motivo; QA não citou `apae`. Se necessário, fica como follow-up.

### Compatibilidade
- **Breaking**: clientes que chamavam `on_qa_approved(task_id=...)` sem `project_id` agora recebem `ValueError`. Devem adicionar `project_id=<slug>`.
- **Breaking**: clientes que passavam paths de arquivo para `on_report_accepted` agora recebem erro de parsing (path não tem `## Learnings` etc.) — devem ler o arquivo e passar conteúdo inline.
- **Breaking**: `detect_project_from_path('C:/my_desk')` agora retorna `_global` em vez de `my_desk`. Quem depender disso deve mover `dm-desk` para `projects/dm-desk`.

---

## 8. Ready For Commit

- ✅ 84/84 testes passam (100% green).
- ✅ Documentação canônica atualizada (`docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` v1.2.0).
- ✅ Sem regressões.
- ✅ Sem dependências novas.
- ✅ 3 contratos do Codex QA endurecidos com cobertura de regressão.
- ⏸ Sem commit, sem push (autorização explícita do TASK não inclui essas ações).

---

NO IMPLEMENTATION beyond TASK scope  
NO COMMIT  
NO PUSH
