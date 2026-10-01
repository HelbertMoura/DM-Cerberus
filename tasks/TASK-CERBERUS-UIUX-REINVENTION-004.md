# TASK-CERBERUS-UIUX-REINVENTION-004

> **Cerberus Inspector — reinvenção completa como Command Workbench Sólido Industrial**  
> Repositório: `C:\DevManiacs\DM-Cerebro` · PO: Helbert Moura  
> Executor: MiniMax M3 · Risco 2 · Estado: READY FOR IMPLEMENTATION · 31/08/2026

## 1. Objetivo e decisão visual

Reformular integralmente as cinco abas como ferramenta operacional corporativa, densa e ergonômica. A direção escolhida é **Command Workbench**: shell compacto, navegação persistente, áreas mestre/detalhe e controles contextuais. Foi preferida a um dashboard de cards (fragmentado) e a um console técnico (hostil à leitura).

A assinatura será o **Evidence Rail**, faixa discreta com estado real do cluster, índice, escopo e última sincronização. Conteúdo precede decoração; bordas de 1 px criam hierarquia; cor comunica ação/estado; há um CTA primário por contexto.

Resultado obrigatório: zero neon, roxo, violeta, gradiente ornamental, glow, glassmorphism, transparência decorativa, partículas ou animação ambiente.

## 2. Escopo e restrições

**Pode modificar:** `engine/server.py`, `tests/test_ui_hardening.py` e, somente se necessário ao contrato, `tests/test_server_api.py`. Templates auxiliares são permitidos se reduzirem materialmente o `UI_HTML`, sem framework/build.

**Não pode:** alterar `engine/auth.py`, banco, migrations ou payloads; adicionar React/Vue/Tailwind/Bootstrap/CDN; enfraquecer auth/sessão/rate limit; tocar arquivos concorrentes; commit/push/deploy sem PO.

## 3. Tokens CSS canônicos

Hex literais fora de `:root` são proibidos, exceto mapa JS do Canvas que replique os tokens.

```css
:root {
  color-scheme: dark;
  --bg-canvas:#0B0F19; --bg-shell:#0F172A;
  --bg-panel:#131B2E; --bg-elevated:#1E293B;
  --bg-input:#0B1220; --bg-hover:#192338; --bg-selected:#172554;
  --border-subtle:#27354F; --border-default:#334155; --border-strong:#475569;
  --text-primary:#F8FAFC; --text-secondary:#CBD5E1;
  --text-muted:#94A3B8; --text-disabled:#64748B; --text-inverse:#FFFFFF;
  --action:#2563EB; --action-hover:#1D4ED8; --action-pressed:#1E40AF;
  --action-soft:#172554; --warning:#D97706; --warning-soft:#451A03;
  --success:#059669; --success-soft:#052E2B;
  --danger:#DC2626; --danger-hover:#B91C1C; --danger-soft:#450A0A;
  --focus:#60A5FA; --focus-ring:0 0 0 3px #0B0F19,0 0 0 5px #60A5FA;
  --font-display:"Space Grotesk","Inter",system-ui,sans-serif;
  --font-body:"Inter",system-ui,-apple-system,sans-serif;
  --font-mono:"IBM Plex Mono","SFMono-Regular",Consolas,monospace;
  --text-2xs:.6875rem; --text-xs:.75rem; --text-sm:.8125rem;
  --text-md:.875rem; --text-lg:1rem; --text-xl:1.25rem; --text-2xl:1.5rem;
  --space-1:.25rem; --space-2:.5rem; --space-3:.75rem; --space-4:1rem;
  --space-5:1.25rem; --space-6:1.5rem; --space-8:2rem; --space-10:2.5rem;
  --radius-sm:4px; --radius-md:6px; --radius-lg:8px;
  --control-height:44px; --header-height:64px; --tabs-height:48px;
  --content-max:1600px; --duration-fast:120ms; --duration-normal:180ms;
  --ease-standard:cubic-bezier(.2,0,0,1);
}
```

### 3.1 Proibições verificáveis

Não pode existir, em qualquer capitalização: `purple`, `violet`, `magenta`, `fuchsia`, `#7c3aed`, `#8b5cf6`, `#a855f7`, `linear-gradient`, `radial-gradient`, `conic-gradient`, `backdrop-filter`, `blur(`, `drop-shadow`, `text-shadow`, sombras decorativas, `shadowBlur` ou `shadowColor` no Canvas. Nenhum pulso, glow, aura, energia ou autorrotação.

Raio: 4–8 px. Pill somente para badge. Motion: 120–180 ms, apenas feedback funcional. Estado disabled conserva opacidade >= .55.

