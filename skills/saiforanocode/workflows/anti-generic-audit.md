# 🧐 Workflow: Auditoria Estética Anti-Vibecode (Design Quality Gate)

Auditoria objetiva e orientada a evidências para detectar e documentar clichês visuais, layouts de template e estética genérica de IA.

---

## 🛑 Regra de Rigor: Não Audite com Base Apenas em Gosto

Cada apontamento deve ser fundamentado em **princípios consolidados de UX, usabilidade, acessibilidade ou identidade de marca**.

Para cada inconsistência encontrada, utilize obrigatoriamente a estrutura:

```markdown
### [ITEM-00X] <Título Curto da Não-Conformidade>
- **PROBLEM:** <Descrição exata do problema visual ou estrutural observado>.
- **WHY IT MATTERS:** <Impacto negativo concreto no usuário, na conversão ou na credibilidade da marca>.
- **EVIDENCE:** <Caminho do arquivo, linha de código, print ou seletor CSS específico>.
- **RECOMMENDATION:** <Sugestão técnica e direta de correção baseada no DESIGN.md e nas bibliotecas maduras>.
- **PRIORITY:** P0 (Blocker) | P1 (Alta) | P2 (Média) | P3 (Polimento)
```

---

## Critérios de Inspeção

1. **Autenticidade vs Template:** O layout parece ter sido desenhado para este negócio específico ou é uma colagem genérica de cards com bordas arredondadas e gradiente roxo?
2. **Hierarquia & Densidade:** O olhar do usuário sabe imediatamente onde focar? A densidade é adequada à função da página?
3. **Ergonomia & Interatividade:** Os botões possuem feedback claro? Modais e gavetas prendem o foco?
4. **Alinhamento & Espaçamento:** Os espaçamentos obedecem a uma grade matemática consistente?
5. **Acessibilidade Visível:** O contraste de texto atende à WCAG? Há foco visível por teclado?
