# Cerberus Inspector — Web UI Dashboard (Localhost Management Plane)
> **Propriedade Intelectual:** Dev Maniac's Systems (Helbert Moura)  
> **Versão:** 1.0.0 (Phase P3) · 30 de Agosto de 2026  
> **Status:** Ativo e Operacional  
> **Complementa:** [`CERBERUS-MEMORY-ARCHITECTURE.md`](./CERBERUS-MEMORY-ARCHITECTURE.md), [`CERBERUS-MCP-INTEGRATION.md`](./CERBERUS-MCP-INTEGRATION.md), [`CERBERUS-ORCHESTRATOR-INTEGRATION.md`](./CERBERUS-ORCHESTRATOR-INTEGRATION.md)

---

## 🎯 Propósito

O **Cerberus Inspector** é um painel web single-page hospedado num HTTP server puramente local. Ele oferece:

- **Inspeção humana** do cérebro corporativo (status, projetos, inbox).
- **Operação assistida** da inbox de candidatos: search, view diff, promote, reject.
- **Onboarding rápido** para novos operadores sem precisar aprender a CLI.

**Não é** um servidor de produção — é uma **management plane local**. Todo o design é fail-closed em torno da premissa "só roda em 127.0.0.1".

---

## 🔒 1. Limites de Segurança (fail-closed)

| Garantia | Como é enforced |
|---|---|
| Bind **loopback-only** por padrão | `make_server()` rejeita host ≠ `127.0.0.1 / localhost / ::1` com `ValueError`. |
| LAN-bind só com opt-in explícito | `CERBERUS_UI_ALLOW_LAN=1` no ambiente (operador responsável). |
| Sem leitura de arquivo arbitrário | `on_report_accepted` é puramente content-only (vide FIX-006). Inspector **não** expõe endpoint de leitura de FS. |
| Sem promoção fora do allowlist | `/api/inbox/<id>/promote` chama `AutoCaptureEngine.promote(apply=True)`, que só escreve em `LEARNINGS.md` / `DECISIONS.md`. |
| Quarantined nunca promove | Server retorna `409 Conflict` se status ≠ `VERIFIED`. |
| Fingerprint é revalidado em promote | Herdado de `engine/capture.py:promote` — `Candidate fingerprint mismatch` aborta. |
| Stdout limpo | Server log via `log_message` no-op por padrão (configurável). |

---

## 🚀 2. Como subir

### 2.1 CLI

```powershell
# Default: 127.0.0.1:7331
cerberus ui

# Custom port + host (loopback only)
cerberus ui --host 127.0.0.1 --port 8080

# Don't open the browser
cerberus ui --no-browser

# Aliases
cerberus serve --port 7331
```

### 2.2 Programático (Python)

```python
from pathlib import Path
from engine.server import make_server

server = make_server(host="127.0.0.1", port=7331,
                     application_root=Path("C:/DevManiacs/DM-Cerebro"))
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.shutdown()
    server.server_close()
```

### 2.3 Auto-open do browser

Se `CERBERUS_UI_OPEN_BROWSER=1` (ou `--open-browser`) for setado, o server chama `webbrowser.open(url)` no launch.

---

## 🌐 3. Endpoints REST

Todos os endpoints retornam `application/json; charset=utf-8` (exceto `GET /` que retorna HTML).

### 3.1 `GET /`

UI single-page (HTML + JS inline). Sem dependências externas — funciona offline.

### 3.2 `GET /api/status`

```json
{
  "bind_host": "127.0.0.1",
  "bind_port": 7331,
  "canonical_root": "C:\\DevManiacs\\DM-Cerebro",
  "files": 142,
  "documents": 487,
  "inbox_count": 3,
  "fts5": true,
  "projects": ["_global", "_shared", "canteirohub", "biolar", "helpdev", "..."],
  "types_breakdown": {"learning": 280, "canonical_adr": 95, "...": 0},
  "indexed_projects": ["_global", "canteirohub", "biolar"]
}
```

