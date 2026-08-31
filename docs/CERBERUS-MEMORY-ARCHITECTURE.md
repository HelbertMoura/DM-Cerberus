# 🧠 Cerberus Memory Intelligence — Arquitetura de Memória Multi-Agente
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)  
> **Versão:** 1.0.0 (Fase P1 Concluída) · 30 de Agosto de 2026  
> **Status:** Ativo e Operacional  

---

## 🏛️ 1. Visão Geral & Filosofia

O **Cerberus Memory Engine** é a camada inteligente de indexação, busca lexical/semântica e geração de **Context Packs** orquestrados para todos os agentes de IA do ecossistema Dev Maniac's (Gemini Maestro, Codex, MiniMax M3, OpenCode, Claude Code).

Inspirado nas lições práticas do projeto `ai-memory` (Fabio Akita) e no conceito *LLM Wiki* (Andrej Karpathy), o Cerberus segue princípios inegociáveis de engenharia:

1. **Source of Truth em Plain Markdown:** A verdade canônica reside exclusivamente nos arquivos `.md` versionados no Git (`C:\DevManiacs\DM-Cerebro` e `$ProjectDir/docs/brain`).
2. **Índice Derivado e 100% Reconstruível:** O banco `SQLite FTS5` (`.cerberus/index.db`) é um cache derivado. Se for deletado ou corrompido, é reconstruído do zero em <1 segundo.
3. **Sem Vendor Lock-in:** O motor opera nativamente em Python standard library com SQLite FTS5 (BM25 + Tokenização Unicode/Porter) sem dependência obrigatória de APIs de embeddings externas ou bancos vetoriais pesados.
4. **Isolamento de Poderes:**
   - **Memória** responde: *"O que sabemos?"*
   - **Orquestrador (Maestro/Gemini)** responde: *"O que deve acontecer agora?"*
   - **Mission Control / Canvas** responde: *"O que está acontecendo?"*
5. **Read-First Security:** MCP Server V1 estritamente somente-leitura. Sem vazamento de `.env`, sem escrita cega na memória.

---

## 🗺️ 2. Topologia do Sistema

```
[Fontes Markdown Canônicas] (Git)
 ├── C:\DevManiacs\DM-Cerebro (Global, Governance, ADRs, Projects, Learnings)
 └── C:\DevManiacs\migra\dm-erp\docs\brain (Local ERP Brain)
          │
          ▼  (Watcher / Incremental Hash / Rebuild)
[SQLite FTS5 Storage Engine (.cerberus/index.db)]
 ├── Table: documents (metadados relacionais e JSON)
 ├── Table: documents_fts (FTS5 BM25 Virtual Table)
 └── Table: file_meta (mtime + sha256 para indexação incremental <50ms)
          │
          ▼
[Cerberus Memory Service (Python)]
 ├── 🔍 Hybrid/Lexical Search (BM25 + Authority Scoring Boost)
 ├── 📦 Budget-Aware Context Pack Generator (~1000 tokens)
 └── 🤖 MCP Server (JSON-RPC 2.0 stdio)
          │
          ▼
[Agentes de IA & IDEs]
 (Codex · Gemini Maestro · MiniMax M3 · OpenCode · Claude Code)
```

---

## ⚖️ 3. Modelo de Autoridade & Ranking

Diferente de sistemas puramente vetoriais onde uma conjectura recente de chat pode se sobrepor a uma decisão formal do PO, o Cerberus aplica **pesos de autoridade** na fórmula de relevância:

$$\text{Final Score} = \text{Score}_{\text{BM25}} \times \left(1.0 + \frac{\text{Authority Level}}{100}\right)$$

| Nível de Autoridade | Peso | Tipos de Documento |
| :--- | :---: | :--- |
| **PO_DECISION** | 100 | Decisões soberanas registradas pelo PO Helbert Moura |
| **CANONICAL_ADR** | 90 | Arquitetura oficial registrada em `DECISIONS.md` / `ADR-*` |
| **GOVERNANCE** | 85 | Regras de governança (`global/ai-governance.md`, `model-routing.md`, `security-baseline.md`) |
| **APPROVED_QA** | 80 | Relatórios de auditoria aprovados e vereditos de segurança |
| **ARCHITECTURE** | 75 | Specs técnicas e topologias (`arquitetura.md`, `superpowers/specs/`) |
| **LEARNING** | 70 | Lições aprendidas corporativas (`LEARNINGS.md`, gotchas de frameworks) |
| **HANDOVER** | 60 | Continuidade operacional e passagens de bastão (`HANDOVER.md`) |
| **WIKI** | 50 | Guias técnicos, fórmulas TCU, SEFAZ e tutoriais |

---

## 🛠️ 4. Uso via Linha de Comando (CLI)

O CLI está disponível em `C:\DevManiacs\DM-Cerebro`:

```bash
# 1. Indexação / Reconstrução do índice
python -m engine.cli index
python -m engine.cli index --rebuild

# 2. Status e métricas
python -m engine.cli status

# 3. Busca por palavra-chave / conceito
python -m engine.cli search "SEFAZ A1 cofre criptografia" --project canteirohub
python -m engine.cli search "BDI TCU maior residuo"

# 4. Gerar Context Pack sob medida para uma tarefa
python -m engine.cli context-pack --project canteirohub --task "Implementar novo endpoint do Robô SEFAZ DF-e" --role DEVELOPER

# 5. Consultar ADRs e Learnings
python -m engine.cli decisions --project canteirohub
python -m engine.cli learnings --topic godot
```

---

## 🔌 5. Configuração do MCP Server para os Agentes

Para conectar o Cerberus MCP aos seus agentes (Codex, Claude Code, Cursor, OpenCode), configure o servidor stdio:

### Configuração JSON (Claude Code / Cursor / OpenCode):
```json
{
  "mcpServers": {
    "cerberus-memory": {
      "command": "python",
      "args": [
        "-m",
        "engine.cli",
        "mcp"
      ],
      "cwd": "C:\\DevManiacs\\DM-Cerebro"
    }
  }
}
```

### Ferramentas Expostas pelo MCP:
1. `cerberus_search_memory(query, project_id?, limit?)`: Busca rápida ponderada por autoridade.
2. `cerberus_get_context_pack(project_id, task_summary, role?)`: Monta o Context Pack pronto para iniciar a tarefa.
3. `cerberus_get_decisions(project_id?, limit?)`: Retorna ADRs canônicas.
4. `cerberus_get_learnings(topic?, project_id?)`: Retorna lições aprendidas e gotchas técnicos.
5. `cerberus_get_project_context(project_id)`: Retorna resumo do projeto.
6. `cerberus_get_stats()`: Retorna métricas do cérebro.
O rebuild é uma mutação administrativa disponível apenas no CLI local (`cerberus index --rebuild`); não é exposto como tool MCP.

## Hardening 002 — fronteira canônica

Entradas automáticas nunca escrevem Markdown. `capture` e `ingest-report` persistem candidatos JSON em `.cerberus/inbox/`, com fingerprint SHA-256 e proveniência obrigatória. O lifecycle operacional é `CANDIDATE -> VERIFIED -> CANONICAL`; `QUARANTINED`, `REJECTED`, `SUPERSEDED` e `ARCHIVED` são estados terminais/administrativos. Somente o CLI local promove: `review <id> --verify`, depois `promote <id>` para preview e `promote <id> --apply` para escrita atômica allowlisted.

O índice SQLite é derivado e ignorado pelo Git. Raízes são resolvidas, ordenadas e desduplicadas por ancestralidade. A identidade de documento inclui hash do caminho canônico, evitando colisões entre `README.md` de raízes independentes.
