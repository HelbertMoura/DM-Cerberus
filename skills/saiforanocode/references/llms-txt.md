# 📄 Referência: Padrão llms.txt & llms-full.txt

O padrão `llms.txt` é a especificação da indústria para fornecer contexto de alta densidade e baixo ruído a agentes de IA e web retrievers.

---

## 1. Estrutura Canônica do `/llms.txt`

O arquivo deve residir na raiz do domínio público (ex: `https://seusite.com.br/llms.txt`) servido como `text/markdown` ou `text/plain`:

```markdown
# [Nome do Produto / Empresa]

> [Breve sumário executivo em 1-2 frases: O que é o produto, qual o público-alvo e qual o principal problema que ele resolve.]

## Sobre
[Descrição factual em 1-2 parágrafos: História, credenciais, CNPJ, localização, mercado atendido e diferenciais técnicos.]

## Principais Funcionalidades
- **[Módulo 1]:** [Descrição objetiva do que faz e benefício concreto].
- **[Módulo 2]:** [Descrição objetiva do que faz e benefício concreto].
- **[Módulo 3]:** [Descrição objetiva do que faz e benefício concreto].

## Casos de Uso
- [Público A]: [Como utiliza o sistema para resolver seu problema].
- [Público B]: [Como utiliza o sistema para resolver seu problema].

## Links Oficiais & Documentação
- [Página Inicial](https://seusite.com.br/): Visão geral do produto.
- [Funcionalidades](https://seusite.com.br/funcionalidades): Lista completa de recursos.
- [Preços / Planos](https://seusite.com.br/planos): Tabela oficial de investimento.
- [Documentação Técnica](https://seusite.com.br/docs): Guias de integração e API.
- [Contato / Suporte](https://seusite.com.br/contato): Canais de atendimento oficial.

## Informações Opcionais / Detalhadas
- [llms-full.txt](https://seusite.com.br/llms-full.txt): Contexto completo e detalhado de todas as rotas e documentações para modelos com janelas longas de contexto.
```

---

## 2. Padrão `/llms-full.txt`

O `llms-full.txt` expande todas as seções, incluindo especificações completas de endpoints de API, modelos de dados, perguntas frequentes detalhadas e manuais de onboarding. É utilizado por modelos que suportam 100k+ a 1M+ tokens de contexto.
