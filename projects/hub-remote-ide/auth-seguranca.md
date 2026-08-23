---
titulo: Auth — Google OAuth + email/senha
tags: [auth, oauth, google, login, 2fa, totp, seguranca, hub]
atualizado: 2026-08-22
status: ativo
fase: 1-de-3
---

# 🔐 Auth do Hub — Google OAuth + email/senha

> **Modo mockup atual:** botão "Entrar com Google" é um link estático que aponta pra `/auth/google`. Vai funcionar quando o backend real (Next.js + NextAuth) entrar na Fase 1.

---

## 🎯 Estratégia: 2 caminhos + 2FA

```
┌────────────────────────────────────────────────────────┐
│                    TELA DE LOGIN                        │
├────────────────────────────────────────────────────────�
│  [🔵 Entrar com Google]          ← mobile-first         │
│  ─────────────── ou ──────────────                       │
│  E-mail:        [_____________]                         │
│  Senha:         [_____________]                         │
│  [✓ Lembrar 30 dias]   Esqueci a senha                 │
│  [→ Entrar]                                              │
└────────────────────────────────────────────────────────┘
                          ↓ (após submit)
┌────────────────────────────────────────────────────────┐
│  PASSO 2 — 2FA (TOTP)                                   │
│  Confirme com 2FA                                        │
│  [ _ ][ _ ][ _ ][ _ ][ _ ][ _ ]   ← código de 6 dígitos  │
│  ⏱️  30 segundos pra inserir                            │
└────────────────────────────────────────────────────────┘
                          ↓ (código válido)
                    ✅ Sessão criada (cookie HttpOnly)
```

---

## 🔵 Google OAuth

### Por que oferecer?

| Vantagem | Descrição |
|---|---|
| **1 toque no celular** | Sem digitar e-mail/senha |
| **2FA do Google** | Google Authenticator / Titan Key / celular |
| **Sem senha pra lembrar** | Você já tem a conta Google |
| **Provisionamento automático** | 1º login cria conta no Hub |
| **Audit nativo** | Google registra IP, device, hora |

### Implementação (Fase 1 — Next.js)

#### 1. Google Cloud Console

1. https://console.cloud.google.com → projeto `DM Hub`
2. **APIs & Services → OAuth consent screen**
   - App name: `Dev Maniac's Hub`
   - User type: **External** (você + colaboradores)
   - Test users: `helbertcurcio@gmail.com`
3. **Credentials → Create OAuth Client ID**
   - Type: **Web application**
   - Name: `DM Hub Web`
   - Authorized JavaScript origins:
     ```
     https://hub.devmaniacs.com.br
     http://localhost:3000  (dev)
     ```
   - Authorized redirect URIs:
     ```
     https://hub.devmaniacs.com.br/api/auth/callback/google
     http://localhost:3000/api/auth/callback/google  (dev)
     ```

#### 2. Variáveis de ambiente

```bash
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx
NEXTAUTH_URL=https://hub.devmaniacs.com.br
NEXTAUTH_SECRET=<openssl rand -hex 32>
```

#### 3. NextAuth config

```typescript
// pages/api/auth/[...nextauth].ts
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import CredentialsProvider from 'next-auth/providers/credentials';

export default NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          response_type: 'code',
        },
      },
    }),
    CredentialsProvider({
      name: 'E-mail + Senha',
      credentials: {
        email: { label: 'E-mail', type: 'email' },
        password: { label: 'Senha', type: 'password' },
        totp: { label: '2FA Code', type: 'text' },
      },
      async authorize(credentials) {
        // 1. Buscar usuário no PostgreSQL
        // 2. Verificar senha com bcrypt
        // 3. Verificar TOTP com speakeasy
        // 4. Criar sessão
        return user;
      },
    }),
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 dias (lembrar)
  },
  callbacks: {
    async signIn({ user, account, profile }) {
      // Se Google: criar usuário se não existir
      // Audit log
      return true;
    },
  },
});
```

#### 4. Botão no login

