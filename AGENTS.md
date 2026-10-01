---
titulo: AGENTS.md — Ponto de Entrada Universal para Agentes
tags: [agents, entry-point, global, contrato, universal]
atualizado: 2026-08-26
status: ativo
---

# 🤖 AGENTS.md — Universal Agent Entry Point (Cerberus)

> **Projeto:** DM-Cerberus / Cerebro Engine
> **Mantenedor & Autoria:** Dev Maniac's Systems (Helbert Moura)
> **Padrão de Governança AI:** Minimal Persistent Context, Taxonomia Canônica e MCP Standard.

---

## 🎯 1. Princípio de Contexto Mínimo Persistente (Minimal Persistent Context)

Modelos modernos não precisam ler a empresa inteira antes de consertar um botão. Carregue permanentemente **apenas as regras universais**:

1. **Invariantes Arquiteturais:** Multi-tenant estrito (`TenantAwareModel`), i18n 100% (PT/EN/ES sem strings hardcoded), UI Industrial Solid-State (sem emojis em botões/tabelas).
2. **Boundaries Inegociáveis:** Proibido commit, push, deploy ou tocar produção sem aprovação humana do PO; proibido versionar credenciais/segredos; proibido mover ou deletar arquivos destrutivamente sem autorização.
3. **Escada Ponytail (Diff Mínimo):** `Deletar (YAGNI)` ➔ `Reaproveitar` ➔ `Nativo/Stdlib` ➔ `Dependência instalada` ➔ `1 linha antes de 50`.
4. **Taxonomia Canônica (`global/taxonomy.md`):** Respeitar a separação entre `KNOWLEDGE`, `SKILL`, `TASK`, `MEMORY`, `TOOL`, `LIBRARY`, `UI PATTERN`, `REFERENCE` e `MODEL`.

---

## 📋 2. O Task Contract (Padrão de Delegação Maestro ➔ Executor)

### Fluxo enxuto do Cerberus

- O hook entrega apenas uma orientação curta; busque memória quando a tarefa exigir. Nas leituras MCP, passe o mesmo `session_id`
  da conversa, preferindo o token `cbr-...` informado pelo hook. Sem token, escolha um ID
  único para esta conversa e preserve-o; projeto e tarefa não identificam uma conversa.
- Comece com até dois previews, com teto padrão de 1.200 caracteres. Expanda apenas fontes pertinentes com `cerberus_get_memory`;
  leia páginas pequenas e respeite o saldo da conversa. Reinicie a cota somente depois de
  compactação ou limpeza efetiva, nunca para contornar o limite durante a mesma janela.
- Salve `cerberus_save_task_state` em marcos e antes de encerrar a tarefa: objetivo,
  decisões, arquivos, validação e próximo passo. Na retomada, leia `cerberus_get_task_state`
  antes de buscar histórico. Registre incertezas e resultados reais; mantenha logs fora do resumo.
- Procure arquivos com `rg` e leia os trechos necessários. Use testes focais com saída
  concisa; amplie a regressão conforme o risco. Delegue contexto e ownership específicos,
  sem copiar a conversa inteira. Relate resultado, evidência e pendência de forma curta.

Toda tarefa delegada pelo Maestro utiliza o contrato conciso:

```markdown
TASK: <resultado desejado claro e direto>
CONTEXT: <apenas contexto não óbvio indispensável>
SCOPE: <arquivos e módulos específicos>
ACCEPTANCE: <critérios verificáveis de sucesso>
BOUNDARIES: <restrições críticas / o que não pode ser alterado>
DONE WHEN: <condição objetiva de parada>
```

> **Autonomia do Executor:** O executor decide **COMO** executar. O Maestro não escreve receitas de 100 passos microgerenciando o código.

---

## 🔄 3. Ciclo Autônomo de Execução

Para qualquer tarefa dentro do escopo autorizado pelo Task Contract, o executor tem autonomia total para seguir o ciclo contínuo:

```text
EXPLORE ➔ IMPLEMENT ➔ VALIDATE ➔ FIX ➔ REVALIDATE ➔ DONE
```

* **Não pare após a primeira implementação:** inspecione o resultado, rode a validação proporcional e corrija eventuais falhas autonomamente até atingir os critérios de aceite (`DONE WHEN`).
* **Não peça aprovação intermediária** para passos previstos no escopo da sandbox local.
* **Pare SOMENTE diante de:**
  - Decisão genuína de produto não especificada;
  - Ação destrutiva não autorizada (exclusão de dados, wipe);
  - Gate de autorização obrigatório (commit, push, deploy);
  - Credencial ou variável indispensável ausente;
  - Bloqueio real intransponível.

---

## 🧪 4. Validação Proporcional ao Risco

Elimine a sobrecarga de "rodar todos os testes sempre". A validação deve ser calibrada pelo impacto real da mudança:

