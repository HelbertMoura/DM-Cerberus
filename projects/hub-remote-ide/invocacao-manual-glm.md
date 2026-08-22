---
titulo: Como invocar GLM 5.3 manualmente (sem mudar o padrão MiniMax M3)
tags: [manual, glm, zai, invocação, on-demand, fallback, hub, devmaniacs]
atualizado: 2026-08-22
status: ativo
decisao: GLM 5.3 fica como INVOCAÇÃO MANUAL (não padrão)
---

# 🧠 Como invocar GLM 5.3 manualmente

> **Decisão:** Mantemos MiniMax M3 como provedor padrão do Hermes Agent.
> GLM 5.3 fica disponível pra **invocação manual** sob demanda.

---

## ✅ Status atual (MiniMax M3 padrão)

```
model:
  default: MiniMax-M3
  provider: minimax
fallback_providers:
  - provider: zai
    model: glm-5.3    ← só ativa se M3 falhar
```

- **Padrão:** MiniMax M3 (todas as sessões normais)
- **Fallback automático:** Z.AI GLM 5.3 (só se M3 falhar/timeout)
- **Manual:** você pode forçar GLM 5.3 em qualquer momento (ver abaixo)

---

## � Como invocar GLM 5.3 manualmente

### Opção 1: Variável de ambiente na hora do comando

```bash
ZAI_API_KEY="e922a58d1cfe4ebd8a3c4ec5937a1264.LaxlbbphPjm8KJ4R" \
  hermes --provider zai --model glm-5.3
```

### Opção 2: Sessão dedicada com `.env` temporário

```bash
# 1. Criar .env temporário
cat > /tmp/glm-session.env <<EOF
ZAI_API_KEY=e922a58d1cfe4ebd8a3c4ec5937a1264.LaxlbbphPjm8KJ4R
HERMES_PROVIDER=zai
HERMES_MODEL=glm-5.3
EOF

# 2. Rodar Hermes com esse env
set -a; source /tmp/glm-session.env; set +a
hermes chat
```

### Opção 3: Por task (sem sessão dedicada)

Quando quiser que UMA task específica use GLM 5.3:

```
/use glm-5.3 para esta task: <descreve a task>
```

Eu detecto o `/use glm-5.3` no início e delego via subagent com provedor `zai`.

---

## 📋 Quando vale a pena usar GLM 5.3

### ✅ Use GLM 5.3 quando precisar de:

| Caso | Por quê GLM 5.3 é melhor |
|---|---|
| **ADRs técnicos complexos** | Raciocínio matemático denso, trade-offs profundos |
| **Cálculo BDI TCU / Curva S / EVM** | Densidade numérica superior |
| **Análise de risco financeiro** | Pensa em cenários múltiplos |
| **Diagnóstico de bug difícil** | Stack trace analysis profundo |
| **Design de schema PostgreSQL** | Trade-offs de normalização + performance |
| **Otimização de query SQL complexa** | EXPLAIN ANALYZE mental |
| **Criptografia SEFAZ (PKCS#12, XMLDSig)** | Raciocínio formal sobre assinaturas |
| **Planejamento arquitetural** | Vê trade-offs não-óbvios |

### ❌ NÃO use GLM 5.3 pra:

| Caso | Por quê M3 é melhor |
|---|---|
| **Scaffold de código** | M3 é mais rápido |
| **TDD / 50 testes** | Volume = velocidade |
| **Copy de UI** | M3 gera mais rápido |
| **Tradução i18n** | Tarefa simples, M3 basta |
| **Refactor mecânico** | M3 é eficiente |
| **Documentação repetitiva** | M3 escreve mais rápido |

---

## 🎯 Padrão recomendado por tarefa

```
┌─────────────────────────────────────────┐
│  Você decide ANTES de cada task:        │
│                                         │
│  "Isso precisa de matemática densa?     │
│   → Sim → GLM 5.3                       │
│   → Não → MiniMax M3"                   │
└─────────────────────────────────────────┘
```

**Regra de bolso:**
- 1 linha de código = M3
- 1 decisão arquitetural = GLM 5.3
- 1 cálculo numérico = GLM 5.3
- 1 página de UI = M3
- 1 ADR formal = GLM 5.3
- 1 bug misterioso = GLM 5.3

---

## 🔑 Sua chave Z.AI (referência)

```
ZAI_API_KEY=e922a58d1cfe4ebd8a3c4ec5937a1264.LaxlbbphPjm8KJ4R
```

**⚠️ NÃO commitar.** Sempre passar por env var ou `.env` local.

**Modelos disponíveis** (validado 22/08/2026):
- `glm-4.5`, `glm-4.5-air`, `glm-4.6`, `glm-4.7`
- `glm-5`, `glm-5-turbo`, `glm-5.1`, `glm-5.2`, **`glm-5.3`**

**Recomendado:** sempre `glm-5.3` (mais recente).

---

## � Teste rápido

```bash
# Testar conexão
curl -s "https://api.z.ai/api/paas/v4/models" \
  -H "Authorization: Bearer $ZAI_API_KEY" | jq '.data[].id'

# Deve listar glm-4.5 até glm-5.3
```

---

## 📝 Histórico da decisão

| Data | Decisão | Motivo |
|---|---|---|
| 2026-08-22 | GLM 5.3 como **invocação manual** | M3 continua padrão, GLM sob demanda |

---

**Owner:** Helbert Moura · Dev Maniac's Systems · 22/08/2026
