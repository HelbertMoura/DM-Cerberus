---
titulo: Mockup — Hub Dev Maniac's (identidade oficial)
tags: [mockup, html, demo, hub, devmaniacs, brand, oficial]
atualizado: 2026-08-22
status: ativo
fase: 1-de-3
---

# 🎨 Mockup HTML — Hub Dev Maniac's

> Mockup visual usando a **identidade oficial da marca** (extraída de devmaniacs.com.br via curl).

---

## 📂 Arquivos

```
mockup/
├── login.html       ← tela de login (com mascote oficial)
├── dashboard.html   ← hub principal (4 cards: Gemini, M3, Z.AI, VSCode Web)
├── styles.css       ← paleta oficial + tipografia Inter/JetBrains Mono
├── app.js           ← interações JS (demo)
└── README.md        ← este arquivo
```

---

## 🎨 Identidade aplicada (oficial)

| Token | Valor | Fonte |
|---|---|---|
| **Navy (principal)** | `#061637` | CSS oficial |
| **Paper (fundo)** | `#fff` + `#faf6ed` | mascote.webp + CSS |
| **Purple (acento)** | `#6b4c9a` | CSS oficial |
| **Cyan (destaque)** | `#08b9ca` | CSS oficial |
| **Coral (alerta)** | `#ff4c4c` | CSS oficial |
| **Yellow (highlight)** | `#ffd166` | CSS oficial |
| **Tipografia sans** | **Inter** | `devmaniacs.com.br` |
| **Tipografia mono** | **JetBrains Mono** | `devmaniacs.com.br` |
| **Logo** | `/brand/dev-maniacs-mark.png` | `devmaniacs.com.br/brand/` |
| **Mascote** | `/brand/dev-maniacs-mascot.webp` | `devmaniacs.com.br/brand/` |
| **Tagline** | Tecnologia feita de perto. Suporte também. | site oficial |

**Estilo:** brutalista industrial, sombras sólidas (`8px 8px 0`), tipografia mono em títulos, prefixos `DM//` (DM//CASE, DM//HUB), numeração `01/02/03/04` industrial.

---

## 🚀 Como visualizar

### Local (rápido)

**Duplo clique** em `login.html` — abre no navegador padrão.

### Servidor local (PWA-friendly)

```bash
cd "C:\Users\Helbert\Desktop\DM-Cerebro\projects\hub-remote-ide\mockup"
python -m http.server 8080
```

Abre: http://localhost:8080/login.html

### No celular (mesma rede)

1. Descobre IP do PC: `ipconfig` (Windows) → IPv4 (ex: `192.168.0.105`)
2. Celular: `http://<IP>:8080/login.html`

### Via Cloudflare Tunnel (qualquer rede)

```bash
cloudflared tunnel --url http://localhost:8080
```

Gera URL pública tipo `https://xxx.trycloudflare.com`.

---

## 🧪 O que testar

### Login

1. Abre `login.html`
2. Vê o mascote oficial à esquerda em fundo navy com pixeis coloridos
3. Digita email/senha qualquer → clica "Entrar"
4. Aparece campo TOTP → digita 6 dígitos → vai pro dashboard

### Dashboard

1. Vê o painel "DM//HUB 2026" com stripe colorida (coral + yellow + cyan + purple)
2. 4 cards: Gemini (online), M3 (trabalhando, 67%), Z.AI (online), VSCode Web
3. Clica "Conectar" em qualquer IDE → simula conexão
4. Bottom nav mobile funciona
5. Redimensiona janela pra ~390px → vira layout celular

---

## ✅ O que mudou (vs. mockup anterior)

| Antes | Agora |
|---|---|
| Tema dark com gradientes roxos | Tema claro com navy `#061637` + acentos |
| Logo "DM" inventado em CSS | Logo oficial `dev-maniacs-mark.png` |
| Fonte Space Grotesk | **Inter** + **JetBrains Mono** (oficial) |
| Cards com bordas arredondadas e sombras suaves | Sombras sólidas `8px 8px 0` (estilo brutalista) |
| Cores inventadas (#7C3AED etc) | **Cores oficiais** do site (extraídas via curl) |
| Sem identidade com o site | **Igual ao devmaniacs.com.br** |
| Estilo "feito por IA" genérico | Estilo **Dev Maniac's** oficial |

---

## � Fontes dos arquivos oficiais

| Arquivo | Origem |
|---|---|
| `assets/brand/dev-maniacs-mark.png` | https://devmaniacs.com.br/brand/dev-maniacs-mark.png |
| `assets/brand/dev-maniacs-mascot.webp` | https://devmaniacs.com.br/brand/dev-maniacs-mascot.webp |
| `assets/brand/dev-maniacs-social-card.png` | https://devmaniacs.com.br/brand/dev-maniacs-social-card.png |
| `assets/brand/devmaniacs-styles.css` | https://devmaniacs.com.br/_next/static/chunks/24-wcb0m4nhax.css |

**Verificado em:** 2026-08-22 22:16 UTC

---

## 🎯 Validação visual

- [ ] O fundo navy + papel claro parece com o site oficial?
- [ ] O mascote aparece no login (estilo cartoon oficial)?
- [ ] O logo "DM" pixel art aparece no header e login?
- [ ] As fontes Inter + JetBrains Mono carregaram?
- [ ] As sombras sólidas `8px 8px 0` estão visíveis nos cards?
- [ ] Os prefixos `DM//` e a numeração `01/02/03/04` aparecem?
- [ ] Falta algo da identidade oficial?

---

## ⏭️ Próximos passos

1. **Validar visual** com você
2. Se aprovado → `setup-fase-1.md` + `docker-compose.yml` + `cloudflare-tunnel.md`
3. Codar versão Next.js substituindo o mockup

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
