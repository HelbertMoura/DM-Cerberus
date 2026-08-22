# 📚 LEARNINGS.md — Caderno de Lições Aprendidas
> **Propriedade:** Dev Maniac's Systems (Helbert Moura)
> **Versão:** 1.0 · 22 de Agosto de 2026
> **Formato:** Append-only (nunca apagar, só adicionar)
> **Vincular com:** DECISIONS.md (decisões) · AGENTS.md (procedimento)

---

## 🎯 Como Usar Este Arquivo

Toda vez que você (humano ou IA) aprender algo **reutilizável** em outros projetos:

1. **Erro de produção** → registrar aqui + causa raiz + fix
2. **Gotcha de biblioteca** → registrar aqui + workaround
3. **Decisão contraintuitiva** → aqui como "aprendizado" + ADR no DECISIONS.md
4. **Padrão que funcionou** → registrar aqui pra replicar

**Regra:** Se não for útil em outro contexto, não entra aqui. Vai pro commit message.

---

## 📖 Lições Registradas

### [LEARN-001] PostgreSQL `select_for_update` em Esteira Multi-Step
> **Data:** 22/08/2026 · **Contexto:** CanteiroHUB · **Agente:** Z.AI Hermes · **ADR:** ADR-002

- **Problema:** Race condition ao converter Orçamento → Contrato → Obra simultaneamente.
- **Causa raiz:** Falta de lock pessimista no `select_for_update` durante transação.
- **Solução:** Usar `transaction.atomic()` + `select_for_update(nowait=False)` em todos os models da esteira.
- **Aplicar em:** Qualquer esteira que envolva transição de estado sequencial.

---

### [LEARN-002] Frontmatter YAML em Todo `.md`
> **Data:** 22/08/2026 · **Contexto:** DM-Cerebro · **Agente:** Gemini · **ADR:** —

- **Problema:** Busca manual por tags/conteúdo era ineficiente.
- **Solução:** Padronizar frontmatter YAML com `titulo`, `tags`, `atualizado`, `status`.
- **Ferramenta:** Editor com suporte a YAML frontmatter (VS Code, Obsidian).
- **Aplicar em:** Todo novo arquivo `.md` no DM-Cerebro.

---

### [LEARN-003] Cloudflare Tunnel Sem Porta 22 Outbound
> **Data:** 22/08/2026 · **Contexto:** Infra Servidor · **Agente:** Helbert · **ADR:** —

- **Problema:** Rede Helbert bloqueia porta 22 outbound → `ssh root@192.168.226.103` falha direto.
- **Workaround:** Usar `cloudflared access tcp :2222 --hostname ssh.devmaniacs.com.br`.
- **Aplicar em:** Qualquer nova VM Dev Maniac's que precise de acesso externo.

---

### [LEARN-004] Largest-Remainder em Normalização de EAP
> **Data:** 22/08/2026 · **Contexto:** CanteiroHUB · **Agente:** MiniMax M3 · **ADR:** ADR-002

- **Problema:** Soma de percentuais da EAP não fechava em 100.00% (ex: 99.97%).
- **Causa raiz:** Arredondamento por linha sem método sistemático.
- **Solução:** Algoritmo Largest-Remainder (Hare) — distribuir resíduo nos maiores restos.
- **Implementação:** Normalizar para 4 casas decimais, distribuir diferença entre maiores restos.
- **Aplicar em:** Qualquer agregação que exige soma exata (BDI, percentuais, rateios).

---

### [LEARN-005] Hash Routing para SPA Sem Framework
> **Data:** 22/08/2026 · **Contexto:** CanteiroHUB Front · **Agente:** Gemini · **ADR:** ADR-003

- **Problema:** F5 em rota específica voltava pro dashboard, perdia estado.
- **Solução:** Usar `window.location.hash` + listeners `hashchange`/`popstate`.
- **Aplicar em:** Qualquer SPA que precise de URL persistível sem React Router/Vue Router.

---

## 🔄 Template Para Novas Entradas

```markdown
### [LEARN-NNN] Título Curto e Descritivo
> **Data:** AAAA-MM-DD · **Contexto:** <produto> · **Agente:** <humano|ia> · **ADR:** [ADR-NNN](link) ou —

- **Problema:** Sintoma observado.
- **Causa raiz:** Por que aconteceu.
- **Solução:** O que foi feito.
- **Aplicar em:** Onde mais usar.
```

---

**Última atualização:** 22 de Agosto de 2026 · **Total de lições:** 5
