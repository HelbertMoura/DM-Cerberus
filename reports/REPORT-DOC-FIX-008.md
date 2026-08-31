# REPORT-DOC-FIX-008 — Documentation Alignments

TASK-ID: `CERBERUS-P2-DOC-FIX-008`  
ACTIVE ROLE: SENIOR DEVELOPER / IMPLEMENTATION ENGINE  
Data: 2026-08-30  
Escopo: 2 correções cirúrgicas de documentação alinhadas pelo Codex QA. **Nenhuma alteração de código.**

---

## 1. Resultado

- **Suíte completa**: `Ran 88 tests in 9.265s` — **OK** (88/88 PASS, sem regressão).
- **Sem commit, sem push** (autorização explícita do TASK).
- **Nenhuma alteração de código** — apenas documentação.

---

## 2. Mapeamento Finding → Fix

| # | Finding do Codex QA | Local | Fix aplicado |
|---|---|---|---|
| **#1** | Assinatura `on_qa_approved(candidate_id=None, task_id=None)` na event table §1 não reflete o parâmetro `project_id` nem sua obrigatoriedade | `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md:27` | Assinatura atualizada para `on_qa_approved(candidate_id=None, task_id=None, project_id=None)` com nota: *"**`project_id` é obrigatório sempre que `task_id` for fornecido** (guard fail-closed anti cross-project) — vide FIX-007."* |
| **#2** | Distribuição de testes por arquivo imprecisa no report (`test_cerberus_engine: 7` / `test_orchestrator_integration: 55`) | `reports/REPORT-FIX-007.md:86-91` | Corrigido para `test_cerberus_engine: 6` e `test_orchestrator_integration: 56` — matches `unittest discover`. Também adicionei tabela per-file breakdown canônica no doc para eliminar ambiguidade futura. |

---

## 3. Mudanças Aplicadas

| Arquivo | Tipo | Δ Linhas | Mudança |
|---|---|---:|---|
| `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` | modificado | +22/−3 | Versão bumped para 1.3.1. Linha 27 atualizada com nova assinatura + nota FIX-007. Tabela per-file breakdown adicionada após o `Total: 88 testes`. Changelog v1.3.1 com resumo do DOC-FIX-008. |
| `reports/REPORT-FIX-007.md` | modificado | +1/−1 | Linha 86: `test_cerberus_engine.py: 7` → `6`. Linha 91: `**55**` → `**56**` para `test_orchestrator_integration.py`. |

### 3.1 Antes vs Depois

**docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md linha 27:**

```diff
-| `QA_APPROVED` | `OrchestratorAdapter.on_qa_approved(candidate_id=None, task_id=None)` | Promove candidatos... |
+| `QA_APPROVED` | `OrchestratorAdapter.on_qa_approved(candidate_id=None, task_id=None, project_id=None)` | Promove candidatos... **`project_id` é obrigatório sempre que `task_id` for fornecido** (guard fail-closed anti cross-project) — vide FIX-007. |
```

**docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md (nova tabela pós-line 341):**

```markdown
Distribuição por arquivo:

| Arquivo | Testes |
|---|---:|
| `tests/test_candidate_pipeline.py` | 11 |
| `tests/test_cerberus_engine.py` | 6 |
| `tests/test_cli_integration.py` | 2 |
| `tests/test_index_hardening.py` | 8 |
| `tests/test_installer.py` | 2 |
| `tests/test_mcp_protocol.py` | 3 |
| `tests/test_orchestrator_integration.py` | 56 |
| **TOTAL** | **88** |
```

**reports/REPORT-FIX-007.md (linhas 85-91):**

```diff
-- `test_cerberus_engine.py`: 7
+- `test_cerberus_engine.py`: 6
-...
-- **`test_orchestrator_integration.py`**: **55** (32 P2 + 12 FIX-005 + 9 FIX-006 + 4 FIX-007...)
+- **`test_orchestrator_integration.py`**: **56** (32 P2 + 12 FIX-005 + 9 FIX-006 + 4 FIX-007...)
```

---

## 4. Verificação Empírica

### 4.1 Contagem real dos testes (via `unittest`)

```
test_candidate_pipeline: 11
test_cerberus_engine: 6
test_cli_integration: 2
test_index_hardening: 8
test_installer: 2
test_mcp_protocol: 3
test_orchestrator_integration: 56
TOTAL: 88
```

### 4.2 Suite completa

```
Ran 88 tests in 9.265s
OK
```

### 4.3 Inspeção manual dos testes em `test_cerberus_engine.py`

```
test_context_pack_generation
test_indexing_and_search
test_project_isolation
test_initialize_and_tools_list
test_parse_frontmatter
test_resolve_project_and_type
```

Confirmado: **6 testes**. O 7º teste MCP (`test_subprocess_capture_is_candidate_only_and_no_promotion_tool`) sempre viveu em `test_mcp_protocol.py` — os reports anteriores confundiram a contagem.

---

## 5. Conformidade com os Requisitos

| Requisito | Status | Verificação |
|---|---|---|
| Update signature from `on_qa_approved(candidate_id=None, task_id=None)` to `on_qa_approved(candidate_id=None, task_id=None, project_id=None)` | ✅ | `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md:27` |
| Note that project_id is mandatory when task_id is specified | ✅ | Nota inline na mesma linha da assinatura + Changelog v1.3.1 |
| Correct test_cerberus_engine: 6 | ✅ | `reports/REPORT-FIX-007.md:86` + `docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` tabela per-file |
| Correct test_orchestrator_integration: 56 | ✅ | `reports/REPORT-FIX-007.md:91` + doc tabela |
| Correct total: 88 | ✅ | Já estava correto em ambos os locais |
| Run full test suite, confirm PASS | ✅ | 88/88 PASS em 9.265s |

---

## 6. Notas sobre Escopo

### Itens NÃO tocados (fora do escopo)

- **`reports/REPORT-FIX-005.md`** e **`reports/REPORT-FIX-006.md`** também têm o mesmo erro histórico (`test_cerberus_engine: 7` em vez de 6). Esses reports **não foram mencionados pela TASK**, então ficaram como registros históricos. Se necessário, podem ser corrigidos em uma task futura de "historical-report cleanup".
- **Nenhuma alteração de código** — apenas documentação.

### Verificação adicional

Rodei a suite completa (`python -B -m unittest discover -s tests -v`) após as alterações para confirmar zero impacto: **88/88 PASS** em 9.265s.

---

## 7. Ready For Commit

- ✅ 88/88 testes passam (100% green).
- ✅ Documentação canônica alinhada (`docs/CERBERUS-ORCHESTRATOR-INTEGRATION.md` v1.3.1).
- ✅ Report alvo corrigido (`reports/REPORT-FIX-007.md`).
- ✅ Sem regressões.
- ✅ Nenhuma alteração de código.
- ⏸ Sem commit, sem push (autorização explícita do TASK não inclui essas ações).

---

NO IMPLEMENTATION beyond TASK scope  
NO COMMIT  
NO PUSH
