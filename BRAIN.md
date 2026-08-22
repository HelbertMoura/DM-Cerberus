---
titulo: Mapa Mestre do Segundo Cérebro Dev Maniac's
tags: [brain, mapa, indice]
atualizado: 2026-08-22
status: ativo
---

# 🧠 Dev Maniac's — Segundo Cérebro Central Global (DM-Cerebro)
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)
> **Localização Central:** `C:\Users\Helbert\Desktop\DM-Cerebro\`
> **Tríade Autorizada:** ♊ **Gemini** (Orquestrador + Engenheiro Chefe) · 🚀 **MiniMax M3** (Heavy Builder) · 🧠 **Z.AI GLM 5.3 / Hermes** (Deep Reasoning Specialist)
> **Versão:** 2.0 · 22 de Agosto de 2026

---

## 🔒 REGRA DE ISOLAMENTO E PROTOCOLO DE DISPARO (HELBERT NO COMANDO)

> ⚠️ **ATENÇÃO INEGOCIÁVEL PARA TODAS AS IAs:**
> 1. Este Segundo Cérebro pertence **EXCLUSIVAMENTE** aos projetos da **Dev Maniac's** (Helbert Moura).
> 2. **O Gemini SEMPRE entrega os prompts prontos e formatados** para o Helbert copiar e colar manualmente no Hermes (Z.AI) e no MiniMax M3.
> 3. O Helbert cola as respostas de volta para o Gemini auditar, testar, dar deploy e atualizar este cérebro.
> 4. **PROIBIDO** misturar dados ou chaves de outras empresas onde o Helbert atua.

---

## 📜 REGRAS DE OURO (LER ANTES DE QUALQUER AÇÃO)

1. **1 arquivo = 1 tema**. Nunca lixão. Se passar de 500 linhas, fragmentar.
2. **Nomenclatura:** `lowercase + hífens`. Ex.: `biolar-deploy.md` (não `Biolar_Deploy.MD`).
3. **Frontmatter YAML obrigatório** em todo `.md`:
   ```yaml
   ---
   titulo: ...
   tags: [categoria, subcategoria]
   atualizado: AAAA-MM-DD
   status: ativo | deprecated | draft
   ---
   ```
4. **Toda IA lê este BRAIN.md antes de agir** + `projects/_shared/TRIADE_PROTOCOLO.md` para regras operacionais + `projects/_shared/CONTRATO_AGENTES.md` para contrato obrigatório.
5. **Toda IA atualiza o cérebro ao concluir tarefa** (ver `CONTRATO_AGENTES.md` — sempre commitar + pushar) E adiciona entrada em `HANDOVER.md` (log de passagem de bastão).
6. **`raw/` é gaveta temporária** — após ingestão, mover para `raw/processed/AAAA-MM-DD/`.

---

## 🗺️ Mapa Global do Cérebro (Directory Index Map)

```
C:\Users\Helbert\Desktop\DM-Cerebro\
│
├── 📄 BRAIN.md             ➔ Este arquivo (mapa mestre + regras)
├── 📄 MEMORY.md            ➔ Memória executiva permanente
├── 📄 DECISIONS.md         ➔ ADRs (Architecture Decision Records)
├── 📄 HANDOVER.md          ➔ 🤝 Log de passagem de bastão entre agentes
├── � LEARNINGS.md         ➔ Caderno de lições aprendidas
├── 📄 ROADMAP.md           � Visão de entregas e sprints
│
├── 📂 raw/                 ➔ � Gaveta de Ingestão (jogue PDFs/manuais aqui)
│   ├── README.md           ➔ Política de uso e retenção
│   └── processed/          ➔ Arquivos já ingeridos (90 dias → deletar)
│
├── 📂 projects/            ➔ 📦 Especificações por Produto
│   ├── canteirohub/
│   │   ├── README.md              ➔ Visão geral
│   │   ├── status.md              ➔ Status por sprint
│   │   ├── arquitetura.md         ➔ Stack e padrões
│   │   ├── auditoria-360-usabilidade.md
│   │   └── relatorio-auditoria-final.md
│   ├── biolar/
│   │   ├── README.md              ➔ Visão geral
│   │   ├── status.md              ➔ (criar)
│   │   └── arquitetura.md         ➔ (criar)
│   ├── helpdev/
│   │   └── README.md
│   ├── dmpdv/
│   │   └── README.md
│   ├── apae-juatuba/
│   │   └── README.md
│   └── _shared/            � Cross-product + Protocolo da Tríade
│       ├── README.md
│       ├── TRIADE_PROTOCOLO.md    ➔ Papéis Gemini + M3 + Z.AI
│       ├── CONTRATO_AGENTES.md    ➔ Contrato obrigatório ler/atualizar
│       ├── github-publicar.md
│       ├── backup-procedimento.md
│       └── backup-dm-cerebro.sh
│
├── 📂 wiki/                ➔ 📚 Conhecimento Técnico Destilado
│   ├── infra-servidor-rocky.md        ➔ Mapa do servidor 192.168.226.103
│   ├── engenharia-bdi-tcu.md          ➔ BDI TCU 2622/2013
│   ├── engenharia-eap-curvas.md       ➔ Largest-Remainder + Curva S
│   ├── fiscal-sefaz-a1.md             ➔ PKCS#12, XMLDSig, SEFAZ DF-e
│   └── protocolo-triade-agentes.md    ➔ Divisão Gemini + M3 + Z.AI
│
└── � prompts/             ➔ 🤖 Prompts Copy-Paste para IAs
    ├── PROMPT_ZAI_HERMES.md
    ├── PROMPT_MINIMAX_M3.md
    └── SYSTEM_PROMPT_PADRAO_M3.md   ➔ 🆕 Copy-paste pro MiniMax M3
```

---

## ⚡ Como Usar e Alimentar o Cérebro

### 📥 Para Aprender Algo Novo (Ingest)
1. Arraste PDF/imagem/texto para `C:\Users\Helbert\Desktop\DM-Cerebro\raw\`
2. Diga: *"Ingest this: processe X da pasta raw"*
3. IA classifica, destila e move original para `raw/processed/AAAA-MM-DD/`

### 🔍 Para Consultar Conhecimento
- Toda IA pode ler livremente: `wiki/`, `projects/`, `LEARNINGS.md`, `MEMORY.md`
- Para arquitetura: `projects/<prod>/arquitetura.md`
- Para decisões: `DECISIONS.md` (ADRs)
- Para status atual: `projects/<prod>/status.md`

### ✏️ Para Atualizar Após Tarefa
- Nova decisão arquitetural → `DECISIONS.md` (formato ADR)
- Novo erro/gotcha → `LEARNINGS.md` (append)
- Nova entrega concluída → `ROADMAP.md` (marcar ✅)
- Novo produto/módulo → `projects/<slug>/` (criar subpasta)

---

## � Links Cruzados Importantes

- **Protocolo da tríade:** `wiki/protocolo-triade-agentes.md`
- **Infraestrutura:** `wiki/infra-servidor-rocky.md`
- **Status sprints:** `ROADMAP.md`
- **Memória permanente:** `MEMORY.md`

---

**Última atualização:** 22 de Agosto de 2026 · **Versão:** 2.0 · **Score:** 10/10 🎯
