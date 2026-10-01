# TASK-ID: TASK-CERBERUS-FRONTEND-HELPDESK-OVERHAUL-002
> **Projeto:** DM-Cerebro (Cerberus Web Inspector & Memory Engine)  
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)  
> **Responsavel:** OpenCode · MiniMax M3 (Frontend & UI/UX Specialist)  
> **Risco:** 2 (MEDIUM)

---

## 🎯 Objetivo Geral
Reformular integralmente a interface Web do DM-Cerebro (Inspector) para seguir com 100% de fidelidade o padrao visual **Solido Industrial do HelpDesk** (`suporte.devmaniacs.com.br` / `/opt/sistemas/helpdev/frontend`), com todas as abas 100% funcionais e reativas, gestao de perfil do usuario, troca de senha e configuracao interativa de 2FA TOTP.

---

## 🎨 Padrao Visual Solido Industrial (Design Tokens)
- **Background Deep:** `#061637`
- **Surface / Containers:** `#0A192F`
- **Card Background:** `#0D2247`
- **Input Background:** `#061637`
- **Border Dark:** `#1E3A6D`
- **Borda Suave:** `#152E5A`
- **Cyan Primario (Acoes & Foco):** `#08B9CA`
- **Yellow (Alertas & Tags):** `#FFC529`
- **Coral / Red (Danger & Rejeitar):** `#FF4C4C`
- **Navy Accent:** `#1E40AF`
- **Tipografia:**
  - Headings & Destaques: `Space Grotesk`, sans-serif
  - Corpo & UI: `Inter`, sans-serif
  - Codigo, Hashes & 2FA Tokens: `IBM Plex Mono` / `ui-monospace`
- **Diretrizes Estritas:** ZERO degradês chamativos de IA, ZERO neon roxo, ZERO emojis no lugar de icones (usar SVGs nitidos), alvos de toque >= 44px (WCAG 2.2 AA).

---

## 🧩 Modulos & Funcionalidades Obrigatorias

### 1. Header Corporativo Dev Maniac's
- Logo SVG oficial Dev Maniac's.
- Titulo: "Cerberus Inspector" + Tag "Dev Maniac's Memory Engine".
- Pill de status do cluster (Online / SQLite FTS5 Ativo).
- Botao / Avatar do Helbert (`admin@devmaniacs.com.br`) abrindo o Modal de Perfil & Seguranca.
- Botao de Logout com acao em `POST /auth/logout`.

### 2. Barra de Abas (Tabs) 100% Funcionais
- `[ 🔍 Busca Semantica ]` (`#tab-search`)
- `[ 📥 Inbox de Memorias ]` (`#tab-inbox`) com contador de pendentes em tempo real.
- `[ 🕸️ Topologia de Grafos ]` (`#tab-topology`)
- `[ ⚙️ Metricas & Reindexacao ]` (`#tab-metrics`)
- `[ 👤 Meu Perfil & Seguranca ]` (`#tab-profile` ou Modal Dedicado)

### 3. Detalhamento das Abas

#### 3.1 Aba de Busca Semantica & Hibrida
- Input de busca com placeholder claro, debounce e suporte a tecla `Enter`.
- Filtros por escopo: `[ Todos ]`, `[ dm-erp ]`, `[ Teenus ]`, `[ HelpDesk ]`, `[ Biolar ]`, `[ Arquitetura ]`.
- Lista de resultados com score de relevancia (ex: `98% match`), caminho do arquivo, trecho contextual e tags.
- Modal de leitura com renderizacao rica de Markdown (titulos, listas, blocos de codigo formatados com botao Copiar).

#### 3.2 Aba de Inbox de Candidatos
- Cards organizados por status (Pendente, Verificado, Rejeitado, Quarentena).
- Botoes de acao assincrona com feedback imediato via Toasts:
  - `[ ✅ Aprovar ]` -> `POST /api/inbox/<id>/promote`
  - `[ 🔍 Verificar ]` -> `POST /api/inbox/<id>/verify`
  - `[ ❌ Rejeitar ]` -> `POST /api/inbox/<id>/reject`
- Ao executar acao, atualizar a lista e o contador do Inbox sem refresh na pagina.

#### 3.3 Aba de Topologia de Grafos (Canvas 2D)
- Canvas 2D protegido contra falhas de contexto, desenhando nos com cores dos tipos de memoria (Decisao = Yellow, Aprendizado = Cyan, Arquitetura = Blue).
- Interatividade com mouse (pan, zoom e selecao de no).

#### 3.4 Aba de Metricas & Reindexacao
- Cards com estatisticas: Total de Documentos, Total de Chunks, Embeddings Vetoriais, Estado do FTS5.
- Botao `[ ⚡ Reindexar Cerebro Agora ]` que executa `POST /api/reindex` e exibe spinner com progresso.

#### 3.5 Painel de Meu Perfil & Seguranca (Helbert / Admin)
- Dados da conta (email, status 2FA, data de criacao).
- **Formulario de Troca de Senha:**
  - Campos: Senha Atual, Nova Senha, Confirmar Nova Senha.
  - Botao "Atualizar Senha" que consome `POST /api/v1/auth/change-password` e exibe toast de retorno.
- **Central de 2FA TOTP:**
  - Status atual (Ativo ou Inativo com badge colorido).
  - Se inativo: Botao "Ativar 2FA" que consome `POST /api/v1/auth/2fa/setup`, renderiza o QR Code SVG na tela, campo de 6 digitos TOTP e botao "Confirmar e Ativar" (`POST /api/v1/auth/2fa/verify-and-enable`).
  - Se ativo: Botao "Desativar 2FA" que abre modal pedindo a senha atual e executa `POST /api/v1/auth/2fa/disable`.

### 4. Telas de Login e 2FA
- Tela de login e tela de 2FA no mesmo padrao visual solido industrial, com foco nitido e tratamento de erros com alertas consistentes.

---

## 🧪 Criterios de Aceite
1. Todas as abas trocam de estado e carregam dados sem erros no console do navegador.
2. Todos os cliques em botoes (Aprovar, Rejeitar, Verificar, Reindexar, Trocar Senha, 2FA) funcionam com feedback visual imediato.
3. Responsivo em desktop (1920x1080 / 1440x900) e mobile (390x844).
