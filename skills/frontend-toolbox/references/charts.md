# Charts & Data Visualization

## Routing
- Simple business chart: Recharts.
- Dashboard design-system chart: Bklit UI.
- Large/real-time/operational data: ECharts.
- Highly custom SVG visualization: Visx or D3.
- Canvas general charts: Chart.js.

## Candidates
- Recharts PRIMARY: React composition, common business charts, MIT. Official https://recharts.org; NPM 3.10.1.
- ECharts SPECIALIZED/PRIMARY for scale: Apache-2.0, official https://echarts.apache.org, NPM 6.1.0. Benchmark bundle and test real-time/update load.
- Bklit UI USE WHEN APPROPRIATE: React/shadcn charts, MIT, official https://github.com/bklit/bklit-ui, docs https://ui.bklit.com/docs. Verify D3/VISX/motion footprint and accessibility.
- Visx SPECIALIZED: low-level custom SVG, MIT, https://airbnb.io/visx.
- D3 SPECIALIZED/REFERENCE: bespoke data grammar, ISC, https://d3js.org. High engineering cost.
- Chart.js ALTERNATIVE: canvas charts, MIT, https://www.chartjs.org.
- Tremor REFERENCE/ALTERNATIVE: dashboard abstraction over charts; check provenance/current maintenance before adoption.

## Requirements
Every chart must pass legibility, keyboard/focus, tooltip, legend, empty/loading/error, responsive, theming, performance and mobile tests. Do not select by aesthetics alone.
