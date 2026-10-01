# 📝 Referência: Arsenal Camada 7 — Formulários Empresariais & Validação

> **Princípio Central:** Formulários corporativos são ferramentas operacionais de entrada de dados, não cartões postais. Transformar um cadastro empresarial em 20 cards flutuantes é anti-produtivo. Agrupe campos semanticamente, forneça validação inline nítida com acessibilidade e nunca perca o trabalho do usuário.

---

## 1. Stack Canônica de Formulários

| Responsabilidade | Tecnologia Recomendada | Licença | Benefício de Engenharia |
| :--- | :--- | :--- | :--- |
| **Gerenciamento de Estado** | **[React Hook Form](https://react-hook-form.com)** ou **[TanStack Form](https://tanstack.com/form)** | MIT | Re-renders isolados nos inputs sem travar a tela inteira; suporte nativo a arrays dinâmicos de campos. |
| **Validação de Schemas** | **[Zod](https://zod.dev)** | MIT | Validação type-safe com inferência de tipos Typescript tanto no cliente quanto no backend. |
| **Máscaras de Entrada (pt-BR)** | **[@react-input/mask](https://github.com/uNmAnNeR/imaskjs)** | MIT | Formatação estrita sem pular cursor: CNPJ, CPF, CEP, Telefone e Moeda BRL (`R$ 1.250,00`). |

---

## 2. Padrões de Arquitetura de Formulários

### A. Agrupamento Semântico (Anti-Card Abuse)
- **NÃO** envolva cada par de campos em um card com sombra e borda arredondada de 16px.
- Use elementos HTML semânticos:
  - `<fieldset>` com `<legend>` para agrupar blocos lógicos (*"Dados da Empresa"*, *"Endereço Fiscal"*, *"Contatos de Cobrança"*).
  - Divisores finos e sutis (`border-t border-border/40`) para separar seções sem inflar o DOM.

### B. Validação Inline Acessível
- **Feedback no Momento Certo:** Não valide enquanto o usuário ainda está digitando os primeiros caracteres de um e-mail; valide no evento `onBlur` (ao sair do campo) ou após a primeira tentativa de submissão.
- **Acessibilidade Obrigatória:**
  ```html
  <!-- Campo com erro conectado semanticamente -->
  <input 
    id="cnpj" 
    name="cnpj" 
    aria-invalid="true" 
    aria-describedby="cnpj-error" 
  />
  <span id="cnpj-error" role="alert" class="text-xs text-destructive">
    CNPJ inválido ou incompleto.
  </span>
  ```

### C. Campos Dependentes (Dependent Fields)
- Quando a seleção de um campo altera as opções do próximo (ex: *Tipo de Empresa* define se o campo *Inscrição Estadual* é obrigatório, ou *Estado* carrega *Cidades*):
  - Mantenha o campo dependente desabilitado (`disabled`) com placeholder explicativo (*"Selecione o estado primeiro"*) enquanto a requisição estiver pendente.
  - Exiba um indicador de carregamento discreto dentro do próprio input, sem piscar o layout.

### D. Arrays Dinâmicos de Campos (Field Arrays)
- Em cadastros como **Itens da Nota Fiscal** ou **Insumos da Ordem de Serviço**:
  - Use `useFieldArray` para permitir adicionar/remover linhas sem re-renderizar o formulário todo.
  - Ofereça teclas de atalho: pressionar `Enter` na última coluna adiciona uma nova linha automaticamente.
  - Botão de exclusão de linha com confirmação sutil ou possibilidade de desfazer (*Undo*).

### E. Proteção contra Perda de Dados (Autosave & Unsaved Changes Guard)
1. **Autosave Silencioso com Indicador Visual:**
   - Em formulários longos, salve o rascunho a cada 2 segundos de inatividade e exiba no rodapé: *"Rascunho salvo às 14:32:05"*.
2. **Guarda de Saída Acidental:**
   - Se o formulário estiver com `isDirty: true` (com alterações não salvas) e o operador tentar fechar a aba ou clicar em um link lateral:
   - Dispare o diálogo de confirmação do navegador (`beforeunload`) ou modal de confirmação do router: *"Você possui alterações não salvas. Deseja realmente sair?"*.
