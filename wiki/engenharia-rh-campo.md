# 🦺 RH & Colaboradores de Campo — Compliance Trabalhista & LGPD
> **Módulo:** 13 · Gestão de Colaboradores, ASOs e EPIs  
> **Sistema:** CanteiroHUB (Dev Maniac's) · Instância Teenus Gestão  
> **Normas Regulamentadoras:** NR-06 (EPI) e NR-07 (PCMSO) do Ministério do Trabalho e Emprego (MTE)  
> **Atualizado em:** 22 de Agosto de 2026

---

## 🎯 1. Visão Geral & Regras de Compliance
A gestão de pessoas no canteiro de obras exige conformidade jurídica rigorosa para evitar embargos, multas do MTE e passivos trabalhistas:

1. **Bandas de Validade de ASO (NR-07):**
   - 31+ dias: `APTO` (Verde)
   - 16 a 30 dias: `VENCENDO_30D` (Amarelo)
   - 6 a 15 dias: `VENCENDO_15D` (Laranja)
   - 0 a 5 dias: `VENCENDO_5D` (Vermelho Alerta Crítico Final)
   - Vencido (<0 dias): `BLOQUEADO_ASO_VENCIDO` (Bloqueio Automático)
   - **Regra de Bloqueio:** Colaborador com ASO vencido ou inapto é impedido de ser alocado em novos RDOs de obras.

2. **Ficha de EPI Digital (NR-06):**
   - Validação obrigatória do número do Certificado de Aprovação (**CA do MTE**).
   - Assinatura touch criptográfica do colaborador com envelope SHA-256 e timestamp UTC.
   - Troca por desgaste fecha o termo anterior como `SUBSTITUIDO` e gera novo termo pendente de assinatura.

3. **Blindagem LGPD:**
   - Mascaramento rigoroso de CPF (`***.###.###-**`) para usuários sem papel de Diretoria/RH/SuperAdmin.
   - Padrão fail-closed: sem requisição autenticada com papel administrativo, o CPF é sempre mascarado.
