# REPORT-FIX-007 — Unconditional project_id guard + Doc Clean-up

TASK-ID: `CERBERUS-P2-FIX-007`  
ACTIVE ROLE: SENIOR DEVELOPER / IMPLEMENTATION ENGINE  
Data: 2026-08-30  
Escopo: 2 refinamentos cirúrgicos endereçando os findings finais do Codex QA.

---

## 1. Resultado

- **Suíte completa**: `Ran 88 tests in 9.017s` — **OK** (32 originais + 31 P2 + 12 FIX-005 + 9 FIX-006 + 4 FIX-007).
- **100% green** — 88 ok, 0 errors, 0 failures.
- **Sem regressões** nos 84 testes pré-existentes.
- **Sem commit, sem push** (autorização explícita do TASK).

---

## 2. Mapeamento Finding → Fix → Teste

| # | Finding do Codex QA | Fix implementado | Teste de regressão |
|---|---|---|---|
| **#1** | Guard `if task_id and not candidate_id and not project_id` deixava brecha: `(candidate_id + task_id)` sem `project_id` passava e mass-verificava candidatos cross-project | Guard reescrito para **`if task_id and not (project_id and str(project_id).strip())`** — dispara **sempre** que `task_id` está presente, mesmo se `candidate_id` também for (orchestrator.py:332-339). Mensagem atualizada: `"project_id is required whenever task_id is specified to prevent cross-project verification"`. | `test_qa_approved_with_both_candidate_id_and_task_id_requires_project_id`<br>`test_qa_approved_with_both_candidate_id_task_id_and_empty_project_id_raises`<br>`test_qa_approved_with_both_candidate_id_task_id_and_valid_project_id_succeeds`<br>`test_qa_approved_candidate_id_only_still_works_without_project_id` |
| **#2** | Doc mostrava exemplos `on_qa_approved(task_id="...")` sem `project_id`; aliases `site`/`desk` ainda listados na tabela; regra de "closest folder" removida do código mas ainda na doc | API example, CLI surface, tabela de aliases, tabela de exemplos e security matrix atualizados (linhas 95-130, 152-167, 47-58, 71-89, 200-201) | — (doc-only changes) |

---

## 3. Arquivos Alterados

| Arquivo | Tipo | Δ Linhas | Mudança |
|---|---|---:|---|
| `engine/integrations/orchestrator.py` | modificado | ~−3/+7 | Guard de `on_qa_approved` reescrito: `if task_id and not (project_id and str(project_id).strip())` → unconditional raise. Mensagem atualizada. |
| `tests/test_orchestrator_integration.py` | modificado | +90 | Nova classe `TestFix007Regression` com 4 testes cobrindo o guard incondicional. |
| `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` | modificado | ~+45/−25 | Versão bumped para 1.3.0; tabela de aliases sem `site`/`desk`; regra #5 renomeada; exemplos `C:/unrelated/site`, `C:/my_desk`, `site-files`, `desktop-tools` corrigidos para `_global`; API example `on_qa_approved` agora exige `project_id`; CLI surface mostra `--project` obrigatório; security matrix atualizada; nova seção Changelog v1.3.0; nova seção de testes FIX-007; total bumped para 88. |
| `reports/TEST-OUTPUT-FIX-007.log` | novo | — | Log verbose da suíte completa (88/88 PASS). |

---

## 4. Conformidade com os Requisitos

### 4.1 Unconditional project_id guard whenever task_id is present

- ✅ `on_qa_approved(candidate_id=None, task_id="TASK-1", project_id=None)` → `ValueError("project_id is required whenever task_id is specified to prevent cross-project verification")`.
- ✅ `on_qa_approved(candidate_id="abc", task_id="TASK-1", project_id=None)` → mesmo `ValueError` (guard incondicional).
- ✅ `on_qa_approved(candidate_id="abc", task_id="TASK-1", project_id="")` → `ValueError` (empty string).
- ✅ `on_qa_approved(candidate_id="abc", task_id="TASK-1", project_id="   ")` → `ValueError` (whitespace).
- ✅ `on_qa_approved(candidate_id="abc", task_id="TASK-1", project_id="biolar")` → succeeds.
- ✅ `on_qa_approved(candidate_id="abc")` (sem `task_id`) → succeeds sem exigir `project_id` (modo puro candidate_id permanece flexível).

Mensagem exata (orchestrator.py:335-338):
```python
raise ValueError(
    "project_id is required whenever task_id is specified to "
    "prevent cross-project verification"
)
```

### 4.2 Documentation Clean-up