## 4. Shell global e contratos DOM

```html
<a class="skip-link" href="#workspace">Pular para o conteúdo</a>
<header id="app-header">...</header>
<nav id="primary-tabs" role="tablist" aria-label="Áreas do Cerberus">...</nav>
<aside id="evidence-rail" aria-label="Estado operacional">
  <span id="evidence-cluster"></span><span id="evidence-index"></span>
  <span id="evidence-scope"></span><span id="evidence-sync"></span>
</aside>
<main id="workspace" tabindex="-1">
  <section id="tab-search" role="tabpanel"></section>
  <section id="tab-inbox" role="tabpanel" hidden></section>
  <section id="tab-topology" role="tabpanel" hidden></section>
  <section id="tab-metrics" role="tabpanel" hidden></section>
  <section id="tab-profile" role="tabpanel" hidden></section>
</main>
<div id="toast-region" role="status" aria-live="polite" aria-atomic="true"></div>
<div id="dialog-root"></div>
```

Header de 64 px: logo SVG oficial, “Cerberus Inspector”, ambiente, `cluster-status`, `profile-btn`, `profile-avatar`, `logout-btn`. Sem hero promocional.

Exatamente cinco tabs. Cada botão tem `role=tab`, `aria-controls`, `aria-selected` e roving tabindex. Setas alternam, Home/End saltam, Enter/Espaço ativam. Ativo: borda inferior Steel Blue de 2 px. Evidence Rail vira faixa rolável no mobile sem overflow do body.

## 5. Aba Busca — Spotlight split-view

```html
<section id="tab-search" role="tabpanel">
  <header class="panel-heading"><h1>Busca</h1><div id="search-index-state"></div></header>
  <form id="search-form" class="spotlight" role="search">
    <label class="sr-only" for="search-q">Pesquisar na memória</label>
    <input id="search-q" type="search"><kbd aria-hidden="true">Ctrl K</kbd>
    <button id="search-btn" type="submit">Pesquisar</button>
  </form>
  <div id="search-filter-bar" role="group" aria-label="Filtros"></div>
  <div id="search-workbench" class="split-workbench">
    <section id="search-master" aria-label="Resultados">
      <div class="pane-toolbar"></div><div id="search-results" aria-live="polite"></div>
    </section>
    <article id="search-preview" aria-labelledby="search-preview-title" tabindex="0"></article>
  </div>
</section>
```

Spotlight: máximo 920 px, centralizado, 52 px desktop/48 px mobile. `Ctrl/Cmd+K` foca; Escape limpa. Submit vazio não chama API. Debounce 350 ms a partir de 3 caracteres; Enter aceita 1+. Usar `AbortController` para cancelar request anterior.

Filtros segmentados: Todos, dm-erp, Teenus, HelpDesk, Biolar; Híbrida, Semântica, Lexical. Preservar controles reais `search-project` e `search-mode`; atualizar `evidence-scope`.

Resultado é `button.search-result-row[data-memory-id]` com título, path mono, projeto, tipo, autoridade, score textual e snippet até quatro linhas. Setas navegam; Enter seleciona/foca preview.

Preview Markdown seguro: escapar HTML primeiro; headings, listas, parágrafo, inline/fenced code, blockquote e tabelas simples. Links somente HTTP/HTTPS com `rel="noopener noreferrer"`. Código tem “Copiar”. Mobile usa drill-down e “Voltar aos resultados”. Empty: “Selecione um resultado para visualizar o conteúdo.”

## 6. Aba Inbox — triagem e diff

```html
<section id="tab-inbox" role="tabpanel">
  <header class="panel-heading"><h1>Inbox</h1></header>
  <div id="inbox-summary" class="telemetry-strip"></div>
  <div id="inbox-workbench" class="split-workbench">
    <section id="inbox-master"><div id="inbox-filters"></div>
      <div id="inbox-list" aria-live="polite"></div></section>
    <article id="candidate-inspector">
      <header id="candidate-header"></header><dl id="candidate-metadata"></dl>
      <div id="candidate-diff" class="diff-viewer"></div>
      <footer id="candidate-actions"></footer>
    </article>
  </div>
</section>
```

Filtros: Todos/Candidato/Verificado/Canônico/Rejeitado, com contadores reais. Lista mostra título, projeto, agente, data e badge textual. Skeleton sólido, sem shimmer.

Diff em IBM Plex Mono 12–13 px, line-height 1.65. Adição usa `--success-soft` + marcador “+”; remoção `--danger-soft` + “−”; contexto neutro. Nunca comunicar apenas por cor. Sem diff, mostrar conteúdo proposto e destino.

