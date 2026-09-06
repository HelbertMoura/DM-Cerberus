# AI UI, ERP/Dashboard & Premium Visual References

## AI UI
- Project-native streaming transport + state machine PRIMARY.
- Markdown renderer/library only when untrusted markdown or rich content requires it; sanitize and test links/headings/code.
- Code blocks with copy, language label, loading/error/retry and accessible status.
- Chat UI: semantic live region, focus management, stop/retry/edit, message roles, streaming error recovery and no generic AI glow.
- Generative UI: never trust generated visual claims; Hermes/Design Critic/Playwright remain authority.

## ERP/CRM/Admin/Operations
Recommended stack:
- Next.js/RSC routing + existing component system.
- TanStack Query for server data.
- TanStack Table + TanStack Virtual for interactive/large tables.
- React Hook Form or TanStack Form + Zod.
- Recharts for common charts; ECharts for scale; Bklit UI for design-system-oriented dashboard charts.
- Base UI/Radix/React Aria for overlay/modal/menu behavior.
- Lucide/one icon family.
- Sonner for transient notifications.
- date-fns + Intl for dates.
- Playwright + axe + keyboard + visual QA.
- cmdk only for command-heavy surfaces.
- AG Grid only when real enterprise features justify it.

Priorities: data density, scan speed, keyboard, predictable interactions, responsive collapse, empty/error states, high performance, large datasets, operational clarity. Do not turn ERP into a generic SaaS landing page.

## Premium visual references, libraries & specialized tools
- **Open Design + DESIGN.md:** PRIMARY source for bespoke project direction.
- **Refero Styles (https://styles.refero.design/):** REFERENCE ONLY. Use for UI/UX research, real product palettes, typography, spacing and layout inspiration. Rule: *Inspiração ➔ Análise ➔ Extração do Princípio ➔ Adaptação ao DESIGN.md próprio*. Never blind copy.
- **Cult UI (https://cult-ui.com/):** OPTIONAL LIBRARY. Use on demand for rich/interactive components, special micro-interactions, or landing pages. Do not install the full library for simple buttons. Verify accessibility and bundle impact before adopting.
- **Shader Gradient (https://shadergradient.co/):** SPECIALIZED VISUAL TOOL. Use for 3D fluid gradients and bespoke hero sections when visually justified. Always provide static fallback and respect `@media (prefers-reduced-motion: reduce)`.
- **Manus:** EXPERIMENTAL EXTERNAL REFERENCE ONLY. Do NOT incorporate into the core agent architecture. The existing Maestro/Cerberus/Worker stack is self-sufficient.
- **Bklit UI:** REFERENCE/production candidate for charts/components.
- **Aceternity/MagicUI:** REFERENCE ONLY until project-specific provenance and license are verified.
- **Any premium component MUST be adapted to project tokens, typography, color, radius, spacing, motion, density and accessibility.**

## Reject
- Visual-only components with broken keyboard/focus/ARIA.
- Generic AI aesthetic (purple glow, excessive glassmorphism, gratuitous bento grids, identical floating cards).
- Libraries with unresolved package identity, typosquatting risk, unclear license, unknown scripts, or unmaintained dependency tree.
- Redundant libraries that solve the same problem without a concrete advantage.
