# 🧭 UI Pattern: Navigation

## 1. Pattern: Segmented Navigation Tabs
- **USE WHEN:** Alternar entre 2 a 5 visualizações ou categorias irmãs no mesmo nível de contexto.
- **AVOID WHEN:** Mais de 6 abas, ou quando as abas navegam para destinos totalmente diferentes da aplicação (usar sidebar/header nav).
- **UX:** Transição fluida com indicador ativo ancorado. Manter estado da aba anterior se houver edição em andamento.
- **A11Y:** WAI-ARIA `role="tablist"`, `role="tab"` com `aria-selected="true|false"`, suporte a navegação por setas (`ArrowLeft`/`ArrowRight`).
- **MOBILE:** Abas com rolagem horizontal contida ou converter para dropdown se houver mais de 3 abas. Touch target mínimo de 44px.
- **DESKTOP:** Compacto, alinhado ao topo do container de conteúdo.
- **REFERENCES:** Radix Tabs, Base UI Tabs.

---

## 2. Pattern: Mobile Bottom Navigation
- **USE WHEN:** 3 a 5 destinos primários de nível superior em aplicações mobile ou PWA.
- **AVOID WHEN:** Telas com teclado aberto, fluxos modais profundos ou quando houver menos de 3 destinos.
- **UX:** Fixo no rodapé. Ícone + rótulo textual conciso. Feedback tátil/visual imediato ao toque.
- **A11Y:** Respeitar `env(safe-area-inset-bottom)`. Rótulos claros para leitores de tela (`aria-label`).
- **MOBILE:** Posição ergonômica dentro da thumb zone. Touch target mínimo 48x48px.
- **DESKTOP:** Ocultar no desktop (`hidden md:flex`) em favor de sidebar ou header.
- **REFERENCES:** Material You Navigation Bar, iOS Tab Bar.

---

## 3. Pattern: Responsive Drawer / Sidebar Navigation
- **USE WHEN:** Navegação hierárquica complexa em ERPs e dashboards corporativos com dezenas de módulos.
- **AVOID WHEN:** Landing pages simples ou sites com poucas páginas.
- **UX:** Estado colapsável com ícones de alta legibilidade. Agrupamento lógico por domínio de negócio.
- **A11Y:** `role="navigation"`, foco preso quando aberto como drawer modal em mobile, fechar com `Esc`.
- **MOBILE:** Drawer lateral sobreposto com backdrop escurecido.
- **DESKTOP:** Barra lateral fixa ou recolhível com persistência de preferência do usuário.
- **REFERENCES:** shadcn/ui Sidebar, Mantine AppShell.
