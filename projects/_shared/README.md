---
titulo: Conhecimento Cross-Product (Compartilhado)
tags: [shared, cross-product, padrões]
atualizado: 2026-08-22
status: ativo
---

# 📦 _shared/ — Conhecimento Compartilhado entre Produtos

Esta pasta contém padrões, utilitários e conhecimento que **se aplicam a múltiplos produtos** da Dev Maniac's.

---

## 🎯 Quando Criar Arquivo Aqui

✅ **USE** quando o conhecimento se aplica a 2+ produtos:
- Ex: Padrão de autenticação reutilizado em CanteiroHUB + Biolar + HelpDev
- Ex: Padrão de deploy Docker comum a todos
- Ex: Padrão de UI (Industrial Solid-State)

❌ **NÃO USE** quando o conhecimento é específico de um produto:
- Vai pra `projects/<slug>/`

---

## 📂 Estrutura Sugerida

```
_shared/
├── README.md           ← este arquivo
├── padroes-ui.md       ← padrões visuais reutilizáveis
├── padroes-deploy.md   ← padrões Docker/CI/CD
├── padroes-auth.md     ← padrões de autenticação/SSO
└── bibliotecas-comuns.md  ← libs Python/JS compartilhadas
```

---

**Última atualização:** 22 de Agosto de 2026
