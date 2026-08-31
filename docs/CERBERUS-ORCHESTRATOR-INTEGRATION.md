# 🔌 Cerberus Memory Intelligence — Orchestrator & Maestri Integration
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)  
> **Versão:** 1.3.1 (DOC-FIX-008) · 30 de Agosto de 2026  
> **Status:** Ativo e Operacional  
> **Complementa:** [`CERBERUS-MEMORY-ARCHITECTURE.md`](./CERBERUS-MEMORY-ARCHITECTURE.md), [`CERBERUS-MCP-INTEGRATION.md`](./CERBERUS-MCP-INTEGRATION.md), [`CERBERUS-AUTO-CAPTURE.md`](./CERBERUS-AUTO-CAPTURE.md)

---

## 🎯 Propósito

Esta fase (P2) define o **contrato de eventos** entre o **Cerberus Memory Intelligence** e o **AI Orchestrator / Gemini Maestro / Maestri Canvas**. O objetivo é acoplar o cérebro corporativo a cada evento do ciclo de vida de uma tarefa **sem quebrar a inegociável separação de poderes**: o Cerberus apenas responde; o Orchestrator decide.

A integração é estritamente:

- **Read-first no início** (sessão de agente começa com `ContextPack` enxuto).
- **Capture-only no meio** (`on_report_accepted` cria candidatos; nunca grava no canônico).
- **Authority-boost no final** (`on_qa_approved` apenas sobe o status; promoção continua exigindo operador humano).

---

## 🏷️ 1. Eventos Suportados

| Evento Orchestrator | Método Cerberus | Efeito |
|---|---|---|
| `TASK_CREATED` | `OrchestratorAdapter.session_start(project_id, task_summary, role)` | Gera um `ContextPack` compacto (markdown + token estimate). Pronto para injetar no prompt do agente. |
| `REPORT_ACCEPTED` | `OrchestratorAdapter.on_report_accepted(report, task_id, project_id, agent_role)` | Extrai learnings/findings do relatório e cria **candidatos** em `.cerberus/inbox/`. Aplicam-se redacção de segredos e proveniência obrigatória (task_id + agent). |
| `QA_APPROVED` | `OrchestratorAdapter.on_qa_approved(candidate_id=None, task_id=None, project_id=None)` | Promove candidatos de `CANDIDATE` para `VERIFIED`. Nunca promove direto para `CANONICAL`. **`project_id` é obrigatório sempre que `task_id` for fornecido** (guard fail-closed anti cross-project) — vide FIX-007. |
| `PROJECT_CLOSED` | `OrchestratorAdapter.get_project_summary(project_id)` | Retorna stats, decisões-chave, learnings e último handover. |

Nenhum desses métodos escreve no Markdown canônico. A promoção canônica continua passando pelo pipeline explícito:

```
CAPTURED → CANDIDATE → VERIFIED → CANONICAL
                          ↑            ↑
                     on_qa_approved    promote --apply
                                       (operador humano)
```

---

## 🧭 2. Resolução Dinâmica de Projetos

Todos os caminhos públicos aceitam um identificador livre (slug, alias ou caminho) e normalizam para um slug canônico via `resolve_project_slug()` / `detect_project_from_path()`.

**Slugs canônicos conhecidos:**

| Slug canônico | Aliases aceitos | Notas |
|---|---|---|
| `_global` | `global` | Governança e ADRs corporativos |
| `_shared` | `shared` | Conhecimento cross-project reutilizável |
| `canteirohub` | `dm-erp`, `dm_erp` | ERP SaaS White-Label (dm-erp raiz) |
| `biolar` | — | Projeto Biolar |
| `helpdev` | — | Projeto HelpDev |
| `dmpdv` | — | Projeto DM-PDV |
| `apae-juatuba` | `apae`, `apae_juatuba` | Projeto APAE Juwatuba |
| `dev-maniacs-site` | `dev_maniacs_site` | Site institucional |
| `dm-desk` | `dm_desk` | DM Desk |

> ⚠️ **FIX-006**: os aliases soltos `site` e `desk` foram **removidos** de
> `PROJECT_ALIASES`. Apenas os nomes completos `dev-maniacs-site` e
> `dm-desk` continuam remapeáveis. Para suportar um projeto literalmente
> chamado `site` ou `desk`, basta criá-lo em `projects/site` ou
> `projects/desk` (a regra `projects/<slug>` aceita qualquer slug
> verbatim).

