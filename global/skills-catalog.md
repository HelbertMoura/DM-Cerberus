---
titulo: skills-catalog.md — Catálogo Oficial de Skills Externas Adotadas
tags: [skills, catalogo, governanca, runtime, agentes]
atualizado: 2026-09-05
status: ativo
---

# 📚 Skills Catalog — DM-Cerebro

> **Função:** registro canônico das skills **externas** (terceiros) adotadas pela Dev Maniac's, com origem, licença, guardrails e onde vivem.
> **Regra de ouro:** skill externa só entra via avaliação (encaixe no pool + inspeção de conteúdo + licença) e fica registrada AQUI. A fonte canônica versionada no Git é `C:\DevManiacs\DM-Cerebro\skills/`. Os runtimes operacionais ativos são espelhados em `~/.claude/skills/` (Claude Code: painéis M3/M2.7/Flash/5.3) e `~/.gemini/config/skills/` (Gemini / Antigravity Maestro).

## 1. Ponytail (dietrichgebert/ponytail · MIT · 100k+ stars)

**O quê:** escada de decisão obrigatória (deletar > reaproveitar > simplificar > escrever) que força o agente a justificar código novo antes de escrever. Operacionaliza a regra 5 do FIRST-TIME-RIGHT ("diff mínimo").
**Instaladas (03-04/09/2026):** `ponytail` (escada na implementação — M3/M2.7), `ponytail-review` (caça sobre-engenharia no QA — Flash), `ponytail-audit` (auditoria de repo inteiro).
**Guardrails:** simplificar implementação NÃO sobrepõe decreto do GLM-5.3 (arquitetura não é alvo da escada). Evidência: [JetBrains test](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/) confirma corte de tokens; é skill de prompt, não garantia.

## 2. Agent Skills do Addy Osmani (addyosmani/agent-skills · MIT · 92k stars)

**O quê:** 25 skills de engenharia sênior (spec-first, TDD, gates). **Cherry-pick deliberado** — ~70% do pack colide com skills canônicas nossas (TDD, debugging, review, plans, verification já existem com versão da casa; instalar tudo = colisão de opiniões).
**Instaladas (04-05/09/2026), só o que era novo:** `spec-driven-development`, `constraint-driven-development`, `code-simplification`, `security-and-hardening`, `observability-and-instrumentation`, `documentation-and-adrs`.
**Não instaladas por colisão:** performance-optimization (existe a nossa), TDD/debugging/review/plans/verification/etc (versões canônicas da casa prevalecem).

## 3. Graphify (Graphify-Labs/graphify · Apache-2.0/MIT · 115k stars)

**O quê:** indexa codebase em grafo de conhecimento consultável (AST tree-sitter local, ~40 linguagens, **zero LLM em modo code-only**, nada sai da máquina). Agente consulta o grafo em vez de reler arquivos.
**Instalação (05/09/2026):** tool `uv tool install graphifyy` (PyPI com dois Y — cuidado typo-squat; verificado: URLs apontam pro repo oficial) + skill `/graphify` registrada em `~/.claude/skills/graphify/` + ponteiro em `~/.claude/CLAUDE.md`.
**Piloto validado (radierhub-marketing-f1, 05/09):** 7719 nós, comunidades detectadas, query "LeadForm WhatsApp" retornou mapa exato das variáveis/arquivos/imports em segundos. Artefato `graphify-out/` no .gitignore do repo.
**Guardrails obrigatórios:**
1. **Grafo = mapa, não território**: indexado fica velho; regenerar no início de sprint (`/graphify .`); mudanças sensíveis = confirmar no código real.
2. **QA/gate de segurança (5.3, auditoria) NUNCA usa grafo** — lê código real, sempre.
3. Build code-only direto por CLI exige os passos A/B/C da skill (fast path: semantic vazio + merge + build); reconstrução por cache AST documentada em `migra/scratch/seg-glm-20260903/graphify-from-cache.py`.

## 4. saiforanocode (Dev Maniac's · Metodologia Canônica V2 · MIT)

**O quê:** Roteador progressivo anti-vibecode, enriquecimento AEO/GEO e qualidade frontend. Purgou o monólito de 1.082 linhas em um roteador raiz (<80 linhas) com 8 referências e 5 workflows carregados sob demanda.
**Instalada em:** `DM-Cerebro/skills/saiforanocode/` e espelhada nos runtimes Claude e Gemini.
**Guardrails:** *Audit-first, fix-on-approval*; anonimização técnica obrigatória; pt-BR impecável; clichês de IA (gradiente roxo, glassmorphism, bento grids gratuitos) proibidos como escolhas automáticas.

## 5. frontend-toolbox (Dev Maniac's · Catálogo de Capacidades V2)

**O quê:** Matriz de decisão de engenharia frontend. Integra primitivas maduras (Radix, Base UI, TanStack), ferramentas especializadas (**Shader Gradient**), referências visuais (**Refero Styles**) e bibliotecas opcionais (**Cult UI**).
**Guardrails:** Component library NÃO define a identidade visual (quem define é o `DESIGN.md`); **Manus** é referência externa experimental, NÃO integrado ao core; nunca instalar biblioteca pesada para botão simples.

## Pendências avaliadas (adiadas pelo PO em 04/09)

- **i-have-adhd** (formato ação-primeiro, MIT) — instalar quando quiser (risco zero).
- **OpenSEO** (MCP SEO/rank) — pós-cutover RadierHUB.
- **Strix** (pentest autônomo com PoC) — só com inspeção de código e SÓ em local/homolog; candidato a complementar a lane Codex · Adversarial nos Risk 3 do dm-erp.

## Processo de adoção (para futuras)

1. Avaliar encaixe na matriz do pool (não duplicar skill canônica da casa).
2. Clonar upstream no scratch, inspecionar conteúdo (sanity-scan por exfiltração/injeção de prompt).
3. Armazenar canonicamente em `C:\DevManiacs\DM-Cerebro\skills/` e espelhar para `~/.claude/skills/` e `~/.gemini/config/skills/` (runtimes).
4. Registrar aqui: origem, licença, guardrails, data.
5. Se tocar governança: 1 linha de guarda na diretriz-master do maestri.
