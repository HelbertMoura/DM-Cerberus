---
titulo: Template — DECISION (ADR)
tags: [template, decision, adr, architecture-decision-record]
atualizado: 2026-08-26
status: ativo
---

# ⚖️ ADR-<NÚMERO>: <TÍTULO DA DECISÃO>

> **Template oficial.** Decisões globais vão em `DECISIONS.md` (raiz). Decisões locais vão em `projects/<slug>/decisions.md`.
> **NUNCA** reescrever ADR anterior. Mudança = **novo** ADR superseding.

---

## Cabeçalho

```markdown
### [ADR-<NÚMERO>] <Título Curto> (Rodada <NN> · <DATA> · <AUTOR ou AGENTE>)
```

- **Data:** AAAA-MM-DD.
- **Rodada:** número da rodada operacional.
- **Autor/Agente:** Helbert / GLM-5.3 Max / Gemini / MiniMax M3 / Z.AI / multi.

## Corpo

```markdown
- **Contexto:** <problema, motivação, restrições>.
- **Decisão:** <o que foi decidido>.
- **Motivo:** <por que essa decisão>.
- **Consequências:** <o que muda; trade-offs>.
- **Supersede (se aplicável):** [ADR-XXX](../DECISIONS.md#adr-xxx) (exemplo; o caminho correto depende de onde o ADR estiver registrado: `DECISIONS.md` na raiz do DM-CEREBRO **ou** `projects/<slug>/decisions.md` local — adapte conforme o escopo).
- **Links:** <projeto, arquivo, ADR relacionada, LEARN relacionada>.
```

## Exemplo Mínimo

```markdown
### [ADR-014] Revisão da Hierarquia de Roteamento de IA (2026-08-26 · Helbert)

- **Contexto:** M2.7 estava como default para tarefas triviais; observado que M3 absorve naturalmente a maior parte da implementação, e a regra de roteamento sugeria M2.7 como par default. Multi-agentes paralelos começaram a aparecer em incidentes reais.
- **Decisão:** M3 vira implementador padrão. M2.7 vira opcional. GLM-5.3-Flash ganha modos MEDIUM/HIGH/MAX. Opus/Antigravity registrado como oportuístico. Campo MODE + 4 campos de paralelismo no MODEL ROUTING. Novas regras de paralelismo/worktree/deploy state machine/failover.
- **Motivo:** Economia de quota sem perder qualidade, separação explícita entre raciocínio (Flash) e implementação (M3), governança preventiva para incidentes paralelos.
- **Consequências:** Documento canônico `protocolo-equipe-ai.md` atualizado. `ai/STAFF_ENGINEER.md` registra modos. `ai/ARCHITECT.md` marcado SUPERSEDED. ADR-014 do dm-erp criado.
- **Supersede:** TASK-GOV-AI-003 (2026-08-26) + AI-GOV-MODEL-ROUTING-007 (2026-08-26).
- **Links:** `dm-erp/docs/DECISIONS.md#adr-014`, `dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`.
```

## Checklist Antes de Submeter

- [ ] Contexto é factual, não opinião.
- [ ] Decisão é clara e inequívoca.
- [ ] Motivo explica o **porquê**, não o **o quê**.
- [ ] Consequências incluem impactos negativos esperados.
- [ ] Não reescreve ADR anterior.
- [ ] Se supersede, linka o anterior.
- [ ] Sem PII ou segredo.
