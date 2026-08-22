---
titulo: Contrato Obrigatório dos Agentes — Ler e Atualizar o Cérebro
tags: [tríade, sistema, cerebro, contrato, gemini, m3, zai, obrigatorio, shared]
atualizado: 2026-08-22
status: ativo
prioridade: maxima
---

# 🔒 Contrato Obrigatório dos 3 Agentes — Sempre Ler & Atualizar o Cérebro

> **Objetivo:** Toda IA (Gemini, MiniMax M3, Z.AI/Hermes) é **obrigada** a:
> 1. **LER** o cérebro antes de agir
> 2. **ATUALIZAR** o cérebro após agir
> 3. **COMMITAR + PUSHAR** no GitHub
>
> Caminho oficial: `C:\Users\Helbert\Desktop\DM-Cerebro\`

---

## 📜 Trecho Universal — Cole no Início de Todo Prompt

```markdown
[SISTEMA — CONTRATO DO CÉREBRO DM-CEREBRO]

Você É OBRIGADO a seguir este protocolo ANTES e DEPOIS de qualquer tarefa técnica:

**1. ANTES de começar:**
- Leia OBRIGATORIAMENTE estes 3 arquivos:
  • C:\Users\Helbert\Desktop\DM-Cerebro\BRAIN.md
  • C:\Users\Helbert\Desktop\DM-Cerebro\projects\_shared\TRIADE_PROTOCOLO.md
  • C:\Users\Helbert\Desktop\DM-Cerebro\DECISIONS.md (últimas 5 ADRs)
- Se a tarefa envolve produto X, leia também:
  • C:\Users\Helbert\Desktop\DM-Cerebro\projects\<slug-do-produto>\README.md
  • C:\Users\Helbert\Desktop\DM-Cerebro\projects\<slug-do-produto>\status.md

**2. APÓS concluir a tarefa:**
- Atualize o arquivo correspondente no DM-Cerebro:
  • Decisão nova → adicione ADR-XXX em DECISIONS.md
  • Armadilha/erro → adicione LEARN-XXX em LEARNINGS.md
  • Mudança de produto → atualize projects/<slug>/status.md
  • Conhecimento técnico novo → crie/atualize wiki/<tema>.md
- Faça commit com mensagem clara:
  • git add . && git commit -m "<tipo>: <descrição objetiva>"
- Faça push:
  • git push origin main

**3. SE NÃO CONSEGUIR atualizar o cérebro:**
- Pare e avise o Helbert explicitamente no relatório final.
- NÃO entregue a tarefa como "pronta" sem atualizar.

**4. REGRAS INEGOCIÁVEIS (TRIADE_PROTOCOLO.md):**
- 🚫 Proibido emojis em UI → use Lucide-React
- 🌐 Obrigatório i18n PT-BR + EN-US + ES via useI18n()
- 👷 ISO 44px + luvas de obra
- 🔒 Multi-tenant estrito + LGPD
- 👑 Helbert sempre no comando manual — você NUNCA dispara outro agente sozinho

FIM DO CONTRATO — Comece executando.
```

---

## 🎯 Como Usar por IA

### 🚀 MiniMax M3 (App / CLI)
1. Abra `prompts/SYSTEM_PROMPT_PADRAO_M3.md` (criado abaixo)
2. Copie o **trecho universal acima**
3. Cole no início do prompt da tarefa
4. Descreva a tarefa

### 🧠 Z.AI GLM 5.3 (Hermes Agent — ESTE CHAT)
✅ **Já roda automaticamente.** A skill `wolf-bridge` + este contrato garante leitura/Atualização.
> Se o cérebro não foi atualizado, você vai ver aviso aqui mesmo.

### ♊️ Gemini (Antigravity)
- **Não dá pra forçar server-side** (Google controla)
- **Solução:** Copie o trecho universal acima e cole **no início de todo prompt** que você mandar pro Gemini
- Dica: salve nos favoritos do navegador

---

## 🚨 Auditoria — Como Saber se o Agente Cumpriu

| Sinal | Significado |
|---|---|
| ✅ Commit novo aparece no GitHub | Agente **CUMPRIU** |
| ❌ Tarefa entregue sem commit | Agente **FALHOU** — cobrar |
| 🟡 Commit só com código, sem wiki/DECISIONS | Agente **CUMPRIU PARCIAL** |
| 🔴 Reportou sem dizer "cérebro atualizado" | Helbert **DEVE COBRAR** |

**Comando de auditoria rápida (você roda sempre):**
```bash
cd C:\Users\Helbert\Desktop\DM-Cerebro
git log --oneline -5
# Veja os últimos 5 commits — cada um é prova que um agente mexeu
```

---

## 🔄 Fluxo Atualizado (com Contrato Ativo)

```
Helbert dispara prompt com CONTRATO embutido
                │
                ▼
   ┌────────────────────────────�
   │  Agente lê 3+ arquivos    │ ← OBRIGATÓRIO
   │  (BRAIN, TRIADE, ADR)     │
   └─────────────�──────────────┘
                 ▼
   ┌────────────────────────────┐
   │  Executa a tarefa         │
   └─────────────┬──────────────┘
                 ▼
   ┌────────────────────────────┐
   │  Atualiza cérebro         │ ← OBRIGATÓRIO
   │  (wiki/DECISIONS/status)  │
   └─────────────�──────────────┘
                 ▼
   ┌────────────────────────────┐
   │  git add + commit + push  │ ← OBRIGATÓRIO
   └─────────────┬──────────────┘
                 ▼
   ┌────────────────────────────┐
   │  Reporta Helbert com link │ ← AUDITÁVEL
   │  do commit no GitHub      │
   └────────────────────────────┘
```

---

## 🎁 Bônus — Prompt Pronto pro M3

Salvei também em `prompts/SYSTEM_PROMPT_PADRAO_M3.md` pra você só copiar e colar.

---

**Última atualização:** 22/08/2026 · **Owner:** Helbert Moura · Dev Maniac's Systems
