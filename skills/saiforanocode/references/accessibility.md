# ♿ Referência: Acessibilidade Digital (WCAG 2.1/2.2 AA)

A acessibilidade não é uma camada adicionada após a entrega — ela é parte intrínseca do design e da engenharia frontend.

---

## 1. Regras Fundamentais de Acessibilidade

### 1.1 Semântica Nativa de HTML
- Use elementos nativos sempre que possível: `<button>` para ações dentro da página, `<a href="...">` para navegação entre rotas.
- Nunca utilize `<div onClick={...}>` sem os devidos atributos de acessibilidade (`role="button"`, `tabIndex={0}`, `onKeyDown`).
- Estrutura de marcos semânticos: `<header>`, `<nav>`, `<main>`, `<section>`, `<aside>`, `<footer>`.

### 1.2 Navegação Completa por Teclado
- Todo elemento interativo deve ser acessível via `Tab` e ativável via `Enter` ou `Space`.
- Menus e listas suspensas devem responder às setas do teclado (`ArrowUp`, `ArrowDown`, `Esc` para fechar).
- **Indicador de foco visível:** Nunca utilize `outline: none` sem fornecer um substituto de alto contraste (ex: `focus-visible:ring-2 focus-visible:ring-blue-600`).
- **Focus Trap:** Modais e gavetas (drawers) devem prender o foco enquanto estiverem abertos e restaurar o foco ao elemento de origem ao fechar.

### 1.3 Contraste de Cores (WCAG AA)
- Texto normal (< 18pt ou < 14pt bold): Contraste mínimo de **4.5:1** contra o fundo.
- Texto grande (≥ 18pt ou ≥ 14pt bold) e componentes de UI essenciais (bordas de inputs, ícones funcionais): Contraste mínimo de **3:1**.
- Não transmita informações críticas exclusivamente através da cor (adicione ícones de status e texto explicativo).

### 1.4 Touch Targets em Dispositivos Móveis
- Dimensão mínima de toque para elementos clicáveis: **44px × 44px** (ou 48px × 48px para Android).
- Espaçamento adequado entre links e botões para evitar toques acidentais.

### 1.5 Preferência de Movimento Reduzido
- Respeite sempre `@media (prefers-reduced-motion: reduce)`.
- Substitua animações de translação e zoom por transições suaves de opacidade ou desative o movimento decorativo.
