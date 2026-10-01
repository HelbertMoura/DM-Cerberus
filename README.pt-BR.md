# 🧠 DM-Cerberus — Inteligência de Memória Local-First & Cockpit Pro para Assistentes de Código IA

<p align="center">
  <a href="https://devmaniacs.com.br/" target="_blank" rel="noopener noreferrer">
    <img src="assets/cerberus_cockpit.png" alt="Logo DM-Cerberus" width="128" height="128" />
  </a>
</p>

<p align="center">
  <strong>O cérebro soberano de memória contínua, busca híbrida e radar de tokens para agentes autônomos de IA.</strong><br>
  Criado para <strong>Google Antigravity</strong>, <strong>OpenAI Codex</strong>, <strong>Claude Code</strong>, <strong>Cursor</strong> e <strong>Windsurf</strong>.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licen%C3%A7a-MIT-emerald.svg" alt="Licença MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg" alt="Versões do Python" />
  <img src="https://img.shields.io/badge/Arquitetura-Local--First-success.svg" alt="Local First" />
  <img src="https://img.shields.io/badge/Privacidade-100%25%20No%20Dispositivo-brightgreen.svg" alt="100% Local" />
  <img src="https://img.shields.io/badge/Telemetria-Zero%20Sa%C3%ADda-lightgrey.svg" alt="Sem Telemetria" />
  <img src="https://img.shields.io/badge/Protocolo-MCP%20Standard-purple.svg" alt="Protocolo MCP" />
  <a href="https://devmaniacs.com.br/"><img src="https://img.shields.io/badge/Dev%20Maniac's-Systems-red.svg" alt="Dev Maniac's Systems" /></a>
</p>

<p align="center">
  <a href="#-recursos-principais">Recursos</a> •
  <a href="#-galeria-visual">Galeria</a> •
  <a href="#-início-rápido">Início Rápido</a> •
  <a href="#-integração-mcp">Configuração de Agentes</a> •
  <a href="#-arquitetura">Arquitetura</a> •
  <a href="#-comunidade--apoio">Apoiar</a> •
  <a href="README.md">English</a> •
  <a href="README.es.md">Español</a>
</p>

---

## ⚡ O Problema: Amnésia de Contexto e Desperdício de Tokens em IA

Ao desenvolver softwares complexos com agentes autônomos de programação (Codex, Antigravity, Claude Code, Cursor, Windsurf), desenvolvedores enfrentam gargalos críticos:
1. **Amnésia de Contexto:** Cada sessão de terminal inicia do zero. Decisões arquiteturais anteriores, esquemas de banco de dados e correções de bugs precisam ser reexplicadas manualmente.
2. **Loops Infinitos e Queima de Cota:** Agentes podem entrar em loops repetitivos de leitura de arquivos e tentativas de testes, consumindo centenas de milhares de tokens sem gerar valor.
3. **Vazamento de Privacidade na Nuvem:** Armazenar conhecimento técnico em bases vetoriais de terceiros expõe regras de negócio proprietárias e a propriedade intelectual da sua empresa.
4. **Alucinação e Desalinhamento:** Sem uma fonte canônica e verificada da verdade, agentes tomam decisões conflitantes entre si.

O **DM-Cerberus** elimina esses problemas. Rodando 100% no seu computador, ele atua como cérebro corporativo unificado e torre de controle de custos.

---

## ✨ Recursos Principais

### 🔍 1. Busca Híbrida SQLite FTS5 com Ranqueamento BM25 por Autoridade
- Varredura instantânea de documentações Markdown, ADRs, contratos de API e regras de negócio.
- Combina a **precisão léxica do SQLite BM25** com pontuação por autoridade documental (de notas temporárias de nível 10 até decisões canônicas de nível 50).
- Resposta em submilissegundos com zero dependência de bancos vetoriais em nuvens externas.

### 📥 2. Pipeline de Aprendizados & Inbox de Triagem Humana
- Conforme os agentes resolvem desafios, eles propõem aprendizados de forma autônoma via `capture_learning`.
- Verificação proativa **Human-in-the-Loop**: inspecione diffs no navegador, valide com um clique ou promova diretamente para a base canônica.
- Estrutura tolerante a falhas que ignora arquivos corrompidos ou legados sem travar a interface.

### 📊 3. Cockpit Pro 5x & Radar Anti-Loop em Tempo Real
- Contabilidade precisa de tokens de Prompt, Conclusão e Raciocínio (Reasoning).
- Modelagem de custos locais para `gpt-6.1-sol`, `gpt-6-luna`, `gpt-6-astra`, `claude-3-7-sonnet` e `gemini-2.5-pro`.
- **Radar Anti-Loop**: Monitora chamadas repetidas de ferramentas e prompts em looping, alertando você antes do estouro de orçamento.
- Exportação completa dos dados para CSV com um clique.

### 🌐 4. Grafo Visual Interativo de Topologia de Memória
- Mapa 2D interativo com forças dinâmicas ilustrando a relação entre projetos, documentos canônicos, decisões tomadas e agentes.
- Inspeção de nós com zoom e panorâmica fluida em canvas HTML5 acelerado por hardware.

