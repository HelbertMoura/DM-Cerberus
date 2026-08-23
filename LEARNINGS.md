# 📚 LEARNINGS.md — Caderno de Lições Aprendidas
> **Propriedade:** Dev Maniac's Systems (Helbert Moura)
> **Versão:** 1.0 · 22 de Agosto de 2026
> **Formato:** Append-only (nunca apagar, só adicionar)
> **Vincular com:** DECISIONS.md (decisões) · AGENTS.md (procedimento)

---

## 🎯 Como Usar Este Arquivo

Toda vez que você (humano ou IA) aprender algo **reutilizável** em outros projetos:

1. **Erro de produção** → registrar aqui + causa raiz + fix
2. **Gotcha de biblioteca** → registrar aqui + workaround
3. **Decisão contraintuitiva** → aqui como "aprendizado" + ADR no DECISIONS.md
4. **Padrão que funcionou** → registrar aqui pra replicar

**Regra:** Se não for útil em outro contexto, não entra aqui. Vai pro commit message.

---

## 📖 Lições Registradas

### [LEARN-001] PostgreSQL `select_for_update` em Esteira Multi-Step
> **Data:** 22/08/2026 · **Contexto:** CanteiroHUB · **Agente:** Z.AI Hermes · **ADR:** ADR-002

- **Problema:** Race condition ao converter Orçamento → Contrato → Obra simultaneamente.
- **Causa raiz:** Falta de lock pessimista no `select_for_update` durante transação.
- **Solução:** Usar `transaction.atomic()` + `select_for_update(nowait=False)` em todos os models da esteira.
- **Aplicar em:** Qualquer esteira que envolva transição de estado sequencial.

---

### [LEARN-002] Frontmatter YAML em Todo `.md`
> **Data:** 22/08/2026 · **Contexto:** DM-Cerebro · **Agente:** Gemini · **ADR:** —

- **Problema:** Busca manual por tags/conteúdo era ineficiente.
- **Solução:** Padronizar frontmatter YAML com `titulo`, `tags`, `atualizado`, `status`.
- **Ferramenta:** Editor com suporte a YAML frontmatter (VS Code, Obsidian).
- **Aplicar em:** Todo novo arquivo `.md` no DM-Cerebro.

---

### [LEARN-003] Cloudflare Tunnel Sem Porta 22 Outbound
> **Data:** 22/08/2026 · **Contexto:** Infra Servidor · **Agente:** Helbert · **ADR:** —

- **Problema:** Rede Helbert bloqueia porta 22 outbound → `ssh root@192.168.226.103` falha direto.
- **Workaround:** Usar `cloudflared access tcp :2222 --hostname ssh.devmaniacs.com.br`.
- **Aplicar em:** Qualquer nova VM Dev Maniac's que precise de acesso externo.

---

### [LEARN-004] Largest-Remainder em Normalização de EAP
> **Data:** 22/08/2026 · **Contexto:** CanteiroHUB · **Agente:** MiniMax M3 · **ADR:** ADR-002

- **Problema:** Soma de percentuais da EAP não fechava em 100.00% (ex: 99.97%).
- **Causa raiz:** Arredondamento por linha sem método sistemático.
- **Solução:** Algoritmo Largest-Remainder (Hare) — distribuir resíduo nos maiores restos.
- **Implementação:** Normalizar para 4 casas decimais, distribuir diferença entre maiores restos.
- **Aplicar em:** Qualquer agregação que exige soma exata (BDI, percentuais, rateios).

---

### [LEARN-005] Hash Routing para SPA Sem Framework
> **Data:** 22/08/2026 · **Contexto:** CanteiroHUB Front · **Agente:** Gemini · **ADR:** ADR-003

- **Problema:** F5 em rota específica voltava pro dashboard, perdia estado.
- **Solução:** Usar `window.location.hash` + listeners `hashchange`/`popstate`.
- **Aplicar em:** Qualquer SPA que precise de URL persistível sem React Router/Vue Router.

---

### [LEARN-006] `php -S` com router quebrado devolve 200 VAZIO (sem erro)
> **Data:** 23/08/2026 · **Contexto:** hub-remote-ide · **Agente:** Z.AI ZCode · **ADR:** —

- **Problema:** Site inteiro servindo páginas vazias com HTTP 200 — sem erro no log, sem 500, e o watchdog via "hub=200" e não reclamava.
- **Causa raiz:** Parse error no `router.php` (typo: `__DIR__ '/../'` sem o ponto de concatenação). O PHP built-in server, com `display_errors=0`, responde 200 com body vazio quando o router não compila — falha **silenciosa**.
- **Solução:** Diagnóstico definitivo foi rodar `php router.php` no CLI (mostra o parse error que o `-S` engole). Regra nova: **`php -l` obrigatório depois de QUALQUER edit em arquivo PHP servido ao vivo** — antes de qualquer curl de teste.
- **Bônus:** descobri junto que o output de `echo` num router é DESCARTADO quando ele termina com `return false` (o built-in server assume a resposta inteira).
- **Aplicar em:** Qualquer uso de `php -S <host:port> router.php` em DevManiacs.

