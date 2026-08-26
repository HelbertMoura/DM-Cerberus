---
titulo: Security Baseline — Baseline de Segurança cross-produto
tags: [global, security, baseline, multi-tenant, pii, segredos]
atualizado: 2026-08-26
status: ativo
---

# 🔐 Security Baseline — DM-CEREBRO

> **Documento canônico de segurança do dm-erp:** arquivo `auditorias-tecnicas-cto.md` dentro do repositório `dm-erp` (fila oficial de auditorias do CTO GLM-5.3 Max) + ADRs 012, 013 do dm-erp. Em ambiente onde `dm-erp` é vizinho do DM-CEREBRO, o caminho relativo a partir deste arquivo costuma ser `../../migra/dm-erp/docs/brain/wiki/auditorias-tecnicas-cto.md`; ajuste conforme seu layout local. O **texto** é o que é canônico.
> **Este arquivo** é o baseline cross-produto. Cada produto pode adicionar regras mais estritas, mas não pode afrouxar este baseline.

---

## 1. Princípios Inegociáveis (qualquer produto Dev Maniac's)

1. **Nenhum segredo em texto-claro no repositório.** Senhas, tokens, chaves privadas, certificados, `.env` reais — **NUNCA** versionados. Usar `.env.example` com placeholders `[CONFIGURADO VIA ENV]`.
2. **Nenhum segredo em logs.** Logs são compartilhados; ofuscar/omitir segredos antes de logar.
3. **Multi-tenant (quando aplicável) é inviolável.** Todo model de negócio herda de `TenantAwareModel` (dm-erp) ou equivalente. Toda query filtra por tenant. Zero `objects.all()` sem contexto.
4. **PII isolada.** CPF, RG, prontuário médico, dados de RH — sempre atrás de permissão explícita; nunca no front público.
5. **HTTPS obrigatório em produção.** Tráfego público via Cloudflare Tunnel com TLS 1.3.
6. **Backups verificados.** Política de backup + restore testado (ver `dm-erp/wiki/auditorias-tecnicas-cto.md` Item 6).
7. **Rotação de credenciais.** Credenciais expostas no histórico git devem ser rotacionadas; rotação é responsabilidade do PO (não do agente).
8. **Auditoria adversarial antes de Risk 3–4 em produção.** `GLM-5.3 Max` (CTO) emite parecer formal.

---

## 2. Padrões Mínimos por Tipo de Sistema

### 2.1. Web/API
- Headers: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (ou `SAMEORIGIN` se necessário), `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy` apropriado.
- Cookies: `HttpOnly`, `Secure`, `SameSite=Lax` (ou `Strict` quando possível).
- CSRF: tokens por sessão; verificação em mutações.
- Rate limiting em endpoints públicos.
- Validação server-side de toda entrada.

### 2.2. Banco de Dados
- Credenciais via `.env`, **nunca** hardcoded.
- Conexão via TLS (PostgreSQL `sslmode=require` ou superior).
- Migrations: preferencialmente aditivas; destrutivas só com plano formal + janela de manutenção.
- `select_for_update` em esteiras multi-step que envolvem transição de estado sequencial (ver `LEARN-001` do `dm-erp`).
- Backups testados periodicamente (restore drills).

### 2.3. Autenticação
- Senhas: bcrypt ou argon2id (nunca MD5/SHA1).
- 2FA / TOTP recomendado para acessos administrativos.
- JWT com `aud` distinto para `control-plane` vs `tenant-api` (ver ADR-013 do dm-erp).
- Tokens com tempo de vida limitado + refresh.

### 2.4. Storage / Arquivos
- Pasta `uploads/` (ou equivalente) **fora** da árvore servida.
- Validação de MIME real (magic bytes), não só extensão.
- Nomes de arquivo sanitizados.
- Antivirus / scanner para uploads sensíveis.

---

## 3. Política de Comunicação Pública

Princípio registrado em `LEARN-009` do dm-erp:

1. **PII nunca no front público** (e-mail, telefone, conta pessoal).
2. **Stack tecnológica específica nunca no front público** (concorrentes inferem estratégia).
3. **Contexto pessoal/profissional nunca no front público** ("canteiro", "bolso" — só em docs internos).
4. **Identidade vem de marca + mascote + logo**, não de copy descritiva.

> Aplica-se a qualquer página pré-auth (login, marketing, error, offline) e metadata pública (`<meta>`, `manifest.webmanifest`, og:image alt text).

---

## 4. Auditoria e Pendências Globais

- **`SEC-CRIT-001`** (dm-erp): escalada de privilégio via `TenantUser` e `SUPERADMIN_MASTER`. Em remediação.
- **`SEC-CRIT-002`** (dm-erp): isolamento cross-tenant em shared database. Em remediação.
- Auditoria de cada produto **local**: `projects/<slug>/security.md` (quando aplicável).

---

## 5. Quando escalar para o CTO (GLM-5.3 Max)

- Mudança em esquema de auth/SSO.
- Mudança em estratégia de multi-tenancy ou isolamento.
- Mudança em criptografia / cofre / certificados.
- Mudança em topologia de banco de dados com impacto cross-produto.
- Decisão de exposição de PII ou dado sensível.
- Incidente de segurança em produção.

---

**Última atualização:** 26 de Agosto de 2026 · Mantido por: Helbert Moura — Dev Maniac's Systems
