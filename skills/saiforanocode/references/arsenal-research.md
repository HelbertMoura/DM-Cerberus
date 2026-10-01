# 🔭 Referência: Arsenal Camada 1 — Design Research & Benchmarking

> **A Regra de Ouro:** Referência serve para extrair **princípios de composição, hierarquia espacial, densidade e padrões de interação**. NUNCA copie páginas inteiras, marcas, copies, cores proprietárias ou trade dress de concorrentes. Produza soluções originais fundamentadas em engenharia.

---

## 1. Catálogo Canônico de Referências Classificadas por Função

Nunca trate todas as galerias de design como equivalentes. Consulte a fonte exata para o domínio da sua tarefa:

| Finalidade da Pesquisa | Fontes Canônicas Recomendadas | O que Analisar e Extrair |
| :--- | :--- | :--- |
| **Product UI / Web Apps / SaaS** | **[Mobbin](https://mobbin.com)**<br>**[Pageflows](https://pageflows.com)**<br>**[SaaSFrame](https://saasframe.io)**<br>**[Screenlane](https://screenlane.com)**<br>**[Nicelydone](https://nicelydone.club)** | Fluxos reais de onboarding, dashboards corporativos, transição de estados de formulário, configurações complexas e hierarquia de menus. |
| **Mobile & PWA Nativo** | **[Mobbin Mobile](https://mobbin.com)**<br>**[Pttrns](https://pttrns.com)**<br>**[UI Sources](https://uisources.com)** | Padrões de gestos, ergonomia do polegar (thumb-reach), sheets/drawers inferiores, navegação persistente e drill-down em telas pequenas. |
| **Desktop Web, Admin & ERP** | **[Refero](https://refero.design)**<br>**[SaaSFrame Tables](https://saasframe.io)**<br>**[Pageflows Desktop](https://pageflows.com)** | Tabelas densas, filtros avançados, split-views, master-detail, visualização de logs e painéis de inspeção lateral. |
| **Editorial & Design High-End** | **[Godly](https://godly.website)**<br>**[SiteInspire](https://siteinspire.com)**<br>**[Minimal Gallery](https://minimal.gallery)**<br>**[Httpster](https://httpster.net)**<br>**[Awwwards](https://awwwards.com)** | Ritmo de leitura tipográfica, composição assimétrica intencional, contraste de escala e direção de arte com personalidade. |
| **Landing Pages & Marketing** | **[Land-book](https://land-book.com)**<br>**[One Page Love](https://onepagelove.com)**<br>**[Lapa Ninja](https://lapa.ninja)** | Estrutura de prova social autêntica, tabelas comparativas de preços sem truques e clareza de proposta de valor. |
| **Padrões Específicos de Componentes** | **[Navbar Gallery](https://navbar.gallery)**<br>**[Footer.design](https://footer.design)**<br>**[Bento Grids](https://bentogrids.com)**<br>**[Dark Mode Design](https://darkmodedesign.com)** | Anatomia anatômica de headers densos, footers organizados e paletas escuras com contraste calibrado (sem neon radioativo). |
| **Micro-Interações & Detalhes Finos** | **[Design Spells](https://designspells.com)**<br>**[Refero Styles](https://styles.refero.design)**<br>**[Layers](https://layers.to)** | Detalhes sutis que tornam o produto agradável: transições de foco, feedback de botão salvo, hover states precisos. |

---

## 2. O Protocolo de Pesquisa Antes da Implementação

Quando receber uma tarefa de interface desafiadora, **NÃO abra o editor de código imediatamente**:

1. **Defina o Problema de UX:** (ex: *"Como apresentar uma lista de 5.000 ordens de serviço com 8 colunas de status no celular e desktop?"*).
2. **Consulte 2 a 3 Fontes Segmentadas:** Abra Mobbin, Refero ou SaaSFrame no nicho de tabelas e ERPs.
3. **Extraia 3 Princípios Concretos:**
   - *Princípio 1:* A coluna de ID e Status deve ser fixa à esquerda no scroll.
   - *Princípio 2:* Filtros rápidos devem viver acima da tabela em uma barra compacta com contador de resultados.
   - *Princípio 3:* Ações rápidas não devem depender de hover (pois falham no toque).
4. **Aplique no seu Design DNA:** Pegue esses princípios e materialize-os utilizando os **tokens, fontes e cores do projeto**, garantindo originalidade e independência tecnológica.