| Campo | Origem |
|---|---|
| `bind_host` / `bind_port` | Argumentos do `make_server()` |
| `canonical_root` | `application_root` resolvido |
| `files` / `documents` | `SQLiteMemoryIndex.get_stats()` |
| `inbox_count` | `glob("*.json")` em `.cerberus/inbox/` |
| `fts5` | Probe live em `_sqlite_fts5_available()` |
| `projects` | `PROJECT_ALIASES.values()` ∪ `discover_dynamic_projects()` |
| `indexed_projects` | `get_stats()['indexed_projects']` |
| `types_breakdown` | `get_stats()['types_breakdown']` |

### 3.3 `GET /api/inbox[?status=...]`

Lista todos os candidatos do `.cerberus/inbox/`, ordenados por `created_at` desc.

```json
{
  "count": 2,
  "candidates": [
    {
      "candidate_id": "c8e94607aaf405b8",
      "project_id": "canteirohub",
      "type": "learning",
      "title": "Cofre SEFAZ A1",
      "content": "...",
      "source": "manual_capture",
      "source_path": null,
      "task_id": "TASK-042",
      "agent": "CODEX",
      "created_at": "2026-08-30T22:30:00+00:00",
      "confidence": 0.5,
      "authority_hint": "AGENT_OBSERVATION",
      "fingerprint": "abcd...",
      "status": "CANDIDATE",
      "secret_findings": [],
      "canonical_path": null
    }
  ]
}
```

Query `?status=CANDIDATE|VERIFIED|QUARANTINED|CANONICAL|REJECTED` filtra server-side.

### 3.4 `GET /api/inbox/<id>`

Detalhe de um candidato + diff preview (se status = `VERIFIED`).

```json
{
  "candidate_id": "c8e94607aaf405b8",
  "status": "VERIFIED",
  "...": "...",
  "diff": "--- LEARNINGS.md\n+++ LEARNINGS.md\n@@ -1 +1,9 @@
-# Learnings
+\n### Cofre SEFAZ A1
+> **Proveniência:** Task `TASK-042` · Agente `CODEX` · ...",
  "target_file": "C:\\DevManiacs\\DM-Cerebro\\LEARNINGS.md"
}
```

Quando status ≠ `VERIFIED` ou a promotion está bloqueada (fingerprint mismatch, secrets), o diff fica vazio e o campo opcional `diff_error` carrega a mensagem.

### 3.5 `POST /api/inbox/<id>/verify`

Promove `CANDIDATE` → `VERIFIED` via `AutoCaptureEngine.verify()`.

### 3.6 `POST /api/inbox/<id>/promote`

Aplica a promoção no canônico via `AutoCaptureEngine.promote(apply=True)`. Requer status `VERIFIED` — senão retorna `409 Conflict` com a mensagem do engine.

### 3.7 `POST /api/inbox/<id>/reject`

Marca como `REJECTED` via `AutoCaptureEngine.reject()`. Bloqueado se já é `CANONICAL`.

### 3.8 `GET /api/search?q=<query>[&project=<slug>]`

Wrapper FTS5 via `CerberusMemoryService.search()`. Query `q` é obrigatória; `project` é filtro opcional.

```json
{
  "query": "SEFAZ",
  "project_id": "canteirohub",
  "count": 2,
  "results": [
    {
      "memory_id": "...",
      "project_id": "canteirohub",
      "title": "...",
      "authority_level": 70,
      "tags": [...],
      "snippet": "...",
      "final_score": 17.0
    }
  ]
}
```

### 3.9 Códigos de status HTTP

| Status | Quando |
|---|---|
| `200 OK` | Sucesso |
| `400 Bad Request` | Query sem `q`, JSON malformado |
| `404 Not Found` | Rota inexistente ou candidate_id inválido |
| `409 Conflict` | Tentativa de promote inválida (status errado, fingerprint mismatch, secrets) |
| `501 Not Implemented` | Método HTTP não suportado (ex: `DELETE /api/status`) |

---

## 🎨 4. UI — Design Industrial

