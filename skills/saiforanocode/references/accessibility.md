# ♿ Referência de Engenharia de Acessibilidade (WCAG 2.1 & 2.2 AA)

> **Princípio:** Acessibilidade não é um favor nem um checklist de compliance burocrático — é engenharia robusta. Uma interface acessível funciona melhor com teclado, leitores de tela, automações de teste (Playwright) e sob condições adversas (sol forte, telas de baixa qualidade).

---

## 1. Semântica Nativa & Hierarquia de Marcos (Landmarks)

### 1.1 Elementos Interativos Nativos
- **Ação vs Navegação:**
  - `<button type="button">`: Para mutações de estado na página (abrir modal, submeter, expandir menu).
  - `<a href="...">`: Para navegação entre URLs/rotas navegáveis.
- ❌ **Crime Frontend:** `<div onClick={...}>` ou `<span onClick={...}>`. Além de não receber foco por padrão, quebra navegação assistiva e atalhos de leitor de tela.

### 1.2 Marcos Estruturais Semânticos
```html
<header> <!-- Cabeçalho global da aplicação --> </header>
<nav aria-label="Navegação Principal"> <!-- Links essenciais --> </nav>
<main id="main-content"> <!-- Conteúdo dinâmico da tela --> </main>
<aside aria-label="Painel de Detalhes"> <!-- Barra lateral contextual --> </aside>
<footer> <!-- Rodapé e metadados legais --> </footer>
```
- Forneça sempre um link para pular para o conteúdo principal (*Skip to Content*):
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-primary focus:text-primary-foreground focus:p-3 focus:rounded-md">
  Pular para o conteúdo principal
</a>
```

---

## 2. Navegação por Teclado & Focus Management

### 2.1 Indicador de Foco Visível (`focus-visible`)
Nunca remova o outline sem fornecer um anel de foco de alto contraste:
```css
/* Padrão Acessível Global */
:focus-visible {
  outline: 2px solid var(--ring-color, #2563eb);
  outline-offset: 2px;
}
```
Em Tailwind:
```tsx
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
```

### 2.2 Focus Trap e Ciclo de Diálogo (Modais & Drawers)
Todo diálogo modal DEVE:
1. Conter `role="dialog"` e `aria-modal="true"`.
2. Conter `aria-labelledby="dialog-title"` e `aria-describedby="dialog-desc"`.
3. Prender o ciclo da tecla `Tab` dentro do modal enquanto estiver aberto.
4. Fechar ao pressionar `Escape`.
5. Retornar o foco ativamente para o botão que disparou a abertura ao fechar.
*(Recomendação: Delegue a primitivas testadas como Base UI Dialog ou Radix Dialog).*

---

## 3. Formulários Acessíveis & Mensagens de Erro

### 3.1 Vínculo Estrito de Labels
- Todo `<input>`, `<select>` e `<textarea>` DEVE ter um `<label>` explicitamente associado via `htmlFor` / `id`.
```tsx
<div>
  <label htmlFor="user-cnpj" className="block text-sm font-medium text-foreground">
    CNPJ da Empresa
  </label>
  <input
    id="user-cnpj"
    type="text"
    aria-invalid={!!errors.cnpj}
    aria-describedby={errors.cnpj ? "cnpj-error" : undefined}
    className="..."
  />
  {errors.cnpj && (
    <p id="cnpj-error" className="mt-1 text-xs text-destructive" role="alert">
      {errors.cnpj.message}
    </p>
  )}
</div>
```

### 3.2 Live Regions para Alertas Dinâmicos
Mensagens de sucesso, cálculo dinâmico ou erros que aparecem sem recarregar a página devem ser anunciadas para leitores de tela:
```tsx
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {statusMessage}
</div>
```

---

## 4. Contraste de Cores & Visibilidade (WCAG 2.1/2.2 AA)

- **Texto Normal (< 18pt regular ou < 14pt bold):** Contraste mínimo de **4.5:1** contra o fundo.
- **Texto Grande (≥ 18pt regular ou ≥ 14pt bold):** Contraste mínimo de **3.0:1**.
- **Controles de Formulário e Ícones Funcionais:** Bordas de inputs e ícones que transmitem status devem ter no mínimo **3.0:1** contra o fundo adjacente.
- **Nunca transmita status apenas por cor:** Combine cor + ícone + texto legível (ex.: 🔴 Erro + ícone `AlertTriangle` + texto "Falha no envio").

---

## 5. Tabelas e Visualizações de Dados

- Use elementos nativos de tabela: `<table>`, `<caption>`, `<thead>`, `<tbody>`, `<th>`, `<td>`.
- Cabeçalhos devem possuir escopo explícito: `<th scope="col">` e `<th scope="row">`.
- Colunas ordenáveis devem declarar estado acessível:
```tsx
<th scope="col" aria-sort={sortDirection === 'asc' ? 'ascending' : sortDirection === 'desc' ? 'descending' : 'none'}>
  <button onClick={toggleSort} className="flex items-center gap-1 w-full text-left">
    <span>Data de Vencimento</span>
    <ArrowUpDown className="h-4 w-4" aria-hidden="true" />
  </button>
</th>
```

---

## 6. Dispositivos Móveis & Touch Targets

- **Dimensão Mínima de Toque:** **48px × 48px** para elementos de clique primário (botões, checkboxes, ícones de menu). Se o ícone visual for de 20px, use `p-3.5` ou área invisível com pseudo-elemento `::before` para atingir 48px.
- **Espaçamento Mínimo:** Mantenha pelo menos `8px` de separação física entre dois touch targets adjacentes para evitar toques incorretos em telas sensíveis.
