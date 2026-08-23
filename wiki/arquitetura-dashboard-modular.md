# 📊 Dashboard Modular Adaptativa (Dashboard Studio v2) — Telemetria & Widgets
> **Módulo:** 03 · Painel Executivo / Command Center  
> **Sistema:** CanteiroHUB (Dev Maniac's) · Instância Teenus Gestão  
> **Versão Oficial:** `v1.0.0-ALPHA (Build 2026.08)`  
> **Suíte de Testes:** `smoke_rodada138.py` (12/12 verdes · budget <= 26 queries)  
> **Atualizado em:** 22 de Agosto de 2026

---

## 🎯 1. Visão Geral & Arquitetura de Entrega
A Dashboard v2 foi totalmente reconstruída em uma arquitetura de widgets desacoplados, adaptativos ao Tenant e com telemetria agregada em lote:

1. **Endpoint de Telemetria em Lote (`GET /api/v1/dashboard/telemetria/`):**
   - Retorna os 6 blocos de telemetria em uma única chamada SQL otimizada (sem N+1).
   - **Garantia de Teste:** O budget de queries ($\le 26$ queries) é assertado na suíte via `CaptureQueriesContext`.
   - **Gates Fail-Safe:** Módulos desabilitados no Tenant retornam `None` e não disparam queries no banco.

2. **Catálogo de 6 Widgets Oficiais:**
   - `WidgetSaudeObras`: 3 obras ativas, progresso EAP, Curva S e aderência financeira.
   - `WidgetRDOCampo`: Clima dos 3 turnos, efetivo total presente, fotos recentes e horímetro.
   - `WidgetContratosOrcamentos`: Total contratado, propostas abertas e atalho de formalização 1-clique.
   - `WidgetRHCompliance`: Alertas ASO 30/15/5 dias, colaboradores bloqueados e entregas de EPI.
   - `WidgetFinanceiroDRE`: Saldo consolidado, contas a pagar hoje e DRE do mês com margem líquida.
   - `WidgetMinhasTarefas`: Kanban pessoal com prioridades (Urgente, Alta, Média, Baixa).

3. **Gaveta Lateral de Personalização (`DashboardCustomizerDrawer.tsx`):**
   - *Toggles* para exibir/ocultar cada widget (com filtro estrito de módulos contratados).
   - Botões para subir/descer a ordem de exibição.
   - Presets Rápidos: `[Modo Engenharia]`, `[Modo Diretoria]` e `[Restaurar Padrão]`.
   - Persistência instantânea no `localStorage` (`dm_erp_dash_layout_v2`).
