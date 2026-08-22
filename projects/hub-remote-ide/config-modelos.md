---
titulo: Configuração de Modelos — Hub Dev Maniac's
tags: [config, modelos, glm-5.3, zai, minimax, m3, fallback, oauth, google]
atualizado: 2026-08-22
status: ativo
---

# ⚙️ Configuração de Modelos e Auth — Hub Dev Maniac's

> **Modelo padrão do projeto:** GLM 5.3 (Z.AI)
> **Fallback:** MiniMax M3

---

## 🧠 Hierarquia de modelos

```
1º GLM 5.3     → Z.AI    (matemática, ADRs, decisões pesadas) ← NOVO PADRÃO
2º MiniMax M3  → MiniMax  (volume de código, TDD, scaffolding)  ← FALLBACK
3º Gemini 3.7  → Google   (orquestração, deploys)               ← via MCP
```

**Por quê essa ordem?**

- **GLM 5.3** tem raciocínio matemático denso e ADRs melhores (uso cirúrgico)
- **MiniMax M3** é o "braçal" — rápido pra código repetitivo, TDD, scaffold
- **Gemini** continua sendo o orquestrador (via MCP, não consome API key direto)

---

## 🔑 Setup local (não versionado)

### 1. Criar `.env` na raiz do projeto

```bash
cd "C:\Users\Helbert\Desktop\DM-Cerebro\projects\hub-remote-ide"
cp .env.example .env
```

### 2. Preencher a chave Z.AI

Você já tem a `ZAI_API_KEY`. Edite o `.env`:

```bash
ZAI_API_KEY=e922a58d1cfe4ebd8a3c4ec5937a1264.LaxlbbphPjm8KJ4R
```

### 3. Validar conexão

```bash
curl -s "https://api.z.ai/api/paas/v4/models" \
  -H "Authorization: Bearer $ZAI_API_KEY" | head
```

Deve retornar JSON com modelos `glm-5.3`, `glm-5.2`, etc.

---

## 🧪 Onde cada modelo é usado no Hub

| Tarefa | Modelo | Por quê |
|---|---|---|
| **ADRs técnicas** (DECISIONS.md) | GLM 5.3 | Raciocínio matemático + trade-offs |
| **Cálculos BDI TCU, Curva S, EVM** | GLM 5.3 | Densidade numérica superior |
| **Scaffold React/Django** | MiniMax M3 | Volume + velocidade |
| **TDD testes repetitivos** | MiniMax M3 | 50+ testes em minutos |
| **Orquestração + deploy** | Gemini | Integração externa + Cloudflare |
| **Prompts de copy** | GLM 5.3 | Texto denso, copywriting |
| **Tradução i18n PT/EN/ES** | MiniMax M3 | Custo menor pra tarefa simples |
| **Diagnóstico de erro** | GLM 5.3 | Stack trace analysis |

---

## 🔐 Login com Google (OAuth 2.0)

### Vantagens

- ✅ Sem precisar lembrar senha do Hub
- ✅ 2FA nativo do Google (mais forte que TOTP caseiro)
- ✅ Provisionamento automático (1º login cria conta)
- ✅ Revogação fácil pelo usuário
- ✅ Auditoria de logins nativos do Google

### Setup no Google Cloud Console

1. Acessa: https://console.cloud.google.com
2. Cria projeto `DM Hub` (ou usa existente)
3. **APIs & Services → OAuth consent screen**
   - User type: **External** (se for só você) ou **Internal** (GSuite)
   - App name: `Dev Maniac's Hub`
   - Scopes: `openid`, `email`, `profile`
   - Test users: `helbertcurcio@gmail.com`
4. **Credentials → Create OAuth Client ID**
   - Type: **Web application**
   - Authorized redirect URIs:
     - `https://hub.devmaniacs.com.br/auth/google/callback`
     - `http://localhost:8765/auth/google/callback` (dev)
5. Copia `Client ID` + `Client Secret` → coloca no `.env`:

