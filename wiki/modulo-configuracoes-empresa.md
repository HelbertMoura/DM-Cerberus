# ⚙️ Configurações da Empresa (Tenant Settings) & Versionamento v1.0.0-ALPHA
> **Módulo:** 14 · Gestão de Usuários, Identidade da Marca, SMTP e Segurança do Cliente  
> **Sistema:** CanteiroHUB (Dev Maniac's) · Instância Teenus Gestão  
> **Versão Oficial:** `v1.0.0-ALPHA (Build 2026.08)`  
> **Atualizado em:** 22 de Agosto de 2026

---

## 🎯 1. Visão Geral
O administrador da construtora (Diretor Geral ou Engenheiro Chefe) precisa de um painel de controle próprio — **distinto do Master Admin da Dev Maniac's** — para gerenciar sua empresa:

1. **Gestão de Usuários & Acessos da Equipe:**
   - Cadastro e edição de novos usuários (Diretoria, Engenharia, Financeiro, Mestre, Compras).
   - Reset de senhas e bloqueio imediato de contas.
   - Matriz granular de permissões por módulo contratado.

2. **Identidade Visual & Personalização da Marca:**
   - Nome de exibição e razão social da construtora.
   - Cor primária institucional aplicada no cabeçalho de minutas e relatórios.
   - Upload do logotipo oficial (PNG/WebP transparente).

3. **Servidor SMTP Próprio:**
   - Configuração de host SMTP (`@construtorateenus.com.br`), porta, usuário, senha e TLS.
   - Teste de disparo de e-mail em tempo real.

4. **Políticas de Segurança & 2FA:**
   - Ativação de autenticação em dois fatores (2FA) para toda a equipe.
   - Bloqueio de sessões simultâneas para impedir compartilhamento indevido de senhas.

5. **Dados Cadastrais & Fiscais:**
   - CNPJ, Inscrição Estadual, Registro CREA/CAU e Website oficial.
