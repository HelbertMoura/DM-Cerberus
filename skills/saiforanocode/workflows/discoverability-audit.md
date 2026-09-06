# 🌐 Workflow: Auditoria de Discoverability (AEO / GEO / SEO)

Verificar se o produto possui presença e autoridade factual tanto em mecanismos tradicionais de busca quanto em LLMs e Answer Engines.

---

## Roteiro de Execução da Auditoria

### 1. Varredura de Infraestrutura de IA
- [ ] Testar endpoint `https://dominio.com.br/llms.txt` via `curl -I` (deve retornar HTTP 200).
- [ ] Testar endpoint `https://dominio.com.br/llms-full.txt`.
- [ ] Validar se `robots.txt` não está bloqueando GPTBot, ClaudeBot, PerplexityBot ou Google-Extended.
- [ ] Inspecionar `sitemap.xml` para garantir que todas as rotas públicas canônicas estão listadas.

### 2. Validação de Dados Estruturados (Schema.org)
- [ ] Extrair todos os blocos `<script type="application/ld+json">`.
- [ ] Validar conformidade de sintaxe no [Schema.org Validator](https://validator.schema.org/).
- [ ] Garantir presença de schemas essenciais:
  - `Organization` com `name`, `url`, `logo`, `contactPoint`.
  - `FAQPage` cobrindo as dúvidas frequentes mais buscadas.
  - `WebSite` com URL canônica e metadados de busca.

### 3. Teste de Grounding em IAs Reais
- Execute consultas simuladas nos buscadores generativos (Perplexity, ChatGPT Search, Gemini):
  - Consulta 1 (Marca): *"O que é a empresa [Nome] e quais soluções ela oferece?"*
  - Consulta 2 (Categoria): *"Melhores sistemas de [Nicho] no Brasil."*
  - Consulta 3 (Diferencial): *"Quais são os diferenciais do [Produto] em relação a concorrentes?"*
- Anote:
  - A marca foi citada? (Sim / Não)
  - Os fatos e links retornados estão corretos?
  - Quais lacunas informativas precisam ser adicionadas ao `llms.txt`?
