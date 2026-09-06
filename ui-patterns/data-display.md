# 📊 UI Pattern: Data Display

## 1. Pattern: Dense Enterprise Data Grid
- **USE WHEN:** Listagens operacionais complexas (pedidos, notas fiscais, medições de obra, orçamentos) com centenas de linhas e múltiplas colunas numéricas.
- **AVOID WHEN:** Landing pages ou telas de consumo onde cards visuais são mais eficazes.
- **UX:** Densidade industrial alta, tipografia tabular monospace para números, alinhamento à direita para valores monetários/quantidades, cabeçalho fixo (sticky header) e paginação ou virtualização eficiente.
- **A11Y:** Marcação semântica de tabela (`<table>`, `<th> scope="col"`, `<td>`). Navegação completa por teclado.
- **MOBILE:** Alternar para visualização em cartões resumidos ou permitir rolagem horizontal explícita com primeira coluna congelada (sticky).
- **DESKTOP:** Linhas compactas (36-40px de altura), ações de linha reveladas por hover ou menu de 3 pontos.
- **REFERENCES:** TanStack Table, AG Grid, MUI X Data Grid.

---

## 2. Pattern: Master-Detail Layout
- **USE WHEN:** Inspeção rápida de itens de uma lista sem perder o contexto da listagem (ex: chamados do HelpDev, auditorias, mensagens).
- **AVOID WHEN:** Conteúdo do detalhe exigir largura total (acima de 12 colunas) ou quando a lista for extremamente curta (<3 itens).
- **UX:** Painel esquerdo com a lista pesquisável; painel direito exibindo os detalhes do item selecionado com ações imediatas.
- **A11Y:** Foco gerenciado ao selecionar um item. Indicação clara de qual item está ativo (`aria-current="true"`).
- **MOBILE:** O detalhe empilha como nova tela com botão de retorno ("Voltar").
- **DESKTOP:** Divisão 30/70 ou 40/60 com scroll independente em cada coluna.
- **REFERENCES:** Outlook Web, Linear, GitHub Issues split view.
