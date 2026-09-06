# ⚡ UI Pattern: Interaction, States & Motion

## 1. Pattern: State Feedback (Empty, Loading, Error, Success)
- **USE WHEN:** Todo componente assíncrono ou tela com busca/dados dinâmicos.
- **AVOID WHEN:** Transições instantâneas síncronas (<50ms).
- **UX:**
  - **Empty State:** Nunca deixar um vazio frio; explicar o motivo e oferecer ação clara (ex: *"Nenhuma medição encontrada. Cadastre a primeira medição"* + botão CTA).
  - **Loading State:** Preferir Skeleton com as dimensões reais do conteúdo em vez de spinners genéricos centralizados.
  - **Error State:** Explicar o que houve e fornecer caminho de recuperação (ex: botão *"Tentar novamente"*).
  - **Success State:** Toast discreto com fechamento automático (Sonner) ou indicador verde sem modal intrusivo.
- **A11Y:** Regiões de anúncio de estado via `aria-live="polite"`.
- **MOBILE:** Manter CTAs em área de alcance confortável.
- **DESKTOP:** Alinhado ao fluxo natural de leitura.
- **REFERENCES:** Sonner, Radix primitives.

---

## 2. Pattern: Purposeful Functional Motion
- **USE WHEN:** Comunicar mudança de estado, continuidade espacial (ex: expansão de acordeão, troca de abas) ou hierarquia.
- **AVOID WHEN:** Animações puramente decorativas que atrasam a interação do usuário (ex: elementos quicando ou demorando 1s para aparecer).
- **UX:** Curvas de aceleração naturais (ease-out), duração curta (150ms a 250ms). A interface deve parecer rápida e responsiva.
- **A11Y:** Respeitar impreterivelmente `@media (prefers-reduced-motion: reduce)`. Em modo reduzido, desativar transformações e usar crossfade instantâneo de opacidade.
- **MOBILE:** Reduzir motion para economizar bateria e evitar tontura visual em telas pequenas.
- **DESKTOP:** Microinterações refinadas no hover e foco ativo.
- **REFERENCES:** Motion (Framer Motion moderno), Web Animations API (WAAPI).
