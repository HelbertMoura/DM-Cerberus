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
1. **Um componente bonito NÃO é uma skill.** É uma referência ou padrão de UI.
2. **Uma biblioteca NÃO é uma skill.** É uma dependência declarada em `frontend-toolbox`.
3. **Uma ferramenta web NÃO é uma skill.** É registrada na Toolbox ou documentada como tool.
4. **Uma skill só é criada se:**
   - Possuir uma capacidade ou workflow operacional reutilizável;
   - Ter descrição curta e precisa (sem "pick me energy");
   - Adotar **Progressive Disclosure** (`SKILL.md` como router enxuto + referências sob demanda).
