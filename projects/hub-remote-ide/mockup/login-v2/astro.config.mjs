// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// Dev Maniac's Hub — login build
// Build output vai pra mockup/login-built/ pra ser servido pelo PHP router.
// Astro gera HTML estático + assets JS/CSS com hash.
export default defineConfig({
  integrations: [react()],
  output: 'static',
  outDir: '../login-built',
  publicDir: '../../assets-public',  // reusa assets/brand do mockup
  build: {
    inlineStylesheets: 'auto',
  },
  vite: {
    build: {
      cssCodeSplit: true,
    },
  },
});
