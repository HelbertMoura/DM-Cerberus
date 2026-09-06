# 📝 UI Pattern: Forms & Inputs

## 1. Pattern: Progressive Disclosure Form
- **USE WHEN:** Cadastros extensos (ex: fornecedores, obras, dados fiscais SEFAZ) que sobrecarregam visualmente se exibidos em uma única tela.
- **AVOID WHEN:** Formulários rápidos com menos de 6 campos (ex: login, busca, contato rápido).
- **UX:** Dividir em etapas lógicas (Etapa 1: Dados Básicos ➔ Etapa 2: Endereço ➔ Etapa 3: Financeiro). Exibir barra de progresso com rótulos de status claros.
- **A11Y:** Anunciar avanço de etapas aos leitores de tela (`aria-live="polite"`). Manter dados salvos caso o usuário volte à etapa anterior.
- **MOBILE:** Formulário de coluna única. Teclado virtual adequado ao tipo (`inputmode="numeric"` para CEP/CNPJ/telefone).
- **DESKTOP:** Grid de 2 ou 3 colunas com alinhamento rigoroso de labels e inputs.
- **REFERENCES:** TanStack Form, React Hook Form + Zod.

---

## 2. Pattern: Inline Validation & Error Signposting
- **USE WHEN:** Qualquer formulário com regras de validação (formato de email, CNPJ, obrigatórios).
- **AVOID WHEN:** Validar agressivamente antes do usuário interagir com o campo (`onBlur` é superior a `onChange` imediato para novos campos).
- **UX:** Mensagem de erro específica e orientativa (ex: *"Informe um CNPJ válido com 14 dígitos"* em vez de *"Campo inválido"*).
- **A11Y:** Associar erro ao campo via `aria-describedby="field-error-id"`, marcar `aria-invalid="true"`.
- **MOBILE:** Mensagem de erro logo abaixo do campo sem causar deslocamento brusco de layout (layout shift).
- **DESKTOP:** Ícone de alerta discreto + mensagem textual em cor de alto contraste.
- **REFERENCES:** W3C Web Accessibility Tutorials: Form Instructions.
