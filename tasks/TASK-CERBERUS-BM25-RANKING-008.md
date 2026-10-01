# TASK-CERBERUS-BM25-RANKING-008

TASK: Preservar a relevância lexical na conversão de pontuações BM25 do SQLite.

CONTEXT: O usuário autorizou continuar as melhorias e a validação local do DM-Cerebro.
A conversão `max(0, raw_bm25)` eliminava as diferenças entre pontuações negativas do FTS5;
a ordenação final passava a depender da autoridade do documento.

SCOPE: Conversão de pontuação em `engine/index.py`, serialização dos scores em
`engine/models.py`, exibição numérica do score em `engine/server.py`, testes e documentação.

ACCEPTANCE: Regressão reproduz o defeito antes da correção; pontuações lexicais distinguem
correspondências melhores; autoridade continua ponderando resultados; buscas lexical e
híbrida mantêm a relevância em consultas curtas, sem depender da prioridade de termos raros.
Pacotes continuam respeitando os orçamentos existentes. O painel exibe valores pequenos
positivos sem transformá-los em zero pelo arredondamento.

BOUNDARIES: Preservar alterações anteriores, filtros de estado, isolamento de projetos e
prioridade de termos raros. Sem dependências novas, reescrita de documentos canônicos,
promoção automática de candidatos, commit, push ou deploy.

DONE WHEN: Testes focais passam e revisão independente confirma a correção.

Estado: implementação local concluída, com revisão independente PASS. A suíte focal
ampliada passou em 163 testes, sem falhas, erros ou skips, em 38,474 segundos. Os nove
testes novos cobrem ranking, autoridade, serialização e exibição do score. A auditoria
reproduziu as falhas antigas somente em memória, preservando arquivos e corpus.

MCP novo: 5.400/6.000 e 944/1.024 caracteres; orçamento fora da faixa rejeitado.
O aprendizado foi capturado como candidato `d49e627b2a11b8b6`, sem promoção canônica.

Ativação: esta conversa ainda respondeu com o formato antigo do MCP no início da rodada.
O disparo automático dos hooks na sessão real continua pendente de confirmação. Isso
permanece separado da correção local validada nesta tarefa.

Referência técnica: [BM25 no SQLite FTS5](https://www.sqlite.org/fts5.html#the_bm25_function).
O FTS5 inverte o sinal do BM25, retornando valores menores para correspondências melhores.
Os scores são relativos à consulta e ao corpus; não representam probabilidade de acerto.
