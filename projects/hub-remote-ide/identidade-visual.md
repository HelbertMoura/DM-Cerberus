---
titulo: Identidade Visual Dev Maniac's — Hub Remoto
tags: [identidade, visual, cores, logo, devmaniacs, hub, brand]
atualizado: 2026-08-22
status: ativo
---

# 🎨 Identidade Visual Dev Maniac's — Hub Remoto

> Cores, tipografia, logo e padrões visuais baseados em https://devmaniacs.com.br/

---

## 🎨 Paleta de Cores

### Cores Primárias

| Nome | Hex | RGB | Uso |
|---|---|---|---|
| **Roxo Dev Maniac's** | `#7C3AED` | `124, 58, 237` | Botões primários, links, ícones ativos |
| **Roxo Profundo** | `#5B21B6` | `91, 33, 182` | Hover, gradientes escuros |
| **Roxo Claro** | `#A78BFA` | `167, 139, 250` | Backgrounds suaves, highlights |
| **Violeta Elétrico** | `#8B5CF6` | `139, 92, 246` | Acentos, badges, status online |
| **Preto Profundo** | `#0F0B1E` | `15, 11, 30` | Background principal (dark) |
| **Branco Puro** | `#FFFFFF` | `255, 255, 255` | Texto principal |

### Cores Secundárias

| Nome | Hex | Uso |
|---|---|---|
| **Cinza Escuro** | `#1E1B2E` | Cards, painéis secundários |
| **Cinza Médio** | `#2D2A3F` | Borders, dividers |
| **Cinza Claro** | `#9CA3AF` | Texto secundário, labels |
| **Verde Sucesso** | `#10B981` | Status "online", sucesso |
| **Vermelho Erro** | `#EF4444` | Status "offline", erro |
| **Amarelo Aviso** | `#F59E0B` | Avisos, alertas |

### Gradientes

```css
/* Gradiente principal (header, hero) */
background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 50%, #0F0B1E 100%);

/* Gradiente secundário (botões) */
background: linear-gradient(90deg, #8B5CF6 0%, #7C3AED 100%);

/* Gradiente card hover */
background: linear-gradient(135deg, #1E1B2E 0%, #2D2A3F 100%);
```

---

## 🔤 Tipografia

| Uso | Fonte | Peso |
|---|---|---|
| **Logo / Título** | **Space Grotesk** | 700 (Bold) |
| **Heading** | **Inter** | 600 (Semi-Bold) |
| **Body** | **Inter** | 400 (Regular) |
| **Code** | **JetBrains Mono** | 400/500 |

```html
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

```css
:root {
  --font-display: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

---

## 🏷️ Logo

A logo "DM" Dev Maniac's segue o padrão de **monograma em shield**:

```
�─────────────────────┐
│                     │
│      ╔══════╗      │
│      ║  D   ║      │
│      ║ M M  ║      │
│      ╚══════╝      │
│                     │
│   DEV MANIAC'S      │
│                     │
└─────────────────────┘
```

**Elementos:**
- Monograma "DM" em **Space Grotesk Bold**
- Fundo do monograma: gradiente roxo `#7C3AED → #5B21B6`
- Contorno: `#A78BFA` (1px)
- Texto "DEV MANIAC'S" abaixo: Inter Semi-Bold 12px, espaçamento 0.2em, uppercase

**SVG placeholder** (criar em `assets/logo.svg`):

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="dmGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7C3AED"/>
      <stop offset="100%" stop-color="#5B21B6"/>
    </linearGradient>
  </defs>
  <rect x="10" y="10" width="80" height="80" rx="16" fill="url(#dmGrad)" stroke="#A78BFA" stroke-width="2"/>
  <text x="50" y="58" text-anchor="middle" font-family="Space Grotesk" font-weight="700" font-size="36" fill="#FFFFFF">DM</text>
</svg>
```

---

## 🧩 Componentes

### Botão Primário

```css
.btn-primary {
  background: linear-gradient(90deg, #8B5CF6 0%, #7C3AED 100%);
  color: #FFFFFF;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 44px; /* ISO 44px (regra Dev Maniac's) */
}

.btn-primary:hover {
  background: linear-gradient(90deg, #7C3AED 0%, #5B21B6 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
}
```

### Card de IDE

```css
.ide-card {
  background: #1E1B2E;
  border: 1px solid #2D2A3F;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
  min-height: 200px;
}

.ide-card:hover {
  border-color: #7C3AED;
  box-shadow: 0 8px 24px rgba(124, 58, 237, 0.2);
}

.ide-card.online {
  border-left: 4px solid #10B981;
}

.ide-card.offline {
  border-left: 4px solid #EF4444;
  opacity: 0.6;
}
```

### Status Badge

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.badge-online { background: rgba(16, 185, 129, 0.15); color: #10B981; }
.badge-offline { background: rgba(239, 68, 68, 0.15); color: #EF4444; }
.badge-working { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }
```

---

## � PWA — Manifest

```json
{
  "name": "Dev Maniac's Hub",
  "short_name": "DM Hub",
  "description": "Hub remoto dos IDEs Dev Maniac's",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0F0B1E",
  "theme_color": "#7C3AED",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

---

## 🚫 O que NÃO usar (regras da casa)

- ❌ **Emoticons no UI** → usar **Lucide-React** (ícones vetoriais)
- ❌ **Fontes decorativas** → só Inter + Space Grotesk + JetBrains Mono
- ❌ **Cores fora da paleta** → manter identidade consistente
- ❌ **Botões < 44px** → ISO 44px (regra Dev Maniac's, luva + sol)
- ❌ **Emojis em logs/messages** → só ícones

---

## 🔗 Referências

- Site oficial: https://devmaniacs.com.br/
- DM-Cerebro identidade: ver `BRAIN.md` e `MEMORY.md`
- Padrão PWA: https://web.dev/learn/pwa/

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
