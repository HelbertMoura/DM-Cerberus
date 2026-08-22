---
titulo: Protocolo da Tríade Multi-Agente — Setup Real em Produção
tags: [tríade, multi-agente, protocolo, gemini, m3, hermes, zai, shared]
atualizado: 2026-08-22
status: ativo
---

# 🤖 Protocolo da Tríade Multi-Agente Dev Maniac's

> **Setup REAL em produção (desde 22/08/2026):**
> - ♊️ **Gemini** → Gerente de Projetos
> - � **Z.AI (Hermes Agent)** → Engenheiro Sênior / Especialista
> - 🚀 **MiniMax M3** → Braçal direto nos CLIs

---

## � Os 3 Agentes — Divisão Real de Papéis

| Agente | Modelo | Papel Real | Onde Roda | Função |
|---|---|---|---|---|
| ♊️ **Gemini** | Gemini 2.5 | **Gerente de Projetos** | Próprio CLI Gemini | Planejamento, status, decisões de prioridade, comunicação com Helbert |
| 🧠 **Z.AI** | Hermes Agent | **Engenheiro Sênior / Especialista** | Hermes Agent (este chat) | Arquitetura, decisões complexas, debug profundo, research |
| 🚀 **MiniMax M3** | MiniMax M3 | **Braçal Direto** | CLI próprio MiniMax | Execução: código pesado, múltiplos arquivos, TDD, scaffolding |

---

## 🎯 Regra de Ouro — Quem Faz O Quê

### ♊️ Gemini (Gerente)
```
- Lê o ROADMAP.md toda manhã
- Decide prioridades da sprint
- Atualiza status.md dos projetos
- Marca bloqueios e dependências
- Reporta pro Helbert (resumo diário)
```

### 🧠 Z.AI (Especialista)
```
- Resolve problemas arquiteturais
- Debugs difíceis (4-phase: reproduce→isolate→fix→verify)
- Research / análise de opções técnicas
- Toma decisões que exigem raciocínio profundo
- Quando M3 empaca, Z.AI destrava
```

### 🚀 MiniMax M3 (Braçal)
```
- Executa tarefas delegadas
- Escreve código multi-arquivo
- Faz TDD (RED → GREEN → REFACTOR)
- Roda scaffolding e migrações
- Commita direto no Git
- Atende demanda direta do Helbert via Telegram
```

---

## 📡 Fluxo Real de Trabalho

```
┌──────────────────────────────────────────────────────────────┐
│                    Helbert Moura (CEO)                       │
│                  canal: Telegram / DM direto                 │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │  ♊️ Gemini (GP)     │
                │  Decide o quê fazer │
                └──────────┬──────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
   │  � Z.AI      │ │  🚀 M3        │ │   📦 Repo      │
   │  (Especial.)  │ │  (Braçal)     │ │   GitHub       │
   │  arquitetura  │ │  código       │ │   (DM-Cerebro) │
   │  debug deep   │ │  TDD/migraç.  │ │                │
   └────────────────┘ └────────────────┘ └────────────────┘
            │                │                │
            └────────────────┴────────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │  DM-Cerebro atualizado     │
                │  + commit + push GitHub    │
                └────────────────────────────┘
```

---

## 📋 Comandos do Helbert (via Telegram)

| Comando | Quem responde | Ação |
|---|---|---|
| `"Gemini: status dos projetos"` | ♊️ Gemini | Lê status.md + reporta |
| `"Z.AI: como arquitetar X?"` | 🧠 Z.AI (Hermes) | Análise profunda + opções |
| `"M3: implementa Y"` | 🚀 M3 | Código direto + commit |
| `"Triade: refatora Z"` | Os 3 em paralelo | Cada um faz sua parte |
| Sem prefixo | 🧠 Hermes (default) | Resolve na hora |

---

## 🔥 Por que essa divisão funciona

1. **Gemini gerencia** → Helbert não precisa decidir prioridade todo minuto
2. **Z.AI pensa** → decisões críticas não vão pro "braçal"
3. **M3 executa** → código sai rápido sem tokenizar raciocínio do especialista
4. **Paralelismo** → 3 agentes podem trabalhar ao mesmo tempo
5. **Cérebro único** → DM-Cerebro é a fonte da verdade pra todos

---

## 📚 Onde Cada Mudança Vai (mapa rápido)

| Mudança | Arquivo |
|---|---|
| Decisão arquitetural | `DECISIONS.md` (formato ADR-XXX) |
| Lição / armadilha | `LEARNINGS.md` (formato LEARN-XXX) |
| Status de produto | `projects/<slug>/status.md` |
| Deploy / infra | `projects/<slug>/deploy.md` |
| Conhecimento técnico | `wiki/<tema>.md` |
| Sprint / prazo | `ROADMAP.md` |
| Prompt reutilizável | `prompts/PROMPT_<agente>.md` |

---

## ✅ Obrigações Compartilhadas

**TODA IA ao concluir tarefa:**
1. Atualiza o DM-Cerebro (arquivo relevante)
2. Commita + pusha no Git
3. Se for decisão nova → marca ADR
4. Se for armadilha → adiciona LEARN

**PROIBIÇÕES:**
1. Mexer em outro projeto sem avisar (commit message claro)
2. Apagar arquivo sem registro em DECISIONS.md
3. Inventar dados de infra (consultar `wiki/infra-servidor-rocky.md`)

---

**Última atualização:** 22/08/2026 · **Owner:** Helbert Moura · Dev Maniac's Systems