### [LEARN-007] Aspect-ratio de mascote vertical dentro de CSS Grid (1:2)
> **Data:** 23/08/2026 · **Contexto:** hub-remote-ide · **Agente:** Z.AI DM Agent · **ADR:** ADR-010

- **Problema:** Asset do mascote (`dev-maniacs-mascot.webp`) tem proporção natural 700×1400 (1:2, vertical, full body). Primeira tentativa de CSS: `.login-mascot img { width: 100%; height: auto; max-width: 360px }`. Resultado: o mascote renderizou com **360×720** (esticado verticalmente) porque o `align-items: center` do grid deu altura sobrando e o browser esticou a imagem pra preencher.
- **Causa raiz:** `width: 100%; height: auto` em imagem dentro de grid com `align-items: center` (que dá altura sobrando) faz o navegador manter `width` mas esticar `height` até preencher — distorcendo a proporção. Não é bug do asset; é armadilha do layout.
- **Solução:** inverter a abordagem — **limitar pela altura, deixar largura fluir**: `height: clamp(280px, 56vh, 460px); width: auto; max-width: 100%`. Agora a imagem respeita o aspect-ratio natural (700/1400 = 1/2) e o `clamp()` impede que ela domine o viewport em telas pequenas nem fique minúscula em telas grandes.
- **Bônus:** validação visual automatizada com Playwright headless (`render-login.js`) tirando screenshot em 3 viewports (1280/768/390). Descobri o bug em segundos porque comparei `naturalWidth` vs `clientWidth` no console do Playwright (`naturalWidth: 700, clientWidth: 360, clientHeight: 720` ← proporção errada).
- **Aplicar em:** Qualquer mascote/ilustração vertical em layout CSS Grid. **Regra:** pra asset não-quadrado, sempre limitar pela dimensão que NÃO distorce (a "estreita"), nunca pela "larga".

---