| Tipo de Mudança | Validação Mínima Exigida |
| :--- | :--- |
| **Typo / Documentação / Ajuste de 1 linha** | Validação sintática local (`git diff`, checagem visual ou linter focal). |
| **Componente de UI / Micro-tarefa** | Testes do componente ou módulo alterado + verificação visual pontual. |
| **Feature / Serviço / Backend Endpoint** | Testes unitários do recurso + testes de integração diretamente afetados. |
| **Mudança Estrutural / Banco / Model** | Migrations em sandbox + suíte de regressão do módulo + validação de integridade. |
| **Segurança / Autenticação / Multi-tenant** | Testes de isolamento de tenant + gates de segurança do Cerberus. |
| **Release / Deploy de Produção** | Suíte completa de testes + smoke checks + Gate formal do PO. |

---

## 📚 5. Carregamento Progressivo de Conhecimento (Lazy Loading)

Consulte documentação especializada **apenas quando a tarefa exigir**:
- Tarefa de Frontend/Design: consulte [`global/frontend-design.md`](./global/frontend-design.md), `DESIGN.md` do projeto e [`ui-patterns/`](./ui-patterns/).
- Tarefa de Skills/Workflows: consulte [`global/skills-catalog.md`](./global/skills-catalog.md) e a pasta da respectiva skill.
- Tarefa de Banco/SEFAZ/Multi-tenant: consulte a documentação do módulo em `projects/<slug>/`.

---

## 🔁 6. Compatibilidade com versões anteriores (legacy)

Os arquivos legados na raiz continuam vivos para evitar quebra de paths referenciados por automação, prompts e outros agentes:

- `BRAIN.md` — age historicamente como índice; **redireciona para `INDEX.md`** (ver topo do `BRAIN.md`).
- `HANDOVER.md` — log append-only; continua sendo o log operacional global.
- `LEARNINGS.md` — caderno global de lições; pode coexistir com `projects/<proj>/learnings.md` (escopo local).
- `ROADMAP.md` — visão macro multi-produto; coexistirá com `projects/<proj>/roadmap.md` (escopo local).
- `MEMORY.md` — memória executiva global.
- `DECISIONS.md` — ADRs globais (decisões que valem para todos os projetos).

> A migração completa para a nova arquitetura target (`global/` + `projects/<slug>/` com arquivos dedicados) é **proposta**, não executada automaticamente. Ver `proposed-migration.md` para o plano aguardando aprovação do PO.

---

## 📐 7. Multi-Modelo (CLAUDE.md, QWEN.md e compatibilidade)

`AGENTS.md` é o canônico. Arquivos de entry-point específicos de modelo (`CLAUDE.md`, `QWEN.md`, `GEMINI.md`, `M3.md`, etc.) **devem** ser finos, apenas importando o canônico:

```markdown
# Claude Agent Entry Point (compat)

@AGENTS.md
@INDEX.md

A governança canônica vive nos arquivos acima. Não duplique política aqui.
```

O mesmo princípio vale para qualquer modelo futuro. Sem exceção.

---

## 🌐 8. Onde está cada coisa (referência rápida)

| Necessidade | Onde olhar |
| :--- | :--- |
| Mapa do cérebro | [`INDEX.md`](./INDEX.md) |
| Governança AI / model routing | [`global/ai-governance.md`](./global/ai-governance.md) + [`global/model-routing.md`](./global/model-routing.md) |
| Governança QA | [`global/qa-policy.md`](./global/qa-policy.md) |
| Governança de deploy | [`global/deploy-governance.md`](./global/deploy-governance.md) |
| Baseline de segurança | [`global/security-baseline.md`](./global/security-baseline.md) |
| Regra de paralelismo | [`global/parallel-agents.md`](./global/parallel-agents.md) |
| Política de documentação | [`global/documentation-policy.md`](./global/documentation-policy.md) |
| Arquitetura RAG & MCP (Langflow) | [`global/langflow-rag-mcp-guide.md`](./global/langflow-rag-mcp-guide.md) |
| Catálogo de APIs Públicas Gratuitas | [`global/public-apis-catalog.md`](./global/public-apis-catalog.md) |
| Memória executiva global | [`MEMORY.md`](./MEMORY.md) |
| Decisões globais (ADRs) | [`DECISIONS.md`](./DECISIONS.md) |
| Lições globais | [`LEARNINGS.md`](./LEARNINGS.md) |
| Roadmap macro | [`ROADMAP.md`](./ROADMAP.md) |
| Handover log global | [`HANDOVER.md`](./HANDOVER.md) |
| Mapeamento de projetos | [`projects/`](./projects/) |
| Conhecimento técnico destilado | [`wiki/`](./wiki/) (legado — manter) |
| Prompts copy-paste | [`prompts/`](./prompts/) (legado — manter) |
| Gaveta de ingestão | [`raw/`](./raw/) |

---

**Última atualização:** 26 de Agosto de 2026 · **Versão do schema:** Second Brain multi-projeto v1 · **Owner:** Helbert Moura — Dev Maniac's Systems
