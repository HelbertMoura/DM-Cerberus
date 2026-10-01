# 🗺️ ROADMAP.md — Visão Executiva de Entregas Dev Maniac's
> **Propriedade:** Dev Maniac's Systems (Helbert Moura)
> **Atualizado em:** 22 de Agosto de 2026
> **Vincular com:** projects/<prod>/status.md (detalhes) · DECISIONS.md (arquitetura)

---

## 🎯 Estratégia Macro

Dev Maniac's opera em **3 frentes paralelas**:

1. **CanteiroHUB / DM-ERP** — Produto-âncora (16 módulos, 6 prontos)
2. **Ecossistema Dev Maniac's** — Biolar, HelpDev, DM-PDV, Drives (operação real)
3. **Infraestrutura** — Servidor Rocky, túneis Cloudflare, observabilidade

---

## 📅 Q3/2026 (Jul–Set) — Foco Atual

### 🔥 Em Andamento (Sprint Atual)
| # | Produto | Módulo/Tarefa | Responsável | Status | Entrega |
|---|---|---|---|---|---|
| 01 | DM-Cerebro | Sistema completo 10/10 | Helbert + Tríade | 🟢 80% | 22/08/2026 |
| 02 | CanteiroHUB | Módulo 07 (Compras) | Z.AI Hermes | 🟡 15% | 15/09/2026 |
| 03 | Biolar | Migração Django 5.2 | MiniMax M3 | 🔴 0% | 30/09/2026 |

### ⏳ Próximas Entregas
| # | Produto | Módulo/Tarefa | Responsável | Início | Entrega |
|---|---|---|---|---|---|
| 04 | CanteiroHUB | Módulo 08 (Medições) | Gemini | 01/09 | 30/09/2026 |
| 05 | DM-Cerebro | Git + GitHub Actions backup | Helbert | 23/08 | 25/08/2026 |
| 06 | Biolar | SEFAZ DF-e módulo fiscal | Z.AI Hermes | 01/09 | 15/10/2026 |

### 💡 Backlog & Pendências Estratégicas
- [ ] **Frontend Global:** Adotar pipeline de **Design Iterativo com MiniMax M3** (prototipagem com Live Preview visual, tokens e UI Industrial Solid-State)
- [ ] **CanteiroHUB (Obras):** Integração **Open-Meteo** (previsão horária de chuva e tempo para Diário de Obra e planejamento de concretagem)
- [ ] **CanteiroHUB (Cronograma):** Integração **BrasilAPI Feriados** (cálculo automático de dias úteis no Cronograma Físico-Financeiro)
- [ ] **CanteiroHUB (Financeiro):** Integração **AwesomeAPI Câmbio & SELIC/CDI** (reajuste automático de parcelas e índices contratuais)
- [ ] **Biolar Dedetizadora:** Integração **Open-Meteo** (bloqueio/alerta automático de agendamento de dedetização externa em dias de chuva)
- [ ] **Biolar & dm-erp (Cadastros):** Integração **ViaCEP & BrasilAPI CNPJ / ReceitaWS** (autopreenchimento e validação cadastral)
- [ ] CanteiroHUB Módulo 09 (Cronograma Físico) — usar dados da wiki EAP
- [ ] HelpDev — v2 com integração WhatsApp Business
- [ ] DM-PDV — NFC-e + SAT (depende de A1 do Biolar)
- [ ] Drive APAE — Migração Collabora 24.04
- [ ] Teenus Drive — SSO unificado com CanteiroHUB

---

## 📅 Q4/2026 (Out–Dez) — Próximo Trimestre

### � Marcos Estratégicos
- **Out/2026:** CanteiroHUB 12/16 módulos prontos (marco de 75%)
- **Nov/2026:** Biolar em produção com SEFAZ + módulo fiscal completo
- **Dez/2026:** DM-PDV com NFC-e validado, primeira venda real processada

### 📋 Entregas Planejadas
- CanteiroHUB: Módulos 10–13 (RH, Folha, Ponto, SST)
- Biolar: WhatsApp bot de agendamento
- HelpDev: Dashboard executivo + métricas
- DevManiacs Portal: v2 com cases reais

---

## 🚧 Bloqueios Atuais

| Bloqueio | Impacto | Plano |
|---|---|---|
| Servidor Rocky sem backup automático | 🔴 Alto | Configurar BorgBackup → B2 (Backblaze) esta semana |
| DNS wildcard `*.devmaniacs.com.br` não configurado | 🟡 Médio | Adicionar ao Cloudflare esta semana |
| Certificados A1 vencendo em Out/2026 | 🟡 Médio | Renovar + automatizar com script Python |

---

## 📊 KPIs de Acompanhamento

| Métrica | Meta Q3 | Atual |
|---|---|---|
| Módulos CanteiroHUB prontos | 8/16 | 6/16 (37.5%) |
| Uptime ecossistema Dev Maniac's | 99.5% | 99.8% ✅ |
| Cérebro atualizado (commits/30d) | 30 | TBD (iniciando agora) |
| Bugs críticos em produção | 0 | 0 ✅ |

---

## 🔗 Links Úteis

- **Status por produto:** `projects/<slug>/status.md`
- **Arquitetura:** `wiki/infra-servidor-rocky.md`
- **Decisões:** `DECISIONS.md`
- **Lições:** `LEARNINGS.md`

---

## 📝 Convenções

- 🟢 **Concluído / No prazo**
- 🟡 **Em andamento / Risco**
- 🔴 **Bloqueado / Atrasado**
- ⚪ **Backlog / Sem data**

**Última revisão:** 22/08/2026 · **Próxima revisão:** 01/09/2026 (sprint review)
