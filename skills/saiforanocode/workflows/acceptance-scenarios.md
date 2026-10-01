# 🎯 Cenários de Aceite & Validação Prática (A a J)

> Este guia estabelece os critérios de avaliação e o raciocínio arquitetural esperado para cada um dos 10 cenários de desafio de interface.

---

### Cenário A: Landing Page de Construção Civil / Engenharia
- **Objetivo:** Persuasão, autoridade, geração de leads qualificados (construtoras, investidores).
- **Diretrizes de Design:**
  - **Hero Section:** Fotografia autêntica de canteiro de obras real em alta resolução com tratamento de cor quente e sóbrio (tons de concreto, aço, terra e detalhe em amarelo/laranja industrial). Tipografia Display forte e geométrica (ex: Cabinet Grotesk ou Syne). Tese direta: "Reduza o desperdício de insumos em até 18% na fase de estrutura".
  - **Prova Social Concreta:** M2 construídos auditados, ARTs emitidas, selos de certificação PBQP-H / ISO 9001 e logos de construtoras reais com depoimento do Diretor de Engenharia.
  - **Interatividade:** Calculadora simples de economia de insumos (cimento/aço) com resultado imediato e CTA: `[ Receber Estudo de Viabilidade ]`.
  - ❌ **Erros Fatais:** Esferas 3D de vidro flutuando, ilustrações coloridas "flat art" de pessoas sorrindo sem capacete, gradiente roxo no fundo.

---

### Cenário B: ERP de Apontamento de Obras em Campo
- **Objetivo:** Eficiência extrema para engenheiros e mestres de obra em canteiro (baixo sinal, sol forte, luvas).
- **Diretrizes de Design:**
  - **Densidade & Ergonomia:** Contraste máximo em modo claro (alto reflexo solar). Botões e áreas de toque de **48px mínimo**.
  - **Grid Operacional:** Tabela de insumos recebidos vs utilizados no dia. Entradas numéricas diretas com teclado numérico ativado no mobile (`inputMode="decimal"`).
  - **Alinhamento Numérico:** Quantidades (sacos, vigas, m³) e valores em R$ rigorosamente alinhados à direita com `font-variant-numeric: tabular-nums`.
  - **Resiliência Offline:** Indicador discreto de sincronização local (`3 apontamentos pendentes de upload via SQLite/Dexie`).
  - ❌ **Erros Fatais:** Cards flutuantes com sombras gigantes, inputs cinza claro sem borda perceptível no sol, animações de abertura de modal demoradas.

---

### Cenário C: Overhaul de Dashboard KPI (De "6 Cards Coloridos" para Command Center)
- **Problema Inicial:** 6 cartões quadrados com fundos coloridos (roxo, verde, amarelo, azul) com números soltos no topo da tela sem contexto de ação.
- **Transformação para Centro de Comando:**
  - **Faixa Superior de Síntese:** Barra compacta de 48px de altura com 4 indicadores de pulso: Status Operacional (Normal/Alerta), Volume Transacionado Hoje, SLA de Atendimento e Itens Críticos que Exigem Atenção.
  - **Área Central (Master-Detail):** Split-view com 70% ocupado pela lista/tabela de ordens críticas filtradas por urgência e 30% ocupado pelo painel contextual de detalhes e despacho imediato.
  - **Ação Direta:** O operador não precisa ir para outra tela para aprovar ou reatribuir uma tarefa; faz diretamente da linha da tabela via menu inline ou atalho de teclado (`A` para aprovar, `R` para rejeitar).

---

### Cenário D: O "Moderno" sem Clichés de IA
- **Conceito:** A modernidade visual não vem de efeitos cosméticos (glows, glassmorphism, gradientes), mas da **precisão da engenharia**.
- **Diretrizes de Execução:**
  - **Tipografia Esculpida:** Contraste marcante entre títulos em peso semi-bold com kerning calibrado (`tracking-tight`) e corpo de texto com altura de linha confortável (`leading-relaxed`).
  - **Espaçamento Negativo Intencional:** Em vez de encher cada pixel com caixas e linhas, use o espaço vazio para guiar os olhos para a informação principal.
  - **Bordas e Superfícies Físicas:** Bordas de `1px` em tons neutros ligeiramente mais escuros que o fundo (`border-border/60`), sombras com raio curto e opacidade de 4% que simulam elevação tátil real.

---

### Cenário E: Customização do shadcn/ui Além do Padrão "Cinza Slate"
- **Diagnóstico:** A maioria dos projetos que usam shadcn parecem clones idênticos com `zinc`/`slate` e `rounded-md` padrão de fábrica.
- **Plano de Customização:**
  - **Geometria:** Alterar a escala de `--radius` para refletir o DNA do produto (`0.2rem` para industrial/financeiro; `0.75rem` para aplicativo criativo).
  - **Paleta Temática:** Substituir a escala fria por uma escala personalizada: ex.: `Warm Stone` (fundo levemente aquecido com off-white `#faf9f6`) ou `Midnight Slate` (azul profundo escuro e elegante).
  - **Componentes Densitários:** Criar variantes compactas dos componentes (`size="dense"` em botões, tabelas e inputs com padding vertical reduzido).
  - **Anéis de Foco:** Modificar o foco genérico para uma cor de destaque com offset e espessura customizada.

