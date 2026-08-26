---
titulo: DECISIONS.md — Índice/ponte company-level de ADRs (post-r161)
tags: [decisoes, adr, indice, ponte, company-level, post-r161]
atualizado: 2026-08-26
status: ativo
---

# ⚖️ DECISIONS.md — Índice/Ponte Company-Level de Decisões

> **Natureza deste arquivo (2026-08-26):** **índice/ponte** entre os vários cérebros da Dev Maniac's. **NÃO** duplica o conteúdo de ADRs de produto.
> **Política de ADRs RadierHUB (e outros produtos `dm-erp`):** novos ADRs do RadierHUB continuam entrando **apenas** em `dm-erp/docs/DECISIONS.md` (canônico).
> **Política de ADRs de outros produtos Dev Maniac's:** cada produto tem o seu próprio `projects/<slug>/decisions.md` local.
> **Histórico preservado:** o conteúdo deste arquivo antes da consolidação r161+ foi arquivado em `archive/historical/decisions-registro-pre-finalize-2026-08.md` (commit `0a1770b`) sem reescrita.

---

## 1. Onde encontrar ADRs por produto

| Produto / Domínio | Repositório | Arquivo canônico |
| :--- | :--- | :--- |
| **RadierHUB (dm-erp)** | `dm-erp` | `docs/DECISIONS.md` (canônico absoluto) |
| Biolar | DM-CEREBRO | `projects/biolar/decisions.md` (criar sob demanda) |
| HelpDev | DM-CEREBRO | `projects/helpdev/decisions.md` (criar sob demanda) |
| DM-PDV | DM-CEREBRO | `projects/dmpdv/decisions.md` (criar sob demanda) |
| APAE Juatuba | DM-CEREBRO | `projects/apae-juatuba/decisions.md` (criar sob demanda) |
| dm-desk | DM-CEREBRO | `projects/dm-desk/decisions.md` (criar sob demanda) |
| dev-maniacs-site | DM-CEREBRO | `projects/dev-maniacs-site/decisions.md` (criar sob demanda) |
| **Hub Remoto de IDEs** (descontinuado) | DM-CEREBRO | `archive/historical/hub-remote-ide.md` (ponteiro) |

> **Texto canônico, link ilustrativo:** o repositório `dm-erp` é, no ambiente atual, vizinho do DM-CEREBRO. O caminho relativo costumeiro é `../migra/dm-erp/docs/DECISIONS.md` (a partir da raiz do DM-CEREBRO); ajuste conforme seu layout local. O **texto** é o que é canônico, não o link.

## 2. Ponteiros para ADRs do RadierHUB (canônico em `dm-erp/docs/DECISIONS.md`)

> **Numeração canônica pós-consolidação r161.** Esta é a **única** numeração válida a partir de 26/08/2026. As numerações legadas que apareciam em cópias antigas deste `DECISIONS.md` raiz foram consolidadas — ver §3.

| ID Canônico | Tema | Texto canônico reside em |
| :--- | :--- | :--- |
| **ADR-001** | Arquitetura Multi-Tenant com `TenantAwareModel` e Bancos Dedicados | `dm-erp/docs/DECISIONS.md` §ADR-001 |
| **ADR-002** | RDO Digital Offline-First com IndexedDB (Dexie) | `dm-erp/docs/DECISIONS.md` §ADR-002 |
| **ADR-003** | Topologia Híbrida de Bancos PostgreSQL 16 | `dm-erp/docs/DECISIONS.md` §ADR-003 |
| **ADR-004** | Esteira Atômica de Formalização 1-Clique | `dm-erp/docs/DECISIONS.md` §ADR-004 |
| **ADR-005** | Módulos Clientes (CRM) e Tarefas (Kanban) com Usabilidade Leiga & Isolamento por Papel | `dm-erp/docs/DECISIONS.md` §ADR-005 |
| **ADR-006** | Módulos Documentos (CNDs) e Notificações In-App | `dm-erp/docs/DECISIONS.md` §ADR-006 |
| **ADR-007** | Code-Splitting Total com React.lazy() & Suspense | `dm-erp/docs/DECISIONS.md` §ADR-007 |
| **ADR-008** | Rebranding Oficial do Produto SaaS para RadierHUB (`radierhub.com.br`) | `dm-erp/docs/DECISIONS.md` §ADR-008 |
| **ADR-009** | Modal de Termos de Uso & Política de Privacidade LGPD Multi-Tenant | `dm-erp/docs/DECISIONS.md` §ADR-009 |
| **ADR-010** | Novo Modelo de Governança e Pipeline Multi-Agente com Gates Estritos | `dm-erp/docs/DECISIONS.md` §ADR-010 |
| **ADR-011** | Encerramento do Bootstrap de Governança — Decisões do Product Owner | `dm-erp/docs/DECISIONS.md` §ADR-011 |
| **ADR-012** | Automação Periódica do Robô SEFAZ DF-e com Cofre A1 Criptografado e Integração Financeira Atômica | `dm-erp/docs/DECISIONS.md` §ADR-012 |
| **ADR-013** | Blindagem Estrutural de Autenticação, Controle de Acesso e Isolamento Multi-Tenant | `dm-erp/docs/DECISIONS.md` §ADR-013 |
| **ADR-014** | Revisão da Hierarquia de Roteamento de IA (AI-GOV-STACK-HIERARCHY-008) | `dm-erp/docs/DECISIONS.md` §ADR-014 |

