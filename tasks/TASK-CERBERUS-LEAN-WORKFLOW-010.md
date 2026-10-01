# TASK-CERBERUS-LEAN-WORKFLOW-010

TASK: Fechar as quatro melhorias de uso aprovadas pelo usuário: respostas MCP enxutas,
deduplicação por conversa entre hooks e MCP, retomada curta e execução proporcional.

BOUNDARIES: Preservar alterações existentes. Sem dependências, serviços, chamadas extras
a modelos, promoção automática, commit, push ou deploy. Capturas continuam candidatas.
Não confundir testes locais com ativação confirmada no Codex em execução.

## Contrato de implementação

1. Leituras MCP: preservar formatos de listas/dicionários existentes; previews com até
três resultados por padrão e teto de 2.400 caracteres de texto JSON. Expansão explícita
com limite até 6.000, usando o conteúdo já indexado, sem abrir paths recebidos do cliente.
Manter IDs/fontes íntegros; retirar registros que não caibam e sinalizar cortes.
2. Conversa: `session_id` opcional nas leituras. Sem ID, leitura limitada por chamada;
com ID, hooks e MCP compartilham estado, lock, fingerprints e 12.000 caracteres por ciclo.
Não usar projeto ou tarefa como identidade da conversa. Token público `cbr-<24 hex>` aponta
ao mesmo estado do ID nativo, sem expor o ID bruto. Reset só em compactação/limpeza explícita.
Metadados de transporte e mensagens administrativas não são orçamento do conteúdo de memória.
3. Retomada: estado operacional sob `.cerberus/task_state/`, por projeto/tarefa. Campos curtos:
objetivo, decisões, arquivos, validação, próximo passo e status. Redação de segredos, escrita
atômica, isolamento, sem transcrição ou reescrita de Markdown canônico. Ferramentas salvar/ler.
4. Execução: regra curta no AGENTS e fluxo dos hooks: leituras pontuais, logs concisos,
delegação com contexto necessário, testes proporcionais, salvar retomada ao encerrar tarefa.

## Interfaces internas para trabalho sem sobreposição

`engine/session_delivery.py` (lane sessão):

- `session_token(session_id: str) -> str`; raw ID e seu token público resolvem o mesmo arquivo.
- `memory_fingerprint(item) -> str`: hash da versão canônica, sem texto persistido.
- `delivery_transaction(root, session_id, reset=False)`: context manager com lock; transação
  expõe `seen` (set), `remaining` (int), `hook_initialized` (bool) e
  `commit(chars, keys, hook_initialized=False)`. Persistir antes de liberar resposta.
- `context_status(root, session_id, reset=False) -> dict`: diagnóstico pequeno.
- Guardar fingerprint na cópia do item em `fit_context_pack`, antes de cortar preview;
  hooks e MCP devem reconhecer a mesma versão apesar de previews de tamanhos diferentes.
- Estado legado/inválido nunca zera silenciosamente a cota; falhas bloqueiam entrega.

`engine/task_state.py` (lane retomada): `TaskStateStore(root).save(project_id, task_id,
objective, decisions=[], files=[], validation=[], next_step='', status='in_progress')`
e `.get(project_id, task_id) -> dict`. Validar tipos, limitar campos, proteger paths,
salvar atomicamente. IDs obrigatórios; estados `in_progress`, `paused`, `done`.

`engine/response_budget.py` + `engine/mcp_server.py` (lane MCP): integração após os módulos
de sessão/retomada estarem disponíveis. Listas existentes continuam listas; não devolver
JSON quebrado. Previews deduplicam versões; detalhe explícito usa fingerprint de página.
Quando cota/novidades acabam, resposta de tool com `content: []`, sem reenviar pacote completo.
Ferramentas novas: `cerberus_get_memory`, `cerberus_save_task_state`, `cerberus_get_task_state`,
`cerberus_context_status` (reset_reason opcional compact/clear). Leituras de memória aceitam
session_id e max_chars; context pack mantém max_tokens e seu teto de 6.000.

## Aceite

Testes reais de protocolo/JSON, entradas enormes e escapes; previews progressivos; fontes
e segredos; hooks→MCP e MCP→hooks; mudança de versão; isolamento; concorrência; falha de
persistência; cotas e compactação; retomada sem chat bruto. Revisão independente PASS e
verificação em processo novo do MCP. Reportar limitações e ativação nativa ainda pendente.

Estado: implementação local concluída; revisão independente PASS. Ativação nativa pendente.

## Evidência de fechamento — 30/09/2026

- Regressão combinada: 215 passed, 2 skipped, 163 subtests (antes das correções finais do redactor).
- Após corrigir aspas escapadas/incompletas: focal cinco módulos 81 passed, 2 skipped,
  113 subtests. Último ajuste de continuação de linha: MCP completo 20 passed, 14 subtests;
  reprodução independente adicional 1 passed, 2 subtests. Não somar rodadas sobrepostas.
- Dois processos MCP concorrentes: uma entrega de 1.500 caracteres, ledger final 12.000.
- Processo CLI novo com entrada UTF-8 sob cp1252: pacote padrão 1.729 caracteres,
  pacote max_tokens256 com 800; busca 1.606; stats 513, repetição sem conteúdo,
  ledger exato 513 e caps inválidos rejeitados.
- Checkpoint real salvo/lido via MCP: versão1, hash consistente, resposta 1.818 caracteres,
  sem truncamento. Lição candidata fc72b83f60c18f0a; sem promoção automática.
- Dois skips exigem privilégio Windows para symlinks; junctions e hardlinks foram cobertos.
- Registros reais dos hooks: quatro manual_check, nenhum dispatch automático observado.
  Reiniciar/reabrir Codex e conferir nova execução permanece pendente.

Sem commit, push ou deploy. Alterações preexistentes preservadas.
