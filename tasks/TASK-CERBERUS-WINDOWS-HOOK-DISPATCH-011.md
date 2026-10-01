# TASK-CERBERUS-WINDOWS-HOOK-DISPATCH-011

TASK: Diagnosticar a ausência de receipts automáticos após reinício e corrigir o lançamento.
BOUNDARIES: Sem modelos/API de produção no smoke, sem trust automático, commit, push ou deploy.
Estado: causa identificada, correção instalada/testada; aguarda revisão humana de confiança.

## Resultado

- Executável quoted sem `&` falha no PowerShell. Fixture do motor nativo recebeu SessionStart
  com versões bare e `&`, sem marcador na versão quoted original.
- engine/installer.py agora acrescenta commandWindows com `&` e paths em aspas simples literais.
- tests/test_installer.py: RED pela ausência de commandWindows; GREEN cinco testes.
- Scripts reais no CLI nativo, raiz temporária e endpoint de modelo local rejeitando requests:
  SessionStart runtime CONTEXT_READY 1049chars; UserPromptSubmit runtime UNCHANGED_CONTEXT0.
  Token cbr chegou ao endpoint; nenhum modelo foi executado. Exit1 deliberado pelo endpoint.
- Global hooks.json instalado com backup hooks.json.bak-cerberus-hooks-1790796808802138200.bak.
  config.toml/trusted_hash preservado byte a byte. Nenhuma definição alheia alterada.
- hooks/list real: cinco enabled, modified, sem erros/warnings. Aprovação humana em Hooks
  necessária antes de confirmar a execução Desktop. Na CLI: /hooks.

Próximo passo: revisar/confiar nos cinco handlers e enviar um prompt para observar receipt
Desktop real. Teste CLI isolado não equivale à confirmação automática nesta conversa.
