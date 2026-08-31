"""
Cerberus Memory Intelligence - Standard MCP Server (stdio JSON-RPC 2.0)
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from engine.retrieval import CerberusMemoryService
from engine.index import SQLiteMemoryIndex, validate_root


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
        return [
            {
                "name": "cerberus_search_memory",
                "description": "Busca híbrida lexical/semântica no Segundo Cérebro da Dev Maniac's (ADRs, governança, decisões, wiki, arquitetura).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Termo de busca ou dúvida (ex: 'SEFAZ A1 cofre', 'BDI TCU 2622', 'WCAG login')"},
                        "project_id": {"type": "string", "description": "Slug do projeto (ex: 'canteirohub', 'biolar', 'helpdev', '_global')"},
                        "limit": {"type": "integer", "description": "Número máximo de resultados (padrão 5)", "default": 5}
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
                        "role": {"type": "string", "description": "Papel do agente (ex: 'DEVELOPER', 'QA', 'CTO', 'STAFF')", "default": "DEVELOPER"}
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
                        "limit": {"type": "integer", "description": "Limite de resultados", "default": 5}
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

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "cerberus_search_memory":
            results = self.service.search(
                query=args.get("query", ""),
                project_id=args.get("project_id"),
                limit=args.get("limit", 5)
            )
            return [r.to_dict() for r in results]

        elif name == "cerberus_get_context_pack":
            pack = self.service.build_context_pack(
                project_id=args.get("project_id", "canteirohub"),
                task_summary=args.get("task_summary", ""),
                role=args.get("role", "DEVELOPER")
            )
            return {
                "markdown": pack.to_markdown(),
                "token_estimate": pack.token_estimate
            }

        elif name == "cerberus_get_decisions":
            results = self.service.get_decisions(
                project_id=args.get("project_id"),
                limit=args.get("limit", 5)
            )
            return [r.to_dict() for r in results]

        elif name == "cerberus_get_learnings":
            results = self.service.get_learnings(
                topic=args.get("topic"),
                project_id=args.get("project_id")
            )
            return [r.to_dict() for r in results]

        elif name == "cerberus_get_project_context":
            return self.service.get_project_context(args.get("project_id", ""))

        elif name == "cerberus_get_stats":
            return self.service.index.get_stats()

        elif name == "cerberus_capture_learning":
            from engine.capture import AutoCaptureEngine
            engine = AutoCaptureEngine(service=self.service, cerebro_root=self.cerebro_root)
            return engine.capture_learning(
                title=args.get("title", ""),
                content=args.get("content", ""),
                project_id=args.get("project_id"),
                task_id=args.get("task_id"),
                agent_role=args.get("agent_role", "MCP_AGENT")
            )

        elif name == "cerberus_ingest_report":
            from engine.capture import AutoCaptureEngine
            engine = AutoCaptureEngine(service=self.service, cerebro_root=self.cerebro_root)
            return engine.ingest_report(
                report_path_or_content=args.get("report_content", ""),
                task_id=args.get("task_id"),
                project_id=args.get("project_id", "canteirohub"),
                allow_file=False,
            )

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
            if invalid:
                return {"jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32602, "message": f"Invalid arguments: {', '.join(invalid)}"}}
            try:
                result_data = self.handle_tool_call(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, indent=2, ensure_ascii=False) if not isinstance(result_data, str) else result_data
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
                        "message": str(e)
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
