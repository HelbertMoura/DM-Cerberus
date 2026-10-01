# 🧬 Referência: Framework Design DNA & Design Signature

> **Princípio Central:** Interfaces consistentes e com identidade proprietária não nascem de improviso tela a tela. Antes de escrever código ou estilizar componentes, derive explicitamente o **Design DNA** do produto e defina a sua **Design Signature**. Isso impede a deriva estética (*aesthetic drift*) entre diferentes desenvolvedores ou sessões de IA.

---

## 1. As 8 Dimensões do Design DNA

Todo produto deve ter seu perfil calibrado nas 8 dimensões abaixo e registrado em seu `DESIGN.md`:

```text
+-------------------------------------------------------------------------+
|                              DESIGN DNA MATRIX                          |
+-------------------+-----------------------------------------------------+
| 1. PERSONALIDADE  | [ ] Industrial  [ ] Técnica  [ ] Editorial          |
|                   | [ ] Utilitária  [ ] Institucional  [ ] Lúdica        |
+-------------------+-----------------------------------------------------+
| 2. DENSIDADE      | [ ] Alta (ERP/Admin)  [ ] Média  [ ] Baixa (Marketing)|
|                   | [ ] Adaptativa por viewport                         |
+-------------------+-----------------------------------------------------+
| 3. GEOMETRIA      | [ ] Reta (0-2px)  [ ] Sutil (4-6px)                 |
|                   | [ ] Arredondada (8-12px)  [ ] Mista Intencional     |
+-------------------+-----------------------------------------------------+
| 4. CONTRASTE      | [ ] Alto (Industrial/A11Y)  [ ] Equilibrado (SaaS)  |
|                   | [ ] Suave (Editorial controlado)                    |
+-------------------+-----------------------------------------------------+
| 5. DISCIPLINA COR | [ ] Neutra Contida  [ ] Expressiva  [ ] Monocromática|
|                   | [ ] Setorial Funcional (Status-Driven)              |
+-------------------+-----------------------------------------------------+
| 6. TIPOGRAFIA     | [ ] Técnica/Mono-assisted  [ ] Grotesk / Humanista  |
|                   | [ ] Geométrica Intencional  [ ] Serifada Editorial |
+-------------------+-----------------------------------------------------+
| 7. MOTION         | [ ] Estritamente Funcional (<150ms)  [ ] Discreto   |
|                   | [ ] Nenhum (Alta Performance)  [ ] Narrativo        |
+-------------------+-----------------------------------------------------+
| 8. LAYOUT SHELL   | [ ] Operacional Split-View  [ ] Command Center      |
|                   | [ ] Canvas Livre  [ ] Editorial Grid                |
+-------------------+-----------------------------------------------------+
```

### Detalhamento das Dimensões:

### 1. Personalidade
- **Industrial / Utilitária:** Foco em robustez, durabilidade visual, ergonomia de dados, ausência total de ornamentos (ex: Biolar, CanteiroHUB, sistemas de chão de fábrica).
- **Técnica / Developer:** Foco em precisão, densidade de código, atalhos de teclado, fontes mono-espaçadas auxiliares (ex: consoles de observabilidade, ferramentas de dev).
- **Editorial / Institucional:** Foco em tipografia refinada, ritmo de leitura, hierarquia assimétrica, autoridade de marca.

### 2. Densidade
- **Alta:** Mínimo de 20 a 30 registros visíveis por viewport; paddings entre 4px e 12px; controles compactos (`h-8` a `h-9`).
- **Média:** Padrão para SaaS B2B com uso misto de formulários e dashboards; controles `h-10`.
- **Baixa:** Reservada para marketing, onboarding ou telas de fluxo único (checkout, login).

### 3. Geometria (Anti-Rounding)
- **NUNCA** aplique `rounded-2xl` ou `rounded-3xl` em tudo por padrão.
- Sistemas corporativos e industriais operam com máxima precisão e seriedade com **raios de 2px a 6px** (`rounded-xs` a `rounded-md`).
- A geometria dos botões, inputs, modais e badges deve ser rigorosamente harmônica.

### 4. Disciplina de Cores
- Defina o papel semântico estrito de cada cor:
  - `Surface`: background base e elevações (níveis 1, 2, 3).
  - `Border`: limites estruturais sutis com contraste garantido.
  - `Text`: primário (alto contraste), secundário (suporte legível), terciário (metadados).
  - `Action / Brand`: cor de ação reservada exclusivamente para botões interativos e seleção.
  - `Status`: Verde (sucesso/ativo), Âmbar (alerta/pendência), Vermelho (erro/crítico), Azul (informativo).

---

## 2. Design Signature (A Assinatura do Produto)

Uma interface profissional possui **2 a 3 traços reconhecíveis próprios** que fazem o usuário bater o olho e saber que está no seu sistema, sem precisar apelar para gimmicks ou truques de IA.

### Exemplos de Assinaturas Válidas:
- **Tratamento de Headers e Divisores:** Um divisor fino característico com acento sutil na cor da marca em títulos principais.
- **Tratamento de Linhas de Tabela:** Linhas zebradas elegantes com highlight na linha ativa e borda lateral indicativa de status.
- **Micro-interações de Foco:** Um anel de foco customizado de alta precisão (`ring-2 ring-primary/40 ring-offset-1`).
- **Estilo de Badges:** Badges com tipografia mono compacta e ponto de status pulsante sutil.
- **Sidebar & Navegação:** Uma barra de navegação retrátil icônica com atalhos numéricos diretos.

> ⚠️ **Regra Anti-Gimmick:** A assinatura deve resolver um problema real de usabilidade ou reforçar a personalidade da marca. Se for puramente decorativa e atrapalhar a velocidade do operador, remova-a.
