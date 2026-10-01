"""
Launcher inteligente e silencioso do DM-Cerebro & Cockpit Pro 5x.
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Comportamento:
1. Verifica se o Inspector ja esta rodando na porta 8765.
2. Se ja estiver rodando, abre a aba no navegador padrao e encerra o processo leve.
3. Se nao estiver rodando, inicia o servidor e, assim que a porta estiver respondendo,
   abre o navegador padrao no Cockpit Pro 5x (100% sem janela preta de terminal).
"""
import os
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PORT = int(os.environ.get("CERBERUS_UI_PORT", "8765"))
URL = f"http://127.0.0.1:{PORT}/"
HEALTH_URL = f"http://127.0.0.1:{PORT}/api/health"
LOG_FILE = ROOT_DIR / ".cerberus" / "launcher.log"


def log(msg: str) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def is_server_running() -> bool:
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "CerberusLauncher/1.0"})
        with urllib.request.urlopen(req, timeout=0.6) as response:
            return response.status == 200
    except Exception:
        return False


def open_browser(target_url: str) -> None:
    try:
        os.startfile(target_url)
    except Exception:
        try:
            webbrowser.open(target_url)
        except Exception as exc:
            log(f"Falha ao abrir navegador: {exc}")


def main() -> None:
    try:
        if is_server_running():
            log(f"Servidor ja ativo na porta {PORT}. Abrindo navegador em {URL}")
            open_browser(URL)
            return

        log(f"Iniciando servidor Cerberus na porta {PORT}...")

        def _wait_and_open():
            for _ in range(50):
                if is_server_running():
                    break
                time.sleep(0.1)
            log(f"Servidor confirmado online! Abrindo navegador: {URL}")
            open_browser(URL)

        opener_thread = threading.Thread(target=_wait_and_open, daemon=True)
        opener_thread.start()

        from engine.server import make_server, serve_forever
        server = make_server("127.0.0.1", PORT, ROOT_DIR)
        log("Servidor escutando requisicoes com sucesso.")
        serve_forever(server)
    except Exception as exc:
        log(f"ERRO FATAL NO LAUNCHER: {exc}")
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"Erro ao iniciar DM-Cerebro:\n{exc}", "DM-Cerebro Cockpit", 0x10)
        except Exception:
            pass


if __name__ == "__main__":
    main()
