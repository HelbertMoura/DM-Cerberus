# Tables, Virtualization, Charts, Forms & Validation

## Tables

### TanStack Table
- PRIMARY for interactive React tables with custom rendering, sorting, filtering, selection, editing and virtualization.
- Official: https://tanstack.com/table
- NPM: `@tanstack/react-table` 9.2.4, MIT.
- Use when: existing project already uses TanStack conventions or needs headless table primitives.
- Tradeoff: headless; must build cells, styling, keyboard, selection, virtualization and accessibility.

### AG Grid
- SPECIALIZED/PRIMARY for enterprise grids, large datasets, advanced interactions and commercial support.
- Official: https://www.ag-grid.com
- NPM: `ag-grid-react` 36.1.0, MIT; check commercial licensing and feature requirements before enterprise adoption.
- Use when: server-side row model, pivot, aggregation, grouping, editing, export and high-scale grids are real requirements.
- Tradeoff: heavier dependency and distinct feature/licensing model.

### MUI X Data Grid
- ALTERNATIVE/SPECIALIZED for MUI projects needing advanced grids.
- Official: https://mui.com/x/react-data-grid
- Tradeoff: MUI coupling and larger runtime.

### PrimeReact DataTable
- REFERENCE/ALTERNATIVE for PrimeReact environments; check current licensing, package identity and maintenance.
- Tradeoff: component-system lock-in and less compelling for projects without PrimeReact.

## Virtualization

### TanStack Virtual
- PRIMARY for modern virtualized lists and tables.
- Official: https://tanstack.com/virtual
- NPM: `@tanstack/react-virtual` 3.14.10, MIT.
- Use when: large lists/feeds/tables; pair with TanStack Table when rows need table semantics.
- Tradeoff: implementation responsibility remains with project.

### react-window
- ALTERNATIVE for lightweight simple lists/grids.
- Official: https://github.com/instructure/react-window
- Use when: simple virtualization and minimal API are preferred.
- Tradeoff: less current product surface/less suitable for complex dynamic layouts.

## Charts

### Recharts
- PRIMARY for simple-to-medium business charts in React.
- Official: https://recharts.org
- NPM: `recharts` 3.10.1, MIT.
- Use when: common business charts, React composition, small/medium datasets.
- Tradeoff: not ideal for extreme real-time/high-density or highly custom visualization.

### ECharts
- PRIMARY/SPECIALIZED for large datasets, high performance, real-time, maps and advanced chart types.
- Official: https://echarts.apache.org
- NPM: `echarts` 6.1.0, Apache-2.0, repository https://github.com/apache/echarts.git
- Use when: high-volume telemetry, finance, operational dashboards and rich interactions.
- Tradeoff: integration discipline, bundle tuning, theming and accessibility need testing.

### Bklit UI
- PRIMARY design-system-oriented charts/components candidate.
- Official: https://github.com/bklit/bklit-ui
- License: MIT.
- Use when: React/shadcn project needs a registry source of chart primitives.
- Tradeoff: D3/VISX/motion dependency surface; validate large datasets, keyboard, legends and mobile.

### Visx
- SPECIALIZED for low-level/custom visual analytics.
- Official: https://airbnb.io/visx
- NPM: `@visx/shape` 4.0.0, MIT.
- Use when: custom chart composition and direct SVG/D3 control.
- Tradeoff: higher engineering cost.

### D3
- SPECIALIZED/REFERENCE for bespoke data visualization.
- Official: https://d3js.org
- NPM: `d3` 7.9.0, ISC, repository https://github.com/d3/d3
- Use when: visualization itself is a product capability and team can own the data-visual grammar.
- Tradeoff: substantial accessibility, testing, theming and performance responsibility.

### Nivo
- REFERENCE/ALTERNATIVE for React chart composition.
- NPM: `@nivo/line` 0.99.0, MIT.
- Tradeoff: maintainers/activity must be rechecked; not primary until project fit proven.

### Tremor
- REFERENCE/ALTERNATIVE for dashboard primitives built on Recharts.
- Tradeoff: styling and chart abstraction can obscure operational semantics; verify current source/repo before adoption.

### Chart.js
- ALTERNATIVE for canvas-based charts and a mature general API.
- Official: https://www.chartjs.org
- NPM: `chart.js` 4.5.1, MIT.
- Use when: canvas charts and broad chart types are needed.
- Tradeoff: React composition/accessibility require project wrappers.

## Forms

### React Hook Form
- PRIMARY for performant controlled form state.
- Official: https://react-hook-form.com
- NPM: 7.87.0, MIT.
- Use when: forms need field arrays, validation integration, async behavior and low rerender cost.
- Tradeoff: accessibility semantics and error UX still need explicit design.

### TanStack Form
- ALTERNATIVE/PRIMARY for framework-agnostic/headless form state, especially larger typed forms.
- Official: https://tanstack.com/form
- NPM: `@tanstack/react-form` 1.33.5, MIT.
- Use when: complex forms, field arrays, server actions and framework portability matter.
- Tradeoff: newer API and less universal adoption than RHF.

### Formik
- REFERENCE ONLY unless a project already standardizes on it.
- Tradeoff: older patterns, larger rerender/architectural concerns and less compelling defaults for new projects.

## Schema and validation

### Zod
- PRIMARY for shared TypeScript schemas, parsing and server/client validation.
- NPM: `zod` 4.5.4, MIT.
- Use when: one schema should cross API, forms and server boundaries.
- Tradeoff: parse cost must be measured; do not over-parse trivial fields.

### Valibot
- ALTERNATIVE for smaller bundle-focused validation.
- Official: https://valibot.dev
- Use when: bundle budget and composable schema API justify it.
- Tradeoff: team familiarity and ecosystem fit must be checked.

### ArkType
- ALTERNATIVE/SPECIALIZED for performant typed validation.
- Official: https://arktype.io
- Tradeoff: smaller adoption and different API semantics; benchmark and audit target project.

### Yup
- REFERENCE/ALTERNATIVE for established object schema validation.
- Tradeoff: no default reason to choose over Zod/Valibot for new architecture.

## Decision rules

- Simple table: native/semantic table or project component system.
- Interactive headless table: TanStack Table.
- Enterprise/large data grid: AG Grid, with license and accessibility review.
- Simple business chart: Recharts.
- Large/real-time operational chart: ECharts or Bklit UI after benchmarks.
- Complex form: TanStack Form or RHF; choose by existing project and API semantics.
- Shared schema boundary: Zod primary.