### 🛡️ 5. Segurança Corporativa e Soberania Local
- **100% No Dispositivo:** Dados nunca saem de `127.0.0.1`. Zero telemetria, zero rastreamento externo.
- Hashing de senha com **PBKDF2-HMAC-SHA256** (200.000 iterações).
- **Autenticação em Duas Etapas (2FA TOTP RFC 6238)** compatível com Google Authenticator, Authy e 1Password.
- Cookies de sessão assinados com HMAC-SHA256 em tempo constante.

### 🔌 6. Servidor Nativo Model Context Protocol (MCP)
- Compatibilidade total com o protocolo universal **Anthropic MCP**.
- Conecte o DM-Cerberus ao Codex, Antigravity, Claude Code, Cursor, Windsurf ou pipelines locais em CrewAI/LangFlow.

---

## 📸 Galeria Visual

| Cockpit Pro 5x & Radar de Tokens | Busca FTS5 & Pré-visualização |
|:---:|:---:|
| ![Cockpit Pro 5x](assets/showcase/showcase_cockpit.png) | ![Busca & Preview](assets/showcase/showcase_search.png) |

| Inbox de Triagem & Revisão | Topologia Interativa de Memória |
|:---:|:---:|
| ![Inbox de Revisão](assets/showcase/showcase_inbox.png) | ![Grafo de Topologia](assets/showcase/showcase_topology.png) |

| Login Soberano & Identidade Dev Maniac's | Conta & Segurança 2FA |
|:---:|:---:|
| ![Tela de Login](assets/showcase/showcase_login.png) | ![Segurança de Conta](assets/showcase/showcase_profile.png) |

---

## 🚀 Início Rápido

### Opção A: Execução Direta em Python (Recomendado)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/HelbertMoura/DM-Cerberus.git
   cd DM-Cerberus
   ```

2. **Indexe sua memória inicial:**
   ```bash
   python -m engine.cli index
   ```

3. **Inicie o Painel Cockpit:**
   ```bash
   python -m engine.cli ui --port 8765
   ```
   Acesse `http://127.0.0.1:8765` no seu navegador.

4. **Atalho de Desktop (Windows):**
   Execute `bin/launch_cockpit.pyw` para abrir a interface em segundo plano com ícone personalizado sem janela de terminal.

---

### Opção B: Docker Compose

```bash
cp .env.example .env
# Configure suas senhas no .env
docker compose up -d
```
Acesse o painel em `http://127.0.0.1:7331`.

---

## 🤖 Integração com Agentes (MCP)

Configure o DM-Cerberus como servidor MCP no seu ambiente:

### 1. Google Antigravity / Gemini CLI
Adicione ao seu `mcp_servers.json`:
```json
{
  "mcpServers": {
    "cerberus-memory": {
      "command": "python",
      "args": ["-m", "engine.cli", "mcp"],
      "cwd": "C:/caminho/para/DM-Cerberus"
    }
  }
}
```

### 2. Claude Code (`~/.claude/config.json`)
```json
{
  "mcpServers": {
    "cerberus": {
      "command": "python",
      "args": ["-m", "engine.cli", "mcp"],
      "cwd": "/caminho/para/DM-Cerberus"
    }
  }
}
```

### 3. Cursor & Windsurf (`cursor_mcp.json` / `settings.json`)
```json
{
  "mcpServers": {
    "cerberus-memory": {
      "command": "python",
      "args": ["-m", "engine.cli", "mcp"],
      "cwd": "/caminho/para/DM-Cerberus"
    }
  }
}
```

### Ferramentas MCP Disponíveis

| Ferramenta | Descrição |
|:---|:---|
| `cerberus_search_memory` | Busca semântica e lexical FTS5 em decisões e documentações |
| `cerberus_get_context_pack` | Pacote instantâneo de contexto e regras para uma tarefa ou projeto |
| `cerberus_get_decisions` | Consulta os registros de decisão de arquitetura (ADRs) |
| `cerberus_capture_learning` | Registra uma nova hipótese/aprendizado para revisão humana no Inbox |
| `cerberus_save_task_state` | Salva o estado da tarefa, progresso e bloqueios entre sessões |
| `cerberus_get_task_state` | Recupera o estado salvo da tarefa para continuar de onde parou |

---

## 📜 Licença

Distribuído sob a **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para detalhes.

---

## ☕ Comunidade & Apoio

O **DM-Cerberus** é mantido à base de café ☕ e eletricidade ⚡ por **Helbert Moura** e a equipe da **Dev Maniac's Systems**.

- 🌐 **Site Oficial:** [devmaniacs.com.br](https://devmaniacs.com.br/)
- 💖 **Apoiar o Projeto & Redes:** [linktr.ee/helbertmoura](https://linktr.ee/helbertmoura)
- 🚀 **Conheça também:** [AI Launcher](https://github.com/HelbertMoura/ai_launcher)
- 🐛 **Reportar Problemas:** [GitHub Issues](https://github.com/HelbertMoura/DM-Cerberus/issues)
