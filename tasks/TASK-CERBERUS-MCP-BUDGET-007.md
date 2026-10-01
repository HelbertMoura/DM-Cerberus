# TASK-CERBERUS-MCP-BUDGET-007

TASK: Aplicar orçamento ao pacote do MCP e filtrar memória vigente nas buscas normais.

CONTEXT: `max_tokens` só estimava consumo; consultas lexicais e semânticas não excluíam
memórias substituídas ou depreciadas. Aprovação do usuário após a recomendação das duas melhorias.

SCOPE: `engine/context_budget.py`, `engine/retrieval.py`, `engine/models.py`,
`engine/index.py`, `engine/search.py`, `engine/mcp_server.py`,
`tests/test_context_budget.py` e documentação.

ACCEPTANCE: Pacote serializado com teto padrão de 6.000 caracteres; orçamento estimado explícito;
fontes mantidas em itens selecionados; buscas operacionais restritas a registros ativos;
prioridade ao projeto nas seções do pacote; argumentos MCP limitados por intervalo.

BOUNDARIES: Preservar alterações anteriores e histórico canônico. Sem dependências novas,
alteração de confiança, promoção automática, commit, push ou deploy. Não atribuir os testes
da etapa anterior à implementação atual nem prometer contagem exata de tokens.

Estado: implementação local validada após aprovação do usuário. Passaram 156 testes dos
módulos afetados, incluindo 12 novos testes de orçamento e memória vigente. Um processo
novo do MCP devolveu 5.400/6.000 e 944/1.024 caracteres nos dois orçamentos verificados e
rejeitou 1.501. O índice mantém os 49 registros inativos encontrados.

Ativação: o Codex reconhece os cinco hooks habilitados e confiáveis. Aceitou a solicitação
de atualização dos MCPs, mas a conexão desta rodada ainda respondeu com o formato antigo.
Verificar o MCP atualizado e o disparo automático dos hooks após reabrir a conversa ou
reiniciar o Codex. A configuração reconhecida não comprova execução automática.

Referência: [Pacote do MCP](../docs/CERBERUS-MCP-CONTEXT-BUDGET.md).
