---
titulo: Normalização de EAP & Curva S Físico-Financeira
tags: [engenharia, eap, curva-s, largest-remainder]
atualizado: 2026-08-22
status: ativo
---

# 📊 Engenharia: Normalização de EAP & Curva S Físico-Financeira
> **Algoritmo:** Maior Resíduo (Largest-Remainder Method / Hamilton-Hare)
> **Garantia:** $\sum \text{Pesos} = 100.00\%$ exato, sem perdas por arredondamento decimal.

---

## 🏗️ Normalização da Árvore EAP
Ao clonar composições de um Orçamento para as Etapas da Obra:
1. Calcula-se a proporção bruta de cada etapa sobre o valor total orçado.
2. Trunca-se em duas casas decimais e calcula-se a soma preliminar.
3. A diferença de centavos residuais ($100.00 - \sum \text{truncado}$) é distribuída 1 centésimo por etapa ordenando pelas etapas de maior resíduo decimal.

---

## 📈 Interpolação da Curva S
- **Previsto:** Distribuição logística / sigmoidal $S(t) = \frac{1}{1 + e^{-k(t - t_0)}}$ ao longo da duração contratual.
- **Realizado:** Somatório acumulado das medições e diários de obra (RDOs) aprovados.
- **EVM (Earned Value Management):**
  - $SPI = \frac{EV}{PV}$ (Índice de Desempenho de Prazo)
  - $CPI = \frac{EV}{AC}$ (Índice de Desempenho de Custo)
