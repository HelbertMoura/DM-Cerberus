---
titulo: Identidade Visual Oficial — Dev Maniac's (Hub Remoto)
tags: [identidade, visual, cores, logo, mascote, fontes, devmaniacs, hub, brand, oficial]
atualizado: 2026-08-22
status: ativo
fonte: https://devmaniacs.com.br/
---

# 🎨 Identidade Visual Oficial — Dev Maniac's

> Identidade extraída diretamente do site oficial via curl em 22/08/2026.
> Arquivos fonte salvos em `assets/brand/`.

---

## 🖼️ Logo e Mascote (originais baixados)

| Arquivo | URL oficial | Uso |
|---|---|---|
| `dev-maniacs-mark.png` | /brand/dev-maniacs-mark.png | Logo principal (64×64 px padrão) |
| `dev-maniacs-mascot.webp` | /brand/dev-maniacs-mascot.webp | Mascote (Helbert, ~146×146 px) |
| `dev-maniacs-social-card.png` | /brand/dev-maniacs-social-card.png | Open Graph / social preview |
| `devmaniacs-styles.css` | /_next/static/chunks/24-wcb0m4nhax.css | CSS fonte (55KB, 1 linha minified) |

**Local:** `assets/brand/`

---

## 🎨 Logo (Mark)

**Descrição visual:**
- Quadrado navy escuro `#061637`
- Letras **"DM"** estilizadas em **pixel art** (estilo 8-bit)
- Cada letra tem 2 cores: **D** (vermelho + roxo), **M** (amarelo + cyan)
- À direita: **gamepad** com D-pad branco + botões coloridos (vermelho, amarelo, cyan)
- Fundo: navy sólido, cantos levemente arredondados
- Funciona em **qualquer fundo** (transparente no entorno)

**Tamanhos padrão:**
- Header: 40×40 px
- Login: 56×56 px
- Favicon: 64×64 px

**Tagline oficial:** "Tecnologia feita de perto. Suporte também."

---

## 🦸 Mascote (Helbert Moura)

**Estilo:** Cartoon 3D semi-realista (Pixar/Blender)

**Características:**
- Boné navy `#061637`
- Headphone preto com detalhes cyan
- Óculos de armação preta, **olhos verdes**
- Jaqueta navy com **zíper cyan** + camiseta branca com **logo "DM" cyan/navy**
- Calça jeans escura
- Tênis navy com detalhes **amarelo + cyan + roxo**
- Mão esquerda: **gamepad preto com botões coloridos**
- Mão direita: **laptop cinza com stickers pixel art**
- Smartwatch preto

**Background do mascote (característico da marca):**
- Bege claro `#faf6ed`
- Pequenos **pixels coloridos** espalhados (vermelho, amarelo, cyan, roxo, coral)

**Uso recomendado no Hub:**
- Tela de login (coluna esquerda)
- Empty states do dashboard
- Footer do PWA
- Avatar padrão (quando usuário não tem foto)

---

## 🎨 Paleta de Cores Oficial

**Extraída do CSS oficial via grep** (variáveis CSS ativas):

| Token | Valor | Uso principal |
|---|---|---|
| `--navy` | `#061637` | Background principal, texto, sombras |
| `--navy-soft` | `#10244d` | Background secundário |
| `--paper` | `#ffffff` | Texto sobre fundo escuro |
| `--paper-warm` | `#faf6ed` | Background do mascote (cards claros) |
| `--ink` | `#17213a` | Texto sobre fundo claro |
| `--line` | `rgba(6, 22, 55, 0.12)` | Bordas e divisores |
| `--muted` | `#435f73` | Texto secundário |

### Acentos (usar com moderação)

| Token | Valor | Quando usar |
|---|---|---|
| `--purple` | `#6b4c9a` | Eyebrows, detalhes sutis |
| `--cyan` | `#08b9ca` | Links, hovers, status online, destaques |
| `--coral` | `#ff4c4c` | Alertas, erros, destaques quentes |
| `--yellow` | `#ffd166` | Highlights, warnings, badges |

### Cores dos parceiros (projetos)

| Parceiro | Accent |
|---|---|
| Teenus Construtora | `--cyan` `#08b9ca` |
| Biolar | `--coral` `#ff4c4c` |
| APAE Juatuba | `--purple` `#6b4c9a` |
| Vitor Tec. | `--yellow` `#ffd166` |
| Terabyte | `--navy` `#061637` |

---

## 🔤 Tipografia Oficial

**Confirmado no site oficial:**

| Família | Uso | Fallback |
|---|---|---|
| **Inter** | Todo texto (sans-serif) | `Arial, sans-serif` |
| **JetBrains Mono** | Código, prefixos `DM//`, tags, números | `Consolas, monospace` |

