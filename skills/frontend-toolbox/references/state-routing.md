# State, Server State, Routing & Utilities

## Local/shared/global state
- useState/useReducer PRIMARY for local state.
- Scoped React context REFERENCE for small dependency-sharing trees.
- Zustand PRIMARY for small-to-medium shared UI state, MIT, https://zustand.docs.pmnd.rs.
- Redux Toolkit ALTERNATIVE for large global state/devtools/ecosystem, MIT, https://redux-toolkit.js.org.
- Jotai ALTERNATIVE for atomic model, MIT, https://jotai.org.
- XState SPECIALIZED for state machines, MIT, https://xstate.js.org.
- TanStack Store SPECIALIZED/REFERENCE when project already uses TanStack.

Never create a global store for local state. Do not put server state in a global client store without caching semantics.

## Server state
- TanStack Query PRIMARY: caching, mutation, invalidation, optimistic updates, offline, SSR/RSC support, https://tanstack.com/query.
- SWR ALTERNATIVE, https://swr.vercel.app.
- Framework-native mechanisms ALTERNATIVE/REFERENCE when Next.js etc already solve the requirement.

## Routing
- Next.js App Router PRIMARY for Next.js.
- TanStack Router ALTERNATIVE for headless/framework-neutral router, https://tanstack.com/router.
- React Router ALTERNATIVE/REFERENCE for non-Next React apps, https://reactrouter.com.
- Do not replace framework-native routing without a concrete benefit.

## Utilities
- clsx PRIMARY for conditional class strings.
- tailwind-merge PRIMARY for Tailwind class conflict resolution.
- class-variance-authority ALTERNATIVE for typed variants.
- nanoid REFERENCE/ALTERNATIVE for IDs.
- Avoid lodash/whole utility bundles when native APIs solve.
