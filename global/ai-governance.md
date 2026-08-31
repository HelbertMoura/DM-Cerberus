---
titulo: AI Governance — Quem é o quê na equipe de IA da Dev Maniac's
tags: [global, ai-governance, multi-model, stack]
atualizado: 2026-08-26
status: ativo
---

# 🤖 AI Governance — DM-CEREBRO (Multi-Projecto)

> **Documento canônico (single source of truth):** arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp` (cérebro do dm-erp / RadierHUB), registrado como `TASK-GOV-AI-008` (26/08/2026) · **ADR-014 (dm-erp)**. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. O **texto** é o que é canônico, não o link.
> **Este arquivo é a ponte corporativa** do DM-CEREBRO. Não duplica a fonte. Apenas referencia, contextualiza para o multi-produto e adiciona guidance de como aplicar a governança AI nos produtos **fora** do dm-erp (Biolar, HelpDev, DM-PDV, APAE, dev-maniacs-site, hub-remote-ide etc.).

---

## 1. Equipe de IA Oficial (resumo)

| Cargo | Modelo | Função | Notas |
| :--- | :--- | :--- | :--- |
| **PO / CEO** | Helbert Moura (humano) | Visão, prioridades, gates, deploy | Autoridade final |
| **CTO / Principal Architect / Security Architect** | `GLM-5.3 Max` (Z.ai / GLM) | Arquitetura, segurança estrutural, modelagem complexa, ADRs, GO/NO-GO (Risk 3–4) | Premium/scarce — uso sob justificativa |
| **Staff Engineer / Operational Architect** | `GLM-5.3-Flash` (Z.ai / GLM) | Raciocínio técnico cotidiano, frontend, backend, debug, refactor médio, planning, recovery (Risk 1–2) | **Modos `MEDIUM` / `HIGH` / `MAX`** declarados no `MODE` do `MODEL ROUTING` |
| **Project Manager / Resident AI Orchestrator** | `Gemini` | Decomposição, Context Packs, **bloco `MODEL ROUTING` obrigatório**, gates | Quando Gemini indisponível por cota → `GLM-5.3-Flash MODE: HIGH` como PM Interino |
| **Senior Developer / Heavy Implementation Engine** | `MiniMax M3` | Implementador **padrão** (substitui M2.7 como default em tarefas triviais) | Backend, frontend, migrations, testes, refactor extenso |
| **Fast Operational Agent** | `MiniMax M2.7-Highspeed` | **Opcional / não-core** — usar só quando velocidade trouxer vantagem operacional real | Preferir M3 sempre que operacionalmente mais simples |
| **QA Engineer / Reviewer** | `Gemini QA` (sessão logicamente separada) | Validação independente | Se Gemini indisponível → nova sessão `GLM-5.3-Flash` dedicada a QA |
| **Opportunistic Capacity / Overflow** | `Opus 4.6 / Antigravity` | **NÃO-core** — aproveitar quando disponível | Gerar HANDOVER antes de sair por cota |
| **Deep Reasoning & Architecture (Token Plan)** | `Qwen 3.8 Max / DeepSeek V4` (Alibaba / Bailian) | **Capacidade Ativa** — Raciocínio profundo, 980k context, refatoração pesada | Disponível no OpenCode / Qwen Code / Maestri |

> Para o detalhamento completo (modos da Flash, gates por risco, paralelismo, worktree, deploy state machine, failover), ler o **canônico** em `protocolo-equipe-ai.md` dentro do repositório `dm-erp` (registrado como `TASK-GOV-AI-008` / **ADR-014 (dm-erp)**).

---

## 2. Aplicação em produtos fora do dm-erp

A governança AI é **global**, não específica do dm-erp. Produtos como Biolar, HelpDev, DM-PDV, APAE e dev-maniacs-site usam a **mesma** hierarquia, com as seguintes adaptações:

- **Risk 1–2** continua igual: M3 implementa, Flash raciocina, Gemini orquestra.
- **Risk 3** (decisão estrutural): escalar para `GLM-5.3 Max` (CTO) **sempre** — não há "CTO local" de produto. O CTO é único e global. Se a decisão envolver multi-tenant ou SEFAZ, citar o ADR correspondente do dm-erp (cross-pollination).
- **Risk 4** (produção/segurança): obrigatório GLM-5.3 Max + Gemini QA + PO Gate + deploy audit + production verified.

**Não invente CTOs locais de produto.** Toda decisão de arquitetura estrutural vai ao CTO global.

---

## 3. Histórico preservado (não reescrever)

- **Rodada 160 (ADR-010)**: primeiro pipeline com `Qwen 3.8 Max` como CTO. **Substituído** na prática; preservado no `dm-erp/docs/DECISIONS.md` ADR-010.
- **TASK-GOV-AI-003 (26/08/2026)**: oficializou `GLM-5.3 Max` como CTO. Removeu `GPT-5.6 Sol` e `Qwen` do pipeline automático.
- **AI-GOV-MODEL-ROUTING-007 (26/08/2026)**: adicionou `GLM-5.3-Flash` como Staff Engineer padrão Z.ai.
- **AI-GOV-STACK-HIERARCHY-008 (26/08/2026) / ADR-014 (dm-erp)**: revisão atual. M3 vira implementador padrão, M2.7 vira opcional, Flash ganha modos formais, Opus registrado como oportuístico, novas regras de paralelismo/worktree/deploy/failover, campo `MODE` no `MODEL ROUTING`.

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
