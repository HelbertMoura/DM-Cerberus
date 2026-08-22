---
titulo: Protocolo da Tríade Multi-Agente (Gemini + M3 + Z.AI)
tags: [tríade, multi-agente, protocolo, gemini, m3, hermes, shared]
atualizado: 2026-08-22
status: ativo
---

# 🤖 Protocolo da Tríade Multi-Agente Dev Maniac's

> **Por que esse arquivo existe:** originalmente seria `AGENTS.md`, mas esse nome é protegido pelo Hermes Agent (auto-carregado). Este arquivo é a versão explícita e versionada.

---

## 👥 Os 3 Agentes e Seus Papéis

| Agente | Modelo | Papel | Força | Limitações |
|---|---|---|---|---|
| ♊️ **Gemini** | Gemini 2.5 | **Orquestrador + QA** | Análise cruzada, leitura de PDFs grandes, validação final | Lento para código extenso |
| 🚀 **MiniMax M3** | MiniMax M3 | **Heavy Builder** | Código completo, múltiplos arquivos, TDD | Não tem contexto entre sessões |
| � **Z.AI (Hermes)** | Hermes Agent | **Deep Reasoning** | Decisões arquiteturais, debug difícil, planejamento | Caro (consome tokens) |

---

## 🎯 Regra de Divisão

```
┌─────────────────────────────────────────────────┐
│ Tarefa complexa (3+ passos)                     │
│   ├─ Gemini → planeja + valida resultado final  │
│   ├─ M3     → escreve código pesado              │
│   └─ Z.AI   → decisões + debug profundo         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Tarefa simples (1-2 passos)                     │
│   └─ M3 direto (mais rápido, barato)            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Decisão arquitetural crítica                    │
│   └─ Z.AI primeiro, Gemini valida, M3 executa   │
└─────────────────────────────────────────────────┘
```

---

## 📋 Obrigações Compartilhadas

### TODA IA é obrigada a:
1. **Atualizar o DM-Cerebro** ao concluir qualquer tarefa técnica
2. **Commitar no Git** as mudanças relevantes
3. **Atualizar status.md** do projeto afetado
4. **Marcar ADR novo** em DECISIONS.md se houver decisão arquitetural
5. **Adicionar LEARNING novo** em LEARNINGS.md se descobriu armadilha

### TODA IA é proibida de:
1. **Mexer em outro projeto** sem avisar via commit message
2. **Apagar arquivos** sem registro em DECISIONS.md
3. **Inventar dados** sobre infra/portas/servidor (consultar wiki/infra-servidor-rocky.md)
4. **Sobrescrever BRAIN.md** sem diff explícito

---

## 📚 Onde Cada Tipo de Mudança Vai

| Mudança | Arquivo |
|---|---|
| Decisão de arquitetura | `DECISIONS.md` (formato ADR-XXX) |
| Lição aprendida / erro | `LEARNINGS.md` (formato LEARN-XXX) |
| Status de produto | `projects/<slug>/status.md` |
| Deploy / infra | `projects/<slug>/deploy.md` |
| Conhecimento técnico | `wiki/<tema>.md` |
| Nova sprint / prazo | `ROADMAP.md` |
| Prompt reutilizável | `prompts/PROMPT_<agente>.md` |

---

## � Workflow Diário

```
09:00  Gemini faz daily-review: lê status.md + ROADMAP.md
      └─ Identifica bloqueios / tarefas do dia

10:00  M3 executa tarefas de código do dia
      └─ Commita direto com mensagem [feat]/[fix]/[chore]

14:00  Z.AI (Hermes) atende demandas complexas
      └─ Sessão única, resumo volta pro cérebro

17:00  Gemini faz daily-close: atualiza status.md + LEARNINGS
      └─ Commit [docs] com resumo do dia
```

---

## 🎓 Caso Especial: Como o Helbert Trabalha

> O Helbert é o **CEO + dev solo**. Ele coordena todas as 3 IAs. Quando ele pede algo, a primeira IA que responde é a **orquestradora da tarefa** (geralmente M3 ou Gemini via Telegram).

**Comando padrão no Telegram:**
- `"tarefa X pro M3"` → Heavy builder
- `"tarefa X pro Gemini"` → Análise / QA
- `"tarefa X pro Hermes"` → Deep reasoning / debug

**Sem prefixo:** Hermes responde primeiro (mais barato + rápido no Telegram).

---

## 🔗 Referências Cruzadas

- `wiki/protocolo-triade-agentes.md` — versão resumida (auto-carregada)
- `BRAIN.md` — mapa-mestre com todas as regras
- `projects/_shared/github-publicar.md` — onde esse cérebro vive online

---

**Última atualização:** 22/08/2026 · **Owner:** Helbert Moura · Dev Maniac's Systems
