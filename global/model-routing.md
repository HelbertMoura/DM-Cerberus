---
titulo: Model Routing — Bloco MODEL ROUTING e Decision Tree
tags: [global, model-routing, model, model-routing-block, decision-tree]
atualizado: 2026-08-26
status: ativo
---

# 🧭 Model Routing — DM-CEREBRO

> **Documento canônico:** arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp`, registrado como `TASK-GOV-AI-008` / **ADR-014 (dm-erp)**, §2.1 e §2.2. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. O **texto** é o que é canônico.
> **Este arquivo** reproduz o bloco `MODEL ROUTING` canônico e a decision tree para uso em qualquer projeto Dev Maniac's. Para a governança AI completa, ler o canônico.

---

## 1. Bloco `MODEL ROUTING` (obrigatório antes de qualquer handoff)

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODEL ROUTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK: <TASK-ID>
PROJECT: <project-slug>
RISK: 1 / 2 / 3 / 4
USE MODEL: <Gemini PM | GLM-5.3 Max | GLM-5.3-Flash | MiniMax M3 | MiniMax M2.7-Highspeed | Gemini QA | Opus 4.6/Antigravity>
USE TOOL: <ZCode | MiniMax | Gemini | Antigravity>
MODE: <MEDIUM | HIGH | MAX | N/A>
ROLE: <Role do Agente>
USE SKILLS: <$skill-name ... ou NONE>
WHY: <1–3 frases justificando a escolha>
ESCALATION CONDITION: <critério claro para escalar para GLM-5.3 Max ou GLM-5.3-Flash MAX>
PARALLEL SAFE: <YES | NO>
SHARED FILES: <[...] ou NONE>
SHARED ENVIRONMENT: <YES | NO>
DEPLOY COLLISION RISK: <LOW | MEDIUM | HIGH | N/A>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **Campos novos ou reforçados em 26/08/2026:**
> - `MODE` — obrigatório para `GLM-5.3-Flash` (MEDIUM/HIGH/MAX). Use `N/A` para modelos sem modos.
> - `PARALLEL SAFE` / `SHARED FILES` / `SHARED ENVIRONMENT` / `DEPLOY COLLISION RISK` — obrigatórios sempre que houver perspectiva de execução concorrente.

---

## 2. Decision Tree (resumo)

1. **PM / orquestração / decomposição**? ➔ `Gemini PM`.
2. **QA independente / testes**? ➔ `Gemini QA` (sessão separada). Se Gemini indisponível, nova sessão `GLM-5.3-Flash` dedicada a QA.
3. **Segurança estrutural, multi-tenant, auth/RBAC, SEFAZ/cofre A1, DR, GO/NO-GO, decisão irreversível**? ➔ `GLM-5.3 Max` (CTO).
4. **Raciocínio técnico, debugging, code review, frontend, backend, planning, refactor médio, UX, browser QA, recovery, audit, release**? ➔ `GLM-5.3-Flash` com `MODE` declarado.
5. **Implementação pesada, grande volume de código, muitos arquivos, execução extensa de plano**? ➔ `MiniMax M3` (default).
6. **Tarefa trivial com vantagem operacional de velocidade**? ➔ `MiniMax M2.7-Highspeed` **apenas** se a velocidade trouxer benefício real. Caso contrário ➔ M3.
7. **Dúvida Flash vs Max**: iniciar com Flash. Escalar para Max se houver ambiguidade arquitetural, risco de segurança estrutural ou decisão irreversível.
8. **Dúvida Flash vs M3**: raciocínio/design ➔ Flash; **implementação pesada** ➔ M3.
9. **Dúvida M2.7 vs M3**: preferir M3. M2.7 é o atalho opcional, não o caminho padrão.

---

## 3. Modos de Raciocínio — GLM-5.3-Flash

| Modo | Quando usar |
| :--- | :--- |
| `MEDIUM` | Tarefas pequenas/normais, review rotineiro, investigação direta. |
| `HIGH` *(default diário)* | Debugging, review multi-arquivo, frontend, performance, UX, release normal. |
| `MAX` | Recovery de tarefa interrompida, debugging difícil, audit abrangente, coordenação de release complexa, alta ambiguidade. |

> ⚠️ **Não confundir:** `Flash MAX` (modo) **≠** `GLM-5.3 Max` (modelo CTO).

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
