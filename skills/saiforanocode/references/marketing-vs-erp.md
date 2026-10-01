# 🏢 Referência: Separação Estrita — Marketing vs ERP / Sistemas Operacionais

> **A Regra de Ouro Inegociável:** NUNCA aplique a composição, o espaçamento ou a estética de uma landing page em um software corporativo ou ERP. Um operador que utiliza o sistema 8 horas por dia possui necessidades cognitivas e ergonômicas completamente opostas às de um visitante casual de marketing.

---

## 1. Matriz de Separação de Domínio

| Dimensão | 📣 Marketing / Landing Pages | 🏗️ ERP / Backoffice / Sistemas Operacionais |
| :--- | :--- | :--- |
| **Objetivo Central** | Persuasão, narrativa, conversão e primeira impressão. | Eficiência, velocidade, precisão, scanning rápido e zero erro de digitação. |
| **Tempo de Sessão** | 30 segundos a 3 minutos. | 4 a 8 horas contínuas de trabalho intenso. |
| **Densidade** | Baixa a Média (espaçada, arejada, respiração visual). | **Alta e Organizada** (máxima informação relevante visível sem scroll desnecessário). |
| **Padrão de Layout** | Seções verticais narrativas, Hero visual, prova social, CTA final. | Shell de aplicação, Sidebar colapsável, Header com contexto global, Split-panes, Master-Detail, Abas contextuais. |
| **Tratamento de Dados** | Números arredondados e destacados ("+10k clientes"). | **Tabular Numerals**, alinhamento à direita para valores monetários/quantitativos, precisão decimal explícita. |
| **Navegação** | Scroll vertical suave, links âncora. | **Atalhos de teclado globais** (`Cmd+K`, `Alt+N`), setas para navegação em tabelas, paginação e visualizações salvas. |
| **Modais e Overlays** | Modais de captura, banners temporários. | **Drawers laterais**, painéis de inspeção persistentes, diálogos de confirmação com foco preso. |
| **Motion** | Expressivo, storytelling, revelação em cascata. | **Estritamente funcional**, instantâneo (<150ms), apenas para indicar causalidade e estado. |

---

## 2. O Princípio da Densidade Operacional Organizada

Densidade NÃO é poluição visual nem bagunça. Densidade é **ergonomia para o trabalho**:

1. **Evitar o "Espaçamento Balão":**
   - Em um ERP, inputs com `h-14` e linhas de tabela com `h-20` forçam o operador a rolar a tela constantemente para comparar duas informações.
   - Padrão recomendado para sistemas: controles compactos (`h-8` a `h-9`), linhas de dados compactas (`h-10` a `h-11`), fontes de dados nítidas de 13px a 14px com contraste calibrado.
2. **Scanning Visual Imediato:**
   - O olhar do operador deve escanear colunas de cima a baixo sem ziguezaguear.
   - Textos alinhados à esquerda; códigos, datas e status centralizados; valores numéricos e monetários **sempre alinhados à direita**.
3. **Informação Simultânea (Sem Esconder atrás de 3 Cliques):**
   - Não esconda dados fundamentais atrás de tooltips, carrosséis ou menus de "três pontinhos" excessivos.
   - Ações principais (Editar, Imprimir, Aprovar) devem estar visíveis na barra de comando ou acessíveis por atalhos.

---

## 3. Command Center em vez de "6 Cards de KPI Iguais"

O vício mais recorrente de IAs ao desenhar dashboards é criar uma grade de 4 ou 6 cartões perfeitamente idênticos com um número gigante e um ícone colorido em um círculo.

### Por que isso é AI Slop Operacional:
- Um dashboard real de gestão não é um mural estático de 6 números; ele é um **centro de comando ativo** que deve responder:
  1. *O que está acontecendo agora?*
  2. *O que mudou desde a última checagem?*
  3. *O que exige minha atenção imediata (exceções, alertas, pendências)?*
  4. *Qual é a próxima ação prioritária que devo executar?*

### Arquitetura de um Command Center Profissional:
1. **Faixa Compacta de Status (KPI Strip):**
   - Em vez de cards gigantes, uma barra horizontal densa contendo métricas com comparativo temporal (`+12% vs mês anterior`) e indicador de tendência direto.
2. **Lista Priorizada de Exceções & Alertas:**
   - Bloco de atenção operacional: *"3 pedidos com atraso de expedição"*, *"2 notas fiscais rejeitadas pela SEFAZ"*.
3. **Painel Central de Trabalho (Master-Detail ou Tabela Ativa):**
   - Visão em tempo real das tarefas ou registros operacionais do dia, permitindo seleção em lote e ações imediatas.
4. **Gráfico Contextual de Distribuição:**
   - Em vez de 4 gráficos circulares inúteis, 1 gráfico denso de série temporal ou funil de conversão com seletor de intervalo.
5. **Timeline de Auditoria / Activity Stream:**
   - Registro cronológico recente com identificação de quem realizou cada ação no sistema.
6. **Command Bar Integrada (`Cmd+K`):**
   - Busca global e disparo de ações rápidas sem tirar a mão do teclado.

---

## 4. Padrões Operacionais Obrigatórios em ERP

- **Master-Detail com Split Panes:** Selecionar um item na lista à esquerda abre seus detalhes, histórico e abas de edição no painel à direita, sem recarregar a página.
- **Filtros Persistentes & Saved Views:** Operadores precisam salvar suas visões comuns (ex: *"Meus chamados em aberto"*, *"Obras de Minas Gerais pendentes de laudo"*).
- **Ações em Lote (Bulk Actions):** Seleção múltipla com barra flutuante de ações (`Exportar Selecionados`, `Aprovar em Lote`, `Alterar Status`).
- **Edição Inline Segura:** Permitir ajustes rápidos de campos simples diretamente na tabela com feedback de salvamento otimista e cancelamento via `Esc`.
