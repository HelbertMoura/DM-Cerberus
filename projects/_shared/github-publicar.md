---
titulo: Instruções para Publicar DM-Cerebro no GitHub
tags: [github, git, procedimento, shared]
atualizado: 2026-08-22
status: ativo
---

# 📤 Como Publicar o DM-Cerebro no GitHub Privado

## 🎯 Por Que Fazer Isso

- **Versionamento real** entre as 3 IAs (Gemini, M3, Hermes) — sem conflito
- **Backup automático** off-site (GitHub mantém snapshots diários)
- **Histórico auditável** de toda mudança
- **Acesso de emergência** de qualquer lugar

---

## � Passo a Passo

### 1. Criar o repositório no GitHub

1. Acesse: https://github.com/new
2. **Owner:** DevManiacs (sua org) ou conta pessoal
3. **Nome:** `dm-cerebro`
4. **Visibilidade:** 🔒 **Private** (CRÍTICO — contém dados internos)
5. � NÃO marcar "Add a README"
6. ❌ NÃO marcar "Add .gitignore"
7. � NÃO marcar "Choose a license"
8. Clicar **Create repository**

### 2. Configurar autenticação SSH (recomendado)

Se você já tem chave SSH configurada no GitHub, pule pra Passo 3.

```powershell
# Gerar chave (se não tiver)
ssh-keygen -t ed25519 -C "helbertcurcio@gmail.com"

# Copiar chave pública
Get-Content ~/.ssh/id_ed25519.pub | clip

# Adicionar no GitHub:
# Settings → SSH and GPG keys → New SSH key → colar
```

### 3. Adicionar remote e fazer push

```bash
cd "C:/Users/Helbert/Desktop/DM-Cerebro/"

# Adicionar origin
git remote add origin git@github.com:DevManiacs/dm-cerebro.git

# Verificar
git remote -v

# Push inicial (forçar porque local já tem commits)
git push -u origin main --force

# Push dos arquivos de backup e procedimentos novos
git push origin main
```

### 4. Configurar proteção da branch main

No GitHub:
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. ✅ Require pull request reviews before merging
4. ✅ Require status checks to pass before merging
5. Salvar

### 5. Configurar backup automático (opcional)

Já documentado em `backup-procedimento.md` — clona o repo no Rocky e roda `backup-dm-cerebro.sh` via cron.

---

## 🔐 Segurança

| Item | Status |
|---|---|
| Repositório **privado** | ✅ Obrigatório |
| SSH key com passphrase | ✅ Recomendado |
| 2FA no GitHub | ✅ Recomendado |
| Não commitar `.env` ou chaves | ✅ Garantido pelo `.gitignore` |
| Não commitar PDFs em `raw/processed/` | ✅ Garantido pelo `.gitignore` |

---

## 📊 Workflow Diário Recomendado

```bash
# Antes de mexer no cérebro
cd "C:/Users/Helbert/Desktop/DM-Cerebro/"
git pull origin main

# Após fazer mudanças
git add .
git commit -m "[tipo] escopo: descrição"
git push origin main
```

**Tipos válidos:** `feat` · `fix` · `docs` · `refactor` · `chore`

**Exemplos:**
- `feat wiki: adicionar protocolo OAuth 2.1`
- `fix biolar: corrigir timezone na fatura`
- `docs brain: atualizar índice com novos produtos`

---

## 🆘 Em Caso de Erro

### "Permission denied (publickey)"
Chave SSH não configurada. Voltar ao Passo 2.

### "Repository not found"
URL do remote errado. Verificar com:
```bash
git remote -v
git remote set-url origin git@github.com:DevManiacs/dm-cerebro.git  # corrigir
```

### "Updates were rejected"
Branch local divergiu. Forçar push (cuidado):
```bash
git push -u origin main --force
```

---

**Última atualização:** 22/08/2026 · **Aguardando execução manual do Helbert**