Ações: Verificar (Steel Blue), Aprovar (Emerald), Rejeitar (Coral + confirmação inline). Loading mantém largura; bloquear somente candidato afetado. Sucesso atualiza lista/inspector; erro preserva dados.

Preservar `GET /api/inbox`, `GET /api/inbox/{id}`, POST `verify`, `promote`, `reject`.

## 7. Aba Topologia — vetorial geométrica HiDPI

Direção Obsidian/Linear: fundo sólido `#0B0F19`; conexões `#334155`; selecionada `#2563EB`; nós neutros `#94A3B8`, selecionado Steel Blue, alerta Amber. Círculo=projeto, quadrado=documento, losango=decisão. Sem 3D, gradiente, halo, partículas, pulso ou autorrotação.

```html
<section id="tab-topology" role="tabpanel">
  <header class="panel-heading"><h1>Topologia</h1></header>
  <div class="topology-toolbar" role="toolbar"></div>
  <div class="topology-layout">
    <div id="topology-stage"><canvas id="brainCanvas"
      aria-label="Mapa interativo da memória corporativa"></canvas>
      <div id="topology-empty" hidden></div></div>
    <aside id="topology-inspector"></aside>
  </div>
</section>
```

HiDPI obrigatório:

```javascript
const dpr=Math.max(1,Math.min(window.devicePixelRatio||1,3));
canvas.width=Math.round(cssWidth*dpr);
canvas.height=Math.round(cssHeight*dpr);
canvas.style.width=cssWidth+"px"; canvas.style.height=cssHeight+"px";
ctx.setTransform(dpr,0,0,dpr,0,0);
```

Usar `ResizeObserver` com fallback resize; coordenadas em pixels CSS; nunca escala cumulativa. Pausar RAF quando tab/documento oculto. Reduced motion remove inércia.

Interações: drag vazio=pan; drag nó=reposição temporária; wheel zoom 0,6–2× ancorado no cursor; clique seleciona; Escape limpa; Centralizar restaura; Ajustar enquadra; filtros por tipo/projeto. Hit-test geométrico. Inércia opcional <=240 ms, sem loop ambiente.

Funções isoladas: `resizeTopologyCanvas`, `buildTopologyModel`, `drawTopologyGrid`, `drawTopologyEdges`, `drawTopologyNodes`, `hitTestTopology`, `renderTopologyFrame`, `destroyTopologyCanvas`.

## 8. Aba Métricas — telemetria densa

```html
<section id="tab-metrics" role="tabpanel">
  <header class="panel-heading"><h1>Métricas</h1>
    <button id="reindex-btn">Reindexar cérebro</button></header>
  <div id="metrics-health-strip" class="telemetry-strip"></div>
  <div id="metrics-grid"></div>
  <section id="index-breakdown" class="data-panel"></section>
  <section id="system-diagnostics" class="data-panel"></section>
</section>
```

Exibir estado geral, FTS5, vetores, chunks/documentos, Inbox e última indexação. Cards: valor 20 px Space Grotesk, unidade/período, descrição; sem ícones grandes ou dados inventados. Breakdown por projeto/tipo em tabela; barra sólida Steel Blue opcional, sempre com valor absoluto.

Reindex: confirmação inline; `aria-busy`; “Reindexando…”; `POST /api/reindex`. Sucesso atualiza dados/horário. Falha mantém valores anteriores. Nunca simular percentual.

## 9. Aba Perfil e 2FA

```html
<section id="tab-profile" role="tabpanel">
  <header class="panel-heading"><h1>Perfil e segurança</h1></header>
  <div class="settings-layout"><nav class="settings-nav"></nav>
    <div class="settings-content">
      <section id="profile-account-card"></section>
      <section id="profile-password-card"></section>
      <section id="profile-twofa-card"></section>
    </div>
  </div>
</section>
```

Preservar IDs atuais: `profile-email`, `profile-active`, `profile-created`, `profile-2fa-status`, `change-password-form`, campos de senha, `twofa-enable-btn`, `twofa-enrollment`, `twofa-qr`, `twofa-secret`, forms/código/desativação.

Conta em `dl`. Troca de senha com labels, autocomplete, requisitos e erros por campo via `aria-describedby`; sucesso limpa campos.

Máquina TOTP: `disabled → setup-loading → qr-ready → verifying → enabled`; `error` preserva estágio recuperável. QR branco sólido, padding 16, SVG do backend, secret mono e copiável. Desativar exige senha e estilo destrutivo.

Preservar endpoints `/api/v1/auth/me`, `change-password`, `2fa/setup`, `verify-and-enable`, `disable`.

## 10. Contratos JavaScript