### [LEARN-008] Crop agressivo de asset vertical com fundo bege (object-position + border-radius circular)
> **Data:** 2026-08-23 · **Contexto:** hub-remote-ide/login v2.1 · **Agente:** Hermes/M3 (DM Agent) · **ADR:** [ADR-011](#adr-011-css-isolado-por-página-crítica)

- **Problema:** O mascote `dev-maniacs-mascot.webp` (700×1400, vertical full body) tem **fundo bege quadrado que aparece como moldura** quando o asset é recortado. Na v1.4 ficou num "cartão paper" parecendo PowerPoint 2010. Na v2.0 desktop ficou num retângulo 280×320 com o fundo bege aparecendo inteiro (porque o `border-radius: var(--r-lg)` no desktop só arredondava cantos, não escondia fundo).
- **Causa raiz:** Crop central (`object-fit: cover` + `object-position: center`) pega o **meio** do asset, que é o corpo do mascote + fundo bege. O rosto fica no TOPO do asset (uns 18% da altura).
- **Solução:** Duas mudanças combinadas:
  1. `object-position: center 18%` (era 22%, depois 50% implícito) — puxa o crop pro topo
  2. `border-radius: 50%` em **todos** viewports (não só mobile) — força circular mesmo no desktop, eliminando a moldura retangular onde o bege aparece
- **Bônus:** removendo o `border-radius: var(--r-lg)` (cantos suaves) do desktop, o bege some porque o círculo + `overflow: hidden` cortam tudo fora do rosto.
- **Aplicar em:** Qualquer asset vertical com fundo indesejado quando renderizado em container retangular. **Regra:** asset vertical com fundo "sujo" → sempre circular (`50%`) + crop no topo (`object-position: center 10-20%`), nunca crop central. E se precisar retangular (ex: cards), limpar o fundo do asset (gerar nova versão PNG/WebP com alpha) ANTES de usar.
- **Validação visual:** screenshots em `C:\Users\Helbert\AppData\Local\Temp\login2-{mobile,desktop}.png` (v2.1) — rosto limpo, sem sliver bege.

---

### [LEARN-009] Copy de superfície: pública vs interna (PII + arquitetura)
> **Data:** 2026-08-23 · **Contexto:** hub-remote-ide/login v2.2 · **Agente:** Hermes/M3 (DM Agent) · **ADR:** [ADR-010](#adr-010-login-do-hub-sob-o-princípio-hub-apenas-rodada-2308-hermesm3-dm-agent--v21)

- **Problema:** A tela de login (página **pública** — qualquer um com a URL vê) tinha no `<p class="login-sub">`: `"Gemini, MiniMax M3, Z.AI e VSCode Web — um login, do canteiro pro bolso."`. O Helbert percebeu: isso **vaza duas informações operacionais** que não interessam a um visitante: (a) **stack tecnológica específica** (concorrentes conseguem inferir estratégia), (b) **contexto pessoal** ("canteiro pro bolso" é específico da operação Dev Maniac's).
- **Causa raiz:** copy não-separada por superfície. A mesma copy que serve pra documento interno de onboarding foi parar na landing pública. Falta de princípio explícito "página pública ≠ página interna".
- **Solução:** copy dupla:
  - **Login (público):** `"Hub Remoto de IDEs"` (título neutro) + `"Seu painel unificado — acesso único a partir de qualquer lugar."` (sub genérico). Identidade vem da marca + mascote, não de texto descritivo.
  - **Dashboard/Hub/Status (internas, pós-auth via cookie SSO + allowlist):** `"Gemini · MiniMax M3 · Z.AI · VSCode Web"` continua aparecendo — é a tela de trabalho, você precisa saber qual IDE está abrindo. Ali sim, a copy técnica faz sentido.
  - **`<meta description>` do login + `manifest.webmanifest` description:** mesma copy genérica.
- **Princípio registrado:**
  1. **PII nunca no front público**: email, telefone, contas pessoais (já removido email no LEARN-008 / a99a136).
  2. **Stack tecnológica específica nunca no front público**: trocada por descrição genérica da função.
  3. **Contexto pessoal/profissional nunca no front público**: "canteiro", "bolso" → só aparecem em docs internos (README, HANDOVER).
  4. **Identidade vem de marca + mascote + logo**: o que distingue "Hub DM" de qualquer outro Hub é a marca visual, não a copy.
- **Aplicar em:** qualquer página com acesso pré-auth (login, marketing, error, offline) + qualquer metadata pública (`<meta>`, `manifest.webmanifest`, og:image alt text). Páginas pós-auth podem manter stack + detalhes operacionais.
- **Trade-off:** copy pública fica menos "vendável" pra um visitante — não lista os produtos. Aceitável: o Hub tem 1 usuário (você), não precisa converter leads. Se um dia virar produto, refaz a copy pública.

---

## 🔄 Template Para Novas Entradas

```markdown
### [LEARN-NNN] Título Curto e Descritivo
> **Data:** AAAA-MM-DD · **Contexto:** <produto> · **Agente:** <humano|ia> · **ADR:** [ADR-NNN](link) ou —

- **Problema:** Sintoma observado.
- **Causa raiz:** Por que aconteceu.
- **Solução:** O que foi feito.
- **Aplicar em:** Onde mais usar.
```

---

**Última atualização:** 23 de Agosto de 2026 · **Total de lições:** 7

---

### [LEARN-010] TOTP custom: valide contra pyotp ANTES de assumir que tá errado
> **Data:** 2026-08-23 · **Contexto:** hub-remote-ide/auth · **Agente:** Hermes/M3 (DM Agent) · **ADR:** ADR-012

- **Problema:** Implementei TOTP RFC 6238 do zero em PHP pra login com 2FA. Código parecia certo (HMAC-SHA1, pack N*8 bytes BE, dynamic truncation). Gerei código TOTP em **Python** pra comparar — divergia do PHP. Achei que PHP tava errado. Reescrevi 3 vezes. Perdi horas.
- **Causa raiz:** Meu **Python de comparação** tava errado, não o PHP. Eu passava `time` direto pro HMAC em vez de `time / 30` (o counter do TOTP). Quando corrigi o Python (`counter = time // 30`), PHP bateu com `pyotp` (biblioteca referência, 11 anos em produção) **no primeiro teste**.
- **Diagnóstico definitivo:** comparar implementação custom com biblioteca de referência (pyotp, otplib, etc) usando o **mesmo secret + RFC test vectors** (time=59, time=1111111109). Se bate com pyotp → tá certo**. Não com código custom meu.
- **Lição:** Pra qualquer RFC crypto (TOTP, JWT, OIDC, etc), **sempre valide contra biblioteca de referência antes de assumir bug**. Implementar RFC do zero pra produção é pedir pra sofrer — prefira libs testadas (chillerlan/php-totp, otplib, pyotp).
- **Aplicar em:** qualquer implementação futura de crypto/auth/protocolo. Antes de debugar por horas, gaste5 minutos rodando o test vector da RFC na lib de referência.

---

### [LEARN-011] PHP `require` em ambos router.php e auth.php = conflito de funções
> **Data:** 2026-08-23 · **Contexto:** hub-remote-ide/mockup · **Agente:** Hermes/M3 (DM Agent)

- **Problema:** Tinha `dm_session_start()` declarada em **router.php** E em **auth.php** (cópia durante refactor). PHP built-in server deu `Fatal error: Cannot redeclare dm_session_start()` em cada request — fail-safe do PHP travou o login inteiro.
- **Causa raiz:** copiei o helper de sessão pro novo `auth.php` sem verificar se já existia no `router.php` que faz `require` dele. PHP **não tem** `ifndef`/`#pragma once` como C — funções同名 em arquivos diferentes ambos required = erro fatal.
- **Solução:** wrap cada helper compartilhado em `if (!function_exists('name')) { function name() {...} }` em **todos os arquivos** que podem ser required juntos. Alternative: pôr helpers em arquivo `_common.php` e fazer require_once em ambos.
- **Por que não detectei antes:** rodei validação via `php -l` (lint) que só checa syntax — não checa redeclaração entre arquivos. Redeclaração só explode em runtime quando ambos são required no **mesmo request**.
- **Aplicar em:** qualquer projeto PHP multi-arquivo. Centralizar helpers em `_common.php` é a forma mais limpa; senão, sempre wrap em `function_exists`.

