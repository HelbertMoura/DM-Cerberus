---
titulo: QA Policy — Política de QA independente
tags: [global, qa, policy, independent-validation]
atualizado: 2026-08-26
status: ativo
---

# 🧪 QA Policy — DM-CEREBRO

> **Documento canônico (dm-erp):** `dm-erp/ai/QA.md` define o papel do QA Engineer (Gemini QA) no contexto do dm-erp.
> **Este arquivo** generaliza a política para todos os produtos Dev Maniac's.

---

## 1. Princípio de Separação de Papéis

> **Quem implementa não aprova o próprio trabalho.** Fluxo padrão:
> `PO → Gemini PM → Developer (M3) → Gemini QA → PO`.
> Em Risk 3–4: `… → Gemini QA → GLM-5.3 Max (CTO) Audit → PO Gate Final → Deploy`.

A QA **nunca** é feita:
- ❌ Pelo próprio executor da tarefa.
- ❌ Pelo PM (Gemini) na mesma sessão em que decompôs a tarefa.
- ❌ Pela IA que escreveu o código.

A QA **sempre** é feita:
- ✅ Por agente distinto.
- ✅ Em sessão logicamente separada (contexto limpo).
- ✅ Tratando a especificação como **hipótese** e o código como **objeto de teste rigoroso**.

---

## 2. Pipeline Padrão de QA

| Risk | Gates |
| :--- | :--- |
| **1** | Implementação (M3) → PO Gate (sem QA formal em mudança trivial). |
| **2** | PM (Gemini) → M3 → **Gemini QA** → PO Gate. |
| **3** | GLM-5.3 Max (CTO) design/ADR → PM → PO Gate → M3 → **Gemini QA** → PO Gate. |
| **4** | GLM-5.3 Max design → PO Gate → M3 incremental → **Gemini QA** → **GLM-5.3 Max Audit** → PO Gate Final → Deploy. |

---

## 3. Checklist Universal de QA

1. **Critérios de aceite** — todos os itens do DoD foram entregues?
2. **Regressão** — algo existente quebrou? Build limpo? Testes passam?
3. **Segurança** — vazamento cross-tenant? Segredo hardcoded? Permissão exposta?
4. **Multi-tenancy (quando aplicável)** — toda query filtra por tenant?
5. **Precisão matemática** (quando aplicável) — centavos, BDI TCU, rateio, Curva S, etc. — soma exata?
6. **Acessibilidade (WCAG 2.2 AA)** — teclado, foco visível, contraste 4.5:1, zoom 200%, semântica, tap-44?
7. **i18n** — strings em PT-BR/EN-US/ES sem hardcode?
8. **Mobile (360–430px)** — sem overflow horizontal, sem quebra de modal?
9. **Logs/observabilidade** — sem PII em log, sem segredo em log?
10. **Migração** — aditiva, sem lock destrutivo em produção?

---

## 4. Relatório de QA (template)

```markdown
# 🧪 RELATÓRIO DE QA & CODE REVIEW · TASK-XXX

**STATUS:** [ APROVADO | REPROVADO | APROVADO COM RESSALVAS ]

### 🔴 1. Problemas Críticos (Bloqueantes de Deploy)
- [Descrição do bug / falha de segurança / vazamento multi-tenant / regressão]

### 🟠 2. Problemas Médios / Regras de Negócio
- [Inconsistência de cálculo / validação de campo / erro em edge case]

### 🟡 3. Testes Faltantes & Melhorias
- [Testes unitários ou de integração necessários]

### 💡 4. Plano de Ação para o Developer
1. [Passo a passo cirúrgico para correção]
```

---

## 5. Failover do QA

Se `Gemini QA` estiver indisponível por cota:
- Substituir por **nova sessão limpa de `GLM-5.3-Flash`** dedicada exclusivamente a QA.
- A sessão substituta **deve** declarar `ACTIVE ROLE: QA ENGINEER` no início.
- A sessão substituta **não** pode ter sido a mesma que implementou.

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
