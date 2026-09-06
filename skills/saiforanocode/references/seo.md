# 🔍 Referência: SEO Técnico & Structured Data (Schema.org)

A fundação do SEO moderno garante que rastreadores tradicionais e extratores de IA interpretem a entidade do seu negócio com precisão matemática.

---

## 1. Dados Estruturados JSON-LD Obrigatórios

Todo produto deve injetar schemas canônicos no `<head>` via `<script type="application/ld+json">`:

### 1.1 Schema `Organization` / `LocalBusiness`
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Nome da Empresa",
  "url": "https://seusite.com.br",
  "logo": "https://seusite.com.br/logo.png",
  "description": "Descrição factual e concisa da empresa.",
  "sameAs": [
    "https://linkedin.com/company/suaempresa",
    "https://instagram.com/suaempresa"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+55-31-99999-9999",
    "contactType": "customer service",
    "areaServed": "BR",
    "availableLanguage": ["Portuguese", "English", "Spanish"]
  }
}
```

### 1.2 Schema `FAQPage` (Rich Snippets & AEO)
O schema de FAQ é um dos fatores de maior impacto para citações diretas no ChatGPT e Google AI Overviews:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Como funciona o sistema de gestão?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "O sistema centraliza compras, medições de obra e financeiro em uma plataforma integrada com sincronização em tempo real."
      }
    }
  ]
}
```

---

## 2. Metadados e Tags Canônicas

- `<link rel="canonical" href="https://seusite.com.br/rota" />`
- `<meta name="description" content="140-160 caracteres com proposta de valor clara e palavras-chave naturais." />`
- OpenGraph completo (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:locale`).
- Twitter Cards (`twitter:card` com `summary_large_image`, `twitter:title`, etc.).
