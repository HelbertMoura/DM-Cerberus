# Images, Creative, Mobile, Tokens, Styling, i18n & Security

## Images/media
- Native picture/img, srcset, sizes, lazy loading and AVIF/WebP PRIMARY.
- Framework image optimization ALTERNATIVE.
- CDN provider SPECIALIZED for transformations/storage. Check cost, privacy and provider lock-in.
Video: native video, lazy load, captions, poster and formats first; avoid heavyweight players unless needed.

## Canvas/WebGL/creative
- p5.js/shader existing local capabilities.
- Konva/Pixi SPECIALIZED for 2D canvas interactions.
- Fabric.js REFERENCE/SPECIALIZED canvas editor.
- Three.js/React Three Fiber SPECIALIZED for 3D.
Do not use WebGL for common UI.

## Mobile/cross-platform
- Reanimated PRIMARY for React Native animations, https://docs.swmansion.com/react-native-reanimated/.
- Gesture Handler PRIMARY for touch/gesture, https://docs.swmansion.com/react-native-gesture-handler/.
- NativeWind ALTERNATIVE, https://www.nativewind.dev.
- Expo Router PRIMARY for Expo navigation, https://docs.expo.dev/router/introduction.
Uilora stays REFERENCE ONLY until public provenance is verified.

## Design tokens
- CSS variables + DESIGN.md PRIMARY; tokens are executable representation of intent.
- Style Dictionary SPECIALIZED for multi-platform token transforms, https://styledictionary.com, Apache-2.0.
- Tokens Studio ecosystem REFERENCE/ALTERNATIVE, verify licensing/tooling.
- Tailwind tokens REFERENCE/ALTERNATIVE when Tailwind is project style.

## Styling
- Native CSS PRIMARY.
- CSS Modules PRIMARY for component-scoped local styles.
- Tailwind PRIMARY for utility-first teams.
- Panda CSS ALTERNATIVE, https://panda-css.com.
- vanilla-extract REFERENCE/ALTERNATIVE, official https://vanilla-extract.style; npm package name was not verified in the registry query.
- CSS-in-JS AVOID by default unless project has a measured reason.

## i18n
- Framework-native/next-intl PRIMARY for Next.js, https://next-intl.dev.
- react-i18next ALTERNATIVE, https://react.i18next.com.
- FormatJS ALTERNATIVE, https://formatjs.github.io.
Require locale formatting, pluralization, RTL, SSR/RSC and translation loading.

## Security catalog
- XSS: prefer text APIs, escape by context, avoid dangerouslySetInnerHTML.
- DOMPurify SPECIALIZED only when accepting untrusted HTML, https://github.com/cure53/DOMPurify, MPL-2.0 OR Apache-2.0.
- isomorphic-dompurify REFERENCE/ALTERNATIVE; do not assume isomorphic means safe; validate server trust boundary.
- CSP/Trusted Types, CSRF controls, upload validation, auth/token handling, secrets, CORS, clickjacking and open redirects remain project/security review topics.
- Dependency audit and lockfile integrity are required for adoption.
- Active pentest remains explicit-only and never automatic frontend QA.
