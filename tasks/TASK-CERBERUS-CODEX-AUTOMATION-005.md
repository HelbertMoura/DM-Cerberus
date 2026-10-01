# TASK-CERBERUS-CODEX-AUTOMATION-005

TASK: Automatizar a recuperação de contexto e a captura de aprendizados do DM-Cerebro no Codex.

CONTEXT: MCP disponível; parser antigo incompatível com `response_item.payload`; somente SessionEnd registrado.

SCOPE: `hooks/claude_session_capture.py`, `hooks/codex_context.py`, `engine/agent_hooks.py`,
`engine/installer.py`, comandos de instalação/doctor em `engine/cli.py`, criação concorrente
de candidatos em `engine/capture.py`, streams UTF-8 em `engine/mcp_server.py` e testes diretamente afetados.

ACCEPTANCE: Envelopes Codex e Claude reconhecidos; contexto limitado e isolado por projeto;
captura estruturada com deduplicação; candidatos revisados preservados em corrida;
diagnóstico sem conteúdo sensível; instalação idempotente preservando outras configurações.

BOUNDARIES: Captura automática cria somente candidatos; promoção humana. Preservar alterações
preexistentes. Não alterar confiança persistida dos hooks, fazer commit/push ou implantar em produção.

DONE WHEN: Código e regressões validados, configuração local instalada e limites da ativação documentados.

Estado: implementação local instalada e validada em 109 testes. Os cinco handlers possuem
registro persistido de confiança, mas isso não comprova confiança na definição atual nem
entrega dos eventos. Falta observar a execução automática em uma sessão nova do Codex.

Referência operacional: [Automação do Codex](../docs/CERBERUS-CODEX-AUTOMATION.md).
