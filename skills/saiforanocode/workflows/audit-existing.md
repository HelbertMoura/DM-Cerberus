# 🛠️ Workflow: Auditoria & Reparo de Sites Existentes (Modo 1)

Este workflow detalha o processo em fases para diagnosticar e recuperar aplicações web e sites que sofrem de vibecode ou invisibilidade para mecanismos de IA.

---

## 🔒 Regra Fundamental: Audit-First, Fix-on-Approval

> **NUNCA** aplique alterações diretamente em produção sem aprovação humana prévia baseada em evidências.

---

## As 7 Fases do Reparo

### FASE 1: Diagnóstico Factual (30-45min)
1. **Captura do Estado Atual:** Execute screenshot da viewport desktop (1440px) e mobile (375px).
2. **Lighthouse / Core Web Vitals:** Medir Performance, Acessibilidade, Melhores Práticas e SEO.
3. **Varredura Axe-core:** Detectar nós com violações de acessibilidade (`critical`, `serious`).
4. **Extração de JSON-LD:** Validar schema.org no Google Rich Results Test.
5. **Checagem de Citações em IAs:** Fazer 3 perguntas de teste em ChatGPT, Claude e Perplexity sobre a empresa.

### FASE 2: Definição de Identidade (Antes de Qualquer Código)
1. Definir paleta de cores institucional de 4 a 6 tons baseados na marca (nunca gradiente roxo padrão).
2. Definir tipografia (1 família Display/Heading + 1 família Body legível).
3. Registrar no `DESIGN.md` do projeto.

### FASE 3: Auditoria dos 50 Itens
- Executar o checklist completo de [`references/anti-vibecode.md`](../references/anti-vibecode.md).
- Classificar cada item em: `PASS (✅)`, `FAIL (❌)` ou `WARNING (⚠️)`.

### FASE 4: Plano de Ação Priorizado (P0 / P1 / P2)
- **P0 (Blockers):** Quebras de layout, falhas graves de acessibilidade, ausência de llms.txt, erros gramaticais gritantes.
- **P1 (Melhorias de Impacto):** Otimização de imagens, schemas ricos de FAQ, refinamento de tipografia.
- **P2 (Polimento):** Microinterações, animações funcionais sutis, meta tags complementares.

### FASE 5: Conserto Cirúrgico (Branch Isolado)
- Seguir a escada Ponytail: menor diff funcional possível.
- Aplicar correções sem reescrever módulos inteiros.

### FASE 6: Revalidação & Evidências
- Capturar screenshot pós-ajuste (*after.png*) e comparar lado a lado.
- Repetir testes automatizados e aferir que violações caíram para zero.

### FASE 7: Camada AEO / GEO
- Publicar `llms.txt` e `llms-full.txt` na raiz.
- Validar indexação e submeter sitemap.