Projetos novos são detectados dinamicamente: qualquer diretório criado em `DM-Cerebro/projects/<slug>/` vira slug válido automaticamente (ver `discover_dynamic_projects()`).

**Regras de detecção por caminho (ordem de prioridade — `detect_project_from_path`):**

1. Ancestral `projects/<slug>/...` → `<slug>` — **ganha** sobre qualquer `_global`/`_shared` no caminho (FIX-005).
2. Ancestral `_global` / `global` → `_global`
3. Ancestral `_shared` / `shared` → `_shared`
4. Match **exato de segmento** contra `STRICT_PATH_ALIASES` (closest ancestor wins). Aliases flexíveis como `site`, `desk`, `apae` são **deliberadamente excluídos** para evitar classificar pastas não-relacionadas como `dev-maniacs-site`/`dm-desk`/`apae-juatuba`.
5. **Nada casou → `_global`** (FIX-006: o fallback de "pasta mais próxima" foi removido para evitar classificação silenciosa de paths não-relacionados).

Exemplos:

| Caminho | Slug resolvido | Motivo |
|---|---|---|
| `C:/DevManiacs/DM-Cerebro/projects/biolar/global/report.md` | `biolar` | Regra #1 (projetos vence global) |
| `C:/DevManiacs/DM-Cerebro/projects/dev-maniacs-site` | `dev-maniacs-site` | Regra #1 |
| `C:/DevManiacs/DM-Cerebro/projects/dm-desk` | `dm-desk` | Regra #1 |
| `C:/DevManiacs/DM-Cerebro/projects/site` | `site` | Regra #1 (slug literal) |
| `C:/DevManiacs/DM-Cerebro/projects/desk` | `desk` | Regra #1 (slug literal) |
| `C:/DevManiacs/DM-Cerebro/global/ai-governance.md` | `_global` | Regra #2 |
| `C:/DevManiacs/migra/dm-erp/docs` | `canteirohub` | Regra #4 (alias `dm-erp`) |
| `C:/Users/jane/site-files/x` | `_global` | Regra #5 — sem match; loose alias `site` foi removido |
| `C:/Users/jane/desktop-tools/y` | `_global` | Regra #5 — sem match; loose alias `desk` foi removido |
| `C:/my_desk` | `_global` | Regra #5 — sem match |
| `C:/unrelated/site` | `_global` | Regra #5 — sem match |

---

## 🧱 3. Arquitetura

```
engine/integrations/
├── __init__.py            # re-exports públicos
├── orchestrator.py        # OrchestratorAdapter + resolve_project_slug
└── maestri.py             # detect_project_from_path + format_agent_session_pack

CLI (engine/cli.py):
  cerberus session-context  --project <p> --task <t> --role <r>
  cerberus on-report-accepted <report> --task <t> --project <p> --agent <a>
  cerberus on-qa-approved  (--candidate <id> | --task <t>)
```

### 3.1 `OrchestratorAdapter` (engine/integrations/orchestrator.py)

API Pythonic consumida pelo Orchestrator (Gemini PM) e por adapters externos:

```python
from engine.integrations import OrchestratorAdapter

adapter = OrchestratorAdapter(application_root=Path("/path/to/DM-Cerebro"))

# TASK_CREATED
ctx = adapter.session_start(
    project_id="canteirohub",
    task_summary="Implementar cofre SEFAZ A1",
    role="DEVELOPER",
)
# -> {"project_id": "canteirohub", "markdown": "...", "token_estimate": 412, ...}

# REPORT_ACCEPTED
report_result = adapter.on_report_accepted(
    report_path_or_content="## Learnings\n- Cofre SEFAZ ...",
    task_id="TASK-042",
    project_id="dm-erp",                # alias aceito -> canteirohub
    agent_role="CODEX",
)
# -> {"status": "COMPLETE", "candidate_count": 1, "candidate_ids": [...], ...}

# QA_APPROVED — task_id é obrigatório vir acompanhado de project_id (FIX-007)
qa_result = adapter.on_qa_approved(
    task_id="TASK-042",
    project_id="canteirohub",           # obrigatório quando task_id é fornecido
)
# -> {"verified": [<candidate_ids>], "skipped": [...], "mode": "task_id",
#     "project_id": "canteirohub"}

# QA_APPROVED — candidate_id sozinho é o único modo onde project_id é opcional
qa_single = adapter.on_qa_approved(candidate_id="<id-do-candidato>")
# -> {"verified": ["<id-do-candidato>"], "skipped": [], "mode": "candidate_id"}

# PROJECT_CLOSED
summary = adapter.get_project_summary("biolar")
# -> {"project_id": "biolar", "stats": {...}, "decisions": [...], "learnings": [...], ...}
```

