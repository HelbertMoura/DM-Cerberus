# 🚀 Workflow: Construção de Novos Projetos do Zero (Modo Greenfield)

> **Regra Primária:** NUNCA comece desenhando o "Hero Section" ou espalhando "Cards". O design profissional começa no domínio de negócio, nos dados e nos fluxos de trabalho reais.

---

## O Ciclo Estruturado de 15 Passos (Do Domínio ao Polimento)

### Passo 1: Classificação do Domínio & Função do Sistema
Identifique a natureza fundamental da aplicação:
- **Marketing / Editorial / Showcase:** Persuasão, storytelling, ritmo visual amplo, foco em conversão.
- **ERP / Backoffice / Ferramenta Operacional:** Eficiência, previsibilidade, densidade ergonômica, suporte a teclado para jornada de 8h/dia.

### Passo 2: Definição do Design DNA (8 Dimensões)
Documente no `DESIGN.md` as 8 dimensões de identidade:
*(Personalidade, Densidade, Geometria, Contraste, Cor, Tipografia, Motion e Layout)* conforme [`references/design-dna-signature.md`](../references/design-dna-signature.md).

### Passo 3: Criação da Assinatura Visual (Design Signature)
Defina o elemento proprietário e memorável da interface que impede que ela seja confundida com qualquer outro template (ex.: cabeçalho operacional com linha do tempo contínua, tipografia editorial gravada, split-view integrado).

### Passo 4: Governança de Dependências & Licenças
Selecione as bibliotecas de fundação seguindo [`workflows/dependency-governance.md`](./dependency-governance.md). Exija licenças permissivas (MIT, Apache-2.0) e vete qualquer dependência GPL/AGPL.

### Passo 5: Arquitetura de Tokens de Design
Configure o sistema de tokens em 3 camadas (Primitivos → Semânticos → Componentes) em CSS Variables globais.

### Passo 6: Tipografia & Calibração Numérica
Selecione tipografia de autor (evite o piloto automático de Inter/Roboto quando o domínio pedir distinção). Configure `font-display: swap` e habilite `tabular-nums` para colunas numéricas e financeiras.

### Passo 7: Instalação de Família Única de Ícones
Adote uma única biblioteca de ícones vetoriais profissionais (ex: Lucide ou Tabler). Vete expressamente o uso de emojis no lugar de ícones em interfaces operacionais.

### Passo 8: Estrutura de Layout & App Shell
Construa o esqueleto da interface (Header, Sidebar retrátil, Área de Trabalho, Breadcrumbs) usando CSS Grid moderno e Container Queries. Evite o vício de centralizar tudo com `max-w-7xl mx-auto` em sistemas operacionais.

### Passo 9: Modelagem Conduzida por Dados e Tarefas Reais
Mapeie os fluxos primários do operador: qual é o dado principal? Qual é a próxima decisão? Desenhe a interface a partir da hierarquia da informação, nunca desenhando caixas vazias para depois preencher.

### Passo 10: Implementação de Grids & Formulários Robustos
Utilize `@tanstack/react-table` para tabelas ricas (com cabeçalho fixo, ordenação acessível e colunas pinadas) e `react-hook-form` + `zod` para formulários validados com labels explícitos e mensagens inline.

### Passo 11: Implementação Mandatória da Tríade de Estados
Toda tela DEVE conter nativamente:
1. **Empty State:** Contexto + Ícone/Ilustração sóbria + CTA de ação direta.
2. **Loading State:** Skeleton screens proporcionais com dimensões exatas da informação final.
3. **Error State:** Feedback claro de erro com instrução de recuperação.

### Passo 12: Dosagem de Motion & Microinterações
Adicione feedback de transição estritamente causal (80ms a 180ms) conforme [`references/motion-discipline.md`](../references/motion-discipline.md), com suporte obrigatório a `prefers-reduced-motion`.

### Passo 13: Recomposição Mobile Responsiva
Projete a adaptação para telas estreitas (360px a 390px): transforme tabelas em cartões operacionais empilhados, mova ações para Bottom Sheets e garanta touch targets mínimos de 48px × 48px.

### Passo 14: Fundação de AEO / GEO & Descoberta
Antes da primeira release, publique na pasta `/public/`:
- `llms.txt` e `llms-full.txt` documentando a organização para IA.
- `robots.txt` e `sitemap.xml`.
- Metadados OpenGraph e schemas JSON-LD estruturados.

### Passo 15: Quality Gate & Vibecode Risk Score
Execute a validação final:
- [ ] Vibecode Risk Score ≤ 15 (conforme [`references/anti-vibecode.md`](../references/anti-vibecode.md)).
- [ ] Zero erros no console e zero quebras horizontais em 360px.
- [ ] Aprovação na suíte de testes e revisão ortográfica rigorosa em pt-BR.