```typescript
import { signIn } from 'next-auth/react';

<button onClick={() => signIn('google', { callbackUrl: '/dashboard' })}>
  Entrar com Google
</button>
```

---

## 🔐 E-mail + Senha + TOTP

### Hashing de senha

```typescript
import bcrypt from 'bcrypt';

const hash = await bcrypt.hash(password, 12);  // 12 rounds = ~250ms
const match = await bcrypt.compare(password, hash);
```

### TOTP (2FA com Google Authenticator)

```typescript
import speakeasy from 'speakeasy';
import qrcode from 'qrcode';

// Setup inicial
const secret = speakeasy.generateSecret({
  name: 'Dev Maniac\'s Hub',
  issuer: 'Dev Maniac\'s',
  length: 32,
});

const qrCodeUrl = await qrcode.toDataURL(secret.otpauth_url);

// Validar código
const verified = speakeasy.totp.verify({
  secret: user.totpSecret,
  encoding: 'base32',
  token: totpCode,
  window: 1,  // aceita ±30s de diferença
});
```

### Setup flow (1ª vez)

1. Usuário cria conta com e-mail + senha
2. Hub gera `secret` TOTP único
3. Mostra QR Code pro usuário escanear no Google Authenticator
4. Usuário digita 1 código pra confirmar setup
5. `secret` é salvo (criptografado) no PostgreSQL

### Login flow (toda vez)

1. E-mail + senha (bcrypt verify)
2. TOTP code (speakeasy verify, window=1)
3. Cria sessão JWT (cookie HttpOnly)

---

## 🛡️ Segurança em camadas

| Camada | Implementação |
|---|---|
| **HTTPS** | Cloudflare Tunnel + TLS 1.3 ✅ |
| **Cookie HttpOnly** | NextAuth default |
| **Cookie Secure** | Apenas HTTPS |
| **SameSite=Lax** | CSRF protection |
| **Rate limiting** | 5 tentativas/min por IP |
| **fail2ban** | Bloqueia IP após 10 falhas |
| **Audit log** | Toda tentativa (sucesso/falha) |
| **2FA obrigatório** | Google OU TOTP |
| **Session timeout** | 30 dias (com "lembrar") ou 24h |
| **Password complexity** | Mínimo 12 chars + 1 maiúscula + 1 número |

---

## 📋 Checklist de setup (quando você criar Google OAuth)

- [ ] Criar projeto no Google Cloud Console
- [ ] Configurar OAuth consent screen
- [ ] Criar OAuth Client ID (Web app)
- [ ] Adicionar redirect URIs (prod + dev)
- [ ] Adicionar JavaScript origins
- [ ] Copiar Client ID + Secret pro `.env`
- [ ] Testar fluxo no localhost
- [ ] Deploy no Rocky + tunnel
- [ ] Adicionar `helbertcurcio@gmail.com` como test user
- [ ] Submeter pra verificação (se for pra outros usuários)

---

## 🔄 Recuperação de conta

Se perder acesso:

| Cenário | Solução |
|---|---|
| **Esqueceu senha** | Magic link por e-mail (15 min expira) |
| **Perdeu 2FA** | Backup codes (gerados no setup) |
| **Perdeu Google** | Recovery e-mail + código de 8 chars |
| **Conta bloqueada** | Admin (você) libera via painel |

---

## 📊 Comparação: Google vs E-mail+TOTP

| Critério | Google OAuth | E-mail + Senha + TOTP |
|---|---|---|
| **Velocidade mobile** | � 1 toque | 🟡 30s (digitar + 2FA) |
| **Segurança** | 🟢 Google cuida | 🟢 TOTP próprio |
| **Offline** | 🔴 Precisa Google | 🟢 Funciona offline |
| **Privacidade** | 🟡 Google sabe que você logou | 🟢 Hub não depende de terceiro |
| **Setup** | 🟢 Zero (já tem conta) | 🟡 Precisa configurar 2FA |
| **Recuperação** | 🟢 Google | 🟡 Backup codes |

**Recomendação:** oferecer ambos. Google como padrão mobile, e-mail+TOTP pra fallback / admin.

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
