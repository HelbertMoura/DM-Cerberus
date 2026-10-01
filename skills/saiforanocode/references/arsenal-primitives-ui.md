# 🧱 Referência: Arsenal Camadas 2, 3 & 4 — Primitives, Product UI & Interações

> **Princípio Central:** Primitives garantem comportamento acessível e robusto; bibliotecas de UI fornecem infraestrutura; componentes diferenciados são o tempero; mas quem define a identidade visual final é o **Design System e o Design DNA do seu produto**.

---

## 1. Camada 2: Headless Primitives (Comportamento sem Imposição Visual)

As primitivas *headless* são a camada mais nobre da engenharia de UI moderna: fornecem controle total de teclado, foco, ARIA roles, posicionamento dinâmico e estados acessíveis **sem impor uma única classe de estilo visual**.

| Primitiva | Mantenedor / Ecossistema | Licença | Melhor Caso de Uso |
| :--- | :--- | :--- | :--- |
| **[Base UI](https://base-ui.com)** | MUI Team | MIT | Acessibilidade pura sem estilos, unstyled components modernos com slots limpos. |
| **[Radix UI](https://radix-ui.com)** | WorkOS | MIT | Padrão da indústria para Dialog, Popover, Tooltip, Dropdown, Tabs e Select acessíveis. |
| **[React Aria / Spectrum](https://react-spectrum.adobe.com/react-aria/)** | Adobe | Apache-2.0 | Acessibilidade de nível enterprise, suporte avançado a leitores de tela e DatePickers complexos. |
| **[Ark UI / Zag](https://ark-ui.com)** | Chakra Team | MIT | Baseado em máquinas de estado (XState/Zag); funciona em React, Vue e Solid. |
| **[Floating UI](https://floating-ui.com)** | Open Source | MIT | Motor matemático de cálculo de posicionamento (tooltips, popovers, menus flutuantes). |
| **[Ariakit](https://ariakit.org)** | Diego Haz | MIT | Focado em comboboxes, menus e diálogos ultra-leves e 100% aderentes à WAI-ARIA. |

> 🛑 **Regra de Ouro:** NUNCA reconstrua manualmente comportamentos complexos como focus trap em modais, navegação por setas em comboboxes ou detecção de colisão de tooltips via `<div>` e `onClick` rasteiro. Use primitives consolidadas.

---

## 2. Camada 3: Product UI & A Regra Anti-Shadcn-Default

Bibliotecas de componentes oferecem blocos pré-construídos para acelerar a engenharia:

| Biblioteca | Abordagem | Licença | Melhor Caso de Uso |
| :--- | :--- | :--- | :--- |
| **[Origin UI](https://originui.com)** | Copy-paste Tailwind | MIT | Variações avançadas de inputs, sliders, seletores e tabs enriquecidas. |
| **[shadcn/ui](https://ui.shadcn.com)** | Copy-paste Radix | MIT | Estrutura base de componentes de aplicação onde o código vive no seu repo. |
| **[Kibo UI](https://kibo-ui.com)** | Extensão de shadcn | MIT | Componentes complexos (color pickers, dropzones, code blocks, QR code). |
| **[Park UI](https://park-ui.com)** | Ark UI + Panda/Tailwind | MIT | Multi-framework (React, Vue, Solid) com tokens de design estruturados. |
| **[Mantine](https://mantine.dev)** | Pacote NPM completo | MIT | Dashboards e ERPs ricos que necessitam de ecossistema integrado robusto. |
| **[Tremor](https://tremor.so)** | Focado em Analytics | Apache-2.0 | Dashboards executivos, gráficos de métricas e tabelas de KPIs limpas. |
| **[Carbon Design System](https://carbondesignsystem.com)** | IBM Enterprise | Apache-2.0 | Referência mundial para softwares industriais de altíssima densidade. |

### ⚠️ A REGRA ANTI-SHADCN-DEFAULT:
O `shadcn/ui` é excelente como código inicial no seu repositório, mas **é terminantemente proibido entregar um produto com a cara padrão do shadcn** (`zinc`, `rounded-md` universal, bordas translúcidas padrão, botões pretos genéricos).

Ao adotar componentes do shadcn ou Origin UI, você DEVE **modificar deliberadamente**:
1. **A Geometria e os Raios:** Alinhe ao Design DNA (ex: 2px para industrial, 6px para SaaS corporativo).
2. **As Alturas e Espaçamentos:** Reduza o padding para atender à densidade operacional do sistema.
3. **A Paleta e Elevação:** Substitua as variáveis de cor cinza neutro pelas cores institucionais do `DESIGN.md`.
4. **Os Estados e Indicadores:** Implemente anéis de foco, hover states e active states próprios da sua marca.

---

## 3. Camada 4: Interações Diferenciadas & A "Regra do Tempero"

Registries modernos oferecem componentes com micro-interações refinadas:
- **[21st.dev](https://21st.dev):** Mercado aberto de componentes React/Tailwind da comunidade.
- **[Cult UI](https://cult-ui.com):** Componentes interativos com física e micro-animações táteis.
- **[Kokonut UI](https://kokonutui.com):** Componentes modernos com IA-prompt inputs e botões táteis.
- **[Fancy Components](https://fancycomponents.dev):** Efeitos tipográficos e botões com feedback gestual.

### 🧂 A Regra do Tempero (Anti-Frankenstein UI):
- Componentes diferenciados são **TEMPERO**, nunca a base da refeição.
- Não construa um sistema colando um botão do Cult UI, uma tabela do Tremor, um card do Kokonut e uma navbar do Aceternity. O resultado parecerá um monstro sem identidade.
- **Protocolo de Incorporação:** Todo componente externo copiado deve ser despojado de suas classes arbitrárias e **redigitado com os tokens locais de cor, tipografia, borda e raio do seu projeto**.
