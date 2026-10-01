# TASK-ID: TASK-CERBERUS-BACKEND-AUTH-PROFILE-001
> **Projeto:** DM-Cerebro (Cerberus Memory Engine)  
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)  
> **Responsavel:** Codex (Backend & Logic Engineer)  
> **Risco:** 2 (MEDIUM)

---

## 🎯 Objetivo Geral
Implementar endpoints REST de Health Publico, Perfil de Usuario, Troca de Senha Segura e Gestao de 2FA TOTP em engine/server.py e engine/auth.py, com testes automatizados em tests/test_auth_profile.py e atualizacao do Dockerfile / docker-compose.yml.

---

## 📋 Especificacao Detalhada dos Endpoints

### 1. Healthcheck Publico (Sem Autenticacao)
- **Rotas:** GET /api/health e GET /healthz
- **Autenticacao:** NENHUMA (publico)
- **Resposta:** Status 200 OK, Content-Type: application/json; charset=utf-8
- **Body:** {"status": "ok", "service": "cerberus-inspector", "version": "1.0.0"}
- **Atualizacao de Infra:**
  - Em Dockerfile: Atualizar HEALTHCHECK para CMD curl -fsS http://127.0.0.1:7331/api/health || exit 1
  - Em docker-compose.yml: Atualizar healthcheck test para ["CMD", "curl", "-fsS", "http://127.0.0.1:7331/api/health"]

### 2. Dados do Usuario Logado (Perfil)
- **Rota:** GET /api/v1/auth/me
- **Autenticacao:** Obrigatoria (Sessao com 2FA verificado)
- **Resposta:** Status 200 OK, Content-Type: application/json
- **Body:** {"email": user.email, "is_active": user.is_active, "has_2fa": bool(user.totp_secret), "created_at": user.created_at}

### 3. Troca de Senha Segura
- **Rota:** POST /api/v1/auth/change-password
- **Autenticacao:** Obrigatoria
- **Request Body (JSON):** {"current_password": "...", "new_password": "..."}
- **Regras de Negocio:**
  1. Valida current_password via verify_password(current_password, user.password_hash). Se invalida, retorna 400 Bad Request com {"error": "Senha atual incorreta."}.
  2. Valida se new_password tem pelo menos 6 caracteres. Se menor, retorna 400 Bad Request com {"error": "Nova senha deve ter pelo menos 6 caracteres."}.
  3. Atualiza user.password_hash = hash_password(new_password).
  4. Salva no UserStore e retorna 200 OK com {"ok": true, "message": "Senha alterada com sucesso."}.

### 4. Gestao de 2FA TOTP

#### 4.1 Iniciar Setup de 2FA (Gerar Segredo & QR Code)
- **Rota:** POST /api/v1/auth/2fa/setup
- **Autenticacao:** Obrigatoria
- **Regra:**
  - Gera novo segredo Base32 via TOTP.generate_secret().
  - Gera QR Code SVG via totp_qr_svg(secret, user.email, issuer="DevManiacs-Cerberus").
  - Gera URI otpauth://totp/DevManiacs-Cerberus:...
- **Resposta:** 200 OK, Content-Type: application/json
  {"secret": secret, "qr_svg": qr_svg, "uri": otpauth_uri}

#### 4.2 Validar e Ativar 2FA
- **Rota:** POST /api/v1/auth/2fa/verify-and-enable
- **Autenticacao:** Obrigatoria
- **Request Body (JSON):** {"secret": "...", "code": "..."}
- **Regra:**
  - Valida o codigo de 6 digitos via TOTP.from_base32(secret).verify(code).
  - Se invalido, retorna 400 Bad Request com {"error": "Codigo TOTP invalido ou expirado."}.
  - Se valido, persiste user.totp_secret = secret no UserStore e retorna 200 OK com {"ok": true, "message": "2FA ativado com sucesso."}.

#### 4.3 Desativar 2FA
- **Rota:** POST /api/v1/auth/2fa/disable
- **Autenticacao:** Obrigatoria
- **Request Body (JSON):** {"password": "..."}
- **Regra:**
  - Valida verify_password(password, user.password_hash).
  - Se invalida, retorna 400 Bad Request com {"error": "Senha incorreta."}.
  - Se valida, limpa user.totp_secret = "" no UserStore e retorna 200 OK com {"ok": true, "message": "2FA desativado com sucesso."}.

### 5. Roteamento & Fallback Web
- Em engine/server.py:
  - Se rota requisitada for /login, tratar como /auth/login (ou redirecionar via HTTP 303 para /auth/login).
  - Se usuario nao autenticado acessar qualquer rota no navegador (com cabecalho Accept contendo text/html), redirecionar via HTTP 303 para /auth/login.

---

## 🧪 Criterios de Aceite & Testes Obrigatorios
1. Criar tests/test_auth_profile.py com testes cobrindo todos os fluxos acima.
2. Executar python -m unittest discover tests com 100% PASS e 0 quebras.
3. Produzir TASK REPORT contendo a lista de arquivos alterados e saida dos testes.
