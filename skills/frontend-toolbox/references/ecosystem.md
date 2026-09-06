# Icons, Motion, Loaders, Drag & Drop, Rich Text, Maps, Command Palette & Search

## Icons

### Lucide
- Primary for most projects.
- Official: https://lucide.dev
- NPM: `lucide-react` 1.38.0, ISC, repository https://github.com/lucide-icons/lucide.
- Use when: consistent, tree-shakable outline icons and React integration.
- Rule: one primary family per product, recorded in DESIGN.md; do not mix arbitrarily.

### Phosphor
- Alternative/strong choice for richer icon weights/styles.
- Official: https://phosphoricons.com
- Use when: visual hierarchy benefits from multiple weights and a slightly more expressive language.
- Tradeoff: design direction differs from Lucide; standardize one family.

### Tabler Icons
- Alternative for large neutral icon catalog and consistent SVG geometry.
- Official: https://tabler.io/icons
- Use when: system needs breadth, simple SVG integration and neutral style.
- Tradeoff: do not combine with Lucide/Phosphor for every icon.

### Material Symbols
- Specialized/alternative for Google Material language.
- Official: https://fonts.google.com/icons
- Use when: product already adopts Material conventions or needs variable font-style symbol delivery.
- Tradeoff: visual language and font-loading strategy must be intentional.

### Heroicons
- Reference/alternative for Tailwind-adjacent projects.
- Official: https://heroicons.com
- Use when: existing Tailwind/Markdown project already uses Heroicons.
- Tradeoff: smaller conceptual surface than Lucide/Phosphor; avoid mixing without reason.

## Motion

### CSS transitions/animations
- Primary for simple state, hover, focus, loading, opacity and transform motion.
- Native, smallest runtime, reduced motion friendly.
- Use when: one element, one state, short duration.

### Web Animations API
- Primary for moderate programmatic motion without a dependency.
- Use when: browser-native playback/timeline control solves the problem.
- Tradeoff: API ergonomics and lifecycle discipline are project responsibility.

### Motion
- Alternative/primary for React/UI coordinated motion, layout and gestures.
- Official: https://motion.dev
- NPM: `motion` 13.1.1, MIT.
- Use when: React UI needs orchestration, layout animation, springs and gesture integration.
- Tradeoff: framework coupling and bundle cost; use CSS/WAAPI when enough.

### GSAP
- ALTERNATIVE/SPECIALIZED for robust timelines, SVG and cinematic sequences.
- Official: https://gsap.com
- NPM: `gsap` 3.15.0; license is the GSAP standard no-charge license, not MIT. Repository https://github.com/greensock/GSAP.git
- Use when: complex coordinated sequences or media motion justify it.
- Avoid when: CSS/WAAPI/Motion is enough. Verify the current license for the exact client/work model.

### Anime.js
- ALTERNATIVE/SPECIALIZED for motion; see existing Frontend Toolbox entry.
- Use for complex timelines, SVG/Canvas/WebGL and programmatic choreography.
- Default: CSS/WAAPI/Motion first.

### View Transitions API
- REFERENCE/SPECIALIZED for page/document transitions where browser support and enhancement strategy are acceptable.
- Never use as required navigation for core product behavior; test accessibility and reduced motion.

## Loaders

### CSS/spinner
- Primary for compact, deterministic and low-overhead loading.

### Skeleton
- Primary for initial page/section loading when structure is known.

### Progress
- Primary for measurable operation duration.

### Optimistic UI
- Primary when action can complete locally and rollback path exists.

### Inline indicator
- Primary for button, filter, row or small operation.

### Branded animation
- SPECIALIZED: project-owned CSS/SVG or a specific branded loader (no canonical `dot-matrix` package exists on npm; community variants such as `dot-anime-react`, `dot-matrix-chart`, `@keyvaluesystems/react-dot-matrix-chart` exist as separate single-maintainer projects — evaluate individually).
- Use only when the operation benefits from product-specific motion and tokens.
- Do not use elaborate loader solely to decorate.
- License/provenance of any third-party branded loader must be confirmed before adoption.

## Drag & Drop

### dnd-kit
- Primary for React sortable, draggable and droppable interactions.
- Official: https://dndkit.com
- NPM: `@dnd-kit/core` 6.3.1, MIT, repository https://github.com/clauderic/dnd-kit.
- Use when: keyboard sensors, touch, sortable lists/kanban and custom rendering matter.
- Tradeoff: accessibility and interaction states need project work.
- Watchout: verify current upstream activity and major-version status before adoption; do not assume the old stable line remains current.

