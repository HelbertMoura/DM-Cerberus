# Automação do DM-Cerebro no Codex

Data: 30/09/2026. Escopo: contexto e captura locais, com revisão humana do conhecimento canônico.

O fluxo segue os princípios de memória própria, Markdown como fonte e índice derivado descritos no
[artigo AI-MEMORY 2.0](https://akitaonrails.com/2026/09/02/ai-memory-2-0-melhor-sistema-memoria-agentes-e-times/).
O contrato dos eventos vem da [documentação oficial dos hooks](https://learn.chatgpt.com/docs/hooks).

## Diagnóstico confirmado

O parser anterior reconhecia envelopes de Claude, mas descartava mensagens públicas do Codex
gravadas como `response_item.payload`. Na inspeção inicial do transcript real da conversa,
havia sete mensagens públicas do assistente e o parser reconhecia zero.

O único evento registrado era `SessionEnd`. No Codex, sair de uma conversa não encerra a sessão
imediatamente. O evento pode ocorrer no fechamento normal, arquivamento ou após o período
documentado de inatividade com a conversa fechada. Por isso, ele é uma proteção final;
`Stop` permite capturar uma seção estruturada ao concluir uma resposta.

Os testes também reproduziram dois problemas de concorrência na inbox: arquivo temporário
compartilhado e substituição de um candidato já revisado após uma consulta concorrente.
A captura agora usa temporários únicos e publica candidatos novos sem substituir os existentes.
Atualizações administrativas continuam usando substituição atômica. Esta mudança protege a
criação concorrente; não implementa uma fila central de todas as mutações administrativas.

Uma captura feita pelo MCP real também revelou mojibake na entrada: Python usava `cp1252`
para ler JSON UTF-8 sem escapes no Windows. O MCP e os hooks agora configuram os streams
explicitamente para UTF-8. Os testes enviam bytes UTF-8 com acentos e forçam o padrão `cp1252`
no processo filho para reproduzir o problema. O processo MCP já aberto precisa reiniciar para
carregar essa correção; abrir uma sessão nova também permite carregar os novos handlers.

## Eventos instalados

| Evento | Ação | Timeout |
| --- | --- | --- |
| `SessionStart` | Entrega uma orientação curta e atualiza o índice local no início da janela. Resume preserva o histórico; compact/clear iniciam um novo período. | 10 s |
| `UserPromptSubmit` | Entrega a orientação se ainda ausente; mensagens seguintes retornam vazio, sem busca ou indexação. | 10 s |
| `Stop` | Prefere `last_assistant_message`, campo oficial; captura somente seções estruturadas. | 3 s |
| `PreCompact` | Tenta capturar seções estruturadas da cauda do transcript antes da compactação. | 3 s |
| `SessionEnd` | Última captura de seções estruturadas ao encerrar a sessão. | 3 s |

O contexto inicial tem teto de 600 caracteres e contém apenas a orientação para usar o MCP.
Não há injeção automática de memórias em mensagens seguintes. Leituras explícitas do MCP
usam até dois previews e 1.200 caracteres por padrão, com expansão explícita até 6.000.
A soma das entregas tem teto de 12.000 caracteres entre compactações ou limpeza da sessão.
Caracteres não medem tokens exatos do provedor. O prompt não é usado como consulta pelo hook
nem salvo nos registros de saúde. A atualização incremental segue a allowlist de raízes
do adaptador existente. Prompts não disparam um rescan completo.

O contexto apresenta memórias como referências históricas e lembra o agente de usar o MCP
para aprendizados reutilizáveis com proveniência. Ele não concede autorização para ações.
Decisões semânticas ainda dependem de registros úteis do agente: os hooks não deduzem uma lição
de qualquer conversa nem transformam chat bruto em conhecimento oficial.

## Orçamento e deduplicação

O estado local guarda contagem de caracteres e fingerprints SHA-256 das versões canônicas
entregues pelo MCP. A orientação do hook participa do mesmo orçamento, sem consumir itens.
Trocar a ordem dos resultados ou voltar a um projeto não repete memória; uma versão alterada
pode ser entregue como novidade. Itens que não cabem não entram no histórico. O lembrete
de captura aparece somente na primeira entrega do hook de cada período, mesmo se o MCP
tiver gasto parte do saldo antes. O token público de conversa também entra na cota do hook.

O orçamento é compartilhado pelos projetos dentro da mesma sessão. `SessionStart` com
`source: resume` ou `startup` não apaga a contagem existente. Somente `compact` ou `clear`
reinicia o período. Uma sessão com outro identificador possui seu próprio orçamento.
Depois de atingir o teto, hooks e leituras MCP com o mesmo `session_id` deixam de acrescentar
memória. O agente passa ao MCP o token público `cbr-…` apresentado pelo hook. Leituras sem
identidade continuam limitadas por chamada, mas não participam da deduplicação acumulada.
`cerberus_context_status` permite observar o saldo sem consumir memória. Todo texto visível
do hook e o JSON retornado nas leituras entram na cota; metadados de transporte ficam fora.

A gravação da contagem ocorre antes de devolver contexto. Um lock do sistema operacional
impede duas chamadas concorrentes de gastar o mesmo saldo; a chamada que encontrar o lock
ocupado deixa de entregar contexto. Falhas podem resultar em menos memória entregue, mas
não devem liberar orçamento adicional. Estado inválido ou identidade de sessão ausente também
impedem a entrega. Os locks são liberados pelo sistema ao terminar o processo.

Estado anterior com digest ou fingerprints de previews não permite cruzar versões canônicas. Essas sessões
aguardam compactação/clear para reabrir a entrega, ou podem continuar em uma sessão nova.
Não apague os arquivos de estado para limpar logs: isso remove a contagem e o histórico.
Arquivos de estado e registros crescem com o número de sessões, mas não contêm chat bruto.
A política de retenção em disco permanece uma melhoria futura.

Esse controle limita a contribuição dos hooks e leituras MCP com identidade do DM-Cerebro. Não controla a soma de prompts,
respostas, arquivos, ferramentas e outras integrações na janela de contexto do modelo.

## Instalação reproduzível

```powershell
Set-Location -LiteralPath 'C:\DevManiacs\DM-Cerebro'
& C:\Python314\python.exe -m engine.cli install-hooks --dry-run
& C:\Python314\python.exe -m engine.cli install-hooks
& C:\Python314\python.exe -m engine.cli doctor
```

`install-hooks` altera somente os handlers dessa instalação no `hooks.json` do Codex.
Preserva handlers de terceiros e campos extras, recusa JSON inválido e cria um backup novo antes
de mudar um arquivo existente. Uma segunda execução não duplica handlers. `--codex-home` seleciona
um diretório explícito; o CLI também respeita `CODEX_HOME` quando configurado.

O instalador não altera `config.toml` nem concede confiança. Novos handlers exigem revisão
no gerenciador de hooks do Codex (`/hooks` no CLI). Depois da revisão, abra uma sessão nova
ou retome a conversa para carregar a configuração. Confiança persistida e registro em JSON
não comprovam que um evento foi entregue.

## Saúde e comprovação

`doctor` mostra os cinco registros, a presença de decisões persistidas de confiança e os últimos
resultados em `.cerberus/hooks/`. Os registros guardam evento, agente, hash de identidade da sessão,
horário UTC, duração, quantidade capturada e tipo de erro. Não guardam prompts, transcripts,
conteúdo recuperado nem mensagens de exceção.

| Resultado | Interpretação |
| --- | --- |
| `CONTEXT_READY` | O handler preparou contexto; conferir `index_errors` quando houver refresh. |
| `UNCHANGED_CONTEXT` | Nenhum trecho novo foi entregue. |
| `BUDGET_EXHAUSTED` | O teto foi atingido ou nenhuma novidade coube no saldo restante. |
| `MISSING_SESSION_ID` | Não houve identidade de sessão para contabilizar a entrega. |
| `CAPTURED` | Novos candidatos entraram na inbox. |
| `NO_NEW_CANDIDATES` | Nenhuma nova seção elegível; também pode indicar deduplicação. |
| `NO_ASSISTANT_TEXT` | Mensagem/transcript ausente ou formato desconhecido. |
| `INDEX_MISSING` | Um prompt chegou antes de haver índice disponível. |
| `ERROR` | Falha interna; o tipo de erro aparece sem seu conteúdo. |

`delivery: manual_check` identifica uma verificação direta com `CERBERUS_HOOK_CHECK=1`.
`delivery: runtime` identifica a execução sem esse marcador. O arquivo sozinho não é prova
criptográfica de origem; confira o evento no Codex ao validar a integração.

Uma validação real requer: revisar os handlers, abrir uma sessão, enviar um prompt e concluir
uma resposta com aprendizado estruturado ou captura via MCP. Depois, conferir os registros de
`SessionStart`/`UserPromptSubmit`/`Stop` e o candidato com proveniência. Não há necessidade de
reiniciar o loop de resposta para capturar: o hook `Stop` responde JSON sem decisão de continuação.

Na validação de 30/09/2026, os 109 testes dos módulos afetados passaram. As chamadas diretas
prepararam 5.612 caracteres de contexto e produziram um único candidato após eventos repetidos.
O refresh registrou quatro exclusões pelo filtro de segredos já existente: `projects/biolar/deploy.md`,
`reports/REPORT-QA-RECHECK-FIX-004.md`, `skills/graphify/references/exports.md` e
`skills/security-and-hardening/SKILL.md`. O filtro pode reconhecer exemplos de documentação;
as exclusões não comprovam que os arquivos contenham credenciais reais. Nenhum desses conteúdos
foi alterado nesta tarefa. Os cinco handlers possuem registros persistidos de confiança, mas
a execução automática dos novos eventos ainda precisa ser observada em uma sessão nova.

## Fronteira canônica

As capturas criam `CANDIDATE` ou `QUARANTINED`. A deduplicação mantém o candidato já existente,
inclusive seu estado de revisão e proveniência. Texto de usuário, saída de ferramenta e raciocínio
privado não entram no parser. A leitura de transcript é limitada a 256 KiB e aos últimos 12 blocos
públicos do assistente; formatos desconhecidos geram captura vazia observável.

Promoção continua administrativa: `review <id> --verify`, preview de `promote` e aplicação
explícita com `promote <id> --apply`. Os hooks não escrevem `LEARNINGS.md` ou `DECISIONS.md`.
Para desativar um evento, use o gerenciador de hooks do Codex e desabilite seu handler DM-Cerebro.

## Conclusão deste escopo e acompanhamento

### Diagnóstico do lançamento no Windows — 30/09/2026

O motor nativo usa PowerShell neste ambiente. O comando que começava por um executável
entre aspas, sem operador de invocação, falhava antes de executar Python. Em fixture nativa,
o comando quoted não gravou o marcador; versões sem aspas ou com `&` receberam `SessionStart`.
O instalador agora preserva `command` e acrescenta `commandWindows` com `&` e paths em
aspas simples literais (apostrofes duplicados), evitando expansão de `$` e backticks.

Validação: cinco testes do instalador passaram, incluindo idempotência, backup,
preservação de handlers alheios e de config.toml/trust. O CLI nativo com endpoint de modelo
local simulado produziu receipts runtime: SessionStart CONTEXT_READY com 1.049 caracteres;
UserPromptSubmit UNCHANGED_CONTEXT com zero. O token de sessão chegou ao endpoint local.
A resposta de modelo foi rejeitada deliberadamente: nenhum modelo foi executado nesse teste.
Isso comprova o fluxo CLI isolado; a confirmação na conversa Desktop aguarda confiança.

Configuração global corrigida com backup. Consulta real hooks/list: cinco handlers
enabled e trustStatus modified, sem erros/warnings. O Codex exige revisão de definições
modificadas; revisar/confiar no gerenciador de hooks (na CLI, `/hooks`). O instalador
não altera trusted_hash nem contorna essa etapa. Não requer outro reinício por enquanto.

- Validar a entrega dos eventos após a revisão de confiança no Codex Desktop e CLI.
- Medir a relevância do contexto em tarefas reais e filtrar handovers que sejam apenas templates.
- Checkpoints curtos por projeto/tarefa estão disponíveis em `cerberus_save_task_state` e
  `cerberus_get_task_state`; salvar nos marcos e ao encerrar, antes de reler o histórico.
- Avaliar retenção de registros e concorrência de revisão/promoção antes de ampliar para um store compartilhado em rede.
