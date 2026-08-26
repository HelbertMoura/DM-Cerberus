---
titulo: Plano de Migração Proposto — DM-CEREBRO (26/08/2026)
tags: [migration, proposed, awaiting-po, destrutivo]
atualizado: 2026-08-26
status: draft
prioridade: maxima
---

# 📋 Plano de Migração Proposto (DESTRUTIVO — aguarda gate do PO)

> **⚠️ ATENÇÃO:** Este documento descreve **movimentos destrutivos** (mover, renomear, mesclar, deletar arquivos) que **NÃO** foram executados nesta rodada. Eles exigem aprovação explícita do PO antes de qualquer execução.
> **Por que não foram executados:** a regra de restrição da task `DM-CEREBRO-SECOND-BRAIN-002` diz "If a destructive move is required: STOP. Describe the proposed migration and wait for PO approval."
> **Estado da working tree após esta task:** apenas **arquivos novos criados** (não destrutivos). Nenhum arquivo existente foi movido, renomeado, mesclado ou deletado. Veja [`ARCHITECTURE-EVOLUTION-2026-08-26.md`](./ARCHITECTURE-EVOLUTION-2026-08-26.md) §Estado atual.

---

## 0. ⚠️ Gate Note — `DECISIONS.md` (PO CONFIRMATION REQUIRED BEFORE COMMIT)

> **Não modificar `DECISIONS.md` nesta task. Não arquivar nem restaurar ADRs sem autorização do PO. Não incluir `DECISIONS.md` em nenhum commit recomendado.**

- **Estado atual:** `DECISIONS.md` (raiz) está com modificações **não-commitadas** (working tree) em 26/08/2026. Essas mudanças são **propriedade do PO** e estão sob decisão do PO.
- **Regra desta task:** trate-as como **resolvidas pelo PO em momento posterior** — não tocar.
- **Implicação para QA / commit:** `DECISIONS.md` **NÃO** faz parte do conjunto de arquivos a serem commitados por esta evolução de Second Brain. O commit (se/quando o PO decidir) deve ser feito **somente pelo PO**, com revisão humana completa do diff.
- **Origem da regra:** tarefa `DM-CEREBRO-SECOND-BRAIN-FIX-004` (QA blocker 3, 26/08/2026).
- **Cross-reference:** ver também `ARCHITECTURE-EVOLUTION-2026-08-26.md` (proposta de ADR para esta evolução, que **também** aguarda integração manual pelo PO em `DECISIONS.md`).

---

## 1. Resumo

| Categoria | Contagem | Observação |
| :--- | :---: | :--- |
| **Arquivos NOVOS criados** | 18 | Aditivos; nenhum path legado alterado |
| **Arquivos EXISTENTES não movidos** | 50+ | Mantidos para compatibilidade |
| **Movimentos propostos** | 6 (sub-tarefas) | Aguardando gate do PO |
| **Decisões que precisam do PO** | 7 | Ver §6 |

---

## 2. Movimentos Propostos (sub-tarefas com gate individual)

### 2.1. Adicionar banner de "redirect" no `BRAIN.md` legado

- **Ação:** Adicionar cabeçalho de redirecionamento no topo do `BRAIN.md` apontando para `INDEX.md` como canônico novo. Manter o conteúdo atual abaixo.
- **Risco:** Baixo. Aditivo, não destrutivo.
- **Impacto:** Paths antigos continuam funcionando; novos agentes vão para `INDEX.md` primeiro.
- **Status:** **PODE SER FEITO AGORA** (se PO aprovar). Não exige migration posterior.

### 2.2. Renomear `projects/_shared/` para `global/_legacy-shared/` (proposta)

- **Ação:** Renomear `projects/_shared/` para `global/_legacy-shared/` ou `archive/historical/_shared/`. Conteúdo de `TRIADE_PROTOCOLO.md`, `CONTRATO_AGENTES.md`, `github-publicar.md`, `backup-procedimento.md` deve ser revisto: parte vai para `global/` (governança), parte vai para `archive/historical/` (específico de projetos antigos).
- **Risco:** **MÉDIO**. Prompts e ADRs podem referenciar `_shared/`.
- **Pré-condições:** (a) grep em todos os `.md` por `_shared` para mapear quem referencia; (b) decisão do PO sobre destino de cada arquivo.
- **Status:** **AGUARDANDO GATE DO PO** + auditoria de referências.

### 2.3. Mover `hub-remote-ide` para `archive/historical/hub-remote-ide/`

