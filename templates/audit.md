---
titulo: Template — AUDIT (CTO Audit / Security Audit)
tags: [template, audit, cto, security, parecer]
atualizado: 2026-08-26
status: ativo
---

# 🏛️ Parecer de Auditoria Arquitetural & Segurança · TASK-XXX

> **Template oficial.** Preenchido por `GLM-5.3 Max` (CTO) em sessões de Risk 3–4.
> **Cross-reference:** `global/qa-policy.md` (separação PM vs QA) + `global/security-baseline.md` (baseline).

---

## Cabeçalho

```markdown
# 🏛️ PARECER DE AUDITORIA ARQUITETURAL & SEGURANÇA · TASK-<XXX>

**Autor:** GLM-5.3 Max (CTO / Security Architect)
**Data:** AAAA-MM-DD
**Sessão:** <breve descrição do escopo da auditoria>
**Task sob auditoria:** [TASK-XXX](../tasks/TASK-XXX.md) *(exemplo/ilustrativo — caminho opcional; a localização real da TASK depende do projeto. Se o repositório/projeto não tiver uma pasta `tasks/`, adapte para o path real: por exemplo, `projects/<slug>/tasks/TASK-XXX.md` quando criada, ou referencie a TASK pelo ID no `HANDOVER.md` global.)*
**Risk Level:** 1 / 2 / 3 / 4
**Modo:** MAX (auditoria sempre no modo mais alto do CTO)
**Skills usadas:** <$skill-1, $skill-2 ou NONE>
```

## Veredito Final

```markdown
**VEREDITO FINAL:** [ AUTORIZADO PARA PRODUÇÃO | AUTORIZADO COM RESSALVAS | BLOQUEADO ]
```

## Avaliação

```markdown
1. **Conformidade com a Arquitetura Global:** [ 100% Conforme | Desvios Identificados ]
2. **Blindagem Multi-Tenant & Segurança:** [ Aprovado | Risco Identificado ]
3. **Integridade de Banco & Migrations:** [ Segura | Requer Ajuste ]
4. **Impacto no Ecossistema:** [ Neutro / Positivo ]
5. **Observabilidade & Failure Modes:** [ Adequado | Requer Plano ]
6. **Performance & Escalabilidade:** [ Adequado | Requer Otimização ]
7. **Acessibilidade (quando aplicável):** [ WCAG 2.2 AA Conforme | Requer Ajuste ]
```

## Findings (classificação proporcional)

Use a taxonomia padrão:

- **Blocker (P0):** Impede continuidade/deploy imediatamente.
- **Binding Condition:** Condição mandatória vinculada ao DoD da próxima fase.
- **Backlog:** Melhoria ou débito técnico não-bloqueante.
- **False Positive:** Alarme falso devidamente justificado.
- **Unknown:** Ponto com informação insuficiente que exige validação empírica.

```markdown
### Findings

| ID | Tipo | Descrição | Arquivo | Ação |
| :--- | :--- | :--- | :--- | :--- |
| F-01 | Blocker P0 | <descrição> | <path> | <correção imediata> |
| F-02 | Binding | <descrição> | <path> | <vincular ao DoD> |
| F-03 | Backlog | <descrição> | <path> | <registrar e seguir> |
| F-04 | False Positive | <descrição> | <path> | <justificar> |
| F-05 | Unknown | <descrição> | <path> | <validar empiricamente> |
```

## Recomendação ao PO

```markdown
**Recomendação ao Product Owner (Helbert):**
[ Liberar para deploy / Solicitar refatoração / Bloquear até X ]
```

## Anexos / Evidência

- <smoke test executado>
- <logs revisados>
- <commits analisados>
- <ADR relacionadas>

---

**Próximo passo:** <o que o Gemini PM / MiniMax M3 deve fazer com base no parecer>
