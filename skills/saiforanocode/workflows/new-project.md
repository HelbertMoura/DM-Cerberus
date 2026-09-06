# 🚀 Workflow: Prevenção Anti-Vibecode para Novos Projetos (Modo 2)

Garantir que novos projetos nasçam com identidade proprietária, acessibilidade nativa e alta discoverability para humanos e IAs desde o primeiro commit.

---

## O Ciclo de Fundação de Novos Projetos

### 1. Brand Lock (Dia 0)
Antes de construir o primeiro componente de UI:
1. **Defina o `DESIGN.md`:** Cores semânticas, tipografia, escalas de espaçamento e regras de densidade.
2. **Defina o Tom de Voz:** Linguagem técnica e assertiva em pt-BR, verbos de ação nos botões.
3. **Selecione a Família de Ícones:** Escolha uma única biblioteca (Lucide ou Tabler) e configure no projeto.

### 2. Scaffold Técnico com AEO/GEO Integrado (Dia 1)
O scaffold inicial do projeto **já deve conter**:
- `/public/llms.txt` e `/public/llms-full.txt` estruturados.
- `robots.txt` permitindo rastreadores legítimos de busca e de IA (Google-Extended, GPTBot, PerplexityBot).
- `sitemap.xml` dinâmico ou estático.
- Componente base de SEO injetando JSON-LD de `Organization` e `WebSite`.

### 3. Componentes com Primitivas Acessíveis
- Utilize a **Frontend Toolbox** para selecionar bibliotecas de base (Radix/Base UI/TanStack).
- Conecte as primitivas aos tokens do `DESIGN.md`.
- Evite criar formulários e tabelas artesanais sem testes de teclado e acessibilidade.

### 4. Quality Gate de Pré-Entrega
Nenhum novo módulo é aprovado para release sem:
- [ ] Zero erros de linter e TypeScript (`tsc --noEmit`).
- [ ] Auditoria visual livre de clichês proibidos (gradientes genéricos, cards idênticos).
- [ ] Verificação responsiva em viewports 360px, 768px e 1440px.
- [ ] Validação ortográfica pt-BR aprovada.
