# 📦 Governança de Dependências & Prevenção de Frankenstein UI

> **Regra Dev Maniac's:** Toda biblioteca externa adicionada a um projeto é uma dívida técnica permanente. Só deve ser introduzida se economizar centenas de horas de testes de acessibilidade ou algoritmos complexos, sob licença permissiva comprovada e harmonizada pelo Design System.

---

## 1. Matriz de Licenças Open-Source (SAFE / REVIEW / BLOCK)

Antes de instalar qualquer pacote via `npm`, `pnpm` ou `yarn`, verifique a licença no `package.json` do repositório upstream:

| Classificação | Licenças | Diretriz de Uso |
| :--- | :--- | :--- |
| 🟢 **SAFE (Aprovação Direta)** | **MIT, Apache-2.0, ISC, BSD-2-Clause, BSD-3-Clause, Unlicense** | Permitido para uso comercial irrestrito e código fechado. Manter aviso de copyright da biblioteca. |
| 🟡 **REVIEW (Exige Avaliação)** | **LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0** | Permitido se consumido estritamente como biblioteca externa dinâmica/npm sem modificação interna do código-fonte da biblioteca. Se houver fork ou alteração direta, requer autorização do PO/Arquiteto. |
| 🔴 **BLOCK (Proibição Total)** | **GPL-2.0, GPL-3.0, AGPL-3.0, SSPL, Licenças com restrição "Non-Commercial", "Commons Clause", "Business Source License (BSL)"** | **TERMINANTEMENTE PROIBIDO** em qualquer software proprietário, SaaS, ERP ou produto comercial Dev Maniac's. Contamina o código proprietário com obrigação de abertura ou risco jurídico de processo. |

---

## 2. A Biblioteca Certa para a Necessidade Certa

| Necessidade | Pacotes Recomendados (Licença Verificada) | Pacotes a Evitar / Depreciados |
| :--- | :--- | :--- |
| **Primitivas Headless Acessíveis** | `@base-ui-components/react` (MIT), `@radix-ui/primitives` (MIT), `@ark-ui/react` (MIT), `react-aria-components` (Apache-2.0) | Próprios componentes recriados com `<div>` e sem suporte a teclado/leitor de tela. |
| **Data Tables & Grids Operacionais** | `@tanstack/react-table` (MIT), `@tanstack/react-virtual` (MIT), `ag-grid-community` (MIT) | Tabela simples em CSS sem paginação virtualizada quando há >100 linhas. |
| **Formulários & Validação** | `react-hook-form` (MIT), `@tanstack/react-form` (MIT), `zod` (MIT) | Estado local disperso com dezenas de `useState` manuais e sem tipagem. |
| **Gráficos & Dashboards** | `echarts-for-react` (Apache-2.0), `recharts` (MIT), `@visx/visx` (MIT), `lightweight-charts` (Apache-2.0) | Bibliotecas abandonadas sem suporte a resize responsivo ou canvas. |
| **Motion & Animação** | CSS Transitions nativas, `@formkit/auto-animate` (MIT), `motion` / `framer-motion` (MIT) | Efeitos de partículas pesados, scripts que sequestram o scroll (*scrolljacking*). |
| **Ícones** | `lucide-react` (MIT), `@tabler/icons-react` (MIT) | Mistura de fontes de ícones diferentes (ex: Lucide + FontAwesome + Material Icons no mesmo app). |

---

## 3. Prevenção da Interface "Frankenstein UI" (Harmonização Obrigatória)

"Frankenstein UI" ocorre quando o desenvolvedor copia componentes de três ou quatro marketplaces diferentes (ex: um botão do shadcn, um card do 21st.dev, um modal do Aceternity e uma tabela do Mantine) e cola no mesmo projeto. O resultado é um monstro visual: bordas com raios diferentes, sombras conflitantes, contrastes incoerentes e fontes desalinhadas.

### Protocolo de Normalização para Importação de Componentes:
Sempre que trouxer um componente ou padrão externo para a base de código:
1. **Descasque as Classes Hardcoded:** Remova classes arbitrárias de cores hexadecimais (ex.: `bg-[#6366f1]`, `text-[#0f172a]`) e substitua pelas variáveis semânticas do projeto (`bg-primary`, `text-foreground`).
2. **Harmonize o Border-Radius:** Substitua o raio arbitrário pela variável global do produto (`rounded-sm` para ERP/industrial, `rounded-md` para B2B). Nunca deixe um container com `rounded-3xl` ao lado de um input com `rounded-none`.
3. **Harmonize a Sombra (Shadow):** Remova sombras neon ou difusas coloridas. Converta para as sombras do sistema (`shadow-sm` ou `shadow-border`).
4. **Alinhe a Família de Ícones:** Se o componente externo veio com SVG embutido ou biblioteca diferente, substitua pelo ícone correspondente da biblioteca padrão única adotada no projeto (ex.: Lucide).
5. **Ajuste o Ritmo Tipográfico:** Garanta que os pesos de fonte (`font-medium`, `font-semibold`) e tamanhos de texto (`text-xs`, `text-sm`, `text-base`) respeitem a escala tipográfica do `DESIGN.md`.
