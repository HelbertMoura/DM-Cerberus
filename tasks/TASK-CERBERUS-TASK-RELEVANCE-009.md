# TASK-CERBERUS-TASK-RELEVANCE-009

TASK: Reduzir a seleção de memórias sem relação com a tarefa no pacote de contexto.

CONTEXT: O usuário autorizou continuar as melhorias e os testes. As consultas específicas
do pacote acrescentam palavras fixas à descrição da tarefa. Como a busca usa OR, documentos
podem entrar somente por conter esses termos acrescentados.

SCOPE: Três consultas em `engine/retrieval.py`, testes de relevância do pacote e documentação.

ACCEPTANCE: Decisões, arquitetura e aprendizados usam a descrição da tarefa sem palavras
fixas adicionais. Uma tarefa sem correspondência deixa esses grupos vazios. Correspondências
reais continuam retornando fontes; resultados globais pertinentes completam as vagas locais.
Prioridade do projeto, filtros de estado, isolamento e orçamentos permanecem válidos.

BOUNDARIES: Manter as consultas próprias de governança e handover. Preservar alterações
anteriores e documentos canônicos. Sem dependências, chamadas a modelos, promoção automática,
commit, push ou deploy.

DONE WHEN: Regressão reproduz o ruído antes da correção, testes focais passam e revisão
independente confirma o resultado.

Estado: implementação local concluída, revisão independente PASS. Foram alteradas três
consultas e acrescentados sete testes com Markdown e SQLite temporários. A regressão
ampliada passou em 170 testes, sem falhas ou erros, em 45,165 segundos.

Na fixture sem correspondência, os três grupos específicos passaram de 1/1/1 itens para
0/0/0; a resposta serializada caiu de 961 para 586 caracteres nos dois orçamentos testados.
Governança e handover permaneceram presentes. Essa medição é do caso controlado.

MCP em processo novo: 5.554/6.000 e 944/1.024 caracteres; argumento 1.501 rejeitado.
O aprendizado foi capturado como candidato `212821e3e1dec4f6`, sem promoção canônica.

Limites: a busca continua lexical com OR; termos genéricos presentes na própria tarefa
ainda podem gerar ruído. A descrição consultada continua limitada a 1.500 caracteres.
A conexão desta conversa ainda respondeu com o formato antigo do MCP, e os quatro
recibos encontrados eram manuais. A ativação nessa conexão e o disparo automático dos
hooks na sessão real permanecem pendentes de confirmação.
