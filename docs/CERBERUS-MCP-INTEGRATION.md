# Cerberus MCP Integration

O servidor usa JSON-RPC 2.0 por stdio, uma mensagem JSON por linha. `stdout` é reservado a respostas; diagnóstico deve ir para `stderr`.

As tools de leitura incluem busca, context pack, decisões, learnings, contexto de projeto e stats. `cerberus_capture_learning` e `cerberus_ingest_report` criam exclusivamente candidatos e exigem proveniência. Não existe tool MCP de promoção nem de rebuild: promoção e manutenção são operações locais administrativas.

Clientes MCP devem iniciar `python -m engine.cli mcp` com `cwd` no DM-Cerebro. `CERBERUS_ROOT` permite isolamento em testes/instâncias explícitas.