### Pragmatic Drag and Drop
- ALTERNATIVE/SPECIALIZED for performance-focused drag/drop, especially large or complex systems.
- Official: https://atlassian.design/components/pragmatic-drag-and-drop, repository https://github.com/atlassian/pragmatic-drag-and-drop.
- NPM core: `@atlaskit/pragmatic-drag-and-drop` 3.0.0 (Apache-2.0, weekly downloads ~1.26M, updated 2026-08-14). Family of scoped packages under `@atlaskit/pragmatic-drag-and-drop-*` (e.g. `…-hitbox`, `…-auto-scroll`).
- Use when: project evidence justifies a different sensor/model architecture, large data, framework-agnostic target or Atlassian Design System usage.
- Tradeoff: framework-agnostic, but optional adapter packages are scoped `@atlaskit/*` and add bundle weight; evaluate before adoption.

Avoid multiple drag libraries.

## Rich text

### Tiptap
- PRIMARY for extensible headless editor with ProseMirror foundation.
- Official: https://tiptap.dev
- NPM: `@tiptap/react` 3.30.6, MIT, repository https://github.com/ueberdosis/tiptap.
- Use when: common editor with extensions, collaboration and structured content.
- Tradeoff: extension/prose-mirror complexity, sanitization still mandatory.

### Lexical
- ALTERNATIVE/SPECIALIZED for Meta-backed extensible editor and React integration.
- Official: https://lexical.dev
- Use when: structured content, collaboration and lower-level extensibility.
- Tradeoff: API/architecture is more involved.

### ProseMirror
- SPECIALIZED foundation for custom editors.
- Use when: Tiptap/Lexical do not meet the model, or the team is prepared to own editor architecture.

### Slate
- REFERENCE/ALTERNATIVE for React-first structured document models.
- Tradeoff: model/schema decisions are project-owned; not automatically simpler.

## Maps / Geo

### MapLibre GL JS
- PRIMARY for powerful vector maps, styles, WebGL and vector tiles.
- Official: https://maplibre.org
- NPM: `maplibre-gl` 6.6.0, BSD-3-Clause.
- Use when: custom map style, vector tiles, large datasets, routes and advanced layers.
- Tradeoff: WebGL/style complexity, data/tile provider costs.

### Leaflet
- PRIMARY for simple maps, markers and lightweight interactions.
- Official: https://leafletjs.com
- NPM: `leaflet` 1.9.4, BSD-2-Clause.
- Use when: straightforward map with markers, basic layers and small footprint.
- Tradeoff: less suited to high-performance custom WebGL/vector-tile visualization.

### React Leaflet
- ALTERNATIVE when React integration with Leaflet is desired.
- NPM: `@react-leaflet/core` 3.0.0, Hippocratic-2.1, repository https://github.com/PaulLeCam/react-leaflet.git.
- Use when: Leaflet is chosen and the team values React composability.
- Tradeoff: wrapper/dependency surface and Leaflet limitations.

### OpenLayers
- SPECIALIZED for advanced GIS, projections, layers, vector/raster data and geospatial systems.
- Use when: map capability is core product complexity.

### Google Maps ecosystem
- ALTERNATIVE when provider ecosystem, Places, Routes, tiles and enterprise support justify vendor costs.
- Never choose without provider pricing, data policy, licensing and offline requirements.

## Command palette

### cmdk
- PRIMARY for React command palette and command menus.
- Official: https://cmdk.paco.me
- Use when: keyboard command search, groups, empty/loading states and large command sets.
- Pair with Base UI/Radix/Headless UI primitive; do not implement focus/dialog semantics twice.
- Use fuzzy search only when command set justifies it.

## Search

### MiniSearch
- PRIMARY for local/full-text search in small-to-medium datasets.
- Official: https://lucaong.github.io/minisearch/
- NPM: `minisearch` 7.2.0, MIT.
- Use when: browser/local index, fuzzy search and no server requirement.
- Tradeoff: no server ranking/synonyms unless project adds them.

### Fuse.js
- ALTERNATIVE for simple fuzzy matching and small datasets.
- NPM: `fuse.js` 7.5.0, Apache-2.0.
- Use when: fuzzy matching is needed over local objects and simplicity wins.
- Avoid for large datasets or server-side search.

### Server search
- REFERENCE/SPECIALIZED: external search engine only when corpus size, ranking, permissions, analytics or scale justify it.
- Keep API and authorization boundaries out of the UI library choice.
