# 📊 Referência: Arsenal Camada 6 — Data-Heavy, Gráficos & ERP

> **Princípio Central:** Interfaces ricas em dados (Data-Heavy) são o coração de sistemas de gestão, construção civil, logística e financeiro. Elas exigem estabilidade extrema, virtualização de DOM para milhares de registros, controles rápidos de teclado e visualizações analíticas limpas sem ruído decorativo.

---

## 1. Motores de Tabela & Data Grids

| Solução | Arquitetura | Licença | Quando Usar |
| :--- | :--- | :--- | :--- |
| **[TanStack Table](https://tanstack.com/table)** | Headless (100% livre de estilo) | MIT | **Padrão Oficial Dev Maniac's.** Controle total de HTML/Tailwind com motor headless de ordenação, filtros, agrupamento e paginação. |
| **[TanStack Virtual](https://tanstack.com/virtual)** | Virtualizador de DOM | MIT | Renderização fluida a 60fps de listas e tabelas com 10.000+ a 100.000+ registros, renderizando apenas os nós visíveis na viewport. |
| **[AG Grid](https://www.ag-grid.com)** | Data Grid Enterprise completo | MIT (Community) / Comercial | Planilhas enterprise complexas com pivot table em tempo real, agrupamento em árvore pesado e exportação Excel nativa. |
| **[Glide Data Grid](https://github.com/glideapps/glide-data-grid)** | Canvas-based | MIT | Grids ultra-densos de milhões de células (estilo Google Sheets / Airtable) renderizados em HTML5 Canvas. |
| **[Handsontable](https://handsontable.com)** | Spreadsheet-like | Comercial / Source-available | Interfaces onde o usuário precisa colar dados diretamente do Excel em células editáveis. |

---

## 2. Motores Gráficos & Visualização de Dados

| Biblioteca | Paradigma | Licença | Melhor Caso de Uso |
| :--- | :--- | :--- | :--- |
| **[Apache ECharts](https://echarts.apache.org)** | Canvas / SVG Completo | Apache-2.0 | Dashboards de alta performance, séries temporais pesadas, gráficos de candlestick, mapas geográficos e gráficos de calor. |
| **[Recharts](https://recharts.org)** | Componentes React / SVG | MIT | Gráficos simples e declarativos integrados a temas Tailwind/SaaS (linhas, barras, áreas). |
| **[Visx](https://airbnb.io/visx/)** | Primitives D3 para React | MIT | Visualizações customizadas exclusivas da marca sem amarras de templates pré-fabricados. |
| **[Lightweight Charts](https://tradingview.github.io/lightweight-charts/)** | TradingView Canvas | Apache-2.0 | Gráficos financeiros e de cotações com zoom e pan em tempo real ultra-leves (<40KB). |
| **[uPlot](https://github.com/leeoniya/uPlot)** | Canvas 2D Minimalista | MIT | Séries temporais de telemetria e IoT com centenas de milhares de pontos por segundo. |

---

## 3. Padrões Operacionais Obrigatórios em Sistemas Densos

### A. Anatomia de uma Tabela Profissional
1. **Sticky Header:** O cabeçalho da tabela deve permanecer fixo ao rolar a página para que o operador nunca perca o contexto da coluna.
2. **Column Pinning:** Colunas essenciais (como `ID` e `Nome da Obra / Cliente`) devem poder ser fixadas à esquerda; a coluna de `Ações` fixada à direita.
3. **Tabular Numerals Obrigatório:** Em fontes modernas, utilize `font-variant-numeric: tabular-nums` (ou classe Tailwind `tabular-nums`). Isso garante que o número `1` e o número `8` ocupem exatamente a mesma largura, alinhando casas decimais verticalmente.
4. **Alinhamento Semântico Rigoroso:**
   - Textos e descrições ➔ Alinhados à **Esquerda**.
   - Datas, códigos e badges de status ➔ **Centralizados**.
   - Quantidades, percentuais, pesos e valores monetários ➔ **Alinhados à Direita**.
5. **Column Visibility & Resizing:** Em sistemas densos, permita que o usuário oculte colunas secundárias e redimensione larguras conforme a necessidade da sua tela.

### B. Master-Detail com Split Panes
- Em vez de forçar o usuário a abrir um modal gigante ou navegar para outra URL a cada clique na lista:
  - Painel esquerdo (60%): Lista de registros com filtros persistentes.
  - Painel direito (40% - Drawer / Split-Pane): Dados detalhados do item selecionado, timeline de histórico, formulário de edição rápida e anexos.

### C. Ações em Lote (Bulk Operations)
- Quando o usuário marca 1 ou mais checkboxes de linhas:
  - Surge uma barra flutuante na base da tela informando: *"14 registros selecionados"*.
  - Ações diretas disponíveis: `Aprovar em Lote`, `Exportar CSV`, `Alterar Responsável`, `Desmarcar Todos`.

### D. Tree Grids & Hierarquias
- Para estruturas como **Orçamento de Obra (Etapas > Subetapas > Insumos)** ou **Plano de Contas Financeiro**:
  - Utilize linhas expansíveis (`ChevronRight` que gira para `ChevronDown`).
  - Indentação matemática proporcional (ex: `pl-4` para nível 1, `pl-8` para nível 2) com linha guia sutil conectando a árvore.
