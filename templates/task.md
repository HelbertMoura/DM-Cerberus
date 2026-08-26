---
titulo: Template — TASK
tags: [template, task, universal]
atualizado: 2026-08-26
status: ativo
---

# 📋 TASK-<NÚMERO>: <TÍTULO DA TAREFA>

> **Template oficial.** Substituir placeholders antes de emitir.
> **Antes de preencher:** ler [`/AGENTS.md`](../AGENTS.md) + [`/INDEX.md`](../INDEX.md) + [`/global/ai-governance.md`](../global/ai-governance.md) + [`/global/model-routing.md`](../global/model-routing.md) + `projects/<slug>/index.md` do projeto.

---

## 0. Header de Roteamento (obrigatório)

```text
PROJECT: <project-slug>
TASK: <task-id>
GLOBAL GOVERNANCE: <path do doc de governança relevante>
PROJECT CONTEXT: <path do project/index.md>
RISK: 1 / 2 / 3 / 4
USE MODEL: <Gemini PM | GLM-5.3 Max | GLM-5.3-Flash | MiniMax M3 | MiniMax M2.7-Highspeed | Gemini QA | Opus 4.6/Antigravity>
USE TOOL: <ZCode | MiniMax | Gemini | Antigravity>
MODE: <MEDIUM | HIGH | MAX | N/A>
ROLE: <role do agente>
USE SKILLS: <$skill-name ... ou NONE>
WHY: <1–3 frases justificando a escolha>
ESCALATION CONDITION: <critério claro para escalar para GLM-5.3 Max ou GLM-5.3-Flash MAX>
PARALLEL SAFE: <YES | NO>
SHARED FILES: <[...] ou NONE>
SHARED ENVIRONMENT: <YES | NO>
DEPLOY COLLISION RISK: <LOW | MEDIUM | HIGH | N/A>
```

## 1. Visão Geral & Objetivo

- **Módulo Alvo:** <app / módulo / componente>
- **Problema a Resolver:** <sintoma, gargalo ou necessidade>
- **Motivação & Contexto:** <por que agora; ADR relacionada; origem>
- **Resultado Esperado:** <o que estará funcionando após a entrega>

## 2. Dependências & Pré-Requisitos

- <Ex: Migration X já aplicada, módulo Y ativo, certificado A1 configurado>

## 3. Escopo

- **Dentro do escopo:** <lista explícita>
- **Fora do escopo:** <lista explícita — evita expansão silenciosa>

## 4. Arquivos Envolvidos

- **Criar (NEW):** <caminhos>
- **Modificar (MODIFY):** <caminhos>
- **Excluir (DELETE):** <caminhos, se houver>
- **Arquivos PROIBIDOS nesta TASK:** <ex: core/settings.py, migrations de outros apps>

## 5. Banco de Dados & Modelagem

- **Model(s):** <novos ou existentes; herança obrigatória se aplicável>
- **Campos:** <tipos, índices, constraints>
- **Migrations:** <impacto, plano de rollback>

## 6. Backend & Endpoints

- **Rotas:** <api/v1/...> · **Métodos:** <GET/POST/PUT/DELETE>
- **Permissões:** <IsAuthenticated, HasTenantModule, IsTenantAdmin, ...>
- **Serializers & Validações:** <entrada, erros>

## 7. Frontend

- **Interface:** <paleta, componentes>
- **Ícones:** Lucide-React vetorial, zero emojis
- **Ergonomia Mobile:** ≥ 44px tap targets, sem overflow 360–430px
- **i18n:** PT-BR · EN-US · ES via `useI18n()`

## 8. Regras de Negócio & Edge Cases

1. **Regra 01:** <descrição>
2. **Edge Case 01:** <descrição>

## 9. Segurança, Multi-Tenancy & Permissões

- [ ] Filtro estrito por tenant (quando aplicável)
- [ ] Nenhum dado sensível exposto (LGPD; Portal read-only sem custos)
- [ ] Nenhum segredo hardcoded/versionado

## 10. Critérios de Aceite Inegociáveis

- [ ] Build limpo (frontend TypeScript 0 erros, backend `manage.py check`)
- [ ] Testes cobrindo regras de negócio (evidência, não suposição)
- [ ] Viewport mobile 360–430px sem quebra
- [ ] Alternância i18n sem strings hardcoded
- [ ] Acessibilidade WCAG 2.2 AA (quando frontend)

## 11. Riscos & Rollback

- **Riscos identificados:** <performance, migração, integração>
- **Plano de rollback:** <como reverter com segurança; backup necessário?>

## 12. Definition of Done (DoD)

- [ ] Código implementado e testado localmente
- [ ] Relatório de QA com STATUS = APROVADO (Risk ≥ 2)
- [ ] Parecer do GLM-5.3 Max com VEREDITO = AUTORIZADO (Risk ≥ 3)
- [ ] Documentação afetada atualizada
- [ ] Homologação e deploy autorizados pelo PO

---

> **Não invente detalhes** para preencher campos — campo sem informação aplicável recebe "N/A".
