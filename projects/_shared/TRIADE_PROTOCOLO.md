---
titulo: Protocolo da Tríade Multi-Agente — Panorâmica Oficial
tags: [tríade, multi-agente, protocolo, gemini, m3, hermes, zai, glm, orquestracao, shared]
atualizado: 2026-08-26
status: superseded
---

> ## ⚠️ SUPERSEDED / LEGACY TRIAD-ONLY ROUTING
>
> **Current operational governance is defined by:**
> - [`AGENTS.md`](../../AGENTS.md)
> - [`INDEX.md`](../../INDEX.md)
> - [`global/`](../../global/) (sete documentos de governança)
> - E a referência canônica de governança AI: arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp`, registrado como `TASK-GOV-AI-008` (26/08/2026) · **ADR-014 (dm-erp)**.
>
> **Legacy instructions such as mandatory commit/push, old triad-only routing, or direct deploy authority must NOT be followed operationally.** Este arquivo descreve a tríade "Gemini + MiniMax M3 + Z.AI GLM 5.3/Hermes" como **única configuração autorizada**. A hierarquia **vigente** (26/08/2026) é mais ampla: inclui também `GLM-5.3-Flash` (Staff Engineer com modos `MEDIUM`/`HIGH`/`MAX`), `Opus 4.6` / `Antigravity` (oportunístico), `GLM-5.3 Max` como CTO formal, e regras de paralelismo, worktree, deploy state machine e failover. Ver `global/ai-governance.md` e `global/model-routing.md`.
>
> **Historical content below is preserved for audit/history only.** Não deletar.

---

# 🤖 Protocolo da Tríade Multi-Agente Dev Maniac's

> **Setup Oficial em produção (22/08/2026)**  
> Comandante-Geral: Helbert Moura · Servidor: Rocky Linux 10.2 (192.168.226.103)  
> Segundo Cérebro: `C:\Users\Helbert\Desktop\DM-Cerebro\`

---

## 👥 Quem Somos & Onde Rodamos

```
                               ┌───────────────────────────────────┐
                               │       Helbert Moura (CEO)         │
                               │   Comandante-Geral de Operações   │
                               └─────────────────┬─────────────────┘
                                                │
       ┌────────────────────────────────────────┼────────────────────────────────────────┐
       ▼                                        ▼                                        ▼
♊️ Gemini (Antigravity)             🚀 MiniMax M3                               🧠 Z.AI (GLM 5.3)
(Orquestrador + Engenheiro Chefe)  (Heavy Builder Engine)                       (Deep Reasoning Specialist)
 📍 CLI / Antigravity               📍 App / CLI M3                              📍 Hermes (App Nativo)
```

| Agente | Onde Roda | Papel & Especialidade |
|---|---|---|
| 👑 **Helbert Moura** | Comando Geral | • Define escopo e prioridades.<br>• Faz disparo manual dos prompts no Hermes e no MiniMax M3.<br>• Valida visualmente as entregas. |
| ♊️ **Gemini** | CLI / Antigravity | • Orquestrador, Arquiteto & Gerente de Projetos.<br>• Desenha arquitetura, schemas, contratos e fluxos.<br>• Gera prompts mastigados pro Helbert disparar.<br>• Integra código, roda testes no servidor 192.168.226.103, faz deploys e alimenta o Segundo Cérebro. |
| 🚀 **MiniMax M3** | App / CLI M3 | • Heavy Builder Engine (Volume de Código).<br>• Telas React 18, componentes Tailwind, views Django, serializers, PWA offline e IndexedDB.<br>• Ergonomia mobile ISO 44px e formulários intuitivos pra leigos/idosos. |
| 🧠 **Z.AI (GLM 5.3)** | Hermes (App Z.AI) | • Deep Reasoning & Alta Densidade Matemática (uso cirúrgico).<br>• Algoritmos de engenharia civil (BDI TCU, EAP Maior Resíduo, Curva S, EVM, Produtividade).<br>• Criptografia SEFAZ A1 (PKCS#12, XMLDSig, SOAP), transações atômicas com lock pessimista, blindagem PostgreSQL 16. |

---

## 🔄 O Ciclo de Operação em 5 Passos (Integration Loop)

```
1. Helbert → Gemini: "Quero implementar o Módulo X"
   Gemini modela arquitetura, dados e fluxos
   Gemini entrega: Prompt 1 (Z.AI) + Prompt 2 (M3)

2. Helbert → Z.AI (Hermes): cola Prompt 1
   Z.AI devolve motor matemático & algoritmos

3. Helbert → MiniMax M3: cola Prompt 2
   M3 devolve telas React & views Django

4. Helbert → Gemini: devolve saídas do Z.AI e M3
   Gemini audita código, integra e compila

5. Gemini → Servidor Rocky: roda 53 testes & faz Deploy DEV/PROD
   Gemini → DM-Cerebro: alimenta wiki/, DECISIONS.md, MEMORY.md
   Gemini → Helbert: reporta 100% Homologado em Produção (200 OK)