Tema visual: **Dev Maniac's Industrial**.

- **Background**: `#0F172A` (slate-900 / dark navy)
- **Card surface**: `#111827` (gray-900)
- **Accent**: `#1E40AF` (steel blue)
- **Borders**: `#334155` (slate-700)
- **Text**: `#E2E8F0` (slate-200)
- **Typography**: IBM Plex Sans + IBM Plex Mono (system fallback chain)

### 4.1 Acessibilidade (WCAG 2.2 AA)

- **Touch targets ≥ 44px** em todos os botões e inputs (`.toolbar button { min-height: 44px; }`).
- **Foco visível**: `:focus-visible { outline: 2px solid #fff; }`.
- **Contraste**: texto principal 12.9:1, texto muted 7.1:1 — ambos acima de 4.5:1.
- **Navegação por teclado**: Tab order respeitado em todos os controles.
- **Labels semânticos**: `aria-label` em inputs, `<h1>/<h3>` para hierarquia, `<table><thead>/<tbody>` para grids.
- **Modal acessível**: `role="dialog"`, `aria-modal="true"`, foco preso.

### 4.2 Sem emojis no UI

O Inspector **não usa emojis** na UI. Comunicação é puramente textual (status tags + mensagens). Isso garante:
- Renderização consistente cross-platform.
- Sem dependência de fontes de emoji.
- Conformidade com a regra permanente do Maestro: "sem emojis no UI".

### 4.3 Layout

```
┌─────────────────────────────────────────────────────────────┐
│ [LOGO] Cerberus Inspector        [localhost] [bind info]    │ header
├─────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│ │ Files    │ │ Docs     │ │ Inbox    │ │ FTS5     │         │ metrics
│ │ 142      │ │ 487      │ │ 3        │ │ online   │         │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
├─────────────────────────────────────────────────────────────┤
│ Search [_______________] [Project v] [Search]              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ results table                                            ││
│ └──────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│ Candidate inbox [Status v] [Refresh]                        │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ status | title | project | task | created | [Open]      ││
│ │ ...                                                     ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

Modal `Open` mostra: status tag, content, diff preview, [Promote to canonical] [Reject] [Close].

---

## 🔌 5. Embedding no Maestri Portal

O Inspector pode ser embeddado no **Maestri Portal** via iframe ou proxy HTTP reverso. Como o server já é loopback-only, o embedding deve ser feito via:

1. **Iframe local**: o Maestro serve a página do portal com `<iframe src="http://127.0.0.1:7331/">`. O navegador do operador aceita porque o iframe também está em `127.0.0.1`.
2. **Proxy reverso**: o Maestro faz `proxy_pass http://127.0.0.1:7331/` apenas para operadores autenticados (autenticação vive no portal, não no Inspector).
3. **WebSocket bridge**: (futuro, P4) — expor um canal WebSocket ao lado do HTTP para updates em tempo real do inbox.

> ⚠️ O Inspector **nunca** deve ser embeddado em um domínio público. A restrição loopback-only é a primeira linha de defesa.

---

## 🛠️ 6. Variáveis de Ambiente

| Variável | Default | Efeito |
|---|---|---|
| `CERBERUS_ROOT` | `<cwd>` | Override do canonical root (passado pelo validate_root). |
| `CERBERUS_UI_HOST` | `127.0.0.1` | Bind host do UI. Loopback-only por padrão. |
| `CERBERUS_UI_PORT` | `7331` | Bind port. |
| `CERBERUS_UI_ALLOW_LAN` | (unset) | Quando `1/true/yes`, libera bind para hosts não-loopback. **Operador-only**. |
| `CERBERUS_UI_OPEN_BROWSER` | (unset) | Quando `1`, chama `webbrowser.open()` no launch. |

---

## 🧪 7. Testes

Cobertura completa em `tests/test_server_api.py` (21 testes):

