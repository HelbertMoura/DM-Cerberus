# Cerberus Client Support

- Tier A: clientes MCP compatíveis podem usar o servidor stdio.
- Tier B: qualquer ambiente capaz de executar comando local pode usar o CLI.
- Tier C: hooks/eventos podem chamar `context-pack` e `ingest-report`.

Arquivos de configuração foram detectados para Codex, Claude, Cursor, OpenCode e Gemini; Maestri também está presente. Existência não equivale a schema validado. O installer atual possui adapters explícitos para Codex, Claude e Cursor. OpenCode, Gemini/Antigravity e Maestri permanecem `NEEDS_ADAPTER`; nenhuma configuração foi inventada ou gravada nesta TASK.
