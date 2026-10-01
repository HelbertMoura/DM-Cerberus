# TASK-CERBERUS-CONTEXT-BUDGET-006

TASK: Limitar a contribuição dos hooks de memória ao contexto do Codex em conversas longas.

CONTEXT: A deduplicação anterior comparava apenas a última entrega. Trocar consultas ou projetos
podia repetir trechos; não havia orçamento acumulado entre compactações.

SCOPE: `engine/agent_hooks.py`, regressões em `tests/test_agent_hooks.py` e documentação operacional.

ACCEPTANCE: Até 6.000 caracteres na primeira entrega, 2.000 nas atualizações e 12.000 na soma
entre compactações/clear. Deduplicação por trecho e versão; retomada e troca de projeto preservam
o histórico. Escrita inválida, estado corrompido ou concorrência não podem liberar orçamento extra.

BOUNDARIES: Preservar mudanças preexistentes; sem dependências novas, alteração de confiança,
promoção automática de candidatos, commit, push ou deploy. Não prometer controle do contexto
total do modelo nem contabilização exata de tokens.

DONE WHEN: Implementação e regressões validadas, comparação de consumo registrada e limites documentados.

Estado: implementação local validada em 121 testes dos módulos afetados. Falta observar a entrega
automática dos hooks no Codex; chamadas diretas são identificadas como verificações manuais.

Referência operacional: [Automação do Codex](../docs/CERBERUS-CODEX-AUTOMATION.md).