| Categoria | Cobertura |
|---|---|
| **Lifecycle** | Default bind é loopback; rejeita non-loopback; aceita LAN apenas com opt-in. |
| **Static UI** | HTML servido em `/`; contém tokens de design industrial (`#0F172A`, `#1E40AF`, 44px touch target); sem emojis. |
| **Status** | `GET /api/status` retorna métricas, projetos, FTS5 availability. |
| **Inbox list** | Lista todos; filtra por status. |
| **Inbox detail** | Diff preview para VERIFIED; 404 para unknown id. |
| **Inbox promote** | Promove VERIFIED para CANONICAL; 409 para CANDIDATE; 409 para QUARANTINED. |
| **Inbox reject** | Marca REJECTED. |
| **Inbox verify** | CANDIDATE → VERIFIED. |
| **Search** | Retorna resultados; 400 sem `q`; filtra por projeto. |
| **Security** | Bind default loopback; método não suportado retorna 501/405. |

Suíte completa: **109/109 PASS** (88 anteriores + 21 novos).

---

## 🛣️ 8. Roadmap

- **P3.5 — WebSocket events**: atualizações live do inbox.
- **P4 — Conflict resolution UI**: marcar candidato como `CONFLICT` quando contradiz ADR existente.
- **P4 — Bulk operations**: promote/reject em lote filtrado por task_id ou project_id.
- **P4 — Authentication hook**: integração com portal Maestro para SSO antes de expor endpoints.

### v1.1.0 (30/08/2026) — FIX-007

Refinamentos de precisão alinhados pelo Codex QA — fail-closed sem exceções:

- **Admin seedado de env vars**: `engine/auth.py:_resolve_admin_credentials()`
  lê `CERBERUS_ADMIN_EMAIL` e `CERBERUS_ADMIN_PASSWORD` do ambiente;
  defaults dev-only (`DEFAULT_DEV_ADMIN_EMAIL`, `DEFAULT_DEV_ADMIN_PASSWORD`).
  Senha fraca estática `Admin@123456` foi **removida**.

- **Secure cookies via proxy**: `should_use_secure_cookie()` retorna `True`
  quando `CERBERUS_SECURE_COOKIES=1` **ou** quando o request passa por
  Cloudflare (`X-Forwarded-Proto: https`, `CF-Visitor` JSON com
  `"scheme":"https"`, `X-Forwarded-Ssl: on`). `AuthState.build_session_cookie`
  consulta essa função e injeta o atributo `Secure` quando apropriado.

- **Trust proxy para IP do cliente**: `resolve_client_ip()` usa o peer
  do socket por padrão; só consulta `CF-Connecting-IP` / `X-Forwarded-For`
  quando `CERBERUS_TRUST_PROXY=1`. Previne header-spoofing em deploy
  exposto.

- **Standard `base64.b32encode`/`b32decode`**: helpers customizados
  removidos em favor do stdlib (`engine/auth.py:_b32encode`/`_b32decode`)
  — handles arbitrary byte lengths e padding corretamente.

- **TOTP retry grace**: `AuthState.PENDING_MAX_ATTEMPTS = 3`. Step 2
  do login não destrói o `pending_token` na primeira falha — aguarda
  até 3 tentativas dentro da janela de 5min; após o limite, invalida
  o token e força o usuário a voltar ao step 1.

- **verify_password fail-closed**: nunca levanta exceção; qualquer
  input malformado (None, não-string, digest corrompido, base64
  inválido, header de algoritmo errado) retorna `False`. Cobre casos
  de borda incluindo `(AttributeError, KeyError)`.

- **Cloudflare Named Tunnel**: `docker-compose.yml` ganhou
  `cloudflared` (default profile) que roda `tunnel --no-autoupdate run`
  consumindo `CLOUDFLARE_TUNNEL_TOKEN` do ambiente. Profile
  `quick-tunnel` mantido para demos. `.env.example` documenta
  `CLOUDFLARE_TUNNEL_TOKEN`, `CERBERUS_TRUST_PROXY`,
  `CERBERUS_SECURE_COOKIES`.

---

NO IMPLEMENTATION beyond TASK scope  
NO COMMIT  
NO PUSH