### 3.2 Maestri Adapter (engine/integrations/maestri.py)

Helper usado por agent terminals conectados ao canvas Maestri:

```python
from engine.integrations.maestri import detect_project_from_path, format_agent_session_pack

slug = detect_project_from_path("C:/DevManiacs/migra/dm-erp/docs")
# -> "canteirohub"

prompt_block = format_agent_session_pack(
    cwd_or_path="C:/DevManiacs/migra/dm-erp",
    task_summary="Auditar BDI TCU",
    role="QA",
)
# -> bloco markdown com <!-- cerberus-context-pack --> sentinels
```

### 3.3 CLI Surface

```powershell
cerberus session-context --project canteirohub --task "Implementar cofre SEFAZ" --role DEVELOPER
cerberus on-report-accepted ./reports/REPORT-X.md --task TASK-042 --project dm-erp --agent CODEX

# QA_APPROVED — modo task_id (FIX-007): --project é OBRIGATÓRIO
cerberus on-qa-approved --task TASK-042 --project canteirohub

# QA_APPROVED — modo candidate_id (project_id opcional; id já é único)
cerberus on-qa-approved --candidate <id-do-candidato>
```

> ⚠️ **FIX-007**: `cerberus on-qa-approved --task TASK-X` sem
> `--project` agora retorna `ValueError` com a mensagem
> `"project_id is required whenever task_id is specified to prevent
> cross-project verification"`. A mesma regra vale para
> `on_qa_approved(task_id=..., project_id=None)` na API Python.

---

## 🔐 4. Garantias de Segurança (mantidas)

| Controle | Garantia | Verificação |
|---|---|---|
| Sem escrita canônica automática | Adapter **nunca** escreve em `LEARNINGS.md` / `DECISIONS.md`. | `tests/test_orchestrator_integration.py::test_session_start_does_not_touch_canonical` |
| Segredos continuam quarantinizados | `on_report_accepted` herda `redact_secrets()` + status `QUARANTINED`. | `test_on_report_accepted_quarantines_secrets` |
| Fingerprint é recalculado em `promote()` | Adapter não bypassa promote; fingerprint re-checked. | herdado de `test_tampered_candidate_fingerprint_blocks_promotion` |
| Root allowlist ainda obrigatório | Adapter valida `CERBERUS_ROOT` quando setado. | herdado de `test_mcp_root_must_be_inside_explicit_allowlist` |
| **`ensure_indexed` sem hardcoded roots** (FIX-005) | Não inclui mais `C:/DevManiacs/migra/dm-erp/docs` por padrão; honra `CERBERUS_ALLOWED_ROOTS` e `CERBERUS_EXTRA_ROOTS`. | `test_ensure_indexed_ignores_hardcoded_dm_erp_when_isolated`, `test_ensure_indexed_rejects_extra_roots_outside_allowlist`, `test_ensure_indexed_returns_empty_when_root_disallowed` |
| **Ingestão de relatório estritamente content-only** (FIX-005 + FIX-006) | `on_report_accepted` **sempre** passa `allow_file=False` para `ingest_report` — nunca abre arquivos do disco. Resultado não carrega `source_path`. | `test_on_report_accepted_calls_ingest_report_with_allow_file_false`, `test_on_report_accepted_does_not_emit_source_path`, `test_on_report_accepted_treats_multiline_string_as_inline` |
| **Aprovação de QA com `project_id` incondicional quando `task_id` está presente** (FIX-005 + FIX-006 + **FIX-007**) | `on_qa_approved(task_id=...)` **raise `ValueError`** se `project_id` for None/vazio, mesmo que `candidate_id` também seja fornecido. O único modo em que `project_id` é opcional é o `candidate_id` sozinho (id já é único). | `test_on_qa_approved_task_id_without_project_id_raises`, `test_qa_approved_by_task_without_project_id_raises_fix006`, `test_qa_approval_by_task_with_project_id_only_verifies_target`, `test_qa_approval_by_candidate_id_with_wrong_project_is_skipped`, `test_qa_approved_with_both_candidate_id_and_task_id_requires_project_id`, `test_qa_approved_with_both_candidate_id_task_id_and_empty_project_id_raises`, `test_qa_approved_with_both_candidate_id_task_id_and_valid_project_id_succeeds`, `test_qa_approved_candidate_id_only_still_works_without_project_id` |
| **Detecção de projeto precisa, sem loose aliases** (FIX-005 + FIX-006) | `projects/<slug>` vence sobre `_global`/`_shared`; loose aliases `site`/`desk` removidos; paths genéricos caem em `_global`. | `test_detect_project_path_projects_subdir_beats_global`, `test_detect_project_path_strict_alias_exact_segment_only`, `test_detect_project_path_global_and_shared_still_work_when_no_projects`, `test_loose_paths_fall_back_to_global`, `test_projects_site_and_projects_desk_keep_literal_slugs`, `test_explicit_full_aliases_still_resolve`, `test_resolve_project_slug_has_no_loose_site_or_desk_keys` |
| Inbox file-per-candidate, status machine | Adapter usa `CandidateStore` oficial. | `test_full_lifecycle_session_to_promotion` |
| Janela de autoridade do agente | Agents não conseguem marcar `CANONICAL`; só `VERIFIED`. | `test_on_qa_approved_only_marks_verified_not_canonical` |

