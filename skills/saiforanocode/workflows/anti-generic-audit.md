# 🧐 Workflow: Auditoria Estética Anti-Vibecode & Design Quality Gate

> **Regra de Rigor:** Toda crítica estética DEVE ser objetiva, técnica e fundamentada em princípios mensuráveis de usabilidade, acessibilidade, identidade de marca ou ergonomia cognitiva. "Não gostei" não é apontamento de engenharia.

---

## 1. Estrutura do Relatório de Auditoria

Todo relatório de auditoria gerado pelo agente DEVE seguir rigorosamente este formato:

```markdown
# 📋 Relatório de Auditoria Anti-Vibecode: [Nome da Aplicação/Tela]

## 1. Sumário Executivo & Diagnóstico
- **Data da Auditoria:** [Data]
- **Tipo de Sistema:** [Marketing / Showcase / Landing] OU [ERP / Dashboard / Operacional]
- **Vibecode Risk Score:** [X / 100] — Classificação: [Pristine / Low / Moderate / High / Critical]
- **Veredito:** [Aprovado / Aprovação com Ressalvas / Bloqueado para Produção]

---

## 2. Não-Conformidades Identificadas

### [VIBE-001] <Título Curto da Não-Conformidade>
- **PROBLEM:** <Descrição exata do vício visual, layout de IA, card abuse ou quebra detectada>.
- **WHY IT MATTERS:** <Impacto negativo concreto na credibilidade, conversão, usabilidade ou cansaço visual do operador>.
- **EVIDENCE:** <Arquivo, linha de código, seletor CSS, viewport (ex: 375px) ou print de tela>.
- **RECOMMENDATION:** <Solução técnica cirúrgica baseada nas referências do arsenal e tokens do DESIGN.md>.
- **PRIORITY:** P0 (Blocker) | P1 (Alta) | P2 (Média) | P3 (Polimento)

---

## 3. Matriz dos 5 Pilares de Inspeção

| Pilar | Status | Pontos Críticos Avaliados |
| :--- | :---: | :--- |
| **1. Autenticidade & Marca** | [PASS/FAIL] | Ausência de gradientes roxo/azul clichês, fotos autênticas, assinatura visual presente. |
| **2. Densidade & Layout** | [PASS/FAIL] | Ausência de card abuse, hierarquia semântica, sem bento grid decorativo vazio. |
| **3. Ergonomia & Teclado** | [PASS/FAIL] | Foco visível (`focus-visible`), touch targets de 48px, atalhos de teclado em ERPs. |
| **4. Dados & Formulários** | [PASS/FAIL] | Alinhamento numérico à direita (`tabular-nums`), labels explícitos, validação inline. |
| **5. Estados & Resiliência** | [PASS/FAIL] | Tríade obrigatória: Empty State acolhedor, Skeletons proporcionais e Error recovery. |
```

---

## 2. Ação Pós-Auditoria

1. **Score ≤ 15 (Pristine):** Aprovado diretamente para publicação/merge.
2. **Score 16 a 35 (Low Risk):** Correções pontuais (P2/P3) executadas no mesmo branch.
3. **Score ≥ 36 (Moderate/High/Critical):** Bloqueio imediato do merge. Disparar **Modo Reparo** (`workflows/audit-existing.md`) atacando primeiramente os itens P0 e P1.
