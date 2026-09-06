# Frontend Toolbox V2 Decision Matrix

## Core routing

```text
NEED
→ CAPABILITY
→ EXISTING STACK
→ CANDIDATE
→ TRADEOFF
→ USE / DON'T USE
```

`CHEAPEST RELIABLE TOOL FIRST`.

## Problem → default → alternative → specialized → avoid when

| Problem | Default | Alternative | Specialized | Avoid when |
|---|---|---|---|---|
| UI primitives | Base UI | Radix UI / Headless UI | React Aria | projeto exige primitives styled |
| Design-system copy-paste | shadcn/ui | Ark UI | Uilora como referência | identidade pronta do catálogo dominar |
| Styled component system | Mantine | HeroUI / MUI | Ant Design | equipe não quer lock-in visual |
| Simple table | native table/shadcn table | Mantine/MUI table | — | tabela é interativa complexa |
| Interactive table | TanStack Table | MUI X | PrimeReact | projeto não tem padrões headless |
| Enterprise grid | AG Grid | MUI X Data Grid | TanStack Table com features | custo/licença não se justifica |
| Large list virtualization | TanStack Virtual | react-window | — | lista pequena |
| Simple business chart | Recharts | Chart.js | Bklit UI | visual altamente específico |
| Dashboard charts | Bklit UI / Recharts | ECharts | Visx | acesso/licença/custo não aprovado |
| Real-time chart | ECharts | Recharts live pattern | Visx | dados e frequência não justificam |
| Highly custom visualization | Visx | D3 | ECharts | equipe não assume curva D3 |
| Simple form | React Hook Form | HTML constraint validation | — | formulário realmente trivial |
| Complex form | TanStack Form | React Hook Form + Zod | — | Formik sem necessidade |
| Validation | Zod | Valibot | ArkType | runtime compartilhado sem validação runtime |
| Icons | Lucide | Phosphor | Tabler/Material | produto mistura famílias |
| Simple motion | CSS | WAAPI | GSAP/Motion | apenas hover/focus/loading |
| Coordinated motion | Motion | GSAP | Anime.js | motion simples resolve |
| Cinematic/SVG/WebGL | Anime.js | GSAP/Motion | Three.js | UI comum |
| Loader | CSS/spinner/skeleton | component state | Dot Matrix | loader é apenas estado transitório |
| Drag and drop | dnd-kit | Pragmatic Drag and Drop | — | dnd não for keyboard/touch |
| Simple rich text | Tiptap | Lexical | Slate | editor apenas campo rico |
| Collaborative editor | Tiptap Collaboration/ProseMirror | Lexical collaboration | Yjs backend | collaboration não foi definida |
| Simple map | Leaflet | MapLibre | React Leaflet | tiles/provider comercial |
| Routes/geo | MapLibre | Leaflet + tiles | OpenLayers | requisitos simples |
| Command palette | cmdk | project-native dialog/list | — | comandos poucos e simples |
| Local fuzzy search | MiniSearch | Fuse.js | — | array pequeno |
| Dates | date-fns | Day.js | Luxon/Temporal | projeto já tem date adapter |
| Upload | native input | react-dropzone | Uppy | upload simples |
| Notifications | Sonner | native/component system | React Hot Toast | tudo virar toast |
| Overlay | Base/Radix/Dialog primitives | Headless UI | portal project-native | primitive já resolve |
| Carousel | Embla | Swiper | — | UX não precisa carrossel |
| Local state | useState/useReducer | context only scoped | — | estado local vira global |
| Shared UI state | Zustand/Jotai | React context | — | server state está sendo erroneamente colocado no client |
| Global app state | Redux Toolkit | Zustand/Jotai | XState | dependência global só para estado simples |
| State machine | XState | reducer explícito | — | fluxo não tem estados complexos |
| Server state | TanStack Query | SWR | framework-native | projeto tem uma solução melhor no framework |
| Routing | Next.js App Router | TanStack Router | React Router | trocar router sem ganho real |
| Accessibility scan | axe-core/Playwright | Lighthouse | Accessibility Insights | zero findings como compliance final |
| Visual testing | Playwright local | Storybook visual tests | Chromatic/Percy | SaaS pago sem necessidade |
| Components docs | Storybook | Ladle/Histoire | — | app sem component system |
| Performance audit | Lighthouse + Playwright | WebPageTest | React Profiler | proxy/ambiente diferente |
| Media | native picture/img/AVIF/WebP | framework optimization | CDN service | upload local inseguro |
| Creative/3D | p5.js/shader | Konva/Pixi | Three.js/R3F | WebGL em UI comum |
| Mobile gestures | Gesture Handler | NativeWind | Reanimated | projeto web-only |
| Tokens | CSS variables + DESIGN.md | Style Dictionary | Tokens Studio/Tailwind | DTCG não foi validado |
| Styling | existing project style | Tailwind/CSS Modules | Panda/vanilla-extract | runtime/style lock-in não compensa |
| Dark/high contrast | semantic token layers | framework theme | Tailwind dark mode | contraste e prefers-contrast não testados |
| i18n | framework-native/next-intl | react-i18next/FormatJS | — | i18n não é requisito real |
| DOM sanitization | DOMPurify only when needed | native text APIs | — | biblioteca sem threat model |
| Unit/component | Vitest + Testing Library | Jest | — | teste E2E para função simples |
| E2E | Playwright | — | — | browser não é a superfície principal |
| Utilities | native/class utilities | clsx/tailwind-merge/CVA | nanoid | instalar lodash inteiro |
| AI UI | project-native chat/stream | Tiptap/Markdown | component library específica | estética AI genérica |
| ERP/CRM/admin | TanStack Query + TanStack Table/Form + accessible primitives | AG Grid for scale | virtualization | grid SaaS-like/dados densos |
| Premium visual reference | Open Design + DESIGN.md | Bklit/Aceternity-style reference | Uilora | não deve virar dependency cega |
