# UI Primitives & Component Systems

## Routing

- Headless primitives are preferred when identity and interaction must remain under project control.
- Copy-paste systems are useful when the project already has tokens, variants and governance.
- Styled systems are useful when speed and enterprise consistency outweigh custom visual identity.
- Avoid selecting a visual system before reading DESIGN.md and package.json.

## UI primitives

### Base UI
- Primary candidate for accessible headless behavior with broad React support.
- Official: https://base-ui.com
- NPM: `@base-ui/react` 1.7.0, MIT, repository https://github.com/mui/base-ui.git
- Use when: robust primitives without owning project styling.
- Tradeoff: newer surface area; validate project fit and migration.

### Radix UI
- Alternative for mature accessible dialogs, menus, popovers, tabs and other primitives.
- Official: https://radix-ui.com/primitives
- NPM: `@radix-ui/react-dialog` 1.1.23, MIT, repository https://github.com/radix-ui/primitives.git
- Use when: mature coverage and composition are more important than Base UI alignment.
- Tradeoff: package-per-primitive dependency surface; use selective imports.

### React Aria
- Specialized accessibility-heavy option for complex widgets, collections, focus, keyboard and i18n.
- Official: https://react-spectrum.adobe.com/react-aria/
- NPM: `react-aria` 3.51.0, Apache-2.0, repository https://github.com/adobe/react-spectrum.git
- Use when: accessibility is a primary requirement, especially complex widgets and i18n.
- Tradeoff: larger conceptual/API surface; styling remains separate.

### Ark UI
- Alternative/headless collection with composability and design-system ownership.
- Official: https://ark-ui.com
- NPM: `@ark-ui/react` 5.39.1, MIT, repository https://github.com/chakra-ui/ark.git
- Use when: headless behavior with strong composition.
- Tradeoff: smaller adoption than Radix/Base UI; verify compatibility.

### Headless UI
- Reference/alternative for Tailwind-adjacent teams.
- Official: https://headlessui.com
- NPM: `@headlessui/react` 2.2.10, MIT, repository https://github.com/tailwindlabs/headlessui.git
- Use when: project is already Tailwind and wants a small curated primitive surface.
- Tradeoff: less general coverage than Radix/React Aria; do not mix blindly.

## Component systems

### shadcn/ui
- Primary for copy-paste React components owned by the project.
- Official: https://ui.shadcn.com
- Licensing: inspect each component/registry item; generated examples are not automatically production code.
- Use when: project needs local source, tokens and governance.
- Tradeoff: quality depends on local integration.

### Mantine
- Alternative/styled system with strong TypeScript/DX and accessible components.
- Official: https://mantine.dev
- Use when: integrated React components and speed matter.
- Tradeoff: visual identity follows Mantine; customize tokens/components.

### HeroUI
- Alternative/styled modern system; validate current version/repo before adoption.
- Use when: modern styled components and a distinct visual baseline are acceptable.
- Tradeoff: identity and migration coupling; check licensing and maintenance.
- For mobile, evaluate actual React Native support; do not assume full web/native parity.

### MUI
- Alternative for mature enterprise/styled React UI and large ecosystem.
- Official: https://mui.com
- Use when: enterprise component coverage and MUI conventions justify the runtime.
- Tradeoff: larger bundle/runtime and stronger visual defaults.

### Chakra UI
- Alternative/REFERENCE for accessible styled components and token-oriented development.
- Tradeoff: styled API, version coupling and visual language.

### Ant Design
- Specialized for enterprise tables/forms/admin surfaces.
- Tradeoff: high CSS/dependency footprint and Ant visual identity.

## Rules

- Do not add a styled system merely to solve one missing primitive.
- Do not import multiple primitive families for overlapping widgets.
- Do not let a component library determine the product identity.
- Validate SSR/RSC, keyboard, touch, contrast, focus, responsive behavior and bundle before adoption.