---

## 🔄 5. Fluxo de Integração

```
┌────────────────────────────┐
│ Orchestrator (Gemini PM)   │
└────────────────────────────┘
            │
   ┌────────┼──────────────────────────────┐
   │ TASK_CREATED                            │
   ▼                                         │
OrchestratorAdapter.session_start()          │
   │                                         │
   ▼                                         │
build_context_pack() → markdown + tokens     │
   │                                         │
   ▼                                         │
inject into agent prompt                     │
                                             │
   ┌─────────────────────────────────────────┘
   │ REPORT_ACCEPTED
   ▼
OrchestratorAdapter.on_report_accepted()
   │
   ▼
AutoCaptureEngine.ingest_report() → CANDIDATE files em .cerberus/inbox/
   │
   ▼
   ┌─────────────────────────────────────────┐
   │ QA_APPROVED                              │
   ▼                                         │
OrchestratorAdapter.on_qa_approved()          │
   │                                         │
   ▼                                         │
CANDIDATE → VERIFIED                          │
                                             │
   ┌─────────────────────────────────────────┘
   │ operador humano executa:
   ▼
CLI: cerberus review <id> --verify
CLI: cerberus promote <id> --apply
   │
   ▼
CANDIDATE → VERIFIED → CANONICAL (escrita atômica em LEARNINGS.md / DECISIONS.md)
```

---

## 🧪 6. Como Testar

```powershell
$env:PYTHONPATH = "C:\DevManiacs\DM-Cerebro"
$env:PYTHONDONTWRITEBYTECODE = "1"
cd C:\DevManiacs\DM-Cerebro
python -B -m unittest discover -s tests -v
```

Cobertura da Fase P2 + FIX-005 + FIX-006 + FIX-007 (ver `tests/test_orchestrator_integration.py` — **56 testes novos no total**):

### P2 — Lifecycle original (31 testes)

