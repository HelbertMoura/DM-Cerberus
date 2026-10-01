# Pacote do MCP e memória vigente

Implementação local em 30/09/2026.

## Início econômico

O hook entrega somente uma orientação de até 600 caracteres por janela de contexto,
sem recuperar trechos históricos. Mensagens seguintes e retomadas da mesma conversa
não entregam contexto adicional. Compactação/limpeza real permite uma nova orientação.
SessionStart atualiza o índice local; UserPromptSubmit não busca nem indexa memórias.
Busca, expansão e retomada de checkpoints continuam disponíveis sob demanda no MCP.
Gravar memória local não a injeta automaticamente no contexto do modelo.
O teto acumulado de 12.000 caracteres permanece como proteção para leituras explícitas;
não é uma meta de consumo. Texto já entregue antes do ajuste continua na conversa.


## Orçamento do pacote

`cerberus_get_context_pack` aceita `max_tokens` entre 256 e 1.500, com padrão 1.500.
Esse parâmetro representa um orçamento estimado de quatro caracteres por unidade.
O gerador usa de 1.024 a 6.000 caracteres. A leitura MCP acrescenta o teto `max_chars`
(padrão 1.200); o menor teto prevalece, inclusive se o saldo da conversa for menor.
A contagem inclui
Markdown, fontes, cabeçalhos, escapes JSON e os campos de diagnóstico devolvidos pela ferramenta.
Não se trata de contagem exata de tokens do modelo.

O resultado mantém `markdown` e `token_estimate` e acrescenta `budget_chars` e `truncated`.
O gerador seleciona itens completos que cabem no saldo; não corta uma resposta JSON no meio.
Ele limita o resumo da tarefa, os títulos e os trechos e preserva referências que caibam.
O corte altera somente o pacote devolvido, sem reescrever documentos ou candidatos.

O orçamento também se aplica ao pacote criado pelo CLI e pelo adaptador de orquestração.
As demais leituras MCP usam previews de até dois resultados por padrão, com `max_chars`
padrão de 1.200 e expansão entre 512 e 6.000 caracteres. Os formatos de lista ou dicionário
existentes são preservados. Registros que não cabem são omitidos; JSON nunca é cortado no meio.
`cerberus_get_memory` expande somente memória ativa já indexada, por ID e página. A redação
de segredos ocorre antes da paginação. IDs e fontes continuam disponíveis para a expansão.

Com `session_id`, hooks e leituras MCP compartilham 12.000 caracteres por conversa entre
compactações/limpezas. Use o token público `cbr-…` entregue pelo hook, ou uma identidade
estável e exclusiva da conversa. Nunca use o projeto ou a tarefa como identidade da conversa.
Sem `session_id`, cada leitura MCP conserva seu teto, mas não deduplica nem participa da cota
acumulada. Respostas sem novidade ou saldo retornam `content: []`. A expansão explícita
usa hashes de página; repetir a mesma página não gasta novamente a cota.

`cerberus_context_status` mostra o saldo. Seu `reset_reason` aceita `compact` ou `clear`
somente depois de uma compactação/limpeza real. Retomar ou reiniciar a mesma conversa não
renova o saldo. Controles administrativos e metadados de transporte ficam fora da cota;
todo o texto JSON das leituras e todo `additionalContext` dos hooks entram na conta.
Estado legado sem identidade canônica das versões bloqueia novas entregas até compact/clear.
Falhas de persistência também bloqueiam a entrega, sem zerar silenciosamente a contagem.

## Retomada curta

`cerberus_save_task_state` grava objetivo, decisões, arquivos, validação, próximo passo e
status por projeto/tarefa em `.cerberus/task_state/`. `cerberus_get_task_state` retoma esse
checkpoint com versão e hash. O estado tem teto de 6.000 caracteres, campos limitados,
redação de segredos e escrita atômica. Não contém transcrição nem promove conhecimento.
Salve nos marcos de trabalho e ao encerrar; consulte antes de reler o histórico inteiro.

Esses tetos limitam a contribuição do DM-Cerebro. Prompts, outras ferramentas, instruções e
respostas do agente continuam usando contexto; caracteres não equivalem a tokens exatos.

