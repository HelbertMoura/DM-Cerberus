# 🪟 UI Pattern: Overlays & Modals

## 1. Pattern: Accessible Modal Dialog
- **USE WHEN:** Ações críticas que exigem atenção exclusiva do usuário (confirmações destrutivas, criação rápida de registro).
- **AVOID WHEN:** Exibir grandes volumes de dados ou navegação profunda (usar página dedicada ou sheet lateral).
- **UX:** Fundo escurecido sem blur exagerado. Foco inicial no primeiro elemento interativo ou no botão de cancelamento (se destrutivo).
- **A11Y:** Focus trap estrito (Tab não vaza pro fundo). Fechamento obrigatório via tecla `Esc` e clique no backdrop. `role="dialog"`, `aria-modal="true"`.
- **MOBILE:** Converter para bottom sheet móvel com arrasto para fechar.
- **DESKTOP:** Centralizado, largura contida (máx 560px para alertas, 720px para formulários).
- **REFERENCES:** Radix Dialog, Base UI Dialog.

---

## 2. Pattern: Command Palette (Search & Quick Action)
- **USE WHEN:** Aplicações ricas com dezenas de atalhos e páginas, onde usuários de poder buscam agilidade pelo teclado (`Cmd+K` / `Ctrl+K`).
- **AVOID WHEN:** Sites públicos institucionais ou aplicativos simples sem ações frequentes.
- **UX:** Entrada de texto instantânea com filtragem fuzzy local, agrupamento por escopo (Ações Recentes, Navegação, Clientes).
- **A11Y:** WAI-ARIA combobox pattern. Suporte a seleção por setas e anúncio de resultados.
- **MOBILE:** Acionamento por botão de busca no topo ou gesto; lista ocupa a tela cheia.
- **DESKTOP:** Modal flutuante no terço superior da tela com backdrop suave.
- **REFERENCES:** cmdk (Pacote maduro), Raycast UI pattern.
