# 📥 raw/ — Gaveta Central de Ingestão

## 🎯 Função

Esta pasta é a **porta de entrada** do Segundo Cérebro. Qualquer documento (PDF, imagem, texto, link) que precise virar conhecimento deve **começar aqui**.

---

## 📋 Política de Uso

### Fluxo Padrão

1. **Você arrasta o arquivo** para `C:\Users\Helbert\Desktop\DM-Cerebro\raw\`
2. **Você aciona uma IA** com o comando:
   > *"Ingest this: processe o arquivo X da pasta raw do DM-Cerebro e adicione na wiki"*
3. **A IA classifica** o conteúdo em uma de 3 categorias:
   - **`wiki/`** → conhecimento destilado reutilizável
   - **`projects/<slug>/`** → contexto específico de produto
   - **Descartar** → irrelevante, deletar após mover para processed/
4. **A IA move o original** para `raw/processed/AAAA-MM-DD/` (data de ingestão)
5. **A IA atualiza** o `BRAIN.md` com nova entrada no índice

### Comando Rápido por IA

| IA | Comando de Ingest |
|---|---|
| Gemini | *"Gemini, ingest this"* |
| MiniMax M3 | *"M3, ingere o arquivo X"* |
| Z.AI Hermes | *"Hermes, processa raw/X"* |

---

## 🚫 Regras

### ✅ PODE
- PDF, DOCX, TXT, MD, imagens (PNG/JPG), áudio (MP3/WAV)
- Screenshots de configurações
- Logs de erro copiados como `.log`
- Snippets de código como `.py`, `.sql`, `.sh`

### ❌ NÃO PODE
- Arquivos > 50 MB (compactar ou dividir antes)
- Dados sensíveis sem criptografia (senhas, chaves privadas, tokens)
- Arquivos temporários (criar pasta `tmp/` em outro lugar)

---

## 🗂️ Estrutura

```
raw/
├── README.md                  ← este arquivo
├── processed/                 ← arquivos já ingeridos (manter por 90 dias)
│   └── AAAA-MM-DD/            ← subpastas por data de ingestão
│       ├── manual-postgres.pdf
│       ├── screenshot-redis.png
│       └── ...
└── (arquivos novos caem aqui direto do Windows Explorer)
```

---

## ⏰ Política de Retenção

| Estado | Tempo | Ação |
|---|---|---|
| Em `raw/` raiz | Indeterminado | Aguardando ingestão |
| Em `raw/processed/AAAA-MM-DD/` | 90 dias | Deletar manualmente (ou script) |
| Promovido para `wiki/` ou `projects/` | Permanente | Linkar no `BRAIN.md` |

**Exceção:** Se o arquivo original tem valor legal/fiscal (ex.: NF-e XML, contrato PDF), manter indefinidamente em `processed/` ou mover para `projects/<slug>/legal/`.

---

## 🧹 Script de Limpeza (90 dias)

Para limpar arquivos > 90 dias em `processed/`:

```bash
# PowerShell (rodar uma vez por mês)
Get-ChildItem -Path "C:\Users\Helbert\Desktop\DM-Cerebro\raw\processed" -Recurse -File |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } |
  Remove-Item -Force -Verbose
```

---

**Última atualização:** 22 de Agosto de 2026