---

### Cenário F: Aplicação dos Princípios do Linear em Software Corporativo B2B
- **Pilares do Linear:** Velocidade instantânea, ergonomia de teclado, densidade refinada e polimento extremo.
- **Implementação:**
  - **Paleta de Comandos Global (`Cmd + K` / `Ctrl + K`):** Acesso instantâneo a qualquer entidade, busca de clientes, mudança de status e atalhos de navegação.
  - **Navegação por Teclas:** Setas `J` e `K` para subir e descer itens em tabelas; `Enter` para inspecionar; `E` para editar.
  - **Feedback Otimista (Optimistic UI):** Ao alterar o status de um registro, a UI atualiza em 0ms enquanto a requisição viaja para o servidor, com rollback suave em caso de erro.
  - **Densidade:** Redução de padding decorativo; fontes de 12px a 13px para metadados e 14px para dados primários.

---

### Cenário G: Justificação e Dosagem de Motion em Sistemas Operacionais
- **Regra:** O usuário trabalha 8 horas por dia no sistema. Qualquer animação que cause cansaço visual ou perda de tempo deve ser eliminada.
- **Onde Motion é Justificado:**
  - Transição de expansão de linha (*accordion/sub-row*): 120ms para o operador não se perder espacialmente na leitura.
  - Reordenação de lista por drag-and-drop: AutoAnimate suave para indicar a nova posição sem salto brusco.
  - Drawer lateral de inspeção: 180ms deslizando do lado direito com curva desacelerada (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Onde Motion é Proibido:**
  - Gráficos que reconstroem barras do zero a cada filtro aplicado.
  - Tabelas que dão fade-in a cada troca de página de paginação.

---

### Cenário H: Escaneamento Rápido em Tabelas de Dados Complexas
- **Desafio:** Tabela com 18 colunas e milhares de linhas onde o operador precisa encontrar discrepâncias fiscais.
- **Solução de Engenharia:**
  - **Fixação de Colunas (Column Pinning):** Coluna "ID / Código" e "Razão Social" fixadas à esquerda; "Ações / Status" fixada à direita durante o scroll horizontal.
  - **Cabeçalho Congelado (Sticky Header):** Permanece visível durante a rolagem vertical.
  - **Alinhamento Numérico & Fontes Tabulares:** Todos os valores contábeis e datas com `tabular-nums` e alinhamento à direita.
  - **Destaque Dinâmico:** Foco na linha atual (`hover:bg-muted/50`) e preservação do estado de seleção via checkbox com contadores ativos (`3 de 150 itens selecionados`).

---

### Cenário I: Recomposição de Telas Densas para Mobile
- **Armadilha:** Tentar espremer uma tabela de 8 colunas dentro de uma tela de 375px criando scroll horizontal infinito ou texto minúsculo ilegível.
- **Estratégia de Recomposição:**
  - Transformar linhas da tabela em **Cards Operacionais Estruturados**:
    - Topo do card: Identificador do pedido + Badge de status alinhado à direita.
    - Meio do card: Nome do cliente (destaque) + Valor financeiro em peso semi-bold.
    - Base do card: Metadados secundários (data, responsável) em tipografia menor e discreta.
  - **Painel de Ações Rápidas:** Em vez de botões minúsculos no card, o toque no card abre um **Bottom Sheet** acessível na base da tela com as ações em botões grandes (48px) ao alcance do polegar.

---

### Cenário J: Estética Premium Autêntica (Sem Falsa Opulência)
- **Definição:** Premium autêntico transmite confiança institucional, precisão técnica e exclusividade, sem recorrer a dourados bregas ou efeitos neon.
- **Elementos Fundamentais:**
  - **Tipografia Editorial:** Títulos em serif contemporânea (ex: Instrument Serif, Newsreader ou Cormorant) contrastando com corpo de texto em sans limpa (ex: Satoshi, General Sans).
  - **Paleta Cromática Monocromática e Quente:** Fundo off-white refinado (`#f8f7f4`), texto em grafite profundo (`#18181b`), bordas extremamente delicadas (`#e4e2dd`).
  - **Materiais e Imagens:** Ensaios fotográficos de altíssima qualidade com iluminação natural, gráficos com linhas finas e precisas.
  - **Microcópia Confiante:** Textos enxutos, afirmativos, sem necessidade de autopromoção exagerada ("Desde 1984 preservando patrimônios familiares").