```

**Fluxo resumido:**
```
Helbert dispara → Z.AI pensa + M3 constrói → Gemini orquestra/deploy → Cérebro alimenta
```

---

## 💎 As 6 Regras de Ouro Inegociáveis da Tríade

### 👑 Regra 1 — Helbert no Comando Manual
O Gemini **nunca** tenta adivinhar ou disparar os outros agentes sozinho.
> Gemini sempre gera blocos de cópia formatados pra Helbert colar no Hermes e no M3.

### 🧠 Regra 2 — Alimentação Perpétua do Segundo Cérebro
Toda decisão técnica, cálculo ou tela criada é **imediatamente** registrada em `wiki/` e `DECISIONS.md`.
> Caminho: `C:\Users\Helbert\Desktop\DM-Cerebro\`

### 🚫 Regra 3 — Banimento Total de Emojis de Celular
**Proibido** usar emojis (`👷`, `💰`, `🏗`, `☕️`, etc.) em UI.
> Padrão obrigatório: ícones vetoriais sóbrios da biblioteca **Lucide-React**.

### 🌐 Regra 4 — Suporte Obrigatório aos 3 Idiomas
100% das telas e mensagens devem alternar perfeitamente entre:
- 🇧🇷 **PT-BR**
- 🇺🇸 **EN-US**
- 🇪🇸 **ES**
> Via hook `useI18n()`.

### 👷 Regra 5 — Ergonomia de Canteiro (ISO 44px) & Usabilidade para Leigos
- Botões grandes (`tap-44` / `tap-48`)
- Fáceis de tocar com o dedão sob sol ou com luvas de obra
- Linguagem direta, sem termos difíceis em inglês

### 🔒 Regra 6 — Isolamento Multi-Tenant Estrito & LGPD
- Nenhum dado vaza entre construtoras (`TenantModelViewSet`)
- Proteção total de dados de colaboradores e clientes

---

## 📋 Comandos do Helbert (via Telegram / DM direto)

| Comando | Quem responde | Ação |
|---|---|---|
| `"Gemini: status dos projetos"` | ♊️ Gemini | Lê `status.md` + reporta |
| `"Z.AI: como arquitetar X?"` | 🧠 Z.AI (Hermes) | Análise profunda + opções |
| `"M3: implementa Y"` | 🚀 M3 | Código direto + commit |
| `"Triade: refatora Z"` | Os 3 em paralelo | Cada um faz sua parte |
| `"Quero implementar módulo X"` | ♊️ Gemini (default orquestrador) | Aciona Integration Loop |
| Sem prefixo | 🧠 Hermes (default aqui) | Resolve na hora |

---

## �️ Onde Cada Mudança Vai (mapa rápido)

| Mudança | Arquivo |
|---|---|
| Decisão arquitetural | `DECISIONS.md` (formato ADR-XXX) |
| Lição / armadilha | `LEARNINGS.md` (formato LEARN-XXX) |
| Status de produto | `projects/<slug>/status.md` |
| Deploy / infra | `projects/<slug>/deploy.md` |
| Conhecimento técnico | `wiki/<tema>.md` |
| Sprint / prazo | `ROADMAP.md` |
| Prompt reutilizável | `prompts/PROMPT_<agente>.md` |
| Passagem de bastão entre agentes/sessões | `HANDOVER.md` (formato padrão) |

---

## ✅ Obrigações Compartilhadas

**TODA IA ao concluir tarefa:**
1. Atualiza o DM-Cerebro (arquivo relevante)
2. Commita + pusha no Git
3. Se for decisão nova → marca ADR em `DECISIONS.md`
4. Se for armadilha → adiciona LEARN em `LEARNINGS.md`
5. Respeita as 6 Regras de Ouro (especialmente 3-emoji, 4-i18n, 5-44px, 6-LGPD)
6. **Adiciona entrada de handover** em `HANDOVER.md` (passagem de bastão rastreável)

**PROIBIÇÕES:**
1. Mexer em outro projeto sem avisar (commit message claro)
2. Apagar arquivo sem registro em `DECISIONS.md`
3. Inventar dados de infra (consultar `wiki/infra-servidor-rocky.md`)
4. Usar emojis em UI (Regra 3)
5. Pular i18n (Regra 4)

---

## 🔥 Por que essa divisão funciona

- **Gemini orquestra** → Helbert não precisa decidir prioridade a cada minuto
- **Z.AI pensa** → decisões críticas não vão pro "braçal"
- **M3 executa** → código sai rápido sem tokenizar raciocínio do especialista
- **Helbert dispara** → controle manual preserva auditoria humana
- **Paralelismo** → 3 agentes podem trabalhar ao mesmo tempo
- **Cérebro único** → DM-Cerebro é fonte da verdade pra todos

---

**Última atualização:** 22/08/2026 · **Owner:** Helbert Moura · Dev Maniac's Systems
