---
titulo: AGENTS.md — Ponto de Entrada Universal para Agentes
tags: [agents, entry-point, global, contrato, universal]
atualizado: 2026-08-26
status: ativo
---

# 🤖 AGENTS.md — Universal Agent Entry Point (DM-CEREBRO)

> **Localização canônica:** `C:\Users\Helbert\Desktop\DM-Cerebro\`
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)
> **Companion (cliente-específico):** o cérebro do **dm-erp** vive em `docs/brain/` no repositório `dm-erp` e segue governança própria. Não duplicar.
> **Governança AI oficial (multimodelo):** arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp` (cérebro do dm-erp / RadierHUB), registrado como `TASK-GOV-AI-008` (26/08/2026) · **ADR-014 (dm-erp)** — este é o **texto canônico**. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. Esta página é a **versão corporativa** (DM-Cerebro), alinhada à do dm-erp mas adaptada ao contexto multi-produto.

---

## 🎯 1. O que você DEVE fazer ao chegar aqui

Você é um agente (humano ou IA) chegando ao **DM-CEREBRO** — o Segundo Cérebro corporativo da Dev Maniac's. Para **NÃO** perder tempo nem quebrar regras:

```text
1. Ler este AGENTS.md (você está aqui)
2. Ler /INDEX.md                         (mapa do cérebro)
3. Identificar o PROJETO da tarefa
4. Ler /global/* (governança aplicável)
5. Ler /projects/<projeto>/index.md
6. Ler /projects/<projeto>/project-state.md (QUANDO PRESENTE — se ausente, use apenas o index)
7. Ler /projects/<projeto>/handover.md     (QUANDO PRESENTE — se ausente, use apenas o index)
8. Ler SÓ os docs task-relevant
```

**NÃO preload o cérebro inteiro.** Ler tudo é proibido — a menos que a tarefa seja literalmente "revisar governança" (e mesmo assim, seletivo).

> **Regra sobre arquivos opcionais:** `project-state.md`, `handover.md`, `security.md`, `database.md`, `architecture.md`, `decisions.md`, `learnings.md`, `roadmap.md`, etc. **só devem ser lidos se existirem** no `projects/<slug>/` do projeto. Se ausentes, o `index.md` age como router único e você **NÃO** deve inventar arquivos vazios só para satisfazer o read order.

---

## 📚 2. Ordem Canônica de Leitura (canonical read order)