**Pesos usados no site:**
- Inter: 400 (body), 600 (subtítulos), 700 (títulos)
- JetBrains Mono: 400 (tags), 500 (destaques), 700 (títulos mono)

**Cuidado:**
- ❌ **NÃO usar** Space Grotesk, Roboto, Open Sans
- ❌ **NÃO usar** mono em parágrafos grandes
- ✅ Mono **apenas** em: tags, prefixos, código, numeração, status

---

## 🎭 Estilo Visual (características da marca)

### Elementos gráficos únicos

- **Sombras sólidas brutalistas:** `box-shadow: 8px 8px 0 var(--navy)`
- **Sombras pequenas:** `box-shadow: 4px 4px 0 var(--navy)`
- **Prefixos `DM//`:** DM//CASE, DM//HUB, DM//BUILD 2026, DM//GAME, DM//PROFILE
- **Numeração industrial:** `01`, `02`, `03`, `04` em boxes navy
- **Stripes coloridas:** sequências coral → yellow → cyan → purple (bandeira Dev Maniac's)
- **Eyebrows com barrinha:** `<span class="eyebrow-bar"></span> TEXTO` em roxo
- **Prompts mono:** `>_ PRODUCT_ENGINEERING` em cyan

### O que NÃO fazer

- ❌ Gradientes vibrantes em backgrounds
- ❌ Efeitos neon / glow / blur
- ❌ Transparências em textos críticos
- ❌ Sombras suaves (`box-shadow: 0 4px 12px rgba(...)`)
- ❌ Border-radius grandes (> 8px) exceto em avatares/circular
- ❌ Animações longas (> 200ms)
- ❌ Emojis decorativos (somente ícones SVG Lucide)

### Componentes oficiais do site

| Componente | Estrutura CSS |
|---|---|
| `.shell` | Container com max-width |
| `.eyebrow` | Texto pequeno + barrinha decorativa |
| `.section` | Seção com padding generoso |
| `.button--primary` | Fundo navy, texto paper, sombra 7px |
| `.button--ghost` | Transparente, border 2px navy |
| `.engine-card` | Card industrial com stripe no topo |
| `.build-panel` | Painel estilo DM//BUILD com barra superior |
| `.build-panel__stripe` | 4 blocos coloridos: coral/yellow/cyan/purple |

---

## 📐 Layout Tokens

```css
/* Espaçamentos (do site oficial) */
:root {
  --shadow: 8px 8px 0 var(--navy);
  --shadow-sm: 4px 4px 0 var(--navy);
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;  /* máximo permitido */
}
```

**Princípios:**
- **Espaço é luxo** — não encher layouts
- **Bordas finas** (2px) ao invés de 1px
- **Sombras sólidas** ao invés de suaves
- **Contraste alto** — texto navy em papel, ou paper em navy
- **Mobile-first** — `shell` com max-width adaptativo

---

## 🆚 Comparação (mockup novo vs. oficial)

| Item | Site oficial | Mockup Hub |
|---|---|---|
| Background | Navy `#061637` + papel | ✅ Mesmo |
| Logo | `dev-maniacs-mark.png` | ✅ Mesmo (mesmo arquivo) |
| Mascote | `dev-maniacs-mascot.webp` | ✅ Mesmo (mesmo arquivo) |
| Tipografia sans | Inter | ✅ Inter |
| Tipografia mono | JetBrains Mono | ✅ JetBrains Mono |
| Sombras | `8px 8px 0` | ✅ `8px 8px 0` |
| Eyebrows | Barrinha roxa | ✅ Barrinha roxa |
| Prompts | `>_ TEXTO` cyan | ✅ `>_ TEXTO` cyan |
| Numeracao | `01/02/03` industrial | ✅ `01/02/03` industrial |
| Stripe colorido | coral/yellow/cyan/purple | ✅ coral/yellow/cyan/purple |
| Tagline | "Tecnologia feita de perto" | ✅ Será exibido no footer |

**Resultado:** Hub visualmente é **gêmeo do site oficial**.

---

## 🛡️ Compliance Checklist

Antes de commitar qualquer página do Hub, verificar:

- [ ] Usa Inter (sans) + JetBrains Mono (mono)
- [ ] Cores só da paleta oficial
- [ ] Sombras sólidas `8px 8px 0`
- [ ] Bordas 2px navy
- [ ] Eyebrows com barrinha roxa
- [ ] Sem emojis decorativos
- [ ] Sem gradientes em backgrounds
- [ ] Sem blur/transparência em texto
- [ ] Logo `dev-maniacs-mark.png` (não inventado)
- [ ] Numeração industrial `01/02/03`

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
**Fonte:** https://devmaniacs.com.br/ + arquivos em `assets/brand/`
