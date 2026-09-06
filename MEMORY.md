---
titulo: Memória Central Permanente da Dev Maniac's
tags: [memory, contexto, permanente]
atualizado: 2026-09-01
status: ativo
---

# 🧠 MEMORY.md — Memória Central Permanente da Dev Maniac's
> **Fundador:** Helbert Moura (Engenheiro Sênior & Arquiteto Chefe)
> **Empresa:** Dev Maniac's Systems  
> **Diretriz de Design:** Industrial Solid-State (Azul Aço #1E40AF, Chumbo #0F172A, Fundo Sólido #F1F5F9, sem neon/gradientes).  
> **Proibição:** BANIMENTO TOTAL DE EMOJIS no UI de botões e tabelas — usar Lucide-React vetorial ou Tabler Icons.  
> **Multi-Tenant Estrito:** Todo modelo novo deve herdar de `TenantAwareModel`.
> **Internacionalização Obrigatória:** Suporte 100% aos 3 idiomas (Português PT-BR, Inglês EN-US e Espanhol ES) em todos os módulos. Zero strings hardcoded.

---

## 🛑 Protocolo de Decomposição Atômica & Anti-Inflação de Tokens
* **Decomposição Obrigatória (1 Tarefa = 1 Componente/Arquivo):** O Maestro (seja Gemini, Qwen 3.8 Max ou GLM) é **terminantemente proibido de delegar tarefas monolíticas** (ex: *"faça 5 abas, todos os componentes e 200 testes de uma vez"*). Tarefas gigantescas forçam o OpenCode a entrar em loops de 50+ tool-calls e esgotam a cota do MiniMax em minutos.
* **Micropassos Atômicos:** Toda meta DEVE ser decomposta em micropassos sequenciais (Passo 1: Componente Header ➔ Passo 2: Aba 1 ➔ Passo 3: Aba 2).
* **Escada Ponytail de Decisão (Diff Mínimo Obrigatório):** Antes de escrever código novo, o agente é obrigado a subir a escada: `1. Deletar (YAGNI)` ➔ `2. Reaproveitar utilitário/tipo já existente` ➔ `3. Usar stdlib/plataforma nativa` ➔ `4. Usar dependência já instalada` ➔ `5. Uma linha antes de cinquenta` ➔ `6. Mínimo código funcional`. Simplificar implementação **NÃO** sobrepõe decreto do GLM-5.3.
* **Graphify (Grafo = Mapa, Não Território):** Em repositórios densos (ex: `dm-erp`), o agente consulta o grafo de conhecimento AST (`/graphify .`) para evitar leituras de dezenas de arquivos inteiros. Regenerar no início de sprint; auditorias e gates de segurança do GLM-5.3 **SEMPRE** leem o código real.
* **Higiene de Contexto (`/compact` & `/clear`):** Entre tarefas, executar `/clear` ou `/compact` para manter a conversa enxuta (~5k tokens) e evitar degradação de raciocínio.

---

## 🎨 Prioridade 1: Design Profissional Anti-Vibecode & Inteligência Frontend
* **Papel de Frontend:** Conduzido pelo Implementation Engineer alocado, guiado pelo `DESIGN.md` do projeto e pela `frontend-toolbox`.
* **Anti-AI Aesthetic:** Proibição de clichês automáticos (gradiente roxo/azul genérico, glassmorphism em tudo, cards flutuantes idênticos, bento grids sem função). Foco em hierarquia tipográfica forte, densidade adequada ao caso de uso, ritmo visual orgânico e acessibilidade WCAG.
* **Componentes Reutilizáveis:** Não reinventar primitivas complexas (tabelas densas, combobox, date pickers) quando bibliotecas maduras e acessíveis estiverem disponíveis na Toolbox. A biblioteca fornece capacidade; a identidade visual vem do `DESIGN.md`.

---

## 🌐 APIs Públicas Homologadas (Padrão Corporativo Dev Maniac's)
Antes de construir scrapers ou cadastros manuais, os agentes de backend **DEVEM** usar as APIs públicas homologadas:
1. 📍 **ViaCEP / BrasilAPI:** Autocompletar CEP, endereços, códigos de compensação bancária e feriados nacionais (cálculo de dias úteis de obra).
2. 🏢 **BrasilAPI CNPJ / ReceitaWS:** Validação e autopreenchimento de cadastros de clientes, parceiros e fornecedores via CNPJ.
3. 🌦️ **Open-Meteo:** Previsão horária meteorológica e índice pluviométrico (crítico para aplicação de dedetização externa na Biolar e concretagem no CanteiroHUB).
4. 💵 **AwesomeAPI Câmbio & SELIC/CDI:** Cotação de moedas em tempo real e taxas econômicas oficiais para cálculos financeiros e reajustes contratuais no dm-erp.

---

## 🖥️ Topologia de Infraestrutura Real
- **Servidor Dedicado (Rocky Linux 10.2 Red Quartz):**
  - **Acesso Tailscale (Global/MagicDNS):** `100.127.233.62` / `devmaniacs-prod` (SSH direto: `ssh root@100.127.233.62` ou `ssh devmaniacs-prod`)
  - **Acesso LAN (Local):** `192.168.226.103` (SSH direto: `ssh root@192.168.226.103`)
- **Hardware:** 1 TB NVMe SSD (12% uso), 32 GB RAM (29% uso), 16 vCPUs Dedicated Intel Xeon Silver.
- **Túnel Cloudflare:** `tunnel a0c5bea6-1a4b-4ffe-a041-da8cb18f419a` gerenciando domínios corporativos seguros HTTPS com SSL automático.

---

## 📦 Ecossistema de Produtos Ativos da Dev Maniac's
1. **CanteiroHUB / DM-ERP:** SaaS de gestão de obras e engenharia (instância piloto Teenus Gestão).
2. **Biolar Dedetizadora:** ERP operacional e financeiro de dedetização (`/opt/sistemas/biolar`).
3. **HelpDev:** Central de suporte técnico e chamados (`/opt/sistemas/helpdev`).
4. **DM-PDV:** Sistema de ponto de venda comercial rápido (`/opt/sistemas/dm-pdv`).
5. **Nextcloud Teenus & APAE:** Armazenamento seguro e suíte de escritório Collabora.
