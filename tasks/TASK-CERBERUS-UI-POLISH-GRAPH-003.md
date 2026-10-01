# 📋 TASK-CERBERUS-UI-POLISH-GRAPH-003
> **Refinamento Estético HelpDesk, Correção de Busca Vazia & Grafo de Topologia em Alta Resolução (HiDPI 3D)**
> Repositório: `C:\DevManiacs\DM-Cerebro`

---

## 🎯 1. Objetivos

1. **Correção do Bug de Busca Vazia (400 Bad Request):**
   - No backend `_serve_search`: se `q` for vazio `""`, retornar HTTP 200 com `{"query": "", "count": 0, "results": []}` em vez de `400 Bad Request`.
   - No frontend `runSearch()`: se `q` estiver vazio ao iniciar a página, exibir o empty state de boas-vindas com atalhos de busca rápida, sem disparar erro na tela.

2. **Reconstrução do Grafo de Topologia em Alta Resolução (HiDPI / Retina):**
   - Suporte a `window.devicePixelRatio` (multiplicar `canvas.width/height` por `dpr` e aplicar `ctx.scale(dpr, dpr)` para eliminar qualquer pixelização/blur).
   - Renderização visual premium de rede neural / constelação 3D:
     * Fundo em gradiente radial escuro (`#061637` a `#0a192f`).
     * Nós esféricos com gradientes e brilho (`shadowBlur`, `shadowColor`), anéis de órbita sutis.
     * Conexões neurais com pulsos de energia (`#08b9ca`, `#38bdf8`) fluindo em tempo real.
     * Tipografia nítida em `Space Grotesk` com labels legíveis.
     * Interatividade: arrastar para rotacionar com inércia, scroll para zoom (in/out) e hover em nós para destacar conexões.

3. **Polimento Visual & Cores Idênticas ao HelpDesk (suporte.devmaniacs.com.br):**
   - Cores exatas: Fundo Deep Navy (`#061637`), Surface (`#0A192F`), Cards (`#0D2247`), Borda nítida (`#1E3A6D`), Acentos Cyan (`#08B9CA`), Coral (`#FF4C4C`), Yellow (`#FFC529`).
   - Header e abas com navegação premium, botões com hover responsivo, tipografia com pesos balanceados (`Space Grotesk` nos títulos, `Inter` nos textos).
   - Cards de busca e inbox com espaçamento harmonioso, tags bem contrastadas e visual limpo.

4. **Validação:**
   - Todos os 217+ testes unitários e de UI devem continuar 100% PASS (`python -m unittest discover tests`).
   - Compilação Node.js limpa, zero syntax warnings.
