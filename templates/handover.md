---
titulo: Template — HANDOVER
tags: [template, handover, passagem-bastao, log]
atualizado: 2026-08-26
status: ativo
---

# 📋 Handover Log — Passagem de Bastão

> **Template oficial.** Toda passagem de bastão entre agentes ou entre sessões deve usar este formato.
> **Local padrão global:** `HANDOVER.md` (raiz). **Local local:** `projects/<slug>/handover.md`.

---

## Formato de Entrada

```markdown
## [<ISO-8601-Data> <HH:MM>] <AGENTE_ORIGEM> ➔ <AGENTE_DESTINO>

**Sessão:** <breve descrição do que estava rolando>
**Tarefa executada:** <o que foi feito>
**Arquivos criados/alterados:**
- <caminho/arquivo1.md>
- <caminho/arquivo2.md>

**Decisão técnica (ADR-XXX):** <link ou resumo>
**Aprendizado (LEARN-XXX):** <link ou resumo>
**Status:** ✅ concluído | 🟡 parcial | 🔴 bloqueado

**Próximo passo:** <o que o próximo agente ou sessão deve fazer>
**Commit:** <sha do commit> *(se houver)*
```

---

## Regras

1. **Append-only** — nunca apagar entradas anteriores; só adicionar (mais recente primeiro).
2. **Granularidade** — uma entrada por sessão ou por transição de estado de uma task.
3. **Cross-reference** — sempre linkar ADR / LEARN / TASK relacionada.
4. **Atomicidade** — se a entrega inclui múltiplas tasks, fazer uma entrada por task + uma entrada de fechamento.
5. **Sem PII** — não incluir senhas, tokens ou dados pessoais.

---

## Exemplo Mínimo

```markdown
## [2026-08-26 17:30] MiniMax M3 (Senior Dev) ➔ Gemini PM

**Sessão:** Implementação do cofre A1.
**Tarefa executada:** backend/apps/nfe/certificado_views.py com AES-256-GCM/HKDF/AAD por tenant.
**Arquivos criados/alterados:**
- backend/apps/nfe/certificado_views.py
- backend/smoke_sefaz_002.py

**Decisão técnica (ADR-012):** Cofre A1 com KEK por tenant + AAD tenant_slug|cnpj.
**Aprendizado (LEARN-013):** Canonical map bug em `modulo_nfe` vs `modulo_rateio_nfe`.
**Status:** ✅ concluído
**Próximo passo:** QA independente no `smoke_sefaz_002.py`.
**Commit:** 8c4f1a2
```
