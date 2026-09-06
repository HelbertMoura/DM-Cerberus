# Forms, Validation & Schemas

## Forms
- React Hook Form PRIMARY: performant form state, broad adoption, official https://react-hook-form.com, NPM 7.87.0 MIT.
- TanStack Form ALTERNATIVE/SPECIALIZED: headless typed form state, official https://tanstack.com/form, NPM @tanstack/react-form 1.33.5 MIT.
- Formik REFERENCE ONLY unless existing project standardizes it.

Separate simple HTML constraint form from complex dynamic/async/server-action form. Test field arrays, validation errors, focus, accessible names, pending, success and rollback.

## Schema
- Zod PRIMARY: shared TypeScript schemas across API/forms, NPM 4.5.4 MIT.
- Valibot ALTERNATIVE: bundle-focused composable validation; verify team ecosystem.
- ArkType ALTERNATIVE/SPECIALIZED: benchmark typed validation; verify maintenance/fit.
- Yup REFERENCE/ALTERNATIVE: established schema validation; not default for new stack.

Security: validation is not authorization, sanitization, upload scanning or secret management. Server-side validation remains mandatory.