| Teste | Cobre |
|---|---|
| `test_resolve_project_slug_aliases` | Mapeamento de aliases canônicos |
| `test_resolve_project_slug_normalizes_separators` | Slugify de paths-like sem recursão |
| `test_resolve_project_slug_loose_aliases_removed_fix006` | **FIX-006** `site`/`desk` não viram `dev-maniacs-site`/`dm-desk` |
| `test_detect_project_from_path_alias_match_in_ancestors` | Detecção por caminho com alias no meio |
| `test_detect_project_from_path_projects_subdir` | `projects/<slug>/...` |
| `test_detect_project_from_path_global_ancestor` | Ancestral `global` → `_global` |
| `test_detect_project_from_path_shared_ancestor` | Ancestral `_shared` → `_shared` |
| `test_detect_project_from_path_empty_returns_global` | Fallback de string vazia |
| `test_discover_dynamic_projects` | Slugs novos em `projects/` são descobertos |
| `test_all_known_project_slugs_includes_base_and_aliases` | Ordenação `_global`, `_shared`, depois alfabético |
| `test_session_start_returns_context_pack_and_token_estimate` | `TASK_CREATED` end-to-end |
| `test_session_start_does_not_touch_canonical` | Canônico intocado |
| `test_session_start_resolves_alias_dm_erp_to_canteirohub` | Alias na entrada |
| `test_on_report_accepted_creates_candidate` | `REPORT_ACCEPTED` |
| `test_on_report_accepted_quarantines_secrets` | Segredos em relatório vão pra quarantine |
| `test_on_report_accepted_extracts_task_id_from_content` | Fallback `TASK-ID:` parser |
| `test_on_report_accepted_requires_task_id` | Erro quando nada é extraível |
| `test_on_qa_approved_marks_candidate_verified` | `QA_APPROVED` por id |
| `test_on_qa_approved_marks_all_candidates_for_task` | `QA_APPROVED` por task (com `project_id` agora obrigatório) |
| `test_on_qa_approved_requires_identifier` | Erro limpo sem id/task |
| `test_on_qa_approved_only_marks_verified_not_canonical` | Sem escalada para CANONICAL |
| `test_on_qa_approved_skips_quarantined` | Quarantined nunca vai para VERIFIED |
| `test_get_project_summary_returns_stats_and_key_docs` | `PROJECT_CLOSED` |
| `test_list_indexed_project_slugs` | Lista de slugs indexados |
| `test_format_agent_session_pack_includes_provenance_sentinels` | Maestri prompt block |
| `test_format_agent_session_pack_respects_explicit_project` | Override explícito |
| `test_full_lifecycle_session_to_promotion` | Ciclo completo end-to-end |
| `test_full_lifecycle_via_maestri_path_detection` | Path detection no lifecycle |
| `test_cli_session_context_command` | CLI `session-context` |
| `test_cli_on_report_accepted_command` | CLI `on-report-accepted` (conteúdo inline, FIX-006) |
| `test_cli_on_qa_approved_command` | CLI `on-qa-approved` |
| `test_cli_on_qa_approved_without_args_fails` | CLI exige argumento |

### FIX-005 — Regressões dos findings do Codex QA (12 testes)

| Teste | Finding do Codex QA |
|---|---|
| `test_qa_approval_by_task_with_project_id_only_verifies_target` | **#1** `TASK-01` em biolar não pode ser aplicado a helpdev |
| `test_qa_approval_by_task_without_project_id_raises_fix006` | **#1 + FIX-006** `task_id` sem `project_id` agora levanta `ValueError` |
| `test_qa_approval_by_candidate_id_with_wrong_project_is_skipped` | **#1** `--candidate` com `project_id` errado é pulado |
| `test_ensure_indexed_ignores_hardcoded_dm_erp_when_isolated` | **#2** Hardcoded `dm-erp` removido sob root isolado |
| `test_ensure_indexed_rejects_extra_roots_outside_allowlist` | **#2** `CERBERUS_EXTRA_ROOTS` fora do allowlist é descartado |
| `test_ensure_indexed_returns_empty_when_root_disallowed` | **#2** `CERBERUS_ROOT` fora do allowlist → 0 arquivos |
| `test_report_accepted_refuses_to_read_path_outside_root` | **#3** Path arbitrário fora do allowlist não é lido |
| `test_report_accepted_never_reads_disk_even_inside_root` | **#3 + FIX-006** Mesmo arquivos dentro de root não são abertos |
| `test_report_accepted_treats_multiline_string_as_inline` | **#3** Strings multi-linha nunca viram file read |
| `test_detect_project_path_projects_subdir_beats_global` | **#4** `projects/biolar/global/x.md` → `biolar` |
| `test_detect_project_path_strict_alias_exact_segment_only` | **#4** `site-files`/`desktop-tools`/`apae-data` não viram projetos |
| `test_detect_project_path_global_and_shared_still_work_when_no_projects` | **#4** `_global`/`_shared` ainda detectados sem `projects/` |

