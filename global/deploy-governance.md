---
titulo: Deploy Governance — State Machine e Gates de Produção
tags: [global, deploy, state-machine, production, gates]
atualizado: 2026-08-26
status: ativo
---

# 🚀 Deploy Governance — DM-CEREBRO

> **Documento canônico (dm-erp):** arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp`, registrado como `TASK-GOV-AI-008` / **ADR-014 (dm-erp)**, §8 (Deploy Governance). Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. O **texto** é o que é canônico.
> **Este arquivo** generaliza a governança de deploy para todos os produtos Dev Maniac's.

---

## 1. State Machine (estados de uma TASK significativa)

```text
IMPLEMENTED
   ↓
VALIDATED
   ↓
QA APPROVED
   ↓
PO GATE
   ↓
DEPLOYED
   ↓
PRODUCTION VERIFIED
   ↓
CLOSED
```

- **`IMPLEMENTED`** — código escrito. Não significa "pronto".
- **`VALIDATED`** — testes locais + smoke executados.
- **`QA APPROVED`** — Gemini QA (ou substituto) emitiu parecer positivo.
- **`PO GATE`** — Helbert Moura aprovou. Sem este gate, **não há transição para `DEPLOYED`**.
- **`DEPLOYED`** — artefato em produção. Em Risk 3–4, exige `GLM-5.3 Max Audit` antes do `PO GATE Final`.
- **`PRODUCTION VERIFIED`** — evidência objetiva pós-deploy (smoke, log, métrica, healthcheck).
- **`CLOSED`** — trabalho terminado e verificado em produção.

> **`IMPLEMENTED` ≠ `CLOSED`.** Não reportar `CLOSED` apenas porque o código foi escrito.

---

## 2. Gates por Risk Level

| Risk | Gates obrigatórios antes de `DEPLOYED` |
| :--- | :--- |
| **1** | `IMPLEMENTED` → `VALIDATED` → `PO GATE` → `DEPLOYED` → `PRODUCTION VERIFIED` → `CLOSED` |
| **2** | `+ QA APPROVED` antes de `PO GATE` |
| **3** | `+ GLM-5.3 Max (CTO) design/ADR` antes da implementação; `+ GLM-5.3 Max Audit` antes de `PO GATE Final` |
| **4** | Tudo do Risk 3 + `PO GATE` antes de `DEPLOYED` + auditoria pós-deploy |

---

## 3. Regras Inegociáveis

- **Nunca** deployar sem `PO GATE`.
- **Nunca** reportar `CLOSED` sem `PRODUCTION VERIFIED` (smoke/log/métrica real).
- **Sempre** preservar evidência (commit SHA, tag, imagem Docker, log, smoke test, métrica).
- **Sempre** manter **rollback** preparado. Sem rollback claro, sem `DEPLOYED`.
- **Nunca** pular `GLM-5.3 Max Audit` em Risk 3–4.
- **Sempre** separar quem implementa de quem aprova.

---

## 4. Compatibilidade com HANDOVER.md

O log `HANDOVER.md` (raiz) é append-only. Cada transição de estado pode (e deve) gerar uma entrada em `HANDOVER.md` quando envolver mais de um agente/sessão. Formato: ver `templates/handover.md`.

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