```bash
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx
```

### Implementação (próximo passo — Fase 1)

Tecnologias sugeridas:
- **NextAuth.js** (com provider Google) — mais simples
- **Auth.js v5** (sucessor do NextAuth)
- **Lucia Auth** (mais leve, sem dependências)

Fluxo:
```
Usuário clica "Entrar com Google"
       ↓
Redireciona pra Google OAuth consent
       ↓
Google valida email + 2FA do Google
       ↓
Callback em /auth/google/callback
       ↓
Hub cria sessão + cookie HttpOnly
       ↓
Audit log: "Login via Google · IP · User Agent"
```

### Combinado com email/senha (recomendado)

| Opção | Uso |
|---|---|
| **Google OAuth** | Login rápido no celular (1 toque) |
| **Email + senha + TOTP** | Login offline / 2FA corporativo |
| **Magic link** | Fallback se esquece senha |

---

## 🌐 Tunnel permanente (hub.devmaniacs.com.br)

### Por que NÃO usar `trycloudflare.com`?

- ❌ URL muda a cada execução
- ❌ Sem garantia de uptime
- ❌ Não tem IP fixo
- ❌ Não serve pra produção

### Setup do tunnel permanente

#### 1. Login no Cloudflare (1 vez)

```bash
cloudflared tunnel login
```

Abre navegador → seleciona zona `devmaniacs.com.br` → autoriza.

#### 2. Criar tunnel nomeado

```bash
cloudflared tunnel create dm-hub
```

Salva `~/.cloudflared/<UUID>.json` (credenciais) + JSON de config.

#### 3. Criar `~/.cloudflared/config.yml`

```yaml
tunnel: dm-hub
credentials-file: /c/Users/Helbert/.cloudflared/<UUID>.json

ingress:
  - hostname: hub.devmaniacs.com.br
    service: http://127.0.0.1:8765
  - service: http_status:404
```

#### 4. Criar DNS no Cloudflare

```bash
cloudflared tunnel route dns dm-hub hub.devmaniacs.com.br
```

Cria registro CNAME → `dm-hub.cfargotunnel.com` com **proxy ligado** (nuvem laranja).

#### 5. Subir tunnel como serviço (Windows)

```bash
cloudflared service install
```

Roda **sempre** em background, mesmo após reboot.

#### 6. Validar

```bash
curl -I https://hub.devmaniacs.com.br/login.html
```

Deve retornar `HTTP/2 200` com `server: cloudflare`.

### Vantagens do tunnel permanente

- ✅ DNS fixo (`hub.devmaniacs.com.br`)
- ✅ Cloudflare proxy (nuvem laranja) → esconde IP do Rocky
- ✅ TLS 1.3 automático
- ✅ WAF + DDoS protection grátis
- ✅ Logs no painel Cloudflare
- ✅ Cloudflare Access pra políticas extras (opcional)

---

## 📋 Checklist de configuração

Antes de subir pra Fase 1:

- [ ] `.env` criado com `ZAI_API_KEY`
- [ ] `curl` à Z.AI retorna modelos disponíveis
- [ ] Tunnel permanente `hub.devmaniacs.com.br` criado
- [ ] DNS CNAME configurado e propagado
- [ ] Google OAuth client criado (se quiser login Google)
- [ ] Sessão secret gerado (`openssl rand -hex 32`)
- [ ] `git status` no DM-Cerebro não mostra `.env`

---

## 🔒 Segurança

| Item | Prática |
|---|---|
| **API keys** | Nunca no Git. Sempre em `.env` |
| **OAuth secrets** | Mesmo princípio |
| **Tunnel credentials** | `chmod 600` no Windows (icacls) |
| **Cookie de sessão** | HttpOnly + Secure + SameSite=Lax |
| **Audit log** | Toda ação sensível registrada |
| **2FA** | TOTP + Google OAuth fallback |

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
**Modelo padrão:** GLM 5.3 (Z.AI) · Fallback: MiniMax M3