### FIX-006 — Contratos finais do Codex QA (8 testes)

| Teste | Contrato enforced |
|---|---|
| `test_on_qa_approved_task_id_without_project_id_raises` | **#1** `ValueError("project_id is required...")` para task_id sem project_id |
| `test_on_qa_approved_candidate_id_only_still_works_without_project_id` | **#1** Modo `candidate_id` não exige `project_id` |
| `test_on_report_accepted_calls_ingest_report_with_allow_file_false` | **#2** Spy verifica `allow_file=False` e payload literal |
| `test_on_report_accepted_does_not_emit_source_path` | **#2** Result nunca tem `source_path` |
| `test_loose_paths_fall_back_to_global` | **#3** `C:/unrelated/site`, `C:/my_desk` → `_global` |
| `test_projects_site_and_projects_desk_keep_literal_slugs` | **#3** `projects/site`, `projects/desk` mantêm slug literal |
| `test_explicit_full_aliases_still_resolve` | **#3** `dev-maniacs-site`, `dm-desk`, `dm-erp` ainda funcionam |
| `test_resolve_project_slug_has_no_loose_site_or_desk_keys` | **#3** `PROJECT_ALIASES` não contém `site` nem `desk` |

### FIX-007 — Guard incondicional de `project_id` quando `task_id` é fornecido (4 testes)

| Teste | Contrato enforced |
|---|---|
| `test_qa_approved_with_both_candidate_id_and_task_id_requires_project_id` | **#1** `(candidate_id, task_id, project_id=None)` levanta `ValueError` |
| `test_qa_approved_with_both_candidate_id_task_id_and_empty_project_id_raises` | **#1** `(candidate_id, task_id, project_id=""/whitespace)` levanta `ValueError` |
| `test_qa_approved_with_both_candidate_id_task_id_and_valid_project_id_succeeds` | **#1** `(candidate_id, task_id, project_id="biolar")` funciona |
| `test_qa_approved_candidate_id_only_still_works_without_project_id` | **#1** `candidate_id` sozinho (sem `task_id`) continua sem exigir `project_id` |

**Total**: **88 testes** (`32 originais + 31 P2 + 12 FIX-005 + 9 FIX-006 + 4 FIX-007`), todos passando — **100% green**.

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

---

## 🛣️ 7. Roadmap (próximas fases)

- **P3 — File watcher**: detectar `REPORT*.md`, `HANDOVER.md`, `ADR*.md` automaticamente.
- **P3 — Adapter formal para Maestri canvas**: mensagens `TASK_CREATED`/`QA_APPROVED` via WebSocket ou canal nativo.
- **P4 — Conflict detection**: dois candidatos contraditórios viram `CONFLICT` em vez de silenciosamente sobrescrever.
- **P4 — Rollback / uninstall** explícito no installer.

---

## 🛠️ 8. Changelog

### v1.1.0 (30/08/2026) — FIX-005

Refinamentos de precisão endereçando 4 findings do Codex QA:

- **`OrchestratorAdapter.on_qa_approved(candidate_id, task_id, project_id=None)`**
  Novo parâmetro `project_id` para escopo de projeto. Quando usado com `task_id`,
  filtra candidatos ao slug alvo. Quando usado com `candidate_id`, recusa
  aplicar a candidato de outro projeto.

- **`OrchestratorAdapter.ensure_indexed()`** sem hardcoded
  `C:/DevManiacs/migra/dm-erp/docs`. Em vez disso, consulta
  `CERBERUS_ROOT` (com validação contra `CERBERUS_ALLOWED_ROOTS`)
  e opcionalmente `CERBERUS_EXTRA_ROOTS` (mesma validação).
  Se nada é configurado, indexa apenas `application_root`.

- **`OrchestratorAdapter.on_report_accepted()`** agora delega a
  `_resolve_report_payload()` que abre arquivo apenas se
  `(a)` a string for path-like e `(b)` o caminho resolvido cair
  dentro do allowlist. Multi-line strings são sempre tratadas como
  conteúdo inline.

- **`detect_project_from_path()`** com nova ordem de prioridade:
  `projects/<slug>/` vence `_global`/`_shared`. Aliases estritos
  (`STRICT_PATH_ALIASES`) substituem o match permissivo por
  `PROJECT_ALIASES` para evitar que pastas como `site-files`,
  `desktop-tools`, `apae-data` sejam classificadas como projetos.

