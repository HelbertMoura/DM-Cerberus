---
titulo: Public APIs Catalog — Catálogo Canônico de APIs Públicas Gratuitas
tags: [global, public-apis, apis, integrations, external-data, backend]
atualizado: 2026-08-31
status: ativo
---

# 🌐 Public APIs Catalog — Catálogo Canônico de APIs Gratuitas (Dev Maniac's)

> **Fonte Canônica / Repositório Oficial:** [github.com/public-apis/public-apis](https://github.com/public-apis/public-apis)  
> **Volume:** Mais de 1.400 APIs públicas gratuitas organizadas em mais de 50 categorias.

---

## 🧭 1. Regra de Engenharia para os Agentes (GLM-5.3 / Codex / MiniMax)

> ⚠️ **REGRA DE OURO:** Antes de criar *mock data* complexo, *scrapers* manuais ou inventar integrações pagas desnecessárias, os Engenheiros de Backend **DEVEM** consultar este catálogo para verificar se já existe uma API pública gratuita homologada.

---

## 🚀 2. Top Categorias & APIs Homologadas para Produtos Dev Maniac's

### A. 🇧🇷 Brasil, Fiscal, Endereços & Empresas (dm-erp / Biolar / HelpDev)
| Serviço | API Recomendada | O que fornece | Auth / Custo |
| :--- | :--- | :--- | :--- |
| **CEP & Endereços** | [ViaCEP](https://viacep.com.br/) / [BrasilAPI](https://brasilapi.com.br/) | Busca de CEP, logradouro, bairro, UF | Sem auth / Gratuito |
| **CNPJ & Empresas** | [BrasilAPI CNPJ](https://brasilapi.com.br/docs#tag/CNPJ) / [ReceitaWS](https://receitaws.com.br/) | Razão social, CNAE, situação cadastral | Sem auth / Gratuito |
| **Feriados Nacionais** | [BrasilAPI Feriados](https://brasilapi.com.br/docs#tag/Feriados-Nacionais) | Calendário oficial de feriados por ano (para cronogramas de obra) | Sem auth / Gratuito |
| **Tabela FIPE** | [BrasilAPI FIPE](https://brasilapi.com.br/docs#tag/FIPE) | Avaliação de veículos e frotas da Biolar | Sem auth / Gratuito |
| **Bancos & PIX** | [BrasilAPI Bancos](https://brasilapi.com.br/docs#tag/BANKS) | Lista de códigos de compensação bancária e ISPB | Sem auth / Gratuito |

### B. 🌦️ Clima, Tempo & Agricultura (Biolar Dedetizadora / CanteiroHUB Obras)
| Serviço | API Recomendada | O que fornece | Auth / Custo |
| :--- | :--- | :--- | :--- |
| **Previsão Meteorológica** | [Open-Meteo](https://open-meteo.com/) | Previsão horária, vento, chuva (crítico para aplicação de dedetização e concretagem) | Sem API Key / Gratuito |
| **Clima Nacional** | [HG Brasil Clima](https://hgbrasil.com/status/weather) | Temperatura, umidade e previsão para cidades brasileiras | API Key gratuita |

### C. 💵 Câmbio, Moedas & Índices Econômicos (dm-erp Financeiro)
| Serviço | API Recomendada | O que fornece | Auth / Custo |
| :--- | :--- | :--- | :--- |
| **Cotações de Moedas** | [AwesomeAPI Câmbio](https://docs.awesomeapi.com.br/api-de-moedas) | Dólar, Euro, cotações em tempo real e histórico | Sem auth / Gratuito |
| **Taxa Selic & CDI** | [BrasilAPI Taxas](https://brasilapi.com.br/docs#tag/Taxas) | Taxas SELIC e CDI oficiais para cálculos financeiros | Sem auth / Gratuito |

### D. 🛡️ Segurança, E-mail & Validação (Auth / Gatekeeper)
| Serviço | API Recomendada | O que fornece | Auth / Custo |
| :--- | :--- | :--- | :--- |
| **Vazamento de Senhas** | [Have I Been Pwned API](https://haveibeenpwned.com/API/v3) | Checagem de senhas vazadas em cadastros de usuários | API Key |
| **Validação de IP / Geo** | [ipapi.co](https://ipapi.co/) | Detecção de país/cidade de acessos suspeitos | Gratuito até limite |

---

## 📚 3. Como Consultar o Catálogo Completo

Para buscar APIs em outras categorias (Saúde, Esportes, Jogos, Notícias, Transporte):
* Repositório: `https://github.com/public-apis/public-apis`
* Raw JSON Index: `https://api.publicapis.org/` ou via search no GitHub repo.