> **Não duplicar** o texto integral desses ADRs aqui. Eles vivem em `dm-erp/docs/DECISIONS.md` (canônico absoluto). Para a fundamentação, consulte a fonte.

## 3. Mapeamento de IDs Legados → Canônicos (pós-r161)

> Esta tabela foi **confirmada pelo QA** em `DM-CEREBRO-PENDING-REVIEW-007`. Use-a sempre que encontrar referência a ID legado.

| Tema | ID Legado (pré-consolidação) | ID Canônico (pós-r161) |
| :--- | :--- | :--- |
| Topologia híbrida de bancos | ADR-001 (legado) | **ADR-003** |
| Esteira atômica de formalização | ADR-002 (legado) | **ADR-004** |
| CRM + Kanban | ADR-008 (legado) | **ADR-005** |
| Documentos/CNDs + Notificações | ADR-009 (legado) | **ADR-006** |
| Code-splitting | ADR-010 (legado) | **ADR-007** |
| Rebranding RadierHUB | ADR-011 (legado) | **ADR-008** |
| Termos/LGPD | ADR-012 (legado) | **ADR-009** |

> **Cuidado:** a regra acima é **só para RadierHUB**. Outros produtos Dev Maniac's (Biolar, HelpDev, etc.) ainda usam numeração local independente. Não aplicar a equivalência cross-produto.

## 4. Ponteiro histórico (Hub Remoto de IDEs)

O projeto **Hub Remoto de IDEs** foi **descontinuado em 23/08/2026** por decisão do PO Helbert Moura. Para preservar a **rastreabilidade** da decisão (e dos ADRs Google OAuth, CSS isolado, login TOTP, etc. gerados durante sua vida), o registro canônico fica em:

- `archive/historical/hub-remote-ide.md` (DM-CEREBRO) — ponteiro + linha do tempo factual.
- `archive/historical/decisions-registro-pre-finalize-2026-08.md` (DM-CEREBRO) — preservação do `DECISIONS.md` raiz **antes** da consolidação r161+ (inclui ADRs 008, 010, 011 do legado Hub Remoto que foram movidas para cá).

> **Não reviver** ADRs antigos do Hub Remoto nem reaplicá-los ao RadierHUB ou outros produtos. Eles estão arquivados apenas para auditoria.

## 5. Política de novas decisões

1. **RadierHUB:** criar ADR apenas em `dm-erp/docs/DECISIONS.md` (formato padrão do repositório `dm-erp`). Adicionar ponteiro em §2 desta raiz se for ADR novo.
2. **Outros produtos Dev Maniac's:** criar ADR em `projects/<slug>/decisions.md` (criar o arquivo na primeira decisão). Adicionar ponteiro em §1 desta raiz.
3. **Cross-produto / governança AI / segurança cross-produto:** registrar em `dm-erp/docs/DECISIONS.md` (canônico AI). Adicionar ponteiro em §1 desta raiz.
4. **Mudança de decisão:** criar **novo** ADR superseding. Nunca reescrever o anterior. Aplica-se inclusive a esta raiz.

## 6. Histórico de mudanças desta raiz

- **2026-08-22** — Estrutura inicial 10/10 do DM-CEREBRO. ADRs registrados localmente (era raiz de verdade).
- **2026-08-23** — ADRs do Hub Remoto de IDEs adicionados durante a vida do projeto (Google OAuth, login v2.1, CSS isolado, Hub v3.0).
- **2026-08-23** — Descontinuação do Hub Remoto de IDEs registrada.
- **2026-08-25/26** — dm-erp: TASK-SEFAZ-001/002 + TASK-GOV-AI-008 / ADR-014 concluídos.
- **2026-08-26** — **Consolidação r161+:** este arquivo é transformado em **índice/ponte company-level**. Conteúdo literal pré-consolidação arquivado em `archive/historical/decisions-registro-pre-finalize-2026-08.md` (commit `0a1770b`). Novos ADRs RadierHUB continuam entrando **apenas** em `dm-erp/docs/DECISIONS.md`.

---

**Owner:** Helbert Moura — Dev Maniac's Systems · **Status:** ATIVO (índice/ponte, **não** repositório de ADRs)
