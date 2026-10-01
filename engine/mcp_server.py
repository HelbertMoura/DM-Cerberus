"""
Cerberus Memory Intelligence - Standard MCP Server (stdio JSON-RPC 2.0)
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import sys
import json
import os
import hashlib
from dataclasses import replace
from pathlib import Path
from typing import Dict, Any, List, Optional
from engine.retrieval import CerberusMemoryService
from engine.index import SQLiteMemoryIndex, validate_root
from engine.context_budget import context_pack_result, GROUPS
from engine.models import MemoryStatus
from engine.response_budget import bounded_response, json_text, query_text, search_text, redact_text, validate_max_chars, DEFAULT_MAX_CHARS

MEMORY_TOOLS = {"cerberus_search_memory", "cerberus_get_context_pack", "cerberus_get_decisions",
                "cerberus_get_learnings", "cerberus_get_project_context", "cerberus_get_stats",
                "cerberus_get_memory"}


class CerberusMCPServer:
    def __init__(self, service: Optional[CerberusMemoryService] = None):
        application_root = Path(__file__).resolve().parent.parent
        configured_value = Path(os.environ.get("CERBERUS_ROOT", application_root))
        allowed_value = os.environ.get("CERBERUS_ALLOWED_ROOTS")
        allowed_roots = (
            [Path(value) for value in allowed_value.split(os.pathsep) if value]
            if allowed_value else [application_root]
        )
        configured_root = validate_root(configured_value, allowed_roots)
        self.cerebro_root = configured_root
        self.service = service or CerberusMemoryService(SQLiteMemoryIndex(configured_root / ".cerberus" / "index.db"))
        self.root_paths = [configured_root]
        if "CERBERUS_ROOT" not in os.environ:
            self.root_paths.append(Path("C:/DevManiacs/migra/dm-erp/docs"))

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        tools = [
            {
                "name": "cerberus_search_memory",
                "description": "Busca híbrida lexical/semântica no Segundo Cérebro da Dev Maniac's (ADRs, governança, decisões, wiki, arquitetura).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Termo de busca ou dúvida (ex: 'SEFAZ A1 cofre', 'BDI TCU 2622', 'WCAG login')"},
                        "project_id": {"type": "string", "description": "Slug do projeto (ex: 'canteirohub', 'biolar', 'helpdev', '_global')"},
                        "mode": {
                            "type": "string",
                            "enum": ["hybrid", "lexical", "semantic"],
                            "description": "Estratégia de recuperação (padrão hybrid)",
                            "default": "hybrid"
                        },
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20,
                            "description": "Número máximo de previews, de 1 a 20 (padrão 2)", "default": 2}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "cerberus_get_context_pack",
                "description": "Gera um Context Pack compacto e orquestrado sob medida para uma tarefa específica e papel de agente.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Slug do projeto (ex: 'canteirohub', 'biolar')"},
                        "task_summary": {"type": "string", "description": "Descrição curta da tarefa a ser executada"},
                        "role": {"type": "string", "description": "Papel do agente (ex: 'DEVELOPER', 'QA', 'CTO', 'STAFF')", "default": "DEVELOPER"},
                        "max_tokens": {"type": "integer", "minimum": 256, "maximum": 1500,
                            "description": "Orçamento estimado: teto real de 4 caracteres por unidade, incluindo JSON e fontes; não é contagem exata de tokens.",
                            "default": 1500}
                    },
                    "required": ["project_id", "task_summary"]
                }
            },
            {
                "name": "cerberus_get_decisions",
                "description": "Recupera os registros formais de decisão arquitetural (ADRs) vigentes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Slug do projeto (opcional)"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20,
                            "description": "Limite de previews, de 1 a 20 (padrão 2)", "default": 2}
                    }
                }
            },
            {
                "name": "cerberus_get_learnings",
                "description": "Recupera lições aprendidas, gotchas e diretrizes corporativas (Godot, React, Django, Maestri).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Tópico específico (ex: 'godot', 'django', 'turnkey', 'telegram')"},
                        "project_id": {"type": "string", "description": "Slug do projeto (opcional)"}
                    }
                }
            },
            {
                "name": "cerberus_get_project_context",
                "description": "Recupera a visão geral, estado e módulos de um projeto específico.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Slug do projeto (ex: 'canteirohub', 'biolar', 'helpdev', 'dmpdv', 'apae-juatuba')"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "cerberus_get_stats",
                "description": "Retorna métricas do Segundo Cérebro (total de documentos, projetos indexados, breakdown de tipos).",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "cerberus_capture_learning",
                "description": "Captura com segurança uma nova lição aprendida, gotcha ou diretriz técnica no cérebro corporativo com deduplicação automática.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Título curto da lição aprendida"},
                        "content": {"type": "string", "description": "Explicação técnica detalhada, gotcha ou solução"},
                        "project_id": {"type": "string", "description": "Slug do projeto (opcional, default _global)"},
                        "task_id": {"type": "string", "description": "ID obrigatório da tarefa de origem"},
                        "agent_role": {"type": "string", "description": "Papel do agente registrador (ex: CODEX, MINIMAX, GEMINI)"}
                    },
                    "required": ["title", "content", "task_id", "agent_role"]
                }
            },
            {
                "name": "cerberus_ingest_report",
                "description": "Analisa o relatório final de uma tarefa e extrai automaticamente aprendizados e gotchas para o cérebro.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "report_content": {"type": "string", "description": "Texto completo do relatório; caminhos locais não são lidos pelo MCP"},
                        "task_id": {"type": "string", "description": "ID da tarefa (opcional)"},
                        "project_id": {"type": "string", "description": "Slug do projeto (default canteirohub)"}
                    },
                    "required": ["report_content"]
                }
            }
        ]
        tools.extend([
            {"name": "cerberus_get_memory", "description": "Expande texto indexado ativo por ID e offset; páginas são limitadas e segredos são redigidos antes da paginação.",
             "inputSchema": {"type": "object", "properties": {
                 "memory_id": {"type": "string"}, "offset": {"type": "integer", "minimum": 0, "default": 0}},
                 "required": ["memory_id"]}},
            {"name": "cerberus_save_task_state", "description": "Salva uma retomada operacional curta ao encerrar a tarefa, com objetivo, decisões e próximo passo.",
             "inputSchema": {"type": "object", "properties": {
                 "project_id": {"type": "string"}, "task_id": {"type": "string"}, "objective": {"type": "string"},
                 "decisions": {"type": "array", "items": {"type": "string"}},
                 "files": {"type": "array", "items": {"type": "string"}},
                 "validation": {"type": "array", "items": {"type": "string"}},
                 "next_step": {"type": "string"},
                 "status": {"type": "string", "enum": ["in_progress", "paused", "done"]}},
                 "required": ["project_id", "task_id", "objective"]}},
            {"name": "cerberus_get_task_state", "description": "Lê a retomada operacional curta de um projeto e tarefa.",
             "inputSchema": {"type": "object", "properties": {
                 "project_id": {"type": "string"}, "task_id": {"type": "string"}},
                 "required": ["project_id", "task_id"]}},
            {"name": "cerberus_context_status", "description": "Consulta a cota de memória da conversa. Use reset_reason somente após compactação (compact) ou limpeza explícita (clear).",
             "inputSchema": {"type": "object", "properties": {
                 "session_id": {"type": "string"}, "reset_reason": {"type": "string", "enum": ["compact", "clear"]}},
                 "required": ["session_id"]}},
        ])
        for tool in tools:
            properties = tool["inputSchema"]["properties"]
            if tool["name"] in MEMORY_TOOLS:
                properties["session_id"] = {"type": "string", "description": "ID da conversa ou token público cbr; omitir para leitura sem estado."}
            if tool["name"] in MEMORY_TOOLS | {"cerberus_get_task_state"}:
                properties["max_chars"] = {"type": "integer", "minimum": 512, "maximum": 6000,
                    "default": DEFAULT_MAX_CHARS, "description": "Teto do texto JSON entregue; expansão explícita até 6.000 caracteres."}
            if tool["name"] in {"cerberus_get_learnings", "cerberus_get_project_context"}:
                properties["limit"] = {"type": "integer", "minimum": 1, "maximum": 20, "default": 2}
        return tools

    @staticmethod
    def _version(value) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def _deliver_memory(self, name, args):
        from engine.session_delivery import delivery_transaction
        cap = validate_max_chars(args.get("max_chars", DEFAULT_MAX_CHARS))
        session_id = args.get("session_id")
        if session_id is None:
            return self._memory_payload(name, args, set(), cap, False)[0]
        with delivery_transaction(self.cerebro_root, session_id) as transaction:
            if transaction.remaining < 512:
                return None
            result, keys = self._memory_payload(name, args, transaction.seen,
                                                min(cap, transaction.remaining), True)
            if not keys:
                return None
            # Persistence completes under the shared lock before stdout can expose memory.
            transaction.commit(len(json_text(result)), keys)
            return result

    def _memory_payload(self, name, args, seen, cap, session):
        from engine.session_delivery import memory_fingerprint
        if name == "cerberus_get_memory":
            return self._memory_page(args, seen, cap)
        if name == "cerberus_get_context_pack":
            pack = self.service.build_context_pack(
                project_id=query_text(args.get("project_id", "canteirohub")),
                task_summary=search_text(args.get("task_summary", "")),
                role=query_text(args.get("role", "DEVELOPER")),
                max_tokens=args.get("max_tokens", 1500))
            keys = set()
            groups = {}
            limit = 2 if "max_chars" not in args else 20
            for group in GROUPS:
                groups[group] = []
                for item in getattr(pack, group):
                    key = memory_fingerprint(item)
                    if key in seen or key in keys or len(keys) >= limit:
                        continue
                    safe = bounded_response(item.to_dict(), 6000)
                    if "source_path" not in safe:
                        pack.truncated = True
                        continue
                    keys.add(key)
                    groups[group].append(replace(item, title=safe.get("title", ""),
                        snippet=safe.get("snippet", ""), source_path=safe["source_path"]))
            if len(keys) < sum(len(getattr(pack, group)) for group in GROUPS):
                pack = replace(pack, truncated=True)
            pack = replace(pack, **groups)
            while len(json_text(context_pack_result(pack))) > cap:
                selected = next((getattr(pack, group) for group in reversed(GROUPS)
                                 if getattr(pack, group)), None)
                pack.truncated = True
                if selected is None:
                    pack.task_summary = ""
                    pack.project_id, pack.role = "projeto", "agente"
                    if len(json_text(context_pack_result(pack))) > cap:
                        result = {"markdown": "", "token_estimate": 0,
                                  "budget_chars": pack.budget_chars, "truncated": True}
                        result["token_estimate"] = (len(json_text(result)) + 3) // 4
                        return result, set()
                else:
                    selected.pop()
            result = context_pack_result(pack)
            keys = {memory_fingerprint(item) for group in GROUPS for item in getattr(pack, group)}
            return result, keys
        if name == "cerberus_get_stats":
            data = self.service.index.get_stats()
            key = self._version(data)
            if key in seen:
                return None, set()
            result = bounded_response(data, cap)
            return result, {key} if result != {"truncated": True} else set()

        limit = args.get("limit", 2)
        project = args.get("project_id")
        project = query_text(project) if project is not None else None
        retrieval_limit = 20 if session else limit
        if name == "cerberus_search_memory":
            results = self.service.search(query=search_text(args.get("query", "")), project_id=project,
                limit=retrieval_limit, mode=args.get("mode", "hybrid"))
        elif name == "cerberus_get_decisions":
            results = self.service.get_decisions(project_id=project, limit=retrieval_limit)
        elif name == "cerberus_get_learnings":
            topic = args.get("topic")
            results = self.service.get_learnings(topic=search_text(topic) if topic is not None else None,
                project_id=project, limit=retrieval_limit)
        else:
            data = self.service.get_project_context(project or "")
            records = data["items"]
            originals = {item.memory_id: item for item in self.service.index.get_items_by_ids(
                [record["memory_id"] for record in records])}
            return self._fit_previews(records, originals, seen, limit, cap,
                                      envelope={"project_id": data["project_id"]})
        return self._fit_previews([row.to_dict() for row in results],
                                 {row.item.memory_id: row.item for row in results}, seen, limit, cap)

    def _fit_previews(self, records, originals, seen, limit, cap, envelope=None):
        from engine.session_delivery import memory_fingerprint
        version_by_id = {identity: memory_fingerprint(item) for identity, item in originals.items()}
        candidates = [record for record in records if version_by_id.get(record["memory_id"]) not in seen]
        selected = candidates[:limit]
        payload = selected if envelope is None else dict(envelope, items=selected)
        result = bounded_response(payload, cap)
        delivered = result if envelope is None else result.get("items", [])
        keys = {version_by_id[record["memory_id"]] for record in delivered if "memory_id" in record}
        if len(candidates) > len(selected):
            # Refit after adding the signal so its JSON is included in the cap.
            if isinstance(result, list):
                if not result or result[-1] != {"truncated": True}:
                    result.append({"truncated": True})
            else:
                result["truncated"] = True
            result = bounded_response(result, cap)
            delivered = result if envelope is None else result.get("items", [])
            keys = {version_by_id[record["memory_id"]] for record in delivered if "memory_id" in record}
        return result, keys

    def _memory_page(self, args, seen, cap):
        from engine.session_delivery import memory_fingerprint
        identity, offset = args["memory_id"], args.get("offset", 0)
        if not isinstance(identity, str) or len(identity) > 512 or type(offset) is not int or offset < 0:
            raise ValueError("Invalid indexed memory ID or offset")
        items = self.service.index.get_items_by_ids([identity])
        if not items or items[0].status != MemoryStatus.ACTIVE:
            raise ValueError("Active indexed memory not found")
        item = items[0]
        key = hashlib.sha256(f"{memory_fingerprint(item)}:detail:{offset}:{args.get('max_chars', DEFAULT_MAX_CHARS)}".encode()).hexdigest()
        if key in seen:
            return None, set()
        text = redact_text(item.full_text)
        if offset > len(text):
            raise ValueError("Offset exceeds indexed memory text")
        title = redact_text(item.title)[:160]
        source = redact_text(item.source_path)

        def page(size):
            end = offset + size
            return {"memory_id": item.memory_id, "source_path": source, "title": title,
                    "full_text": text[offset:end], "offset": offset,
                    "next_offset": end if end < len(text) else None, "truncated": end < len(text)}

        low, high = 0, min(len(text) - offset, cap)
        if len(json_text(page(0))) > cap:
            return {"truncated": True}, set()
        while low < high:
            midpoint = (low + high + 1) // 2
            if len(json_text(page(midpoint))) <= cap:
                low = midpoint
            else:
                high = midpoint - 1
        if not low and offset < len(text):
            return {"truncated": True}, set()
        return page(low), {key}

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Any:
        if name in MEMORY_TOOLS:
            return self._deliver_memory(name, args)
        elif name == "cerberus_context_status":
            from engine.session_delivery import context_status
            return context_status(self.cerebro_root, args["session_id"], reset=bool(args.get("reset_reason")))
        elif name in {"cerberus_save_task_state", "cerberus_get_task_state"}:
            from engine.task_state import TaskStateStore
            store = TaskStateStore(self.cerebro_root)
            if name == "cerberus_save_task_state":
                return store.save(**args)
            result = store.get(args["project_id"], args["task_id"])
            return bounded_response(result, args.get("max_chars", DEFAULT_MAX_CHARS), preview=False)
        elif name == "cerberus_capture_learning":
            from engine.capture import AutoCaptureEngine
            engine = AutoCaptureEngine(service=self.service, cerebro_root=self.cerebro_root)
            return bounded_response(engine.capture_learning(
                title=args.get("title", ""),
                content=args.get("content", ""),
                project_id=args.get("project_id"),
                task_id=args.get("task_id"),
                agent_role=args.get("agent_role", "MCP_AGENT")
            ), preview=False)

        elif name == "cerberus_ingest_report":
            from engine.capture import AutoCaptureEngine
            engine = AutoCaptureEngine(service=self.service, cerebro_root=self.cerebro_root)
            return bounded_response(engine.ingest_report(
                report_path_or_content=args.get("report_content", ""),
                task_id=args.get("task_id"),
                project_id=args.get("project_id", "canteirohub"),
                allow_file=False,
            ), preview=False)

        else:
            raise ValueError(f"Unknown tool: {name}")

    def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(message, dict):
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}
        msg_id = message.get("id")
        if message.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32600, "message": "Invalid Request"}}
        method = message.get("method")
        params = message.get("params", {})
        if not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": "Invalid params"}}

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "cerberus-memory-engine",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.get_tool_definitions()
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if not isinstance(tool_args, dict):
                return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": "Invalid tool arguments"}}
            known_tools = {tool["name"] for tool in self.get_tool_definitions()}
            if tool_name not in known_tools:
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                }
            definition = next(tool for tool in self.get_tool_definitions() if tool["name"] == tool_name)
            missing = [key for key in definition["inputSchema"].get("required", []) if key not in tool_args]
            if missing:
                return {"jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32602, "message": f"Missing required arguments: {', '.join(missing)}"}}
            python_types = {"string": str, "integer": int, "object": dict, "array": list, "boolean": bool}
            invalid = []
            for key, value in tool_args.items():
                schema = definition["inputSchema"].get("properties", {}).get(key)
                if not schema:
                    invalid.append(key)
                    continue
                expected = python_types.get(schema.get("type"))
                if expected is not None and (not isinstance(value, expected) or
                                              (expected is int and isinstance(value, bool))):
                    invalid.append(key)
                elif "enum" in schema and value not in schema["enum"]:
                    invalid.append(key)
                elif expected is int and (value < schema.get("minimum", value) or
                                          value > schema.get("maximum", value)):
                    invalid.append(key)
            if invalid:
                return {"jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32602, "message": f"Invalid arguments: {', '.join(invalid)}"}}
            try:
                result_data = self.handle_tool_call(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [] if result_data is None else [
                            {
                                "type": "text",
                                "text": json_text(result_data) if not isinstance(result_data, str) else result_data
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32603,
                        "message": redact_text(str(e))[:240]
                    }
                }

        else:
            if msg_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }
            return None

    def run_stdio(self):
        """
        Runs the MCP server loop over standard input and output.
        """
        # MCP JSON-RPC is UTF-8, including unescaped arguments on native Windows.
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
        valid_roots = [p for p in self.root_paths if p.exists()]
        self.service.index.index_roots(valid_roots)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_message(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = CerberusMCPServer()
    server.run_stdio()
