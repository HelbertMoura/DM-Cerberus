# 🎨 Referência: Identidade Visual, Anonimização & Redação Técnica

## 1. Regra de Ouro: Anonimização por Padrão

A metodologia **não atribui autoria a pessoa física ou empresa específica em artefatos técnicos públicos** para preservar a neutralidade de auditoria.

### Assinaturas Canônicas Permitidas:
- `saiforanocode` (uso primário e marca metodológica)
- `saiforanocode · metodologia` (em rodapés técnicos de relatórios)
- `auditoria tecnica · saiforanocode` (em capas de relatórios e PDFs)
- `data · saiforanocode` (em metadados e carimbos de data/hora)

> ⚠️ **NUNCA** substitua essas strings por nomes pessoais, marcas de terceiros, CNPJs ou contatos sem autorização explícita do Product Owner.

---

## 2. Regra de Ouro: Português Impecável (pt-BR)

Todo texto gerado ou revisado — copies de interface, headlines, CTAs, FAQs, footers, dados estruturados JSON-LD e relatórios — deve atender ao padrão culto da língua portuguesa:

### Erros Comuns Terminantemente Banidos:
| Errado | Correto | Regra |
| :--- | :--- | :--- |
| Voce, nao, codigo, servico, negocio, saude, ciencia | Você, não, código, serviço, negócio, saúde, ciência | Acentuação gráfica obrigatória em oxítonas, paroxítonas e proparoxítonas. |
| Auto-atendimento, anti-vibecode | Autoatendimento, antivibecode | Novo Acordo Ortográfico (sem hífen quando o segundo elemento não inicia por 'h' ou vogal idêntica). |
| Pontuação ausente ou vírgulas soltas | Leitura corrida e ritmo pausado correto | Pontuação revisada linha a linha. |
| Mistura desordenada de idiomas | Português (Brasil) nativo | Termos técnicos mantêm forma internacional (commit, deploy), o restante em pt-BR impecável. |

### Protocolo de Revisão de Texto:
1. **Passada dedicada de ortografia:** Antes de entregar qualquer artefato ou commit, faça uma leitura exclusivamente focada em acentuação, crases e concordância.
2. **JSON-LD não é exceção:** Textos dentro do `schema.org` são lidos por humanos e indexadores; devem ter acentuação perfeita.
3. **i18n:** Em sistemas multi-idioma (PT/EN/ES), cada dicionário de tradução é mantido e revisado de forma isolada e sem contaminação.

---

## 3. Brand Lock & Personalidade Própria

Interfaces corporativas profissionais devem expressar a identidade do produto:
1. **Padrão Industrial Solid-State (Dev Maniac's):**
   - Cores: Azul Aço (`#1E40AF`), Chumbo (`#0F172A`), Fundo Sólido Neutro (`#F1F5F9`).
   - Sem gradientes neon, sem transparências excessivas.
   - Banimento total de emojis em botões e tabelas — utilizar ícones vetoriais de traço limpo (Lucide / Tabler).
2. **Não confundir Profissional com Minimalismo Vazio:**
   - Profissional não significa tela branca deserta sem dados. Um ERP de engenharia precisa ser **denso, eficiente e legível**. Uma landing page de conversão precisa ser **expressiva e persuasiva**.
   - Cada tela deve responder à necessidade de negócio do seu usuário.
