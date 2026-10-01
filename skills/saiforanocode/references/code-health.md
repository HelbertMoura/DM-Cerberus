# 🩺 Referência: Code Health, Visual Performance & Pitfalls Operacionais

> **Diretriz:** A percepção de qualidade de uma interface é destruída instantaneamente se ela travar na rolagem, demorar a responder ao clique ou provocar pulos de layout durante o carregamento.

---

## 1. Métricas de Performance Visual (Core Web Vitals)

| Métrica | Meta Operacional | Causa Raiz de Falha | Prevenção na Arquitetura |
| :--- | :--- | :--- | :--- |
| **LCP** (*Largest Contentful Paint*) | **< 2.0s** (Bom: < 1.2s) | Imagens pesadas no hero, fontes customizadas blocantes, scripts no `<head>` | Imagem do hero com `priority` / `fetchpriority="high"`, fontes pré-carregadas via `next/font` ou CDN local. |
| **CLS** (*Cumulative Layout Shift*) | **< 0.05** (Alvo: 0.0) | Banners dinâmicos sem espaço reservado, imagens sem `aspect-ratio`, fontes mudando tamanho | Espaço reservado para skeletons e anúncios, dimensões explícitas em todas as tags `<img>` e `<video>`. |
| **INP** (*Interaction to Next Paint*) | **< 150ms** (Bom: < 100ms) | Handlers de clique pesados, loops síncronos na main thread, re-renders em cascata | Handlers assíncronos, `useTransition` para filtragens grandes, virtualização de listas. |

---

## 2. Renderização a 60 FPS & Aceleração por GPU

### 2.1 Propriedades Seguras para Animação
Animações e transições CSS devem utilizar **apenas** propriedades compostas diretamente pela GPU:
- ✅ **Permitido:** `transform` (`translate3d`, `scale`, `rotate`) e `opacity`.
- ❌ **Proibido para transição:** `top`, `bottom`, `left`, `right`, `width`, `height`, `margin`, `padding`, `border-width`. Estas propriedades disparam **Reflow / Layout Shift** completo e travam o motor de renderização.

```css
/* Correto (GPU / 60 FPS) */
.drawer {
  transform: translateX(-100%);
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1);
}
.drawer.open {
  transform: translateX(0);
}

/* Errado (CPU / Queda de Quadros) */
.drawer-slow {
  left: -400px;
  transition: left 200ms;
}
```

### 2.2 Limite Rígido de Filtros e `backdrop-blur`
- O efeito `backdrop-filter: blur(...)` recalcula pixels translúcidos a cada quadro de scroll.
- **Regra:** Limite `backdrop-blur` a cabeçalhos fixos pequenos ou modais pontuais. **NUNCA** aplique blur translúcido em tabelas longas, cards repetidos em grid ou áreas extensas com scroll ativo. Provoca throttling térmico imediato em notebooks e smartphones.

---

## 3. Higiene de DOM & Virtualização de Dados

- **Limite de Nós no DOM:** Mantenha o DOM total abaixo de **1.500 elementos**.
- **Virtualização Mandatória:** Qualquer tabela, histórico de logs, feed de mensagens ou lista que possa renderizar **mais de 100 itens simultâneos** DEVE implementar virtualização com `@tanstack/react-virtual` ou similar.
- **Bundle Tree-Shaking:** Evite importações de barrel files gigantes. Prefira imports específicos ou garanta que o bundler (Vite, Next.js, Turbopack) faça tree-shaking correto de bibliotecas de ícones.

---

## 4. Tipografia & Prevenção de FOUT / FOIT

- Utilize sempre `font-display: swap` para garantir que o texto seja legível imediatamente com fonte de sistema enquanto a webfont é baixada.
- No Next.js, utilize o pacote `next/font` que hospeda as fontes localmente e injeta CSS inline com ajuste automático de métricas (`size-adjust`) para zerar o CLS.

---

## 5. Otimização de Imagens & Mídia

- **Formatos Modernos:** Servir imagens em **WebP** ou **AVIF** como padrão. Reservar PNG apenas para gráficos com transparência estrita e SVG para logotipos/ícones vetoriais.
- **Dimensões Explícitas:** Declare sempre `width` e `height` (ou `aspect-ratio` no CSS) para eliminar completamente o CLS.
- **Lazy Loading Nativo:** Utilize `loading="lazy"` para todas as imagens abaixo da dobra. No hero section (LCP), use `loading="eager"` e `fetchpriority="high"`.

---

## 6. Pitfalls Operacionais Descobertos em Produção

1. **Next.js Export vs Servidores Estáticos:**
   - Ao rodar `next build` com output estático (`output: 'export'`), rotas dinâmicas geram diretórios `/rota/index.html`. Servidores simples (como `python -m http.server`) podem falhar ao resolver URLs sem `.html`.
   - **Solução:** No nginx ou Cloudflare Pages, configure regras limpas de URL (*trailing slash* consistente e *clean URLs*).
2. **Container Rebuild vs Docker Restart:**
   - Em deploys com Docker, executar apenas `docker restart <container>` **NÃO** atualiza código estático compilado nem arquivos modificados em build-time.
   - **Solução:** O deploy exige `docker compose build <service> && docker compose up -d <service>`.
3. **Cache Invalidation:**
   - Ativos com cache longo (1 ano) em CDN devem utilizar hashes de conteúdo nos nomes dos arquivos (ex: `app.3a8f9c.js`).
