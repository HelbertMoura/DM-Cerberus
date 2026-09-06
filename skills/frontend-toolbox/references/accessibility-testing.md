# Accessibility, Visual Testing & Performance

## Accessibility stack
- axe-core engine and @axe-core/playwright PRIMARY automated scan, official https://github.com/dequelabs/axe-core and https://playwright.dev/docs/accessibility-testing.
- Lighthouse accessibility ALTERNATIVE/REFERENCE for performance/accessibility signals, https://developer.chrome.com/docs/lighthouse.
- Accessibility Insights SPECIALIZED/REFERENCE for assisted/manual workflows, https://accessibilityinsights.io/.
- Playwright semantic/inspection/dom and keyboard tests PRIMARY.

Zero automated findings does not equal WCAG compliance. Required layers: automated + semantic + keyboard + visual + human reasoning.

## Visual testing
- Playwright screenshots PRIMARY local.
- Storybook visual tests ALTERNATIVE for component-level visual isolation.
- Chromatic SPECIALIZED managed SaaS, https://www.chromatic.com.
- Percy SPECIALIZED managed SaaS, https://percy.io.
Use local Playwright until collaboration/hosted CI requirements justify SaaS.

## Component development
- Storybook PRIMARY for React component work, official https://storybook.js.org.
- Ladle REFERENCE/ALTERNATIVE, https://ladle.js.org.
- Histoire REFERENCE for Vue, https://histoire.dev.
Use framework-native alternatives when project does not use React.

## Performance
- Lighthouse PRIMARY local audit.
- WebPageTest REFERENCE/SPECIALIZED controlled testing, https://www.webpagetest.org.
- React DevTools/Profiler PRIMARY React profiling.
- Next.js bundle analyzer and framework analyzers ALTERNATIVE.
- Chrome DevTools Performance, Network, Rendering and Lighthouse tooling PRIMARY.

Measure LCP, INP, CLS, JS/CSS cost, long tasks, hydration, network, images/fonts and real device/mobile. Never treat one score as universal.

## Runtime gaps in automated a11y scans

axe-core is the primary scanner, but it does NOT catch two classes of
regression that are common in real production frontends. Add explicit
checks for both, otherwise the gate will pass with hidden defects.

### 1. Horizontal overflow on small viewports

axe-core inspects per-element contrast, ARIA, semantics, etc. It does
NOT flag elements whose bounding box exceeds the viewport, so a hero
`bg-cover` extending 7px past the right edge will pass axe silently.

Pattern (paste into the same Playwright page after axe):

```js
const overflow = await page.evaluate(() => {
  const docW = document.documentElement.clientWidth;
  const out = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.right > docW + 0.5 || r.left < -0.5) {
      out.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className || '').toString().slice(0, 100),
        left: Math.round(r.left), right: Math.round(r.right),
        width: Math.round(r.width),
        text: (el.textContent || '').slice(0, 60),
      });
    }
  }
  return { docW, count: out.length, samples: out.slice(0, 25) };
});
```

Common culprits: hero `bg-cover` inside an aside, footer `flex-none`
containers, untruncated brand links. Always include 360 in the viewport
matrix when the project targets mobile.

### 2. Modals/version-guards masking the real route

If the app has a VersionGuard, onboarding wizard, or release dialog that
gates the real route, the first screenshot may capture only the modal
and axe will scan only the modal — both will look fine while the real
page underneath is broken.

Always:
1. `grep -nE "CURRENT_RELEASE|versionKey|VERSION_KEY" src/` to find the
   literal version constant. Do not guess.
2. Pre-seed localStorage via `page.addInitScript` BEFORE `page.goto`:
   ```js
   await page.addInitScript((ver) => {
     try { localStorage.setItem('dm_erp_app_version', ver); } catch {}
   }, '<literal-from-source>');
   ```
3. Verify the screenshot is the real route, not the modal. If the modal
   appears, you forgot step 1 or used the wrong sentinel name.
