# 🏛️ Referência: Arsenal Camadas 8 a 12 — Fundações de Design & Engenharia

> **Princípio Central:** A infraestrutura fundamental de uma interface de software — Tipografia, Iconografia, Layout moderno, Mobile e Tokens — deve ser matematicamente coesa, acessível por padrão e imune aos vícios preguiçosos de templates de IA.

---

## 1. Camada 8: Tipografia com Intenção (Sem "Inter no Piloto Automático")

A tipografia define a voz e a autoridade da interface:

| Repositório de Fontes | Tipo de Licença | Uso Recomendado |
| :--- | :--- | :--- |
| **[Fontshare](https://www.fontshare.com)** | Gratuita para uso comercial (ITF) | Tipografias premium com personalidade rica (Satoshi, General Sans, Clash Display, Cabinet Grotesk). |
| **[Google Fonts](https://fonts.google.com)** | Open Source (OFL / Apache-2.0) | Fontes estáveis de alta cobertura de glifos e diacríticos pt-BR (Plus Jakarta Sans, DM Sans, Outfit, Space Grotesk). |
| **[Fontsource](https://fontsource.org)** | Self-hosted NPM | Empacotamento de fontes locais no bundle sem dependência de CDNs externas que vazam IP de usuários. |
| **[Velvetyne](https://velvetyne.fr) & [Collletttivo](http://www.collletttivo.it)** | Open Source Experimental | Fontes Display de alta assinatura para projetos editoriais ou identidades expressivas. |

### Regras de Tipografia Dev Maniac's:
1. **Banimento de Inter / Roboto como escolha preguiçosa:** Não use apenas porque o Figma ou o shadcn vieram configurados com ela. Justifique a escolha tipográfica no Design DNA.
2. **Tabular Numerals Obrigatório em Sistemas:** Em tabelas e métricas, declare `font-variant-numeric: tabular-nums` (Tailwind: `tabular-nums`) para que dígitos tenham larguras idênticas.
3. **Escala Modular Calibrada:** Máximo de 2 famílias tipográficas (uma para Headings/Display e uma para Body/UI). Mantenha uma proporção fixa (ex: Major Third 1.25x) com line-heights generosos no corpo de texto (`leading-relaxed`).

---

## 2. Camada 9: Iconografia Consistente

- **Fontes Homologadas:** **[Tabler Icons](https://tabler.io/icons)**, **[Phosphor Icons](https://phosphoricons.com)**, **[Lucide](https://lucide.dev)**, **[Remix Icon](https://remixicon.com)**, **[Heroicons](https://heroicons.com)**.
- **Regras Inegociáveis:**
  1. **Uma Única Família por Produto:** Nunca misture ícones do Lucide com ícones do FontAwesome e Material Symbols no mesmo sistema. O peso visual (stroke width), raio dos cantos e viewBox diferem e criam ruído.
  2. **Não coloque ícones em tudo:** Um botão com texto claro ("Salvar Alterações") não precisa obrigatoriamente de um disquete do lado. Ícone serve para **ancoragem visual de scanning**, não decoração compulsiva.
  3. **Banimento de Emojis em UI Industrial/ERP:** Emojis (🚀, 💡, 🔥) não são ícones vetoriais; quebram a seriedade do software empresarial.

---

## 3. Camada 10: Layout Moderno (Sem a Muleta do `max-w-7xl`)

A IA sempre tenta enfiar todo o conteúdo do mundo dentro de um container centralizado `max-w-7xl mx-auto px-4`. Isso quebra dashboards e sistemas que precisam de amplitude horizontal em monitores ultrawide.

### Práticas Modernas de Layout:
- **CSS Grid & Subgrid:** Use `subgrid` para alinhar itens de cartões filhos à grade do container pai, garantindo que botões de rodapé fiquem perfeitamente alinhados mesmo com títulos de tamanhos diferentes.
- **Container Queries (`@container`):** Componentes devem responder ao espaço disponível no seu próprio container, e não apenas à largura da viewport (`@media`). Uma tabela dentro de um split-pane de 400px deve se comportar como mobile mesmo em um monitor 4K.
- **Logical Properties:** Use `inline-size` (largura lógica), `block-size` (altura lógica), `margin-inline` e `padding-inline` para suporte natural a i18n e direções textuais.
- **Funções Matemáticas CSS:** Use `clamp(1rem, 2.5vw, 2rem)` para tipografia e espaçamentos fluidos em vez de dezenas de breakpoints manuais (`sm:`, `md:`, `lg:`, `xl:`).

---

## 4. Camada 11: Mobile Recomposto (Não é Apenas Empilhar Desktop)

Desenvolver para mobile **NÃO É** simplesmente aplicar `flex-col` e empilhar uma tabela de 10 colunas:

1. **Touch Targets de 48x48px:** Todo botão ou controle interativo no celular deve ter área de toque mínima de **48x48px** (WCAG 2.2 Success Criterion 2.5.8), mesmo que o elemento visual seja menor.
2. **Ergonomia do Polegar (Thumb Reach):** Ações principais, menus e buscas devem viver na **metade inferior da tela**, facilmente acessíveis pelo polegar do operador em campo.
3. **Tabelas Complexas em Mobile:**
   - **Opção 1 (Card Transform):** A linha da tabela se transforma em um cartão estruturado com rótulo e valor.
   - **Opção 2 (Frozen Identifier + Horizontal Scroll):** Fixe a coluna de identificação à esquerda e permita scroll horizontal contido apenas nas métricas secundárias.
   - **Opção 3 (Master-Detail Drilldown):** A lista exibe apenas Nome + Status; o toque abre uma folha inferior (*Bottom Sheet / Drawer*) com o restante dos dados.

---

## 5. Camada 12: Sistema de Design Tokens

Toda aplicação profissional deve centralizar seus valores em tokens semânticos:
- **Cores & Superfícies:** `--bg-base`, `--surface-1`, `--surface-2`, `--border-subtle`, `--text-primary`, `--text-muted`.
- **Escala de Espaçamento:** 4px, 8px, 12px, 16px, 20px, 24px, 32px, 48px, 64px.
- **Escala de Raios (Geometry):** 2px (sharp), 4px (subtle), 6px (default), 8px (soft).
- **Sombras Físicas:**
  - `shadow-xs`: elevação de borda sutil.
  - `shadow-sm`: cards em repouso.
  - `shadow-md`: dropdowns e popovers.
  - `shadow-lg`: modais e drawers.
- **Z-Index Disciplinado:** `--z-dropdown: 100`, `--z-sticky: 200`, `--z-modal: 500`, `--z-toast: 1000` (evitar valores arbitrários como `z-[99999]`).
