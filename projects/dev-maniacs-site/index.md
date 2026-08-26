---
titulo: Dev Maniac's Site (Portfólio) — Índice do Projeto (UNKNOWN — NOT DOCUMENTED)
tags: [dev-maniacs-site, project-index, unknown, needs-po, portfolio]
atualizado: 2026-08-26
status: draft
---

# 🌐 Dev Maniac's Site (Portfólio) — Project Index

> **Slug:** `dev-maniacs-site`
> **Status:** **`UNKNOWN — NOT DOCUMENTED — NEEDS PO DECISION`**

---

## ⚠️ 1. Por que este projeto está como `UNKNOWN`

A pasta `projects/dev-maniacs-site/` foi criada em 26/08/2026 como parte da evolução do DM-CEREBRO para o formato multi-projeto (ver [`ARCHITECTURE-EVOLUTION-2026-08-26.md`](../../ARCHITECTURE-EVOLUTION-2026-08-26.md)).

**Não existe conteúdo técnico** sobre `dev-maniacs-site` no DM-CEREBRO hoje:
- Nenhum `README.md`, `status.md`, `arquitetura.md`, `deploy.md`, `brand.md`, `accessibility.md`, `legal.md` no DM-CEREBRO.
- Nenhuma pasta `projects/dev-maniacs-site/` pré-existente.

**O que EXISTE** (conhecimento tangencial, não canônico):

- `wiki/infra-servidor-rocky.md` registra: `devmaniacs.com.br` (:2543) — `portifoliodev` (Next.js / SSG). Esse é o **site institucional** da Dev Maniac's.
- `MEMORY.md` menciona: "Portfólio Dev Maniac's: `https://devmaniacs.com.br/` (Next.js / SSG na porta 2543 com RadierHUB no topo)."
- Em `dm-erp/docs/PROJECT_STATE.md` (canônico) há referência: "Portfólio Dev Maniac's: `https://devmaniacs.com.br/` (:2543) — 🟢 ONLINE (RadierHUB como Projeto #01)".

> Estes registros **são** conhecimento existente. Foram incorporados abaixo como **referências**, não como especificação técnica completa.

## 2. Conhecimento Existente (apenas o confirmado)

| Item | Fonte | Confiança |
| :--- | :--- | :--- |
| Domínio: `https://devmaniacs.com.br/` | `dm-erp/docs/PROJECT_STATE.md` §1 | Alta |
| Stack: Next.js / SSG | `MEMORY.md`, `wiki/infra-servidor-rocky.md` | Média (não oficial) |
| Porta: :2543 | `wiki/infra-servidor-rocky.md` | Média |
| Status: ONLINE | `dm-erp/docs/PROJECT_STATE.md` | Alta |
| Posicionamento: RadierHUB é o "Projeto #01" do portfólio | `dm-erp/docs/PROJECT_STATE.md` §1 | Alta |
| Container: `portifoliodev` | `wiki/infra-servidor-rocky.md` | Média |

## 3. Conhecimento NÃO Existente (precisa do PO)

- Identidade visual oficial (cores, tipografia, mascote, tom de voz) — não documentada no DM-CEREBRO.
- Estrutura de páginas e seções do site.
- Pipeline de CI/CD.
- Stack detalhada (Next.js versão, fontes, CMS, etc.) — só "Next.js / SSG" genérico.
- Quem mantém / owner técnico.
- ADRs locais.
- Handover local.

## 4. Pendências ao PO (precisa de decisão)

1. **`dev-maniacs-site` é o mesmo que `portifoliodev` (Next.js em :2543)?** (Yes/No).
2. Se sim: **conhece o repositório-fonte** (GitHub local? `/opt/sistemas/portfolio-dev`?)? Onde fica o código?
3. **Há ADRs / decisões de marca registradas em outro lugar** (e.g., `docs/brand/` do dm-erp)?
4. **Escopo**: site institucional estático, blog, área de cases, área de contato com formulário? Cada um tem regras próprias.
5. **Quem é o owner**?

## 5. Cross-references (já existentes)

- `dm-erp/docs/brand/` (assets de marca — não auditei nesta task por ser escopo do dm-erp).
- `dm-erp/docs/PROJECT_STATE.md` §1 (URLs ativas).
- `wiki/infra-servidor-rocky.md` (mapa do servidor).
- `MEMORY.md` (memória global, menciona o portfólio).

## 6. Read Order Provisional (somente após o PO confirmar)

Quando o PO confirmar o escopo, o read order típico será:
- `projects/dev-maniacs-site/index.md` (este arquivo, atualizado)
- `projects/dev-maniacs-site/project-state.md` (a criar)
- `projects/dev-maniacs-site/architecture.md` (a criar)
- `projects/dev-maniacs-site/brand.md` (a criar — pode espelhar `dm-erp/docs/brand/`)
- `global/security-baseline.md` (security)

---

**Owner declarado:** Helbert Moura — Dev Maniac's Systems · **Owner efetivo:** `UNKNOWN — NEEDS PO DECISION`