### v1.2.0 (30/08/2026) — FIX-006

Endurecimento final dos contratos do Codex QA — fail-closed sem exceções:

- **`OrchestratorAdapter.on_qa_approved(task_id=..., project_id=None)`**
  agora **levanta `ValueError`** quando `project_id` é `None`, vazio ou só
  espaços em branco, com a mensagem
  `"project_id is required when approving by task_id to prevent
  cross-project verification"`. O modo `candidate_id` continua
  opcional para escopo de projeto (o id já é único).

- **`OrchestratorAdapter.on_report_accepted()` é estritamente
  content-only.** Sempre passa `allow_file=False` para
  `AutoCaptureEngine.ingest_report()`. O helper
  `_resolve_report_payload()` e o campo `source_path` foram removidos.
  Nenhum arquivo do disco é aberto, mesmo que esteja dentro do
  allowlist. Caller deve ler o arquivo e passar o conteúdo inline.

- **`PROJECT_ALIASES` perdeu os aliases soltos `site` e `desk`**.
  Apenas os nomes completos `dev-maniacs-site` e `dm-desk` continuam
  remapeáveis. Para suportar um projeto literalmente chamado
  `site` ou `desk`, basta criar `projects/site` ou `projects/desk`
  (a regra `projects/<slug>` aceita qualquer slug verbatim).

- **`detect_project_from_path()` ficou mais conservador.** Removida a
  regra de fallback que pegava o "closest non-empty folder name".
  Paths genéricos que não batem em `projects/<slug>`, `_global`,
  `_shared` ou alias exato agora retornam **`_global`** —
  incluindo `C:/unrelated/site` e `C:/my_desk`.

### v1.3.0 (30/08/2026) — FIX-007

Refinamento cirúrgico do guard de QA — fail-closed incondicional:

- **`OrchestratorAdapter.on_qa_approved` agora exige `project_id`
  sempre que `task_id` é fornecido**, mesmo que `candidate_id` também
  seja fornecido. A combinação `(candidate_id, task_id, project_id=None)`
  era uma brecha silenciosa onde `task_id` poderia mass-verificar
  candidatos em outros projetos. Mensagem:
  `"project_id is required whenever task_id is specified to prevent
  cross-project verification"`.

- **Apenas o modo puro `candidate_id`** (sem `task_id`) continua
  permitindo `project_id` opcional — o id já é único, não há risco
  de cross-project.

- **CLI e exemplos de API atualizados** para refletir o contrato
  obrigatório: `cerberus on-qa-approved --task TASK-X --project SLUG`
  (o `--project` é obrigatório quando `--task` é fornecido).

- **Doc clean-up**: tabela de aliases sem `site`/`desk`, regra #5
  renomeada para "nada casou → `_global`" (sem fallback "closest folder"),
  exemplos `C:/unrelated/site` e `C:/my_desk` corrigidos para `_global`.

### v1.3.1 (30/08/2026) — DOC-FIX-008

Dois ajustes de documentação alinhados pelo Codex QA (sem mudança de código):

- **§1 (event table)** — assinatura de `on_qa_approved` atualizada de
  `on_qa_approved(candidate_id=None, task_id=None)` para
  `on_qa_approved(candidate_id=None, task_id=None, project_id=None)`,
  com nota explícita de que `project_id` é **obrigatório** sempre que
  `task_id` for fornecido (guard fail-closed anti cross-project, vide
  FIX-007).

- **§6 (test breakdown table)** — adicionada a distribuição por
  arquivo canônica:
  - `test_candidate_pipeline.py`: 11
  - `test_cerberus_engine.py`: 6
  - `test_cli_integration.py`: 2
  - `test_index_hardening.py`: 8
  - `test_installer.py`: 2
  - `test_mcp_protocol.py`: 3
  - `test_orchestrator_integration.py`: 56
  - **TOTAL: 88**

  Correção: `test_cerberus_engine.py` tem **6** testes (não 7 — o 7º
  teste MCP vive em `test_mcp_protocol.py`).

---

NO IMPLEMENTATION  
NO COMMIT  
NO PUSH