## Recuperação de informação

O escopo de uso enxuto foi fechado com revisão independente PASS em 30/09/2026.
A regressão combinada passou com 215 testes e dois skips de symlink; as correções finais
de redação foram revalidadas em suítes focais. O MCP completo passou com 20 testes e
14 subtestes após o último ajuste. Em processo novo no índice real, os pacotes usaram
1.729 e 800 caracteres, e o checkpoint salvo/lido usou 1.818. A ativação dos novos
handlers no Codex em uso continua pendente; ver TASK-CERBERUS-LEAN-WORKFLOW-010.

As consultas lexicais usam somente registros com estado `ativo`. Isso exclui `superseded`,
`deprecated`, `draft` e `proposta`. O estado precisa estar representado no índice pelos valores
suportados pelo parser; valores desconhecidos ainda seguem a interpretação legada do parser.

A busca semântica sincroniza os vetores apenas de registros ativos e verifica o estado antes
de devolver um resultado. A busca híbrida herda os dois filtros. Os documentos e o histórico
continuam no Markdown e no índice; apenas os vetores derivados de itens inativos saem da busca.

No pacote, decisões, arquitetura, aprendizados e handovers do projeto têm prioridade dentro de
cada grupo. Referências globais completam as vagas restantes. A governança global continua
com seu grupo próprio. A priorização não mede relevância em tarefas reais nem identifica
contradições entre documentos ativos; essas avaliações permanecem pendentes.

As consultas de decisões, arquitetura e aprendizados usam a descrição da tarefa sem termos
fixos acrescentados. O filtro de tipo seleciona as classes de memória. Sem correspondência
lexical com a tarefa, esses grupos ficam vazios; uma tarefa vazia também deixa esses grupos
vazios. A governança e o handover mantêm consultas próprias para fornecer contexto geral.
Isso elimina correspondências causadas pelos termos artificiais, mas palavras comuns na
própria descrição ainda podem retornar documentos pouco pertinentes.

## Ativação e validação

Após aprovação do usuário para verificar a implementação, passaram 156 testes dos módulos
afetados, incluindo 12 testes novos em `tests/test_context_budget.py`. Eles cobrem o teto do
JSON serializado, escapes, fontes, deduplicação, redação de segredos, faixas de argumentos,
prioridade local e exclusão de memórias inativas nos três modos de busca. A regressão também
cobre hooks, captura, protocolo MCP, candidatos e instalação. A suíte emitiu um
`ResourceWarning` sobre limpeza de `HTTPError 400`; terminou com sucesso em 37,906 segundos.

Um processo novo do MCP foi validado pelo protocolo real, usando o repositório local:

| Orçamento nominal | Teto em caracteres | Resposta serializada | Corte |
| --- | ---: | ---: | --- |
| 1.500 | 6.000 | 5.400 | Não |
| 256 | 1.024 | 944 | Sim |

O argumento 1.501 foi rejeitado. O índice consultado preservou 1.656 registros ativos,
22 rascunhos e 27 registros substituídos; esses 49 registros inativos continuam no histórico.

O servidor nativo do Codex 0.159.2 reconheceu os cinco hooks do DM-Cerebro como habilitados
e confiáveis, sem erros ou avisos de descoberta, tanto no projeto quanto nesta conversa.
Isso comprova configuração reconhecida, mas não o disparo automático: os recibos encontrados
eram de verificações manuais e o transcript atual não continha eventos de hooks.

O Codex aceitou `config/mcpServer/reload`, que enfileira atualização dos MCPs das conversas
carregadas, conforme a [documentação do app-server](https://learn.chatgpt.com/docs/app-server).
Uma chamada posterior nesta mesma rodada ainda devolveu o formato antigo, sem `budget_chars`
ou `truncated`. Portanto, a ativação nesta conversa permanece pendente. Reabrir a conversa
ou reiniciar o Codex e enviar uma mensagem permite verificar o novo esquema e observar os
recibos automáticos. Nenhum arquivo de confiança foi alterado nesta validação.
