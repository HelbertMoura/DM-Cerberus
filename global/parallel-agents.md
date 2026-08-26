---
titulo: Parallel Agents — Regra de execução paralela entre agentes
tags: [global, parallel, worktree, branch, deploy-collision]
atualizado: 2026-08-26
status: ativo
---

# 🧵 Parallel Agents — DM-CEREBRO

> **Documento canônico:** arquivo `protocolo-equipe-ai.md` dentro do repositório `dm-erp`, registrado como `TASK-GOV-AI-008` / **ADR-014 (dm-erp)**, §6 e §7. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../../migra/dm-erp/docs/brain/wiki/protocolo-equipe-ai.md`; ajuste conforme seu layout local. O **texto** é o que é canônico.
> **Este arquivo** é a versão cross-produto da regra de paralelismo.

---

## 1. Regra-Mãe

> **Não executar múltiplos agentes em paralelo contra o mesmo:**
> - ambiente de produção;
> - árvore de deploy;
> - worktree compartilhado;
> - arquivo crítico de `auth/` / `tenant/` / `deploy/` / `login/` / `security/` / `database` / configuração de vault/criptografia.

**Baseada em incidente real de produção** (dm-erp, agosto/2026). A regra existe porque ownership sobreposta + deploy colidindo causou regressão e rollback.

---

## 2. Quando a Execução Paralela É Permitida

Somente quando **todos** os itens abaixo forem verdade:

- ✅ Escopos são independentes (features distintas, sem dependência mútua).
- ✅ Ownership de arquivos **não se sobrepõe** (cada agente mexe em arquivos diferentes).
- ✅ Alvos de deploy **não se sobrepõem** (containers / hosts / portas distintos).
- ✅ Fronteiras de rollback estão claras (rollback de um não desfaz o outro).

> Se qualquer um for `NO` ou `HIGH`, a execução paralela é **vetada**. Paralelizar com ownership sobreposta é falha de governança, não otimização.

---

## 3. Worktree / Branch

- Preferir `branch` separado ou `git worktree` para implementações concorrentes.
- Evitar múltiplos agentes acumulando alterações não relacionadas no mesmo arquivo.
- **Especialmente proibido** acumular uncommitted changes compartilhadas entre agentes em:
  - `auth/`
  - `tenant/`
  - `deploy/`
  - `login/`
  - `security/`
  - `database/`
  - arquivos de configuração de vault/criptografia.

> Se for inevitável paralelizar sobre essas áreas, escalonar para o **CTO (GLM-5.3 Max)** definir estratégia de serialização.

---

## 4. Bloco `MODEL ROUTING` — campos obrigatórios para paralelização

```text
PARALLEL SAFE: <YES | NO>
SHARED FILES: <[...] ou NONE>
SHARED ENVIRONMENT: <YES | NO>
DEPLOY COLLISION RISK: <LOW | MEDIUM | HIGH | N/A>
```

Estes campos são **obrigatórios** no `MODEL ROUTING` sempre que houver perspectiva de execução concorrente (mesmo que a tarefa atual seja serial — registre a perspectiva para que o próximo agente saiba o que evitar).

---

## 5. Handoff & Comunicação entre Agentes Paralelos

- Cada agente paralelo deve ter um **bloco `MODEL ROUTING` próprio** com `PARALLEL SAFE: YES` e `SHARED FILES: NONE`.
- Cada agente paralelo deve produzir **handover independente** ao final (formato em `templates/handover.md`).
- Se um agente paralelo descobrir que precisa tocar um arquivo de outro agente, **parar** e escalonar (não invadir).

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
