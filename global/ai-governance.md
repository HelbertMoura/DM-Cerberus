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

## 1. Papéis Canônicos Universais (Model-Agnostic)

A arquitetura define **responsabilidades e contratos**, não marcas de inteligência artificial. Os papéis do ecossistema são:

| Papel Universal | Responsabilidade Primária | O que NÃO faz |
| :--- | :--- | :--- |
| **👑 Maestro / Lead Architect** | Decomposição em micropassos, emissão de **Task Contracts**, seleção de contexto mínimo, coordenação de gates. | Não escreve código de implementação diretamente; não microgerencia passos óbvios do executor. |
| **🛠️ Implementation Engineer** | Execução de código (frontend/backend/migrations/testes) com autonomia no ciclo `EXPLORE ➔ DONE` e escada Ponytail. | Não altera arquitetura estrutural sem gate; não comita ou dá deploy sem autorização humana. |
| **🔎 QA Engineer / Reviewer** | Validação independente contra critérios de aceite, testes de estresse, segurança e veredito PASS/FAIL. | Não aprova a própria implementação; não emite opiniões sem evidências de teste/diff. |
| **🧠 Principal Architect & Gatekeeper** | Decretos de arquitetura, contratos de API/DB, invariants de segurança e aprovação formal de release (Risk 3–4). | Não faz tarefas braçais de rotina quando delegáveis ao executor padrão. |

---

## 1.1 Matriz de Alocação Operacional de Modelos (Configuração Atual)

Os modelos atuam como **motores de raciocínio intercambiáveis** alocados aos papéis acima conforme capacidade e cota:

| Papel | Motor Primário Atual | Motor Alternativo / Reserva |
| :--- | :--- | :--- |
| **Maestro & Orquestrador** | `Gemini / Antigravity` | `GLM-5.3-Flash` (Modo High) / `Claude` |
| **Implementation Engineer (Braçal)** | `MiniMax M3` | `MiniMax M2.7` (tarefas de 1 arquivo) / `GLM-5.3-Flash` |
| **QA Engineer / Reviewer** | `GLM-5.3-Flash` (effort high) | `Gemini QA` / `Argus` (Codex sob demanda do PO) |
| **Principal Architect & Gatekeeper** | `GLM-5.3 Max` | `Qwen 3.8 Max` (Reserva temporária) / `Claude Opus` |

> **Princípio Model-Agnostic:** Se amanhã um novo modelo (ex: GPT-6 Astra, Claude 3.7) for plugado no pool, ele herda o **contrato do papel**, sem necessidade de reescrever a governança corporativa.

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
