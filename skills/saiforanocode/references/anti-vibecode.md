# 🚫 Anti-Vibecode: Diretrizes, Detecção de AI Slop & Risk Score

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
| **Acessibilidade** | Totalmente ignorada: `<div>` simulando `<button>`, sem foco visível por teclado, contraste insuficiente, sem labels semânticos. | Acessibilidade nativa WCAG 2.1/2.2 AA (semântica, foco, teclado, leitores de tela). |
| **Identidade** | Genérica: poderia pertencer a qualquer startup SaaS. Sem personalidade própria. | Identidade visual proprietária, adaptada ao segmento (ERP industrial, clínica médica, fintech, obra). |

---

## 2. Vibecode Risk Score (0 a 100)

O **Vibecode Risk Score** quantifica a probabilidade de uma interface ser rejeitada como amadora ou gerada por IA:

$$\text{Score} = \sum (\text{Pontos de Penalidade})$$

| Faixa de Score | Classificação | Ação do Agente |
| :---: | :--- | :--- |
| **0 – 15** | **Pristine / Engineered** | Aprovado. Interface madura, sólida e orientada ao domínio. |
| **16 – 35** | **Low Risk** | Ajustes pontuais (tipografia, microcopy ou espaçamentos). |
| **36 – 60** | **Moderate Risk (Generic AI)** | Refatoração recomendada: remover cards desnecessários, unificar ícones, redefinir paleta. |
| **61 – 80** | **High Risk (Vibecoded)** | Intervenção obrigatória: layout quebrado, bento grid gratuito, clichês visuais óbvios. |
| **81 – 100** | **Critical AI Slop** | Reescrita estrutural necessária. Interface comunica amadorismo absoluto. |

### Tabela de Penalidades de Risco:
- `+25 pts`: Gradiente roxo e azul / glow neon em botões ou hero.
- `+20 pts`: Quebra ou overflow horizontal em viewport de 360px a 390px (mobile fake).
- `+15 pts`: "Card Abuse": mais de 8 cards aninhados na mesma viewport sem necessidade de agrupamento.
- `+15 pts`: `rounded-2xl` ou `rounded-3xl` aplicado indistintamente em todos os containers de software corporativo/ERP.
- `+15 pts`: Bento Grid decorativo com caixas vazias ou sem relação lógica de dados.
- `+10 pts`: Emojis utilizados no lugar de ícones em cards, tabelas ou botões.
- `+10 pts`: Travessões longos (`—`) em sequência no copywriting de landing page ou dashboard.
- `+10 pts`: Headline genérica pasteleira ("Soluções Inteligentes para o Seu Futuro").
- `+10 pts`: Ausência de foco visível (`focus-visible`) em botões, links e inputs ao navegar por teclado.
- `+10 pts`: Ausência de Empty States estruturados (tela branca ou erro JS quando lista está vazia).
- `+10 pts`: Spinner central único que bloqueia tela inteira em vez de skeleton loader proporcional.

---

## 3. Diretrizes de Combate a Clichês Críticos

### A. Anti-Card Abuse (A Ditadura dos Cards de IA)
As IAs colocam tudo dentro de "cards" com bordas cinzas e sombras suaves porque não sabem criar hierarquia tipográfica e espacial.
- **Regra do Desmanche:** Se você remover a borda (`border`) e o fundo (`bg-card`) do container e a hierarquia continuar legível via espaçamento (`margin`/`padding`) ou uma divisória sutil (`border-t border-border`), **o card era desnecessário**.
- **Use Cards SOMENTE quando:**
  1. O bloco for uma entidade discreta, arrastável ou reordenável (ex.: cartão Kanban).
  2. O bloco tiver interação de hover/clique como um todo que navega para outra tela.
  3. For uma janela modal, popover ou cartão de resumo flutuante.
- **Em ERPs e Dashboards:** Prefira tabelas contínuas, listas divididas por linhas sutis (`divide-y divide-border`), e painéis planos delimitados pela estrutura do grid.

