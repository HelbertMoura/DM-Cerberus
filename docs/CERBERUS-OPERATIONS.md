# Cerberus Operations

Comandos principais: `status`, `doctor`, `search`, `context-pack`, `capture`, `ingest-report`, `inbox`, `review`, `promote`, `reject`, `index`, `index --rebuild` e `mcp`.

Fluxo de promoção:

1. Capture/ingira com task e agente.
2. Inspecione com `cerberus review <id>`.
3. Verifique com `cerberus review <id> --verify`.
4. Veja o diff com `cerberus promote <id>`.
5. Aplique somente após gate humano: `cerberus promote <id> --apply`.

Os launchers CMD/PowerShell fazem `pushd` para a raiz e usam o interpretador absoluto verificado, sem depender de `PYTHONPATH`. `doctor` informa Python, FTS5, UTF-8, raiz, índice, inbox e permissão, sem imprimir segredos.
