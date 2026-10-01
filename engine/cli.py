"""
Cerberus Memory Intelligence - Command Line Interface (CLI)
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import sys
import argparse
import json
import os
import sqlite3
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from engine.index import SQLiteMemoryIndex, validate_root
from engine.retrieval import CerberusMemoryService
from engine.mcp_server import CerberusMCPServer


def get_default_roots():
    application_root = Path(__file__).resolve().parent.parent
    known_project_root = Path("C:/DevManiacs/migra/dm-erp/docs")
    configured = os.environ.get("CERBERUS_ROOT")
    if configured:
        allowed_value = os.environ.get("CERBERUS_ALLOWED_ROOTS")
        allowed_roots = (
            [Path(value) for value in allowed_value.split(os.pathsep) if value]
            if allowed_value else [application_root]
        )
        return [validate_root(Path(configured), allowed_roots)]
    return [
        application_root,  # C:\DevManiacs\DM-Cerebro
        known_project_root,
    ]


def main():
    parser = argparse.ArgumentParser(description="🧠 Cerberus Memory Intelligence Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Command: index
    p_index = subparsers.add_parser("index", help="Indexar repositórios de memória Markdown")
    p_index.add_argument("--rebuild", action="store_true", help="Reconstruir índice do zero")

    # Command: search
    p_search = subparsers.add_parser("search", help="Buscar no cérebro")
    p_search.add_argument("query", type=str, help="Termo de busca")
    p_search.add_argument("--project", type=str, default=None, help="Filtrar por projeto (ex: canteirohub, biolar)")
    p_search.add_argument("--limit", type=int, default=5, help="Limite de resultados")

    # Command: context-pack
    p_ctx = subparsers.add_parser("context-pack", help="Gerar Context Pack para uma tarefa")
    p_ctx.add_argument("--project", type=str, required=True, help="Slug do projeto")
    p_ctx.add_argument("--task", type=str, required=True, help="Descrição/resumo da tarefa")
    p_ctx.add_argument("--role", type=str, default="DEVELOPER", help="Papel do agente (ex: DEVELOPER, QA, CTO)")

    # Command: decisions
    p_dec = subparsers.add_parser("decisions", help="Listar decisões arquiteturais (ADRs)")
    p_dec.add_argument("--project", type=str, default=None, help="Filtrar por projeto")
    p_dec.add_argument("--limit", type=int, default=5, help="Limite de resultados")

    # Command: learnings
    p_learn = subparsers.add_parser("learnings", help="Listar aprendizados e gotchas")
    p_learn.add_argument("--topic", type=str, default=None, help="Tópico específico")
    p_learn.add_argument("--project", type=str, default=None, help="Filtrar por projeto")

    # Command: capture
    p_cap = subparsers.add_parser("capture", help="Capturar uma nova lição aprendida de forma segura")
    p_cap.add_argument("--title", type=str, required=True, help="Título da lição")
    p_cap.add_argument("--content", type=str, required=True, help="Conteúdo / Gotcha")
    p_cap.add_argument("--project", type=str, default=None, help="Slug do projeto")
    p_cap.add_argument("--task", type=str, default=None, help="ID da task de origem")
    p_cap.add_argument("--agent", type=str, required=True, help="Papel/agente que originou o candidato")

    # Command: ingest-report
    p_ing = subparsers.add_parser("ingest-report", help="Ingerir relatório de task e extrair aprendizados automaticamente")
    p_ing.add_argument("report", type=str, help="Caminho do arquivo de relatório ou texto")
    p_ing.add_argument("--task", type=str, default=None, help="ID da task")
    p_ing.add_argument("--project", type=str, default="canteirohub", help="Slug do projeto")
    p_ing.add_argument("--agent", type=str, default="REPORT_INGESTER", help="Papel/agente que originou o relatório")

    subparsers.add_parser("inbox", help="Listar candidatos pendentes")
    p_review = subparsers.add_parser("review", help="Exibir candidato e preview")
    p_review.add_argument("candidate_id")
    p_review.add_argument("--verify", action="store_true", help="Marcar candidato como revisado/VERIFIED")
    p_promote = subparsers.add_parser("promote", help="Pré-visualizar ou aplicar promoção local")
    p_promote.add_argument("candidate_id")
    p_promote.add_argument("--apply", action="store_true", help="Aplicar explicitamente no Markdown canônico")
    p_reject = subparsers.add_parser("reject", help="Rejeitar candidato")
    p_reject.add_argument("candidate_id")
    subparsers.add_parser("doctor", help="Diagnosticar runtime e armazenamento sem revelar segredos")

    # Command: install-mcp
    p_inst = subparsers.add_parser("install-mcp", help="Instalar/atualizar MCP em todos os Agentes e IDEs")
    p_hooks = subparsers.add_parser("install-hooks", help="Instalar hooks de contexto/captura do Codex")
    p_hooks.add_argument("--dry-run", action="store_true", help="Mostrar o escopo sem gravar configurações")
    p_hooks.add_argument("--codex-home", type=str, default=None, help="Diretório de configuração do Codex")

    # Command: status
    p_stat = subparsers.add_parser("status", help="Métricas e status do índice")

    # Command: mcp
    p_mcp = subparsers.add_parser("mcp", help="Iniciar servidor MCP stdio")

    # Command: ui / serve (Phase P3 - Localhost Inspector)
    for cmd_name, cmd_help in (
        ("ui", "Iniciar o Inspector Web UI (loopback-only por padrão)"),
        ("serve", "Alias de 'ui' para o Inspector Web UI"),
    ):
        p_ui = subparsers.add_parser(cmd_name, help=cmd_help)
        p_ui.add_argument("--host", type=str, default=None,
                          help=f"Bind host (default: 127.0.0.1; loopback-only)")
        p_ui.add_argument("--port", type=int, default=None,
                          help="Bind port (default: 7331)")
        p_ui.add_argument("--no-browser", action="store_true",
                          help="Não abrir o browser do sistema no launch")
        p_ui.add_argument("--open-browser", action="store_true", default=False,
                          help="Abrir o browser do sistema no launch")
        p_ui.add_argument("--canonical-root", type=str, default=None,
                          help="Override CERBERUS_ROOT para esta sessão")

    # Command: session-context (Phase P2 - Orchestrator integration)
    p_sess = subparsers.add_parser(
        "session-context",
        help="Gerar Context Pack para o início de sessão de um agente"
    )
    p_sess.add_argument("--project", type=str, required=True,
                        help="Slug do projeto (ex: canteirohub, biolar, _global)")
    p_sess.add_argument("--task", type=str, required=True,
                        help="Descrição/resumo da tarefa atribuída")
    p_sess.add_argument("--role", type=str, default="DEVELOPER",
                        help="Papel do agente (DEVELOPER, QA, CTO, etc.)")

    # Command: on-report-accepted (Phase P2 - Orchestrator integration)
    p_rep = subparsers.add_parser(
        "on-report-accepted",
        help="Ingerir relatório aceito e gerar candidatos na inbox"
    )
    p_rep.add_argument("report", type=str,
                       help="Caminho do arquivo de relatório ou conteúdo inline")
    p_rep.add_argument("--task", type=str, required=True, help="ID da task")
    p_rep.add_argument("--project", type=str, required=True, help="Slug do projeto")
    p_rep.add_argument("--agent", type=str, default="REPORT_INGESTER",
                       help="Papel/agente que originou o relatório")

    # Command: on-qa-approved (Phase P2 - Orchestrator integration)
    p_qa = subparsers.add_parser(
        "on-qa-approved",
        help="Marcar candidato(s) como VERIFIED após aprovação de QA"
    )
    p_qa.add_argument("--candidate", type=str, default=None,
                      help="ID do candidato a ser verificado")
    p_qa.add_argument("--task", type=str, default=None,
                      help="ID da task (verifica todos os candidatos da task)")

    # Commands: handoff-* (claim-exactly-once delegation protocol)
    p_hcreate = subparsers.add_parser(
        "handoff-create",
        help="Criar handoff tipado para delegação (estado OPEN)"
    )
    p_hcreate.add_argument("--task", type=str, required=True, help="ID da task")
    p_hcreate.add_argument("--project", type=str, required=True, help="Slug do projeto")
    p_hcreate.add_argument("--summary", type=str, required=True, help="Resumo do que deve ser feito")
    p_hcreate.add_argument("--from-agent", type=str, required=True, help="Agente/role que delega")
    p_hcreate.add_argument("--to-role", type=str, default="", help="Role reservada (opcional; vazio = qualquer)")

    p_hclaim = subparsers.add_parser(
        "handoff-claim",
        help="Reivindicar handoff OPEN (apenas 1 agente consegue; atômico)"
    )
    p_hclaim.add_argument("handoff_id")
    p_hclaim.add_argument("--agent", type=str, required=True, help="Agente/role que reivindica")

    p_hdone = subparsers.add_parser(
        "handoff-done",
        help="Concluir handoff CLAIMED (somente o agente que reivindicou)"
    )
    p_hdone.add_argument("handoff_id")
    p_hdone.add_argument("--agent", type=str, required=True)
    p_hdone.add_argument("--result", type=str, default="", help="Resumo do resultado")

    p_hcancel = subparsers.add_parser(
        "handoff-cancel",
        help="Cancelar handoff OPEN/CLAIMED (CLAIMED: só o dono do claim)"
    )
    p_hcancel.add_argument("handoff_id")
    p_hcancel.add_argument("--agent", type=str, required=True)

    p_hlist = subparsers.add_parser("handoff-list", help="Listar handoffs (filtro opcional por status)")
    p_hlist.add_argument("--status", type=str, default=None,
                         choices=["OPEN", "CLAIMED", "DONE", "CANCELLED"])

    args = parser.parse_args()

    # Validate the MCP root before constructing SQLiteMemoryIndex; otherwise an
    # invalid environment override could create files before the server rejects it.
    if args.command == "mcp":
        server = CerberusMCPServer()
        server.run_stdio()
        return

    if args.command in {"ui", "serve"}:
        from engine.server import (
            DEFAULT_HOST, DEFAULT_PORT,
            make_server, run_from_args,
        )
        host = args.host or os.environ.get("CERBERUS_UI_HOST", DEFAULT_HOST)
        port = args.port or int(os.environ.get("CERBERUS_UI_PORT", str(DEFAULT_PORT)))
        from types import SimpleNamespace
        ns = SimpleNamespace(
            host=host, port=port,
            canonical_root=args.canonical_root,
            no_browser=args.no_browser,
            open_browser=args.open_browser,
        )
        return run_from_args(ns)

    if args.command == "install-hooks":
        from engine.installer import CerberusEnvironmentInstaller
        installer = CerberusEnvironmentInstaller()
        result = installer.install_codex_hooks(dry_run=args.dry_run,
            codex_home=Path(args.codex_home or os.environ.get("CODEX_HOME")) if args.codex_home or os.environ.get("CODEX_HOME") else None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    roots = [r for r in get_default_roots() if r.exists()]
    canonical_root = roots[0] if roots else Path(__file__).resolve().parent.parent
    service = CerberusMemoryService(SQLiteMemoryIndex(canonical_root / ".cerberus" / "index.db"))

    if args.command == "index":
        print(f"🔄 Indexando raízes: {[str(r) for r in roots]}...")
        if args.rebuild:
            res = service.index.rebuild(roots)
            print(f"✅ Índice reconstruído do zero: {res}")
        else:
            res = service.index.index_roots(roots)
            print(f"✅ Indexação concluída: {res}")

    elif args.command == "search":
        results = service.search(query=args.query, project_id=args.project, limit=args.limit)
        print(f"\n🔍 Resultados para: '{args.query}' (Total: {len(results)})")
        print("=" * 60)
        for idx, r in enumerate(results, start=1):
            print(f"{idx}. [{r.item.project_id.upper()}] {r.item.title} (Auth: {r.item.authority_level} | Score: {r.final_score})")
            print(f"   📁 {r.item.source_path}")
            if r.matched_snippets:
                print(f"   💬 {r.matched_snippets[0]}")
            print("-" * 60)

    elif args.command == "context-pack":
        pack = service.build_context_pack(
            project_id=args.project,
            task_summary=args.task,
            role=args.role
        )
        print(pack.to_markdown())
        print(f"\n📊 Estimativa de tokens: ~{pack.token_estimate} tokens")

    elif args.command == "decisions":
        results = service.get_decisions(project_id=args.project, limit=args.limit)
        print(f"\n🏛️ Decisões Arquiteturais (Total: {len(results)})")
        print("=" * 60)
        for idx, r in enumerate(results, start=1):
            print(f"{idx}. {r.item.title} (`{r.item.source_path}`)")
            print(f"   > {r.item.snippet}")
            print("-" * 60)

    elif args.command == "learnings":
        results = service.get_learnings(topic=args.topic, project_id=args.project)
        print(f"\n💡 Lições Aprendidas & Gotchas (Total: {len(results)})")
        print("=" * 60)
        for idx, r in enumerate(results, start=1):
            print(f"{idx}. {r.item.title} (`{r.item.source_path}`)")
            print(f"   > {r.item.snippet}")
            print("-" * 60)

    elif args.command == "capture":
        from engine.capture import AutoCaptureEngine
        engine = AutoCaptureEngine(service=service, cerebro_root=canonical_root)
        res = engine.capture_learning(
            title=args.title,
            content=args.content,
            project_id=args.project,
            task_id=args.task,
            agent_role=args.agent
        )
        print(json.dumps(res, ensure_ascii=False))

    elif args.command == "ingest-report":
        from engine.capture import AutoCaptureEngine
        engine = AutoCaptureEngine(service=service, cerebro_root=canonical_root)
        res = engine.ingest_report(
            report_path_or_content=args.report,
            task_id=args.task,
            project_id=args.project,
            agent_role=args.agent,
        )
        print(json.dumps(res, ensure_ascii=False))

    elif args.command in {"inbox", "review", "promote", "reject"}:
        from engine.capture import AutoCaptureEngine
        engine = AutoCaptureEngine(service=service, cerebro_root=canonical_root)
        if args.command == "inbox":
            print(json.dumps([item.to_dict() for item in engine.store.list()], ensure_ascii=False, indent=2))
        elif args.command == "review":
            verification = engine.verify(args.candidate_id) if args.verify else None
            item = engine.store.get(args.candidate_id)
            result = {"candidate": item.to_dict(), "verification": verification,
                      "promotion": engine.promote(args.candidate_id, apply=False)}
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "promote":
            result = engine.promote(args.candidate_id, apply=args.apply)
            print(result["diff"] if not args.apply else json.dumps(result, ensure_ascii=False))
        else:
            print(json.dumps(engine.reject(args.candidate_id), ensure_ascii=False))

    elif args.command == "doctor":
        from engine.agent_hooks import get_hook_health, inspect_codex_hooks
        fts5 = False
        try:
            con = sqlite3.connect(":memory:")
            con.execute("CREATE VIRTUAL TABLE health USING fts5(value)")
            fts5 = True
            con.close()
        except sqlite3.Error:
            pass
        inbox = canonical_root / ".cerberus" / "inbox"
        payload = {
            "runtime": sys.executable,
            "python": {"version": sys.version.split()[0], "fts5": fts5, "utf8": sys.stdout.encoding},
            "canonical_root": str(canonical_root.resolve()),
            "canonical_root_available": canonical_root.is_dir(),
            "index": str(service.index.db_path),
            "candidate_inbox": str(inbox),
            "candidate_count": len(list(inbox.glob("*.json"))) if inbox.exists() else 0,
            "write_permissions": {"inbox": os.access(inbox if inbox.exists() else inbox.parent, os.W_OK)},
            "codex_hooks": inspect_codex_hooks(canonical_root),
            "hook_health": get_hook_health(canonical_root),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    elif args.command == "install-mcp":
        from engine.installer import CerberusEnvironmentInstaller
        installer = CerberusEnvironmentInstaller()
        results = installer.install_all()
        for r in results:
            print(f"✅ {r['target']}: {r['status']}")

    elif args.command == "status":
        stats = service.index.get_stats()
        print("\n📊 Cerberus Memory Engine — Status do Índice")
        print("=" * 50)
        print(f"• Banco SQLite: {stats['db_path']}")
        print(f"• Arquivos rastreados: {stats['total_files']}")
        print(f"• Chunks indexados: {stats['total_documents']}")
        print(f"• Projetos detectados: {', '.join(stats['indexed_projects'])}")
        print("• Tipos de documento:")
        for stype, count in stats['types_breakdown'].items():
            print(f"  - {stype}: {count}")

    elif args.command == "session-context":
        from engine.integrations.orchestrator import OrchestratorAdapter
        adapter = OrchestratorAdapter(application_root=canonical_root, service=service)
        result = adapter.session_start(
            project_id=args.project, task_summary=args.task, role=args.role
        )
        print(result["markdown"])
        print(f"\n📊 Estimativa de tokens: ~{result['token_estimate']} tokens")

    elif args.command == "on-report-accepted":
        from engine.integrations.orchestrator import OrchestratorAdapter
        adapter = OrchestratorAdapter(application_root=canonical_root, service=service)
        result = adapter.on_report_accepted(
            report_path_or_content=args.report,
            task_id=args.task,
            project_id=args.project,
            agent_role=args.agent,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "on-qa-approved":
        if not args.candidate and not args.task:
            raise SystemExit("ERROR: --candidate <id> or --task <id> is required")
        from engine.integrations.orchestrator import OrchestratorAdapter
        adapter = OrchestratorAdapter(application_root=canonical_root, service=service)
        result = adapter.on_qa_approved(
            candidate_id=args.candidate, task_id=args.task
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command in {"handoff-create", "handoff-claim", "handoff-done",
                          "handoff-cancel", "handoff-list"}:
        from engine.handoffs import HandoffStore
        store = HandoffStore(cerebro_root=canonical_root)
        if args.command == "handoff-create":
            result = store.create(project_id=args.project, task_id=args.task,
                                  summary=args.summary, from_agent=args.from_agent,
                                  to_role=args.to_role)
        elif args.command == "handoff-claim":
            result = store.claim(args.handoff_id, agent=args.agent)
        elif args.command == "handoff-done":
            result = store.complete(args.handoff_id, agent=args.agent, result=args.result)
        elif args.command == "handoff-cancel":
            result = store.cancel(args.handoff_id, agent=args.agent)
        else:
            result = [item for item in store.list(status=args.status)]
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