- ✅ Tabela de aliases (linhas 47-58): removidos `site` e `desk` das colunas de alias de `dev-maniacs-site` e `dm-desk`. Apenas `dev_maniacs_site` e `dm_desk` (separadores `_`) permanecem como aliases formais. Callout ⚠️ adicionado explicando a remoção FIX-006.
- ✅ Regra #5 renomeada (linha 74): "Nada casou → `_global`" (FIX-006: o fallback "closest folder" foi removido).
- ✅ Tabela de exemplos (linhas 79-89): `C:/Users/jane/site-files/x`, `C:/Users/jane/desktop-tools/y`, `C:/my_desk`, `C:/unrelated/site` agora corretamente mostram `_global`. Adicionados exemplos positivos `projects/site` e `projects/desk` mostrando slug literal via regra #1.
- ✅ API example (linhas 124-127): `qa_result = adapter.on_qa_approved(task_id=..., project_id=...)` agora mostra `project_id` obrigatório. Adicionado também exemplo do modo puro `candidate_id` (sem `project_id`).
- ✅ CLI surface (linhas 159-176): `cerberus on-qa-approved --task TASK-042 --project canteirohub` é o comando recomendado. Callout ⚠️ explicita que `--project` é OBRIGATÓRIO com `--task`.
- ✅ Security matrix (linha 200): entrada de "Aprovação de QA com `project_id` incondicional" reflete o guard FIX-007 e lista os 8 testes correspondentes.
- ✅ Seção de testes (linhas 333-339): nova seção FIX-007 com 4 testes.
- ✅ Total bumped (linha 341): `88 testes` (32 + 31 + 12 + 9 + 4).
- ✅ Changelog v1.3.0 adicionado (linhas 413-431) resumindo o guard incondicional + doc clean-up.

### 4.3 Tests + full suite

- ✅ `test_qa_approved_with_both_candidate_id_and_task_id_requires_project_id` adicionado (linha 1130+).
- ✅ `python -B -m unittest discover -s tests -v` → **88/88 PASS** (log em `reports/TEST-OUTPUT-FIX-007.log`).

---

## 5. Resultados dos Testes

```
Ran 88 tests in 9.017s
OK
```

Distribuição:
- `test_candidate_pipeline.py`: 11
- `test_cerberus_engine.py`: 6
- `test_cli_integration.py`: 2
- `test_index_hardening.py`: 8
- `test_installer.py`: 2
- `test_mcp_protocol.py`: 3
- **`test_orchestrator_integration.py`**: **56** (32 P2 + 12 FIX-005 + 9 FIX-006 + 4 FIX-007 — incl. 1 novo em TestProjectResolution)

Log completo em `reports/TEST-OUTPUT-FIX-007.log`.

### FIX-007 — 4 testes novos

| Teste | Cobre |
|---|---|
| `test_qa_approved_with_both_candidate_id_and_task_id_requires_project_id` | `(candidate_id, task_id, project_id=None)` → `ValueError` |
| `test_qa_approved_with_both_candidate_id_task_id_and_empty_project_id_raises` | `(candidate_id, task_id, project_id=""/whitespace)` → `ValueError` |
| `test_qa_approved_with_both_candidate_id_task_id_and_valid_project_id_succeeds` | `(candidate_id, task_id, project_id="biolar")` → success |
| `test_qa_approved_candidate_id_only_still_works_without_project_id` | `candidate_id` sozinho (sem `task_id`) → success sem `project_id` |

---

## 6. Segurança — Garantia Adicional (FIX-007)

| # | Antes do FIX-007 | Depois do FIX-007 |
|---|---|---|
| Guard de QA com `task_id` | Disparava apenas se `candidate_id` era None | Dispara **sempre** que `task_id` é fornecido (mesmo com `candidate_id` também) |
| Mensagem de erro | `"project_id is required when approving by task_id to prevent cross-project verification"` | `"project_id is required whenever task_id is specified to prevent cross-project verification"` (reflete a unconditional nature) |
| Casos cobertos | `(task_id, project_id=None)` | `(task_id, project_id=None)` + `(candidate_id, task_id, project_id=None)` + empty/whitespace `project_id` |

---

## 7. Compatibilidade e Decisões

### Compatibilidade
- **Breaking**: clientes que chamavam `on_qa_approved(candidate_id=..., task_id=...)` sem `project_id` agora recebem `ValueError`. Devem adicionar `project_id=<slug>`.
- **Backwards-compat**: clientes que só passam `candidate_id` (sem `task_id`) permanecem inalterados — `project_id` permanece opcional.

### Decisões
1. **Guard unconditional via `if task_id and not (project_id and str(project_id).strip())`** — dispara sempre que `task_id` está presente, sem exceções.
2. **`str(project_id).strip()` em vez de `project_id.strip()`** — protege contra `None` e outros tipos não-str.
3. **Apenas modo puro `candidate_id` mantém `project_id` opcional** — porque o id já é único, não há risco de cross-project.
4. **Sem adicionar testes redundantes** — os 4 testes FIX-007 cobrem os 4 cenários críticos sem duplicar cobertura existente.

---

## 8. Ready For Commit

- ✅ 88/88 testes passam (100% green).
- ✅ Documentação canônica atualizada (`docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` v1.3.0).
- ✅ Sem regressões.
- ✅ Sem dependências novas.
- ✅ Guard de cross-project completamente fail-closed.
- ⏸ Sem commit, sem push (autorização explícita do TASK não inclui essas ações).

---

NO IMPLEMENTATION beyond TASK scope  
NO COMMIT  
NO PUSH