- **Ação:** Criar `archive/historical/hub-remote-ide/` com `README.md` resumindo o histórico (já descontinuado em 23/08/2026, conforme `HANDOVER.md` 2026-08-23 17:50). Mover conteúdo mínimo de referência.
- **Risco:** Baixo. Projeto **já descontinuado**; só formalizar o arquivo.
- **Pré-condições:** confirmar que nenhum agente ativo referencia `projects/hub-remote-ide/` (grep em `.md` e em `prompts/`).
- **Status:** **PODE SER FEITO** com aprovação do PO (verificar referências primeiro).

### 2.4. Migrar conteúdo de `wiki/` para `global/` ou `projects/<slug>/`

- **Ação:**
  - `wiki/projeto-radierhub-dmerp.md` → `projects/canteirohub/product-vision.md` (escopo local) **ou** deletar (já que `projects/canteirohub/index.md` agora cobre).
  - `wiki/infra-servidor-rocky.md` → manter em `wiki/` (cross-produto) **ou** mover para `global/infra.md`.
  - `wiki/engenharia-bdi-tcu.md`, `wiki/engenharia-eap-curvas.md`, `wiki/engenharia-rdo-digital.md`, `wiki/engenharia-rh-campo.md`, `wiki/fiscal-sefaz-a1.md`, `wiki/infra-monitoramento-ai-sentinel.md`, `wiki/modulo-*.md`, `wiki/arquitetura-dashboard-modular.md` → `projects/canteirohub/wiki/*.md` (escopo local) **ou** manter em `wiki/` (cross-produto destilado).
  - `wiki/protocolo-triade-agentes.md` → `archive/historical/` (substituído por [`global/ai-governance.md`](./global/ai-governance.md) + canônico dm-erp).
- **Risco:** **ALTO**. Wiki é referenciada por muitos lugares.
- **Pré-condições:** (a) grep em todos os `.md` por cada path; (b) decisão do PO caso a caso.
- **Status:** **AGUARDANDO GATE DO PO** + auditoria caso a caso.

### 2.5. Migrar `prompts/` para `templates/_legacy-prompts/`

- **Ação:** Mover `prompts/PROMPT_MINIMAX_M3.md`, `PROMPT_ZAI_HERMES.md`, `SYSTEM_PROMPT_PADRAO_M3.md` para `templates/_legacy-prompts/` ou `archive/historical/prompts/`. A nova governança AI está em [`global/ai-governance.md`](./global/ai-governance.md).
- **Risco:** **MÉDIO**. Prompts são usados em produção (copy-paste).
- **Pré-condições:** (a) grep em `.md` por `prompts/`; (b) decisão do PO sobre destino final.
- **Status:** **AGUARDANDO GATE DO PO** + auditoria de referências.

### 2.6. Preencher `projects/dm-desk/` e `projects/dev-maniacs-site/` quando PO responder

- **Ação:** Após o PO responder as perguntas em [`projects/dm-desk/index.md`](./projects/dm-desk/index.md) §3 e [`projects/dev-maniacs-site/index.md`](./projects/dev-maniacs-site/index.md) §4, criar os arquivos restantes (`project-state.md`, `architecture.md`, etc.).
- **Risco:** Baixo se guiado pelo PO. ALTO se tentarmos preencher sem o PO.
- **Status:** **AGUARDANDO RESPOSTA DO PO**.

---

## 3. Files NOT Moved For Compatibility (preservados por compatibilidade)

| Path | Motivo |
| :--- | :--- |
| `BRAIN.md` | Age como índice legado; agentes antigos podem referenciar. Banner de redirect proposto. |
| `HANDOVER.md` | Log append-only com 31 KB de histórico. Mover agora quebraria 23/08/2026 → 26/08/2026. Manter. |
| `LEARNINGS.md` | Append-only. Manter. |
| `ROADMAP.md` | Visão macro multi-produto. Manter. |
| `MEMORY.md` | Memória global estável. Manter. |
| `DECISIONS.md` | ADRs globais. **Estado modificado não-commitado pelo PO** — não tocar. |
| `wiki/` | Cross-produto destilado. Mover só com aprovação. |
| `prompts/` | Prompts copy-paste. Mover só com aprovação. |
| `raw/` | Gaveta de ingestão. Manter. |
| `projects/_shared/` | Cross-produto. Mover só com aprovação. |
| `projects/canteirohub/README.md` | Legado; coexiste com `index.md` (este age como mapa, aquele como visão geral). |
| `projects/canteirohub/status.md` | Legado; coexiste com `index.md` (este aponta para ele). |
| `projects/canteirohub/arquitetura.md` | Legado. |
| `projects/canteirohub/modulos-16-roadmap.md` | Legado. |
| `projects/canteirohub/auditoria-360-usabilidade.md` | Legado. |
| `projects/canteirohub/relatorio-auditoria-final.md` | Legado. |
| `projects/biolar/{README,status,arquitetura,deploy}.md` | Legado; coexiste com `index.md`. |
| `projects/helpdev/{README,status}.md` | Legado; coexiste com `index.md`. |
| `projects/dmpdv/{README,status}.md` | Legado; coexiste com `index.md`. |
| `projects/apae-juatuba/{README,status}.md` | Legado; coexiste com `index.md`. |

