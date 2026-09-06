# 🩺 Referência: Code Health, Performance & Pitfalls Operacionais

Diretrizes práticas para manter alta velocidade de carregamento, tracking confiável e evitar erros descobertos em ambientes reais de produção.

---

## 1. Otimização de Imagens & Mídia

- **Formatos Modernos:** Servir imagens em **WebP** ou **AVIF** como padrão. Reservar PNG apenas para gráficos com transparência estrita e SVG para logotipos/ícones.
- **Dimensões Explícitas:** Declare sempre `width` e `height` (ou `aspect-ratio` no CSS) para eliminar completamente o *Cumulative Layout Shift* (CLS).
- **Lazy Loading Nativo:** Utilize `loading="lazy"` para todas as imagens abaixo do hero fold. No hero section (LCP), use `loading="eager"` e `fetchpriority="high"`.
- **Uso de `<picture>`:** Forneça variantes com resoluções responsivas para economizar dados em mobile.

---

## 2. Tracking, Analytics & Consentimento

- **Tags Assíncronas:** Carregue scripts de métricas (Google Analytics, Clarity, Meta Pixel) com `defer` ou via gerenciador de tags para não bloquear a renderização inicial da página.
- **Conformidade LGPD:** Respeite o consentimento do usuário. Não dispare rastreamentos invasivos antes da interação do cookie consent quando aplicável.

---

## 3. Pitfalls Operacionais Descobertos em Produção

1. **Next.js Export vs Servidores Estáticos:**
   - Ao rodar `next build` com output estático (`output: 'export'`), rotas dinâmicas geram diretórios `/rota/index.html`. Servidores simples (como `python -m http.server`) podem falhar ao resolver URLs sem `.html`.
   - **Solução:** No nginx ou Cloudflare Pages, configure regras limpas de URL (*trailing slash* consistente e *clean URLs*).
2. **Container Rebuild vs Docker Restart:**
   - Em deploys com Docker, executar apenas `docker restart <container>` **NÃO** atualiza código estático compilado nem arquivos modificados em build-time.
   - **Solução:** O deploy exige `docker compose build <service> && docker compose up -d <service>`.
3. **Cache Invalidation:**
   - Ativos com cache longo (1 ano) em CDN devem utilizar hashes de conteúdo nos nomes dos arquivos (ex: `app.3a8f9c.js`).