| Tarefa | Ordem de leitura |
| :--- | :--- |
| **Tarefa normal de produto** | AGENTS.md → INDEX.md → global/* → projects/<proj>/index.md → project-state.md (QUANDO PRESENTE) → handover.md (QUANDO PRESENTE) → docs específicos |
| **Tarefa de segurança** | AGENTS.md → INDEX.md → global/security-baseline.md → projects/<proj>/security.md (QUANDO PRESENTE) → architecture.md (QUANDO PRESENTE) → decisions (QUANDO PRESENTE) |
| **Tarefa de banco/dados** | AGENTS.md → INDEX.md → projects/<proj>/database.md (QUANDO PRESENTE) → architecture.md (QUANDO PRESENTE) → decisions (QUANDO PRESENTE) |
| **Tarefa de frontend/UX** | AGENTS.md → INDEX.md → projects/<proj>/project-state.md (QUANDO PRESENTE) → architecture.md (QUANDO PRESENTE) → ux/accessibility docs (QUANDO PRESENTE) |
| **Tarefa de IA/governança** | AGENTS.md → INDEX.md → global/ai-governance.md → global/model-routing.md → global/parallel-agents.md → global/qa-policy.md |
| **Tarefa de deploy/infra** | AGENTS.md → INDEX.md → global/deploy-governance.md → global/security-baseline.md → projects/<proj>/deployment* (QUANDO PRESENTE) |

> O `projects/<proj>/index.md` é o **mapa de roteamento** do projeto — não é conteúdo. Ele diz **o que ler** para cada tipo de tarefa.

---

## 🧭 3. Princípio de Contexto Seletivo

> **Minimum sufficient context.** Se a tarefa é sobre autenticação de um único tenant, NÃO leia BDI, Curva S, ou Rateio. Leia `security.md` + `architecture.md` + `decisions` de auth. Só.

Cada `index.md` traz um **Document Routing Guide** explícito. Use-o.

---

## 🧱 4. Regras Universais (NÃO NEGOCIÁVEIS)

1. **Não versionar segredos.** Nenhuma senha, token, key, `.env` real. Usar placeholder `[CONFIGURADO VIA ENV]` ou armazenar em gerenciador externo.
2. **Não mover/deletar arquivos destrutivamente** sem aprovação explícita do PO. Preferir referência nova, redirect, ou migration gradual (ver `global/documentation-policy.md`).
3. **Não reescrever ADRs antigos** para refletir a realidade atual. Mudança = criar **novo** ADR superseding. Histórico é histórico.
4. **Não inventar detalhes técnicos.** Se não existe, marque como `UNKNOWN — NOT DOCUMENTED — NEEDS PO DECISION`. Cérebro prefere lacuna honesta a fabricacão.
5. **Não aplicar suposições de um projeto a outro.** Biolar não herda pressupostos de canteirohub. Cada `projects/<slug>/` é um **silo técnico isolado**. Regras globais (auth, deploy, governança AI) aplicam; detalhes de produto não.
6. **Não commitar/pushar/deployar** sem autorização explícita do PO. Read-only é livre. Tudo o que altera estado do repositório ou produção exige gate.
7. **Markdown simples.** Sem frameworks, sem build steps, sem dependências. Este cérebro tem que abrir em qualquer editor de texto, Obsidian, VSCode ou terminal `cat`.
8. **Frontmatter YAML opcional mas recomendado** (YAML leve: `titulo`, `tags`, `atualizado`, `status`).

---

## 🤖 5. Contrato do Agente (ler antes de agir)

Antes de qualquer tarefa técnica substantiva:

1. **Ler** `INDEX.md` + governança global aplicável + `projects/<proj>/index.md` + `project-state.md` (QUANDO PRESENTE) + `handover.md` (QUANDO PRESENTE).
2. **Confirmar escopo** com o PO se a tarefa tocar mais de um projeto ou `auth/`/`tenant/`/`deploy/`/`security/`/`database`.
3. **Classificar risco** (1–4) conforme `global/model-routing.md` (alinhado a `AI-GOV-STACK-HIERARCHY-008` do dm-erp).
4. **Emitir bloco `MODEL ROUTING`** (template em `templates/task.md`).
5. **Executar** somente com arquivos permitidos.
6. **Atualizar** o cérebro ao concluir: handover entry + status + learnings (se houver) + ADR (se houver decisão nova).
7. **Não commitar** sem PO. A entrega do agente = mudanças no working tree, prontas para revisão.

---

## 🔁 6. Compatibilidade com versões anteriores (legacy)

Os arquivos legados na raiz continuam vivos para evitar quebra de paths referenciados por automação, prompts e outros agentes:

- `BRAIN.md` — age historicamente como índice; **redireciona para `INDEX.md`** (ver topo do `BRAIN.md`).
- `HANDOVER.md` — log append-only; continua sendo o log operacional global.
- `LEARNINGS.md` — caderno global de lições; pode coexistir com `projects/<proj>/learnings.md` (escopo local).
- `ROADMAP.md` — visão macro multi-produto; coexistirá com `projects/<proj>/roadmap.md` (escopo local).
- `MEMORY.md` — memória executiva global.
- `DECISIONS.md` — ADRs globais (decisões que valem para todos os projetos).

> A migração completa para a nova arquitetura target (`global/` + `projects/<slug>/` com arquivos dedicados) é **proposta**, não executada automaticamente. Ver `proposed-migration.md` para o plano aguardando aprovação do PO.

---

## 📐 7. Multi-Modelo (CLAUDE.md, QWEN.md e compatibilidade)

`AGENTS.md` é o canônico. Arquivos de entry-point específicos de modelo (`CLAUDE.md`, `QWEN.md`, `GEMINI.md`, `M3.md`, etc.) **devem** ser finos, apenas importando o canônico:

```markdown
# Claude Agent Entry Point (compat)

@AGENTS.md
@INDEX.md

A governança canônica vive nos arquivos acima. Não duplique política aqui.
```

O mesmo princípio vale para qualquer modelo futuro. Sem exceção.

---

## 🌐 8. Onde está cada coisa (referência rápida)

| Necessidade | Onde olhar |
| :--- | :--- |
| Mapa do cérebro | [`INDEX.md`](./INDEX.md) |
| Governança AI / model routing | [`global/ai-governance.md`](./global/ai-governance.md) + [`global/model-routing.md`](./global/model-routing.md) |
| Governança QA | [`global/qa-policy.md`](./global/qa-policy.md) |
| Governança de deploy | [`global/deploy-governance.md`](./global/deploy-governance.md) |
| Baseline de segurança | [`global/security-baseline.md`](./global/security-baseline.md) |
| Regra de paralelismo | [`global/parallel-agents.md`](./global/parallel-agents.md) |
| Política de documentação | [`global/documentation-policy.md`](./global/documentation-policy.md) |
| Memória executiva global | [`MEMORY.md`](./MEMORY.md) |
| Decisões globais (ADRs) | [`DECISIONS.md`](./DECISIONS.md) |
| Lições globais | [`LEARNINGS.md`](./LEARNINGS.md) |
| Roadmap macro | [`ROADMAP.md`](./ROADMAP.md) |
| Handover log global | [`HANDOVER.md`](./HANDOVER.md) |
| Mapeamento de projetos | [`projects/`](./projects/) |
| Conhecimento técnico destilado | [`wiki/`](./wiki/) (legado — manter) |
| Prompts copy-paste | [`prompts/`](./prompts/) (legado — manter) |
| Gaveta de ingestão | [`raw/`](./raw/) |

---

**Última atualização:** 26 de Agosto de 2026 · **Versão do schema:** Second Brain multi-projeto v1 · **Owner:** Helbert Moura — Dev Maniac's Systems