Estado mínimo: `uiState.activeTab`; busca com query/project/mode/selectedId/controller; Inbox com filter/selectedId/pendingMutationId; topologia com selectedNodeId/zoom/pan/rafId; profile com status/secret. Sem store externo.

Inicializadores idempotentes, isolados e protegidos: `initTabs`, `initEvidenceRail`, `initSearch`, `initInbox`, `initTopologyCanvas`, `initMetrics`, `initProfile`, `initDialogs`, `initKeyboardShortcuts`.

Boot obrigatório via `DOMContentLoaded`, executando cada função em try/catch separado. Falha de módulo não bloqueia demais.

Centralizar HTTP em `requestJSON`: Accept JSON; Content-Type em POST; body vazio; erro com status/mensagem; 401 redireciona uma vez a `/auth/login`; busca vazia não requesta; busca cancela anterior.

Render seguro: dados por `textContent` ou `escapeHTML`; nenhum erro de servidor por innerHTML; Markdown sem HTML cru/scripts/handlers/`javascript:`/data URLs; IDs externos com `CSS.escape`. QR SVG autenticado só entra se raiz for `<svg`.

Toasts usam texto + estado, 5 s, pausam no hover/foco; erro bloqueante persiste. Dialog nativo, foco preso, Escape seguro, foco retorna ao invocador.

## 11. Responsividade e acessibilidade

Breakpoints: >=1280 split 42/58; 960–1279 45/55; 720–959 mestre/detalhe alternável; 360–719 uma coluna e tabs roláveis.

Obrigatório: zero overflow no body em 360/390/430; controles 44×44; padding lateral 16; tabelas/diffs rolam internamente; QR 100%; preview/diff com voltar; zoom 200% funcional.

WCAG 2.2 AA: contraste >=4,5:1; foco `--focus-ring`; nenhuma informação só por cor; headings corretos; tabs ARIA; `aria-busy` e live regions; Canvas com inspector textual; `prefers-reduced-motion`; `prefers-contrast:more`; SVG decorativo aria-hidden; zero emoji de UI.

Estados por aba: idle, loading, populated, empty, recoverable error, unauthorized e busy. Mensagens orientam ação, sem desculpas vagas.

## 12. TDD, validação e aceite

Criar testes RED antes do código:

- tokens exatos presentes e proibições ausentes;
- exatamente cinco tabs/tabpanels; IDs preservados únicos; IDs split/diff/Evidence/inspector presentes;
- inputs com labels, live regions e ARIA;
- Node compila `new Function(script)`;
- todos os inicializadores no boot;
- busca retorna antes de `requestJSON` quando vazia e usa `AbortController`;
- Canvas usa DPR, `setTransform`, `ResizeObserver`; não usa gradiente, shadowBlur ou autorrotação;
- reduced motion e endpoints preservados.

Comandos:

```powershell
python -m unittest tests.test_ui_hardening -v
python -m unittest tests.test_server_api -v
python -m unittest discover tests
python -m compileall -q engine tests
git diff --check -- engine/server.py tests/test_ui_hardening.py tests/test_server_api.py
```

Baseline mínimo: 219 PASS; Node exit 0; nenhum warning de sintaxe.

Ordem M3: testes RED → tokens/shell → Busca → Inbox → Topologia → Métricas → Perfil → HTTP/dialog/toast → mobile/a11y → suíte/diff. Cada etapa RED→GREEN→REFACTOR.

Aceite: paleta exclusivamente industrial; zero roxo/neon/gradiente/glow; cinco abas conforme contrato; Markdown seguro; diff funcional; grafo geométrico HiDPI; telemetria real; TOTP completo; estados e a11y auditados; Node limpo; >=219 PASS; diff só em arquivos autorizados.

## 13. Evidências, relatório e stop conditions

QA exige screenshots desktop 1440×900 de cada aba; mobile 390×844 de Busca/Inbox/Topologia/Perfil; foco por teclado; Canvas DPR 1/2; estados empty/loading/error/success.

TASK REPORT: `DESIGN_SYSTEM_IMPLEMENTED`, `IMPLEMENTATION`, `FILES_CHANGED`, `TESTS`, `BROWSER_QA`, `ACCESSIBILITY`, `RESPONSIVE_QA`, `SECURITY_IMPACT`, `REGRESSIONS`, `KNOWN_LIMITATIONS`, `GIT_STATUS`, `READY_FOR_INDEPENDENT_QA`.

Parar se exigir alterar endpoint/payload, nova dependência, houver colisão em `engine/server.py`, regressão auth/2FA, menos de 219 testes, divergência de segurança ou ação em produção. Implementação termina em **VALIDATED**; QA independente e PO Gate permanecem obrigatórios.