### B. Anti-Rounding (Geometria Intencional)
A IA padrão usa `rounded-2xl` (16px) e `rounded-3xl` (24px) em tudo para parecer "amigável", destruindo a seriedade de sistemas operacionais.
- **Softwares Industriais, ERPs, Finanças, Ferramentas:** Bordas sóbrias de `2px` a `6px` (`rounded-sm` a `rounded-md`). Cantos vivos comunicam precisão e densidade de dados.
- **SaaS B2B Modernos:** Máximo de `8px` (`rounded-lg`) em botões e inputs.
- **Modais e Containers Flutuantes:** Máximo de `12px` (`rounded-xl`).
- **Pills/Badges:** `rounded-full` é reservado exclusivamente para tags pequenas e contadores de status, **NUNCA** para blocos estruturais inteiros de layout.

### C. Color Discipline & Paleta Funcional
- **Evite o "Rainbow UI":** Uma interface onde cada badge tem uma cor saturada diferente (amarelo, roxo, rosa, verde-limão, azul-piscina).
- **Proporção Clássica de Cores:**
  - **80% a 85% de Neutros:** Brancos, off-whites, cinzas ou pretos operacionais de alto contraste.
  - **10% a 15% de Marca/Primária:** Direcionada estritamente aos CTAs principais, estados ativos de navegação e indicadores de seleção.
  - **< 5% de Cores Semânticas:** Sucesso (verde sóbrio), Alerta (âmbar), Erro (vermelho carmesim), Info (azul técnico). Nunca use verde neon ou vermelho fluorescente.

### D. Empty States, Loading States & Feedback
- **Empty State Profissional (Tríade Obrigatória):**
  1. Contexto imediato: "Nenhum pedido cadastrado neste período."
  2. Ação direta (CTA primário): `[ + Cadastrar Primeiro Pedido ]`.
  3. Ajuda contextual secundária: Link para "Importar via planilha CSV" ou "Aprenda como configurar pedidos".
- **Loading State:** Skeletons que espelham exatamente a altura e largura das linhas ou cards finais. Zero layout shifts (`CLS = 0`).
- **Feedback Transacional:** Notificações Toast no canto inferior/superior direito com duração entre 3s e 5s, com botão explícito de "Desfazer" quando aplicável.

---

## 4. Clichês e Vícios Mortais de AI Slop (Lista Negra Completa)

1. ❌ **Gradiente roxo e azul sobre fundo escuro:** O clichê número 1 das IAs. Use paletas ancoradas na marca real e no domínio do cliente (`DESIGN.md`).
2. ❌ **Uso excessivo de travessões longos (`—`):** Vício de LLMs traduzidas ao pé da letra. Em português corporativo soa pedante e truncado. Prefira frases diretas e pontuação natural.
3. ❌ **Layout quebrado no celular (Mobile Fake):** Páginas que só funcionam em 1920x1080 com blocos sambando e quebrando no smartphone. O teste em 360px é eliminatório.
4. ❌ **Tags/Pills arredondadas na primeira dobra:** Selos genéricos de categoria (ex.: `• Para Personal Trainers`, `• Nova Era`) logo no topo da página. Desperdiçam a área mais nobre da tela.
5. ❌ **Excesso de emojis nos cards (🚀, 💡, 🔥):** Amadorismo puro. Use ícones vetoriais profissionais consistentes de uma única família (Lucide, Tabler).
6. ❌ **Glassmorphism Cego (`backdrop-blur` com borda branca 10%):** Cards translúcidos ilegíveis em telas com claridade. Use fundos sólidos com contraste WCAG AA (4.5:1).
7. ❌ **Bento Grid gratuito e desconexo:** 6 blocos assimétricos onde 3 têm apenas uma frase e um ícone gigante ocupando 2 colunas. Bento grid só é válido quando organiza dados heterogêneos reais.
8. ❌ **Glows neon e sombras radioativas (`box-shadow: 0 0 30px #8b5cf6`):** Parecem cassinos online ou jogos arcade. Em sistemas B2B, use sombras físicas e discretas (`shadow-sm`, `shadow-md` com opacidade de 5% a 8%).
9. ❌ **Objetos 3D abstratos flutuantes no Hero:** Esferas espelhadas, rosquinhas de vidro ou cubos flutuantes sem relação com o produto. Mostre o software real, dados ou imagens autênticas do setor.
10. ❌ **Copywriting pasteleiro com adjetivos vazios:** *"Revolucione sua operação com o poder incomparável da nossa solução inteligente concebida para o amanhã"*. Fale em **verbos e métricas reais**: *"Emita a guia de transporte em 30 segundos e envie direto pro WhatsApp"*.
11. ❌ **Faixas de "Confiado por 10.000+ empresas" com logos inventados:** Silhuetas genéricas que ninguém reconhece. Substitua por cases reais, métricas auditáveis ou certificações técnicas (LGPD, SEFAZ, ANVISA).
12. ❌ **Falta de densidade de informação em ERPs (Espaçamento Balão):** Formulários com `padding: 40px` onde cabem apenas 3 linhas por tela. Sistemas de trabalho exigem densidade ergonômica.
13. ❌ **Esquecimento de Empty States e Error States:** Telas que viram buracos brancos ou cospem erros de JavaScript (`cannot read properties of undefined`) quando o banco está vazio.
14. ❌ **Scrolljacking e animações em cascata lentas:** Animações com delays de 1 segundo que travam a leitura do usuário enquanto rola a página. Transições devem ser < 150ms e funcionais.
15. ❌ **Inputs de formulário sem estados visíveis:** Inputs sem feedback de foco por teclado, sem validação inline e sem loading state no botão de envio (evitar cliques duplicados).

