# 🚫 Anti-Vibecode: Diretrizes & Detecção de AI Slop

> *"Site que parece gerado por IA não converte, não impressiona, não vende. Quem visita em 3 segundos decide se confia ou fecha a aba."*

---

## 1. O que é "Vibecoded" (AI Aesthetic Slop)

"Vibecoded" descreve interfaces geradas por prompts de IA sem curadoria profissional de design. Carregam clichês repetitivos e superficiais que denunciam amadorismo.

| Categoria | Sinais Típicos de Vibecode | Diretriz Profissional V2 |
| :--- | :--- | :--- |
| **Visual** | Gradientes roxo/azul sem justificativa, glassmorphism em tudo, glow excessivo, sombras super suaves difusas, dezenas de cards idênticos com `border-radius: 16px+`. | Cores ancoradas na marca e no domínio (`DESIGN.md`), contraste WCAG rigoroso, bordas e sombras funcionais com elevação intencional. |
| **Layout** | Hero centralizado previsível ("Welcome to the future"), headline gigante com gradiente de texto por padrão, bento grid decorativo sem função, 3 cards flutuantes idênticos. | Layout conduzido pelo conteúdo real, assimetria controlada, hierarquia espacial, grid com ritmo visual orgânico. |
| **Conteúdo** | Lorem ipsum disfarçado ("Sarah Johnson", "Acme Corp", "AI-powered solution"), botões com microcopy vaga ("Get started", "Learn more"). | Conteúdo realista do domínio de negócio, verbos de ação específicos no imperativo ("Solicitar Orçamento", "Emitir Nota"). |
| **Código** | Componentes inchados de 500+ linhas, dezenas de CSS vars não utilizadas, comentários redundantes de IA, bibliotecas inteiras para um botão. | Código limpo, componentes atômicos, escada Ponytail (diff mínimo), dependências justificadas. |
| **Acessibilidade** | Totalmente ignorada: `<div>` simulando `<button>`, sem foco visível por teclado, contraste insuficiente, sem labels semânticos. | Acessibilidade nativa WCAG 2.1 AA (semântica, foco, teclado, leitores de tela). |
| **Identidade** | Genérica: poderia pertencer a qualquer startup SaaS. Sem personalidade própria. | Identidade visual proprietária, adaptada ao segmento (ERP industrial, clínica médica, fintech, obra). |

---

## 2. Clichês Proibidos como Escolhas Automáticas

Os elementos abaixo **NÃO** são proibidos por completo, mas são **TERMINANTEMENTE PROIBIDOS como escolha automática ou padrão de template**:

1. ❌ **Gradiente roxo/azul padrão:** Escolha paletas com personalidade real do produto.
2. ❌ **Glow / Neon excessivo:** Reserve efeitos luminosos para estados ativos pontuais quando justificado.
3. ❌ **Glassmorphism universal:** Usar blur e transparência apenas onde houver sobreposição espacial real e legibilidade garantida.
4. ❌ **Bento Grid por modismo:** Bento grid só faz sentido quando agrupa dados de naturezas heterogêneas com hierarquia assimétrica intencional.
5. ❌ **Pills e Badges decorativos:** Cada badge deve comunicar um status real do sistema (`Ativo`, `Pendente`, `Vencido`), nunca decoração vazia.
6. ❌ **Dashboards feitos só de cards idênticos:** Alterne entre tabelas densas, gráficos funcionais, métricas de destaque e listas operacionais.
7. ❌ **Microcopy vazia de IA:** "Unlock the power of...", "Seamlessly integrate...". Fale a linguagem real do usuário.

---

## 3. Checklist de Auditoria dos 50 Itens (Anti-Vibecode Matrix)

Ao auditar uma tela existente, verifique:

