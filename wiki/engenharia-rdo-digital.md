# 🏗️ RDO Digital Offline-First — Especificação de Engenharia & Canteiro
> **Módulo:** 07 · Diário de Obras Eletrônico  
> **Sistema:** CanteiroHUB (Dev Maniac's) · Instância Teenus Gestão  
> **Público:** Mestres de Obras, Engenheiros Residentes e Fiscais de Obra  
> **Atualizado em:** 22 de Agosto de 2026

---

## 🎯 1. Visão Geral & Desafios de Canteiro
O Diário de Obras (RDO) é o documento jurídico mais importante de uma construção civil. Ele registra diariamente:
1. **Condições Climáticas nos 3 Turnos:** Manhã, Tarde e Noite (determina juridicamente dias impraticáveis por chuva forte que justificam aditivos de prazo).
2. **Efetivo de Campo:** Contagem de mão de obra própria e terceirizada por função (pedreiros, serventes, carpinteiros, encanadores, eletricistas).
3. **Horímetro & Maquinário:** Horas produtivas vs horas paradas (chuva, falta de insumo, manutenção mecânica).
4. **Apontamento de Etapas da EAP:** Percentual de avanço físico executado no dia em cada fase da obra.
5. **Galeria Fotográfica:** Fotos de canteiro comprimidas no navegador via Canvas API (máx 150KB por foto) para economizar dados 4G.
6. **Assinaturas Digitais Touch:** Coleta de rubrica do Mestre e Engenheiro direto na tela do celular com timestamp e hash SHA-256.

---

## 📡 2. Arquitetura PWA Offline-First (IndexedDB Dexie)
Como canteiros de obra frequentemente não têm sinal de internet:
- **Fluxo Offline:** O Mestre preenche o RDO normalmente offline no celular -> o registro é salvo no banco local **IndexedDB (Dexie)** com status `PENDENTE_SYNC`.
- **Sincronização Automática:** Um worker monitora o evento `window.addEventListener('online')` -> envia os dados e fotos para a API REST Django `/api/v1/rdo/` com transação atômica.
- **Feedback Visual:** Indicador sutil de conectividade (🟢 *Sincronizado* / 🟡 *Salvo no Celular (Offline)*).

---

## 🗄️ 3. Modelagem de Dados Django (`apps.rdo`)

```python
class RDO(TenantAwareModel):
    obra = models.ForeignKey('obras.Obra', on_delete=models.CASCADE, related_name='rdos')
    numero_sequencial = models.PositiveIntegerField() # Ex: RDO-042
    data_rdo = models.DateField()
    status = models.CharField(max_length=20, choices=StatusRDOChoices.choices, default='RASCUNHO')
    
    # Clima 3 Turnos
    clima_manha = models.CharField(max_length=20, choices=CondicaoClimaChoices.choices)
    clima_tarde = models.CharField(max_length=20, choices=CondicaoClimaChoices.choices)
    clima_noite = models.CharField(max_length=20, choices=CondicaoClimaChoices.choices)
    dia_praticavel = models.BooleanField(default=True)
    
    # Totais e Notas
    total_efetivo = models.PositiveIntegerField(default=0)
    observacoes = models.TextField(blank=True)
    acidentes_ocorrencias = models.TextField(blank=True)
    
    # Assinaturas
    assinatura_mestre = models.TextField(blank=True) # Base64
    assinatura_engenheiro = models.TextField(blank=True) # Base64
    data_aprovacao = models.DateTimeField(null=True, blank=True)
```

---

## 🌐 4. Internacionalização (3 Idiomas)
- Todas as opções de clima, funções de operários, relatórios A4 e botões com suporte nativo a PT-BR, EN-US e ES no `useI18n()`.