---

## 5. Diretriz para Ferramentas de Motion e Vídeo com IA (ex: Higgsfield)

- **Classificação Taxonômica:** Ferramentas generativas de vídeo e motion como **Higgsfield** são classificadas estritamente como **`TOOL` externa de Marketing e Showcase**, e **NUNCA** como biblioteca de runtime (`LIBRARY`) ou dependência do core do frontend.
- **Quando usar:** Produção de vídeos promocionais de demonstração de produto, reels, anúncios e backgrounds de hero exportados para MP4/WebM otimizado via CDN.
- **Quando NÃO usar:** Nunca acoplar SDKs pesados de vídeo generativo ou frameworks de motion não determinísticos dentro de ERPs, painéis de gestão ou fluxos transacionais.

---

## 6. Checklist de Auditoria dos 50 Itens (Anti-Vibecode Matrix)

Ao auditar uma tela existente, verifique:

### Visual & Layout (1-15)
- [ ] 1. Paleta de cores tem propósito (não é gradiente roxo/azul de template).
- [ ] 2. Contraste texto/fundo atende WCAG 2.1/2.2 AA (4.5:1 para texto normal, 3:1 para títulos).
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
- [ ] 17. Indicador de foco visível e nítido ao navegar por Tab (`focus-visible`).
- [ ] 18. Navegação por teclado completa em menus, abas, modais e formulários.
- [ ] 19. Touch targets mínimos de 44x44px (ou 48x48px no mobile) em interfaces móveis.
- [ ] 20. Modais implementam focus trap e fecham com `Esc`.
- [ ] 21. Formulários possuem labels visíveis associados (`for`/`id` ou `htmlFor`).
- [ ] 22. Erros de validação indicados por texto e cor, com `aria-describedby` e `aria-invalid`.
- [ ] 23. Estados vazios (Empty States) acolhedores com CTA orientativo.
- [ ] 24. Estados de carregamento (Loading) utilizam Skeletons proporcionais em vez de spinners centrais.
- [ ] 25. Animações respeitam `@media (prefers-reduced-motion: reduce)`.
- [ ] 26. Duração de transições entre 80ms e 200ms (nunca animações arrastadas que atrasam a ação).
- [ ] 27. Responsividade fluida entre 360px e 1920px sem overflow horizontal.
- [ ] 28. Tabelas em mobile possuem scroll horizontal contido ou visualização em cartões responsivos.
- [ ] 29. Rótulos de botões utilizam verbos de ação diretos e no imperativo.
- [ ] 30. Textos e números em tabelas possuem alinhamento semântico (texto à esquerda, números à direita com `tabular-nums`).

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
