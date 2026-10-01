---
titulo: Taxonomia Canônica do Ecossistema Dev Maniac's (Arquitetura V2)
tags: [governanca, taxonomia, conceitos, anti-bloat]
atualizado: 2026-09-06
status: ativo
---

# 🏛️ Taxonomia Canônica — Dev Maniac's Systems

> **Princípio Central:** Conhecimento, capacidade, ferramenta, tarefa e biblioteca possuem papéis distintos. Armazenar a mesma regra simultaneamente em múltiplos lugares ou transformar qualquer ferramenta nova em uma skill gera ruído, colisão de prompts e context bloat.

---

## 1. As 9 Entidades Canônicas

| Entidade | Definição | Onde Vive | Exemplo Real |
| :--- | :--- | :--- | :--- |
| **KNOWLEDGE** | Fatos estáveis, documentação técnica, regras de negócio e arquitetura do produto. | `DM-Cerebro/docs/`, `projects/<slug>/`, `global/` | Multi-tenant schema, APIs homologadas, regras tributárias SEFAZ. |
| **SKILL** | Procedimento ou workflow especializado reutilizável, carregado **sob demanda** quando a tarefa exigir. | `DM-Cerebro/skills/`, runtimes (`~/.claude/skills`, `~/.gemini/config/skills`) | `saiforanocode`, `ponytail`, `graphify`, `spec-driven-development`. |
| **TASK** | Unidade pontual de trabalho atual com escopo e critérios de aceite delimitados. | Emitido pelo Maestro via **Task Contract** e registrado no quadro. | `TASK-SEC-AUTHZ-STAFF-001`, fix de responsividade mobile. |
| **MEMORY** | Decisões arquiteturais permanentes (ADRs), invariantes e lições aprendidas entre sprints. | `MEMORY.md`, `DECISIONS.md`, `LEARNINGS.md` | Banimento de emojis em UI industrial, stack Rocky Linux, padrão JWT em cookie. |
| **TOOL** | Capacidade executável externa (CLI, binário, API, MCP) que executa uma ação mecânica. | `bin/`, CLI do sistema, MCP servers | `graphifyy` CLI, `git`, `docker`, `pytest`, `curl`, `lighthouse`. |
| **LIBRARY** | Pacote reutilizável de código/componentes integrado à aplicação via gerenciador de pacotes. | `package.json`, `requirements.txt` | Radix UI, TanStack Table, Lucide Icons, Sonner, Zod. |
| **UI PATTERN** | Solução de interação ou layout recorrente e consolidada na experiência do usuário. | `DM-Cerebro/ui-patterns/` | Navigation tabs, bottom sheet, master-detail, command palette. |
| **REFERENCE** | Fonte de inspiração, benchmark visual ou referência de produtos reais. **Nunca é copiada cegamente**. | Catálogos em `references/`, links documentados | Refero Styles, capturas de UI real, benchmarks de concorrentes. |
| **MODEL** | Motor de raciocínio/execução substituível e intercambiável que atua em um papel. | Alocado na matriz de roteamento do Maestro | Gemini, GLM-5.3-Flash, MiniMax M3/M2.7, Claude, GPT-6. |

---

## 2. Protocolo Anti-Bloat: Regra de Classificação de Novas Descobertas

Sempre que surgir uma nova ferramenta, repositório GitHub, artigo, Reel, biblioteca ou padrão visual:

```text
DESCOBERTA
    ↓
É uma capacidade de código reutilizável no projeto? ──────→ LIBRARY (ex: Cult UI, TanStack)
    ↓ (Não)
É uma solução de layout ou interação de UX? ────────────→ UI PATTERN (ex: bottom navigation)
    ↓ (Não)
É uma inspiração visual ou benchmark de produto? ───────→ REFERENCE (ex: Refero Styles)
    ↓ (Não)
É um executável mecânico, script ou CLI? ───────────────→ TOOL (ex: Shader Gradient, tree-sitter)
    ↓ (Não)
É uma regra de negócio ou documentação de sistema? ─────→ KNOWLEDGE (ex: doc de API)
    ↓ (Não)
É um workflow com instruções especializadas e repetíveis? → SKILL (com Progressive Disclosure!)
```

### 🛑 Regras de Ouro

1. **DEFAULT = NÃO CRIAR NOVA SKILL.**
   - Uma nova skill somente deve existir quando representar uma capacidade ou workflow especializado, recorrente, reutilizável e com intenção suficientemente distinta para routing confiável.
2. **Um componente bonito NÃO é uma skill.** É uma referência (`REFERENCE`) ou padrão de interface (`UI PATTERN`).
3. **Uma biblioteca NÃO é uma skill.** É uma dependência declarada (`LIBRARY` em `frontend-toolbox`).
4. **Uma ferramenta web ou executável NÃO é uma skill.** É uma ferramenta externa (`TOOL`).
5. **Uma regra de negócio ou modelo de dados NÃO é uma skill.** É conhecimento permanente (`KNOWLEDGE`).

---

## 3. Checklist Obrigatório Pré-CREATE (Governança do Maestro)

Antes de autorizar a criação de qualquer nova skill via `skill-creator`, o Maestro deve responder obrigatoriamente às 6 perguntas:

1. **Já existe skill equivalente no ecossistema?**
2. **Uma skill existente pode absorver isso mantendo alta coesão interna?**
3. **Deveria ser apenas uma referência (`references/`) ou workflow (`workflows/`) de uma skill existente?** (ex: o caso do `saiforanocode`)
4. **É somente uma tool, library, UI pattern ou referência externa?**
5. **Será realmente reutilizado em múltiplas sprints e projetos corporativos?**
6. **Possui trigger suficientemente distinto e discriminativo contra skills semanticamente próximas?**

---

## 4. Governança da Meta-Skill `skill-creator`

A **`skill-creator`** oficial da Anthropic opera no ecossistema Dev Maniac's como **META-SKILL ADMINISTRATIVA DO MAESTRO**.

### Diretrizes de Isolamento:
- **NÃO é contexto padrão:** Agentes executores (M3, M2.7, Flash) **nunca** recebem a `skill-creator` em seu prompt ou contexto inicial.
- **Carregamento sob demanda:** Carregada exclusivamente pelo Maestro diante de uma das 6 necessidades formais de ciclo de vida:
  1. `CREATE SKILL`
  2. `AUDIT SKILL`
  3. `REFACTOR SKILL`
  4. `MERGE SKILLS`
  5. `SPLIT SKILL`
  6. `DEPRECATE SKILL`

### Padrão para Criação e Refatoração de Skills:
- **Descrição curta e discriminativa** no frontmatter YAML;
- **Trigger claro e específico** (evitar "catch-all" ou "pick me energy");
- **Seção explícita de "Quando usar" e "Quando NÃO usar"**;
- **`SKILL.md` mínimo** atuando como roteador progressivo;
- **Progressive disclosure:** subdiretórios `references/` e `workflows/` carregados sob demanda;
- **Zero duplicação** de documentação canônica já existente no repositório;
- **Zero scaffolding obsoleto** destinado a limitações de modelos legados;
- **Zero instruções model-specific no core** (a skill deve ser model-agnostic);
- **Validação técnica obrigatória** com `scripts/quick_validate.py` e testes de routing.
