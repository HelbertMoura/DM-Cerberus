# 🎨 Workflow: Desintoxicação Visual (Visual Repair)

Procedimento cirúrgico para remover o aspecto de "template de IA" de interfaces já construídas.

---

## Passo a Passo da Desintoxicação

### Passo 1: Purga de Cores & Gradientes
- **Ação:** Identifique gradientes roxo/azul nos fundos ou textos.
- **Correção:** Substitua por fundos sólidos de alto contraste (ex: `#F1F5F9` ou `#0F172A`) com cores de destaque sólidas definidas no `DESIGN.md`.

### Passo 2: Eliminação de Glassmorphism & Glow
- **Ação:** Localize cards com `backdrop-blur`, transparências `rgba` e sombras coloridas difusas.
- **Correção:** Substitua por superfícies sólidas com bordas nítidas de 1px (`border-slate-200` ou `border-slate-800`) e sombras de elevação discretas (`shadow-sm` ou `shadow-md`).

### Passo 3: Ajuste de Raio de Borda (Border Radius)
- **Ação:** Cards e modais com bordas excessivamente redondas (`rounded-2xl`, `rounded-3xl` / 16px+).
- **Correção:** Traga para escalas funcionais e profissionais (`rounded-md` / 6px a 8px para sistemas industriais; máx 12px para componentes de consumo).

### Passo 4: Desconstrução de Grids Predictíveis
- **Ação:** Grids de 3 cards perfeitamente idênticos com ícones redondos no topo.
- **Correção:** Agrupe as informações por relevância. Transforme itens secundários em listas compactas, destaque a métrica principal e crie ritmo visual assimétrico intencional.

### Passo 5: Substituição por Conteúdo Real
- **Ação:** Remover "John Doe", textos em latim, números redondos artificiais.
- **Correção:** Insira dados plausíveis do negócio (nomes reais de obras, valores monetários verossímeis, CNPJs válidos de teste, estados operacionais autênticos).
