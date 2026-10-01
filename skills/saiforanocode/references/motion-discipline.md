# Disciplina de Motion & Microinterações

> **Regra de Ouro:** Motion existe para comunicar causalidade e estado espacial, NUNCA para fazer teatro visual. Se uma animação atrasa o usuário em 1 milissegundo sequer durante uma tarefa repetitiva, ela é um defeito de engenharia.

---

## 1. O Princípio da Causalidade

Toda animação em interface profissional deve responder a três perguntas:
1. **De onde veio?** (Origem espacial do elemento, ex.: drawer desliza da borda onde foi acionado).
2. **Por que mudou?** (Causalidade direta de ação do usuário ou evento de stream/SSE).
3. **Para onde foi o foco?** (Orientar o olho humano para o próximo ponto de decisão sem desorientação).

### Proibições Absolutas (*Design Theater* & AI Slop):
- ❌ **Stagger Delays Excessivos:** Cards que entram em cascata com 100ms de delay entre cada um fazendo o usuário esperar 1.5s para ver o dashboard.
- ❌ **Contadores de Números Animados (*Count-up*):** Métricas que ficam girando de 0 a R$ 1.540.230,00 toda vez que a página carrega.
- ❌ **Partículas e Gradientes Orbitais Animados:** Efeitos de fundo que consomem GPU e transmitem infantilidade técnica.
- ❌ **Bounce Exagerado (*Elastic/Spring* descalibrado):** Menus e modais que quicam como gelatina em software corporativo/financeiro.

---

## 2. Escalas de Tempo e Curvas de Aceleração (Timing & Easing)

| Tipo de Interação | Duração Alvo | Easing Recomendado | Exemplos |
| :--- | :--- | :--- | :--- |
| **Micro (Instantâneo)** | **80ms – 120ms** | `ease-out` ou `cubic-bezier(0, 0, 0.2, 1)` | Hover de botão, foco de input, toggle switch, checkbox, tooltip |
| **Pequeno (Expansão local)** | **120ms – 180ms** | `cubic-bezier(0.16, 1, 0.3, 1)` | Dropdown select, accordion, badge pop, toast notification |
| **Médio (Estrutural)** | **180ms – 240ms** | `cubic-bezier(0.16, 1, 0.3, 1)` (Quart Out) | Modal dialog, slide-over drawer, sheet lateral, tab content switch |
| **Página / View Transition** | **200ms – 280ms** | `cubic-bezier(0.25, 1, 0.5, 1)` | Transição de rotas via View Transitions API |
| **> 300ms** | ⚠️ **PROIBIDO** | N/A | Inaceitável em interfaces operacionais e produtivas |

---

## 3. Pilha Tecnológica Recomendada por Caso de Uso

### A. CSS Nativo (Primeira Opção SEMPRE)
Para 90% das transições de estado, use transições CSS com propriedades aceleradas por hardware (`transform`, `opacity`).
```css
/* Transição rápida e física de botão */
.btn-action {
  transition: transform 100ms cubic-bezier(0.16, 1, 0.3, 1),
              background-color 120ms ease-out,
              box-shadow 120ms ease-out;
}
.btn-action:active {
  transform: scale(0.98);
}
```

### B. FormKit AutoAnimate (Zero Config para Listas e Grids)
Para animação automática e fluida de inserção, remoção e reordenação de itens em listas/tabelas/kanbans sem sobrecarga de bundle (~2KB).
```tsx
import { useAutoAnimate } from '@formkit/auto-animate/react';

export function OrderList({ orders }) {
  const [parent] = useAutoAnimate({ duration: 150, easing: 'ease-out' });
  return (
    <div ref={parent} className="divide-y divide-border">
      {orders.map(order => <OrderRow key={order.id} order={order} />)}
    </div>
  );
}
```

### C. Motion (Framer Motion / Motion One)
Para transições de layout complexas (`layoutId`), sheets com arraste gestual (*gestures*) e animações orquestradas de diálogo.
- Restrinja o bundle utilizando importação modular (`m` component ou `LazyMotion`).
- Nunca use `damping` muito baixo que cause oscilação elástica longa.

### D. View Transitions API Nativa
Para SPAs modernas e navegação de rotas no Next.js/Remix/Vite. Suave, performático no nível do browser e sem bibliotecas pesadas.

---

## 4. Acessibilidade Obrigatória: `prefers-reduced-motion`

Todo sistema deve honrar imediatamente a preferência do usuário por redução de movimento no SO.
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
Em Tailwind CSS:
```tsx
<div className="transition-transform duration-150 motion-reduce:transition-none motion-reduce:transform-none">
```

---

## 5. "Boring Where Boring is Good" (Onde Manter o Chão Firme)

Em sistemas operacionais (ERP, CRM, Saúde, Finanças, Logística):
- **Tabelas de Dados:** Mudança de página ou ordenação de coluna deve renderizar os novos dados **instantaneamente**. Não use fade-in demorado de tabela inteira.
- **Formulários:** O aparecimento de um campo condicional deve empurrar o conteúdo abaixo de forma suave (via `AutoAnimate` em 120ms), mas o foco do teclado deve ir para o campo imediatamente.
- **Autosave:** Um micro-indicador discreto (`Salvando...` → `Salvo há 2s`) no canto superior sem modais intrusivos ou banners piscantes.
