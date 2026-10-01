# 🧠 Dev Maniac's — Base de Conhecimento e Aprendizados Corporativos
> Repositório central de conhecimento compartilhado entre todos os PCs, repositórios e agentes.

## 🏛️ 1. Princípios Universais da Dev Maniac's (Helbert Moura)
1. **O humano (Helbert Moura) é a autoridade final** de negócio, produto e deploy.
2. **Separação de Poderes:** Quem implementa nunca aprova sozinho a própria implementação.
3. **Código e evidência antes de opinião:** Investigue antes de propor; valide com testes antes de declarar pronto.
4. **Zero Breaking Changes:** Alterações são incrementais, versionadas e blindadas contra regressões.
5. **TDD Obrigatório:** Escreva testes unitários/lógicos antes da implementação.

## 🎮 2. Diretrizes Game Dev (Godot 4.x / GDScript)
- **Indentação:** Use SEMPRE TABS (padrão Godot Engine).
- **Tipagem Estática:** Obrigatória em tudo (`var score: int = 0`, `func update_pos(delta: float) -> void:`).
- **Comunicação:** Use Sinais (`Signals`) para desacoplamento de nós. Evite `get_parent()`.
- **Performance:** 60+ FPS constante, sem memory leaks, nós modulares e reutilizáveis.

## 🌐 3. Diretrizes Web & Backend (Python / Django / React / Go)
- **Python:** Pydantic V2 e Type Hints em 100% dos métodos e schemas. Async/await para I/O.
- **Go:** Tratamento de erro explícito sempre (sem panic em produção).
- **Frontend:** React, TypeScript estrito, acessibilidade WCAG 2.2 AA e botões com `tap-44` (≥44px).
- **Design System Industrial:** Fundo Sólido (#F2EFE8 / #FFFFFF / #0F172A), Azul Aço (#1E40AF), Laranja (#E4570F), ZERO emojis em UI (usar Lucide-React).

## 🚀 4. Portabilidade Turnkey & Ecossistema Multi-Agente (Maestri + OpenCode)
- **Pacote Universal:** `devmaniacs-turnkey-pack.zip` exportado via `export_devmaniacs_pack.py` e instalado via `install.ps1`.
- **Duplo Cérebro (Dual Brain):** `~/Desktop/DM-Cerebro` (corporativo global) + `$ProjectDir/docs/brain/` (local de cada projeto).
- **Hierarquia no Maestri Canvas (`.maestri/roles/`):**
  1. 👑 **Lead Architect / Maestro (Gemini / Antigravity):** Orquestrador, planejamento, TASK-*.md e Code Review de relatórios.
  2. 💻 **Senior Builder (MiniMax M3):** Frontend, UI/HUD, Game Dev Godot 4.x (TABS/Signals) e construção pesada.
  3. ⚡ **Systems Engineer (GLM-5.3 Flash / Max):** Backend, State Machines, APIs, matemática e TDD rigoroso.
  4. 🧪 **QA Gatekeeper (Gemini QA / GLM QA):** Testes de estresse, profiling 60+ FPS, zero memory leaks e GO / NO-GO.
- **Telegram Bridge:** Isolado por projeto com `.env` próprio para evitar colisões de polling HTTP 409.
## 🧠 5. Cerberus Memory Intelligence Engine (SQLite FTS5 + MCP + Auto-Capture)
- **Persistência de Memória:** Plain Markdown em disco como Source of Truth versionado no Git (`DM-Cerebro` e `dm-erp/docs/brain`).
- **Índice Derivado:** SQLite FTS5 (`.cerberus/index.db`) com WAL mode, BM25 ranking e boost por autoridade (`PO_DECISION = 100` até `WIKI = 50`).
- **Auto-Capture & Deduplicação:** Ingestão de relatórios (`REPORT-*.md`) e lições com verificação anti-duplicação e proveniência obrigatória (`task_id`, `agent_role`, `timestamp`).
- **Protocolo MCP stdio:** Servidor nativo JSON-RPC 2.0 integrado ao Claude Code, Codex, Cursor e OpenCode expondo ferramentas seguras somente-leitura.

### Defeitos nasceram de briefing sub-especificado do maestro, não de execução do worker
> **Proveniência:** Task `TASK-ECOMM-042` · Agente `ARCHITECT` · Projeto `ecommerce-platform` · Capturado `2026-09-08T23:27:51.442487+00:00` · Fingerprint `528d6db616ff31d673632287940dcb8998e3631c39caddc7e617c2a7a27d6279`

Em esteiras de IA autônomas, defeitos sutis de implementação frequentemente nascem de briefing sub-especificado no nível do maestro (ex: ausência de restrições de tipografia, tokens rígidos ou contratos de API vagos). Testes automatizados e linting comumente passam, sendo indispensável a triagem e verificação canônica por QA humano no Inbox do Cerberus.