### Visual & Layout (1-15)
- [ ] 1. Paleta de cores tem propósito (não é gradiente roxo/azul de template).
- [ ] 2. Contraste texto/fundo atende WCAG 2.1 AA (4.5:1 para texto normal, 3:1 para títulos).
- [ ] 3. Espaçamentos seguem escala sistemática (4px, 8px, 12px, 16px, 24px, 32px, 48px).
- [ ] 4. Tipografia tem no máximo 2 famílias e escala hierárquica clara (Display, Heading, Body, Caption).
- [ ] 5. Zero glassmorphism gratuito sobre textos longos.
- [ ] 6. Sombras comunicam elevação real (níveis 1 a 3), sem borrões cinzas gigantes.
- [ ] 7. Border-radius consistente com o estilo do produto (industrial = 4px a 8px; landing = intencional).
- [ ] 8. Hero section possui tese clara e elemento de assinatura único.
- [ ] 9. Ausência de grids de 3 cards perfeitamente simétricos com ícones em círculos coloridos.
- [ ] 10. Assimetria controlada ou ritmo visual orgânico presente.
- [ ] 11. Densidade de informação adequada ao tipo de aplicação (ERP denso vs landing espaçada).
- [ ] 12. Imagens são autênticas e representativas do domínio, sem fotos de banco genéricas.
- [ ] 13. Ícones pertencem a uma única família coerente (ex: Lucide ou Tabler).
- [ ] 14. Zero emojis utilizados como ícones de botões e tabelas no padrão industrial Dev Maniac's.
- [ ] 15. Elementos visuais possuem justificativa funcional demonstrável.

### Interação & Acessibilidade (16-30)
- [ ] 16. Todo elemento clicável é um `<button>` ou `<a>` nativo, ou componente com role e teclado equivalentes.
- [ ] 17. Indicador de foco visível e nítido ao navegar por Tab.
- [ ] 18. Navegação por teclado completa em menus, abas, modais e formulários.
- [ ] 19. Touch targets mínimos de 44x44px em interfaces móveis.
- [ ] 20. Modais implementam focus trap e fecham com `Esc`.
- [ ] 21. Formulários possuem labels visíveis associados (`for`/`id`).
- [ ] 22. Erros de validação indicados por texto e cor, com `aria-describedby`.
- [ ] 23. Estados vazios (Empty States) acolhedores com CTA orientativo.
- [ ] 24. Estados de carregamento (Loading) utilizam Skeletons proporcionais em vez de spinners centrais.
- [ ] 25. Animações respeitam `@media (prefers-reduced-motion: reduce)`.
- [ ] 26. Duração de transições entre 150ms e 250ms (nunca animações arrastadas que atrasam a ação).
- [ ] 27. Responsividade fluida entre 360px e 1920px sem overflow horizontal.
- [ ] 28. Tabelas em mobile possuem scroll horizontal contido ou visualização em cartões responsivos.
- [ ] 29. Rótulos de botões utilizam verbos de ação diretos e no imperativo.
- [ ] 30. Textos e números em tabelas possuem alinhamento semântico (texto à esquerda, números à direita).

### Código & Integridade (31-40)
- [ ] 31. Componentes divididos com responsabilidade única (<250 linhas).
- [ ] 32. Zero dependências redundantes para resolver tarefas triviais.
- [ ] 33. CSS classes e seletores sem especificidade conflitante.
- [ ] 34. Tokens de cor e espaçamento centralizados em CSS variables ou `DESIGN.md`.
- [ ] 35. Ausência de estilos inline arbitrários repetidos.
- [ ] 36. Imagens otimizadas com WebP/AVIF e dimensões explícitas para evitar layout shift.
- [ ] 37. Scripts de terceiros carregados com `defer` ou `async`.
- [ ] 38. Suporte completo a internacionalização (i18n PT/EN/ES) sem strings literais no código.
- [ ] 39. Tratamento seguro de inputs sem risco de XSS.
- [ ] 40. Ausência de TODOs ou comentários óbvios gerados por IA ("// This function adds two numbers").

### Discoverability & Presença (41-50)
- [ ] 41. Presença de `llms.txt` e `llms-full.txt` na raiz para indexação por LLMs.
- [ ] 42. Dados estruturados JSON-LD válidos (`Organization`, `WebSite`, `FAQPage`).
- [ ] 43. Meta tags OpenGraph e Twitter Cards configuradas com imagens reais.
- [ ] 44. `robots.txt` e `sitemap.xml` válidos e submetidos aos motores de busca.
- [ ] 45. Favicon e Web App Manifest configurados corretamente.
- [ ] 46. Copy escrita em pt-BR impecável (acentuação, pontuação e crase revisadas).
- [ ] 47. Regra de anonimização respeitada em relatórios técnicos.
- [ ] 48. Headings semânticos estruturados (h1 único, h2 e h3 em ordem hierárquica).
- [ ] 49. Citações da marca testadas e verificáveis nos principais Answer Engines (ChatGPT, Perplexity).
- [ ] 50. Performance Core Web Vitals verde (LCP < 2.5s, CLS < 0.1, INP < 200ms).
