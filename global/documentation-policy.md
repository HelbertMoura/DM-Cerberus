---
titulo: Documentation Policy — Política de documentação do DM-CEREBRO
tags: [global, documentation, policy, markdown, frontmatter, nomenclatura]
atualizado: 2026-08-26
status: ativo
---

# 📚 Documentation Policy — DM-CEREBRO

> **Filosofia:** *plain Markdown files, semantic folders, one topic = one file, one root map/index, selective reading, minimal duplication, human-readable + AI-readable.*

---

## 1. Princípios

### 1.1. One File = One Topic

Evitar arquivos gigantes contendo assuntos não relacionados. Se passar de ~500 linhas, fragmentar.

**Exemplos bons:**
- `architecture.md` (só arquitetura)
- `database.md` (só banco)
- `security.md` (só segurança)
- `business-rules.md` (só regras de negócio)

**Exemplos ruins:**
- `notes-everything.md`
- `README.md` gigante com tudo

### 1.2. Root Files Are Maps, Not Databases

- `AGENTS.md` — entry point universal (regras para agentes).
- `INDEX.md` — mapa do cérebro.
- `MEMORY.md` — somente memória global realmente estável.
- `DECISIONS.md` — decisões globais / ADRs.
- `LEARNINGS.md` — aprendizados reutilizáveis entre projetos.

**Não** transformar `AGENTS.md` ou `INDEX.md` em arquivos gigantes.

### 1.3. Global ≠ Project

- **GLOBAL** contém somente o que vale para TODOS os projetos (fica em `global/`).
- **PROJECT** contém conhecimento específico de um produto (fica em `projects/<slug>/`).
- Regra: **GLOBAL defines HOW we work. PROJECT defines WHAT we are working on.**
- Nunca aplicar silenciosamente as suposições técnicas de um projeto a outro.

### 1.4. Single Source of Truth

Cada regra/conhecimento deve ter **UM** documento canônico. Outros arquivos devem **REFERENCIAR** esse documento, não copiar blocos grandes.

- ✅ `[descrição](./path/canônico.md)`
- ✅ `@path/canônico.md` (em arquivos de entry-point)
- ❌ Copiar 50 linhas de política em cada `index.md` de projeto

### 1.5. No Hallucination

Se a informação não existir:
- ❌ Inventar.
- ✅ Marcar como `UNKNOWN — NOT DOCUMENTED — NEEDS PO DECISION`.

O cérebro prefere **lacuna honesta** a **fabricação**.

### 1.6. Backward Compatibility

**CRÍTICO.** Paths existentes podem ser referenciados por:
- `AGENTS.md` / `HANDOVER.md` de outros cérebros.
- Tarefas em andamento.
- ADRs.
- Outros agentes.
- Automação.
- Prompts copy-paste em `prompts/`.

**NÃO** mover/deletar cegamente. Estratégias preferidas:
1. Manter o path canônico existente quando razoável.
2. Criar índice/referência no novo local.
3. Marcar path legado como `SUPERSEDED — ver <canônico novo>`.
4. Migrar gradualmente com aprovação do PO.

---

## 2. Nomenclatura

- **Arquivos:** `lowercase + hifens`. Ex.: `biolar-deploy.md` (não `Biolar_Deploy.MD`).
- **Pastas:** `lowercase + hifens`. Ex.: `projects/dm-desk/`.
- **Sem espaços**, sem `camelCase`, sem underscores em nomes de arquivo.
- **Datas:** ISO 8601. Ex.: `2026-08-26`.

---

## 3. Frontmatter YAML (opcional mas recomendado)

```yaml
---
titulo: <título legível>
tags: [<tag1>, <tag2>, ...]
atualizado: AAAA-MM-DD
status: ativo | deprecated | draft
---
```

- `titulo` — frase curta, humana.
- `tags` — minúsculas, hifens, sem acentos, em array.
- `atualizado` — ISO 8601.
- `status` — `ativo` (em uso), `deprecated` (substituído), `draft` (em construção).

> O frontmatter **não** é obrigatório (manter o cérebro simples), mas é recomendado para indexação e busca.

---

## 4. Decisões (ADRs)

- Formato ADR: **Contexto · Decisão · Consequências**.
- Local canônico global: `DECISIONS.md` (raiz).
- Local local de produto: `projects/<slug>/decisions.md`.
- **NUNCA** reescrever ADRs antigos para refletir a realidade atual.
- Mudança = **novo** ADR superseding (linkando o anterior).

---

## 5. Lições (Learnings)

- `LEARNINGS.md` (raiz) é **append-only** (nunca apagar, só adicionar).
- `projects/<slug>/learnings.md` é local ao produto.
- Entrada típica: `[LEARN-NNN] Título Curto e Descritivo` + Data + Contexto + Agente + ADR relacionado + Problema + Causa raiz + Solução + Aplicar em.

---

## 6. Handover (passagem de bastão)

- `HANDOVER.md` (raiz) é **append-only**.
- `projects/<slug>/handover.md` é local ao produto.
- Formato padrão: ver `templates/handover.md`.

---

## 7. Migração & Arquivo

- Mover um arquivo para `archive/historical/` **só com aprovação do PO**.
- Marcar com banner `SUPERSEDED — ver <canônico novo>` antes de mover.
- Preservar leitura histórica. Não deletar.

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
