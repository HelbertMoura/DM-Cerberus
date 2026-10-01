---
titulo: Langflow — RAG Visual & Servidores MCP para Produtos
tags: [global, langflow, rag, mcp, vector-database, ai-pipeline]
atualizado: 2026-08-31
status: ativo
---

# 🌊 Langflow — RAG Visual & Servidores MCP (Dev Maniac's)

> **Repositório Oficial:** [github.com/langflow-ai/langflow](https://github.com/langflow-ai/langflow)  
> **Propósito:** Construtor visual drag-and-drop para pipelines de RAG (busca vetorial, embeddings, leitura de PDFs/tabelas/documentos) e agentes que podem ser expostos como **API REST** ou **Servidor MCP (Model Context Protocol)**.

---

## 🎯 1. Onde o Langflow entra na Arquitetura Dev Maniac's

O Langflow **NÃO substitui o Maestri/OpenCode** (que são nossos ambientes de engenharia de software e código).  
Ele é a nossa **ferramenta de esteira de dados e RAG para os produtos finais**:

```text
┌────────────────────────────────────────────────────────┐
│  Documentos de Negócio (Leis, SEFAZ, Manuais, Orçamentos) │
└──────────────────────────┬─────────────────────────────┘
                           │ Ingestão / Embeddings
                           ▼
               ┌────────────────────────┐
               │    LANGFLOW ENGINE     │
               │  (Pipeline RAG Visual) │
               └───────────┬────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
 🔌 Servidor MCP                         🌐 API REST / Webhook
 (Consumido pelos Agentes                (Consumido pelo Frontend
 no Maestri / OpenCode)                  do Biolar / dm-erp)
```

---

## 🛠️ 2. Casos de Uso Oficiais por Produto

| Produto | Caso de Uso Langflow | Formato de Saída |
| :--- | :--- | :--- |
| **dm-erp (CanteiroHUB)** | RAG para busca semântica em tabelas SINAPI, composições de custo e normas ABNT. | Servidor MCP + Endpoint REST |
| **Biolar Dedetizadora** | Consulta inteligente a fichas técnicas de praguicidas, FISPQ, certificados e laudos. | Servidor MCP para o agente de suporte |
| **HelpDev / Central** | Triagem automática de tickets com base na base de conhecimento histórica. | Webhook / API REST |

---

## 🔌 3. Como plugar um fluxo do Langflow como MCP no OpenCode / Maestri

Quando um pipeline de RAG for publicado no Langflow como MCP Server (porta padrão `7860` ou endpoint customizado), qualquer agente no OpenCode pode consumi-lo adicionando no `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "langflow-rag-service": {
      "type": "remote",
      "url": "http://127.0.0.1:7860/api/v1/mcp",
      "enabled": true
    }
  }
}
```

---

## 🚢 4. Padrão de Deploy (Container Docker)

* **Host:** `127.0.0.1` ou IP do servidor interno
* **Container:** `docker run -d --name cerberus-langflow -p 7860:7860 -v ./data/langflow:/data langflowai/langflow:latest`
* **Persistência:** Volumes montados em `./data/langflow`.
