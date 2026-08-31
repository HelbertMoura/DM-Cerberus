# Cerberus Security

Invariantes: nenhuma tool oferece shell, exec, read_file ou write_file genérico; MCP não promove; destinos canônicos são allowlisted para `LEARNINGS.md` e `DECISIONS.md`; IDs de candidato aceitam formato estrito; escrita usa arquivo temporário e replace atômico.

Filtros detectam/redigem private keys, Authorization Bearer/Basic, passwords, connection strings, JWTs, tokens comuns de providers (`gh*`, `sk-*`, AWS) e assignments de token/chave. Achados viram `QUARANTINED` e não podem ser verificados/promovidos. `.git`, `.cerberus`, `.env`/diretórios ocultos, nomes sensíveis (`secrets.md`, `credentials.md`, tokens/private keys) e ambientes virtuais ficam fora do walk do índice. Caminhos resolvidos devem permanecer contidos na raiz; symlinks/reparse escapes não são seguidos.

Risco residual: similaridade semântica, contradições e supersessão de ADR ainda exigem revisão humana; o mecanismo implementado garante dedupe exato e não faz merge silencioso.
