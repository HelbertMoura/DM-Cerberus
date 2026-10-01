# 🛠️ Workflow: Auditoria & Reparo de Interfaces Existentes (Modo Reparo)

> **Regra Fundamental (Audit-First):** NUNCA altere código em produção antes de concluir o inventário completo de 13 passos, calcular o Vibecode Risk Score e obter aprovação explícita do PO com base no plano priorizado.

---

## 1. O Inventário Diagnóstico de 13 Passos

Antes de escrever qualquer linha de CSS ou refatorar componentes, o agente executa a varredura factual:

1. **Captura Visual Multi-Viewport:** Registrar screenshots em `1440px` (Desktop), `768px` (Tablet) e `360px–375px` (Mobile estreito).
2. **Inventário Cromático & Contraste:** Mapear todas as cores hexadecimais em uso. Identificar gradientes roxo/azul clichês, baixo contraste (<4.5:1) e dispersão de cores ("Rainbow UI").
3. **Inventário Tipográfico:** Identificar famílias de fontes carregadas, tamanhos soltos fora de escala hierárquica e ausência de `tabular-nums` em tabelas numéricas.
4. **Inventário de Ícones & Emojis:** Varrer a base em busca de mistura de bibliotecas (ex.: FontAwesome + Lucide) ou uso de emojis decorativos (🚀, 💡, 🔥) em cards e botões.
5. **Inventário de Estrutura & Card Abuse:** Contar o número de cards aninhados na viewport. Identificar bento grids desconexos e excesso de `rounded-2xl` / `rounded-3xl`.
6. **Inventário de Semântica & Primitivas:** Checar tags HTML. Identificar `<div onClick>` ou `<span>` substituindo `<button>` e `<a>` nativos.
7. **Inventário de Acessibilidade (Axe-core):** Executar auditoria de acessibilidade para detectar nós com violações `critical` e `serious`, verificar anéis de foco (`focus-visible`) e labels de formulário.
8. **Inventário de Estados Críticos:** Testar a tela sem dados (Empty State), em carregamento (Loading Skeleton) e sob falha de rede (Error State).
9. **Inventário de Tabelas & Densidade:** Em sistemas de gestão e backoffice, verificar se há alinhamento numérico à direita, fixação de cabeçalho e colunas travadas (*pinning*).
10. **Inventário de Motion & Transições:** Medir tempos de animação. Identificar *Design Theater* (contadores girando, delays em cascata > 150ms) e checar suporte a `prefers-reduced-motion`.
11. **Inventário de Dependências & Licenças:** Varrer `package.json` para detectar pacotes órfãos, licenças proibidas (GPL/AGPL/BSL) ou bundles inchados.
12. **Inventário de Performance (Core Web Vitals):** Medir LCP (< 2.0s), CLS (alvo 0.0) e INP (< 150ms). Detectar imagens sem dimensões explícitas e filtros `backdrop-blur` abusivos.
13. **Inventário de AEO / GEO & Descoberta:** Verificar existência e validade de `llms.txt`, `llms-full.txt`, dados estruturados Schema.org (JSON-LD), `sitemap.xml` e meta tags OpenGraph.

---

## 2. Matriz de Priorização de Reparo (P0 a P4)

Após o inventário, os problemas encontrados são categorizados e atacados estritamente nesta ordem:

| Nível | Categoria | Critério de Defeito | Ação Imediata |
| :---: | :--- | :--- | :--- |
| **P0** | **Critical Blocker** | Quebra funcional no mobile (overflow horizontal), dependência contaminada por licença restritiva (GPL), falha total de foco por teclado, quebra de build. | Bloqueio imediato de deploy. Correção cirúrgica prioritária. |
| **P1** | **High Priority** | Card abuse generalizado, ausência de Empty/Loading states (tela branca), inputs sem labels/erros acessíveis, LCP > 3.0s, ausência de `llms.txt`. | Correção estrutural na primeira sprint de reparo. |
| **P2** | **Medium Priority** | Clichês visuais óbvios de IA (gradientes roxo/azul genéricos, glow neon, bento grid decorativo), emojis em botões/cards, ausência de `tabular-nums`. | Harmonização visual e alinhamento ao `DESIGN.md`. |
| **P3** | **Low / Polish** | Ajuste fino de microinterações (<120ms), calibração de curvas de animação, refinamento de hierarquia tipográfica e espaçamentos. | Polimento de experiência e retenção. |
| **P4** | **Documentation** | Limpeza de CSS legado ou não utilizado, atualização de documentação técnica de design tokens e registro no repositório. | Manutenção contínua e higiene de código. |

---

## 3. Protocolo de Execução Cirúrgica (Escada Ponytail)

1. **Branch Isolado:** Crie um branch específico para o reparo (ex.: `fix/ui-audit-overhaul`).
2. **Diff Mínimo:** Mantenha as correções contidas. Não reescreva módulos inteiros quando um ajuste de classes CSS ou substituição de primitiva resolver.
3. **Validação Before/After:** Registre screenshots comparativos antes e depois da correção para apresentação de evidências ao PO.
4. **Zero Regressão:** Execute suíte de testes de integração/unitários e garanta que nenhuma funcionalidade de negócio foi quebrada.
