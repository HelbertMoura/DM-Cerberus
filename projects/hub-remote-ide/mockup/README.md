---
titulo: Mockup HTML — Hub Dev Maniac's
tags: [mockup, html, demo, hub, devmaniacs, identidade-visual]
atualizado: 2026-08-22
status: ativo
fase: 1-de-3
---

# 🎨 Mockup HTML — Hub Dev Maniac's

> **Visualizar a cara do Hub AGORA**, sem precisar de Docker, Next.js ou servidor. Só abrir o HTML no navegador.

---

## 📂 Arquivos

```
mockup/
├── login.html       ← tela de login (email + senha + 2FA)
├── dashboard.html   ← hub principal com 3 cards (Gemini, M3, Z.AI)
├── styles.css       ← identidade visual completa (Dev Maniac's)
├── app.js           ← interações JS (demo)
└── README.md        ← este arquivo
```

---

## 🚀 Como visualizar

### Opção 1 — Abrir direto (mais rápido)

1. Navega até: `C:\Users\Helbert\Desktop\DM-Cerebro\projects\hub-remote-ide\mockup\`
2. **Duplo clique** em `login.html`
3. Abre no navegador padrão
4. Clica em "Entrar" (fake) → mostra 2FA → digita qualquer 6 dígitos → vai pro dashboard

### Opção 2 — Servidor local (PWA-friendly)

```bash
cd "C:\Users\Helbert\Desktop\DM-Cerebro\projects\hub-remote-ide\mockup"

# Python
python -m http.server 8080

# OU Node.js
npx serve -p 8080
```

Abre: http://localhost:8080/login.html

**Por que servidor?** O mockup simula PWA. Pra testar "instalar como app", precisa de HTTP (não `file://`).

---

## � Como testar no celular

### Via rede local (mesmo Wi-Fi)

1. Sobe servidor (Opção 2 acima)
2. Descobre IP do PC: `ipconfig` (Windows) → procura "IPv4"
3. No celular, abre: `http://<IP>:8080/login.html`
4. Exemplo: `http://192.168.0.105:8080/login.html`

### Via Cloudflare Tunnel (já funciona!)

Se você já tem `cloudflared` rodando, expõe o mockup:

```bash
cloudflared tunnel --url http://localhost:8080
```

Ele gera URL pública tipo `https://xxx.trycloudflare.com` que abre **em qualquer rede, qualquer lugar**.

---

## 🎨 O que tá incluído no mockup

### ✅ Identidade Dev Maniac's
- Paleta de cores oficial (roxos `#7C3AED`, `#5B21B6`, `#A78BFA`)
- Tipografia (Space Grotesk + Inter + JetBrains Mono)
- Logo monograma "DM" com gradiente
- Tema dark nativo
- Botões ISO 44px (regra da casa)

### ✅ Login Page
- Campo email com autocomplete
- Campo senha com botão mostrar/ocultar
- Checkbox "Lembrar por 30 dias"
- Link "Esqueci a senha"
- **Fluxo 2FA fake** (simula o passo real: login → código TOTP)
- Input 2FA com auto-submit nos 6 dígitos

### ✅ Dashboard
- Header com logo, status, notificações, avatar
- Saudação personalizada (Helbert 👋)
- **4 cards de IDE:**
  - �️ **Gemini** (online)
  - 🚀 **MiniMax M3** (trabalhando, com barra de progresso)
  - 🧠 **Z.AI Code** (online)
  - 🆚 **VSCode Web** (code-server, compacto)
- Ações rápidas (3 botões)
- Atividade recente (4 últimos eventos)
- Bottom nav mobile-first

### ✅ PWA-ready
- `manifest.json` (estrutura criada em `pwa/public/`)
- Service Worker placeholder
- Meta tags iOS (apple-mobile-web-app-*)
- Theme color `#7C3AED`

---

## ⚠️ O que é MOCK vs. REAL

| Feature | Mock | Real (Fase 1) |
|---|---|---|
| **Login** | Frontend só, fake submit | Backend Node.js + Auth.js + Argon2id |
| **2FA** | Input visual, aceita qualquer código | TOTP real (otplib + Google Authenticator) |
| **Status IDEs** | Hardcoded | Heartbeat via WebSocket + Docker healthcheck |
| **Conectar IDE** | Alert "demo" | iframe real + code-server :8446 |
| **Audit log** | Não registra | PostgreSQL `dm_hub.audit_log` |

**Importante:** o mockup serve pra **validar a cara visual**. A lógica real vem nas Fases 1-3 (docker-compose + code-server + Guacamole).

---

## 🎯 Como dar feedback

Você pode mexer em **qualquer** coisa:

### Mudar cores
Edita `styles.css` → bloco `:root`:
```css
--color-primary: #7C3AED;      /* roxo principal */
--color-primary-dark: #5B21B6; /* hover */
```

### Mudar logo
Edita `login.html` ou `dashboard.html` → bloco `.logo`:
```html
<div class="logo">
  <span class="logo-d">D</span><span class="logo-m">M</span>
</div>
```

### Adicionar campo
Edita o `<form>` em `login.html` + adiciona estilo em `styles.css`.

---

## 📋 Checklist visual (validação)

Antes de eu seguir pra Fase 2, confere:

- [ ] As cores combinam com a identidade Dev Maniac's?
- [ ] O layout funciona no celular? (resize a janela)
- [ ] Os 3 cards (Gemini, M3, Z.AI) tão claros?
- [ ] O fluxo login → 2FA → dashboard tá intuitivo?
- [ ] Falta alguma informação nos cards?
- [ ] Quer mudar nome de alguma coisa?
- [ ] A barra de progresso do M3 faz sentido?
- [ ] A atividade recente mostra o que você precisa?

---

## 🔗 Próximos passos

Quando você aprovar o mockup:

1. **Crio** `setup-fase-1.md` (passo a passo code-server no Rocky)
2. **Crio** `docker-compose.yml` (stack mínimo Fase 1)
3. **Crio** `cloudflare-tunnel.md` (config subdomínio)
4. **Crio** `auth-seguranca.md` (login + 2FA real)
5. **Codifico** Next.js substituindo este mockup (mas mantendo o visual)

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