## 4. Legacy References (links de compatibilidade criados nesta task)

- `BRAIN.md` — **a redirecionar** para `INDEX.md` (proposto em §2.1, aguardando gate).
- `INDEX.md` §12 — declara explicitamente o status de cada arquivo (legado / novo / proposto).
- `projects/canteirohub/index.md` — aponta para `dm-erp/docs/` como canônico (single source of truth cross-repo).
- `projects/dm-desk/index.md` — marca `UNKNOWN — NEEDS PO DECISION`.
- `projects/dev-maniacs-site/index.md` — marca `UNKNOWN — NEEDS PO DECISION`.
- `global/ai-governance.md` — referencia `dm-erp/docs/brain/wiki/protocolo-equipe-ai.md` como canônico.

## 5. Duplicações Encontradas (informativo)

| Item | Onde duplica | Ação proposta |
| :--- | :--- | :--- |
| Protocolo da Tríade (Gemini+M3+GLM) | `wiki/protocolo-triade-agentes.md` + `projects/_shared/TRIADE_PROTOCOLO.md` + `dm-erp/docs/brain/wiki/protocolo-equipe-ai.md` + `dm-erp/AGENTS.md` | Não remover aqui (mover para `archive/historical/` exige gate). `global/ai-governance.md` referencia o canônico dm-erp. |
| Info do servidor Rocky | `MEMORY.md` + `wiki/infra-servidor-rocky.md` + `dm-erp/docs/brain/MEMORY.md` | Manter (formato cross-cérebro é OK). |
| ADRs 001-012 do dm-erp | `dm-erp/docs/DECISIONS.md` + `DECISIONS.md` (raiz) com versões parciais | **Não** reescrever `DECISIONS.md` raiz. Versão canônica é `dm-erp/docs/DECISIONS.md`. `DECISIONS.md` raiz pode ser eventualmente consolidado. |
| Contrato de agentes | `projects/_shared/CONTRATO_AGENTES.md` + `global/ai-governance.md` (registro) | `CONTRATO_AGENTES.md` é o contrato operacional copy-paste; `global/ai-governance.md` é o registro declarativo. Coexistem. |

## 6. Decisões que Precisam do PO

| # | Decisão | Onde documentar |
| :--- | :--- | :--- |
| 1 | Aprovar esta proposta de migração? | Resposta no `HANDOVER.md` global. |
| 2 | Aceitar `ARCHITECTURE-EVOLUTION-2026-08-26.md` como ADR formal (integrar ao `DECISIONS.md`)? | `DECISIONS.md`. |
| 3 | Adicionar banner de redirect no `BRAIN.md`? | Editar `BRAIN.md`. |
| 4 | Confirmar escopo real de `dm-desk` (NOC/SOC, hub de IDEs, ou outro)? | `projects/dm-desk/index.md` atualizado. |
| 5 | Confirmar escopo real de `dev-maniacs-site` (é o mesmo que `portifoliodev` em :2543)? | `projects/dev-maniacs-site/index.md` atualizado. |
| 6 | Mover `wiki/protocolo-triade-agentes.md` e `projects/_shared/{TRIADE_PROTOCOLO,CONTRATO_AGENTES}.md` para `archive/historical/`? | `archive/historical/`. |
| 7 | Comitar toda a working tree (DECISIONS.md + 4 wiki não-commitados + 18 novos arquivos)? | `git commit`. |

> **Nota sobre #7:** a tarefa `DM-CEREBRO-SECOND-BRAIN-FIX-004` (QA blocker 3) instrui **NÃO** incluir `DECISIONS.md` no commit recomendado desta evolução. Se/quando o PO decidir comitar, deve fazê-lo **manualmente** após revisão humana completa do diff de `DECISIONS.md`. Os outros arquivos (BRAIN.md com banner, 4 wiki não-commitados, novos arquivos da evolução) podem ser commitados pelo PO separadamente.

## 7. UNKNOWN Items

- **NÃO** conhecemos o owner real (humano) de cada projeto além do Helbert.
- **NÃO** conhecemos o stack detalhado de `helpdev` e `dmpdv` (apenas domínio/porta).
- **NÃO** conhecemos o escopo real de `dm-desk` e `dev-maniacs-site`.
- **NÃO** conhecemos se há referências externas (outros agentes, automação, prompts) a `wiki/` ou `prompts/` além do que conseguimos auditar localmente.

---

**Última atualização:** 26 de Agosto de 2026 · **Status:** PROPOSTA aguardando gate do PO
