# 🏛️ Referência: Design Profissional, Organicidade & Bibliotecas Maduras

## 1. Princípios do Design Profissional e Orgânico

Um produto profissional se diferencia de uma interface gerada por IA através de **intenção, ritmo e composição**:

### Organicidade vs Mecânica
- **Composição Não-Mecânica:** Evite layouts onde todos os blocos possuem o mesmo peso, altura e largura. Crie variedade intencional através de contraste de escala e densidade.
- **Ritmo Visual:** Alterne entre momentos de alta densidade (tabelas de dados, painéis de métricas) e momentos de respiro e leitura focada.
- **Hierarquia Tipográfica Clara:** A relação entre títulos, subtítulos, corpo e legendas deve guiar a ordem de leitura do usuário sem esforço.
- **Affordance e Feedback:** Cada elemento clicável deve declarar visualmente sua capacidade de interação (hover state, active state, cursor pointer, foco por teclado).

---

## 2. Não Reinventar a Roda: Uso Inteligente de Bibliotecas Maduras

Nunca implemente primitivas complexas do zero apenas para evitar dependências quando existirem soluções consolidadas, acessíveis e testadas pela comunidade:

### Quando Usar Bibliotecas Maduras:
| Problema Complexo | Solução Consolidada Recomendada | Justificativa |
| :--- | :--- | :--- |
| **Tabelas & Grids Interativos** | TanStack Table / AG Grid | Lógica complexa de ordenação, paginação, filtros, colunas fixas e virtualização. |
| **Formulários & Validação** | React Hook Form / TanStack Form + Zod | Gerenciamento de estado de inputs, re-render otimizado e schemas de tipo robustos. |
| **Primitivas de Acessibilidade** | Radix UI / Base UI / React Aria | Focus trap, controle de ARIA roles, teclados nativos em modais, dropdowns e tooltips. |
| **Notificações Temporárias** | Sonner | Empilhamento acessível de toasts sem quebrar layout. |
| **Command Palette** | cmdk | Navegação instantânea por teclado (`Cmd+K`). |
| **Ícones Vetoriais** | Lucide React / Tabler Icons | Consistência de traço (stroke), espessura e viewBox uniforme. |

### Regra Anti-Abuso:
- **NÃO** instale bibliotecas pesadas para resolver problemas triviais (ex: instalar uma lib de botões ou de grid simples CSS).
- Avalie sempre: *Maturidade, Impacto no Bundle, Acessibilidade nativa, Suporte a Types e Licença MIT/Apache*.

---

## 3. Component Library NÃO É Design System

- **Bibliotecas fornecem capacidades:** Radix dá a acessibilidade; TanStack dá o motor de dados; Lucide dá os ícones.
- **A identidade visual vem do projeto:** As cores, espaçamentos, tipografia, raios de borda, sombras e variantes de estilo pertencem exclusivamente ao **`DESIGN.md`** do produto.
- Nunca deixe que a biblioteca padrão dite a aparência do seu sistema.
