# DEV MANIACS FRONTEND TOOLBOX V2

Decision catalog for modern frontend development. This is a capability map, not a dependency manifest.

## Invocation contract

Before choosing a tool, read project stack, `package.json`, lockfile and `DESIGN.md`. Reuse an existing good solution before adding a new library.

Use:

```text
NEED
→ CAPABILITY
→ EXISTING STACK
→ CANDIDATE
→ TRADEOFF
→ USE / DON'T USE
```

`CHEAPEST RELIABLE TOOL FIRST`.

## Category map

| Category | Primary | Alternative | Specialized | Reference/Avoid |
|---|---|---|---|---|
| UI primitives | Base UI | Radix UI | React Aria | Headless UI reference; mixed primitives avoid |
| Component system | shadcn/ui | Mantine | MUI/Ant Design | HeroUI reference until project fit |
| Simple table | native/project table | Mantine/MUI table | — | MUI X for MUI only |
| Interactive table | TanStack Table | MUI X | PrimeReact | custom headless needs project work |
| Enterprise grid | AG Grid | MUI X Data Grid | TanStack Table advanced | license/accessibility gate |
| Virtualization | TanStack Virtual | react-window | — | no virtualization for small lists |
| Simple business chart | Recharts | Chart.js | Bklit UI | Nivo/Tremor reference until verified |
| Large/real-time chart | ECharts | Recharts streaming | Visx | benchmark memory/update rate |
| Highly custom chart | Visx | D3 | ECharts | team must own testing/performance |
| Simple form | React Hook Form | HTML validation | — | Formik reference only |
| Complex form | TanStack Form | React Hook Form + Zod | — | avoid giant forms without need |
| Validation | Zod | Valibot | ArkType | Yup reference/alternative |
| Icons | Lucide | Phosphor | Tabler/Material | one family per product |
| Simple motion | CSS | WAAPI | Motion/GSAP | Anime.js only complex |
| Coordinated motion | Motion | GSAP | Anime.js | GSAP license review |
| Cinematic/SVG/WebGL | Anime.js | GSAP/Motion | Three.js | not common UI |
| Loader | CSS/skeleton | project state | Dot Matrix | no decorative loader |
| Drag/drop | dnd-kit | Pragmatic Drag and Drop | — | verify current official package before use |
| Simple rich text | Tiptap | Lexical | ProseMirror | Slate reference/alternative |
| Collaborative editor | Tiptap + collaboration | Lexical | ProseMirror | need backend/sanitization |
| Simple map | Leaflet | MapLibre | React Leaflet | provider costs |
| Advanced map | MapLibre | OpenLayers | MapLibre + vector tiles | Google ecosystem cost |
| Command palette | cmdk | project-native dialog | — | use only when command set needs it |
| Local search | MiniSearch | Fuse.js | — | no search engine for small arrays |
| Date/time | date-fns | Day.js | Luxon/Temporal | use project adapter first |
| Simple upload | native input | react-dropzone | Uppy | security always server-side |
| Large/resumable upload | Uppy | FilePond | S3 multipart | verify provider flow |
| Notifications | Sonner | native/component system | React Hot Toast | avoid toast for everything |
| Overlays | Base/Radix primitives | Headless UI | project portal | use one primitive family |
| Carousel | Embla | Swiper | — | avoid if UX does not need it |
| Local state | useState/useReducer | context scoped | — | no global store by default |
| Shared UI state | Zustand | Jotai | XState | Redux Toolkit for large global state |
| State machine | XState | reducer explícito | — | only explicit complex states |
| Server state | TanStack Query | SWR | framework-native | use one cache owner |
| Routing | framework-native | TanStack Router | React Router | do not replace router without benefit |
| A11y scan | axe + Playwright | Lighthouse | Accessibility Insights | zero findings != compliance |
| Visual testing | Playwright local | Storybook visual | Chromatic/Percy | no SaaS without need |
| Component dev | Storybook | Ladle/Histoire | — | React vs Vue appropriate |
| Performance | Lighthouse/Playwright | WebPageTest | React Profiler | measure real route/device |
| Images | native picture + AVIF/WebP | framework optimizer | CDN | prioritize native |
| 2D creative | p5.js/Konva/Pixi | Fabric | — | keep specialized |
| 3D | Three.js/R3F | WebGL custom | — | not common UI |
| Mobile gestures | Gesture Handler | NativeWind | Reanimated | web-only avoid |
| Tokens | CSS variables + DESIGN.md | Style Dictionary | Tokens Studio/Tailwind | tokens are executable intent |
| Styling | project style | CSS Modules/Tailwind | Panda/vanilla-extract | CSS-in-JS avoid by default |
| i18n | framework-native/next-intl | react-i18next | FormatJS | require SSR/RSC/RTL tests |
| Sanitization | DOMPurify only when needed | native text APIs | — | sanitization is boundary-specific |
| Unit/component | Vitest + Testing Library | Jest | — | E2E is not unit test |
| E2E | Playwright | — | — | browser surface only |
| Utilities | clsx/tailwind-merge | CVA/nanoid | — | avoid lodash whole bundle |
| AI UI | project-native stream/chat | Markdown/Tiptap | specialized AI components | no generic AI glow |
| ERP/admin | TanStack Query/Table/Form + Zod | AG Grid at scale | virtualization | prioritize scannability |
| Premium visuals | Open Design + DESIGN.md | Cult UI (lib opcional) | Shader Gradient (tool) | Refero Styles (inspiração/referência) |

## Full references

Read only what the task needs:

- `references/primitives.md`
- `references/tables-charts-forms.md`
- `references/charts.md`
- `references/forms-validation.md`
- `references/ecosystem.md`
- `references/ecosystem-2.md`
- `references/state-routing.md`
- `references/accessibility-testing.md`
- `references/security-mobile-styling.md`
- `references/visual-premium-ai-erp.md`
- `references/decision-matrix.md`

## Project-aware gate

1. Read existing stack.
2. Read package and lockfile.
3. Read DESIGN.md.
4. Find existing equivalent.
5. Reject redundant additions.
6. Verify license, maintenance, advisories, scripts, dependency tree and provenance.
7. Measure bundle, SSR/RSC, mobile, accessibility, theming, performance, tests and cleanup.
8. Adapt to local tokens, typography, color, radius, spacing, motion, density and accessibility.
9. Record decision and post-adoption verification.

## Future self-update

For new tools:

`DISCOVER → VERIFY → COMPARE → SECURITY CHECK → CLASSIFY → ADD ONLY IF USEFUL`

Reclassify or remove tools when abandoned, compromised, deprecated or superseded. Preserve history of decisions.
