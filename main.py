import argparse
import json
import mimetypes
import os
import socket
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import markdown
import psutil

BASE_DIR = Path(__file__).resolve().parent
APPS_FILE = BASE_DIR / "apps.json"
UI_DIR = BASE_DIR / "ui"

LAUNCHED_PIDS: dict[str, list[int]] = {}


def load_apps() -> list[dict[str, Any]]:
    with open(APPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_app(app_id: str) -> dict[str, Any] | None:
    for item in load_apps():
        if item["id"] == app_id:
            return item
    return None


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.15)
        return s.connect_ex(("127.0.0.1", port)) == 0


def collect_running_processes() -> list[dict[str, Any]]:
    procs = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
        try:
            info = proc.info
            procs.append({
                "pid": info["pid"],
                "name": (info.get("name") or "").lower(),
                "cmdline": " ".join(info.get("cmdline") or []).lower(),
                "cwd": (info.get("cwd") or "").lower(),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return procs


def is_app_active(item: dict[str, Any], procs: list[dict[str, Any]]) -> bool:
    app_id = item["id"]
    match = item.get("process_match") or {}
    exe_names = [e.lower() for e in match.get("exe_names", [])]
    cmd_tokens = [c.lower() for c in match.get("cmdline_contains", [])]
    ports = match.get("ports", [])
    app_path = item["path"].lower()

    for port in ports:
        if is_port_open(port):
            return True

    tracked = LAUNCHED_PIDS.get(app_id, [])
    alive_tracked = []
    for pid in tracked:
        if psutil.pid_exists(pid):
            try:
                p = psutil.Process(pid)
                if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                    alive_tracked.append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    LAUNCHED_PIDS[app_id] = alive_tracked
    if alive_tracked:
        return True

    for p in procs:
        if exe_names and p["name"] in exe_names:
            return True
        if cmd_tokens:
            if all(tok in p["cmdline"] or tok in p["cwd"] for tok in cmd_tokens):
                return True
            for tok in cmd_tokens:
                if tok in p["cmdline"] and (app_path in p["cmdline"] or app_path in p["cwd"] or tok != "main.py"):
                    if tok == "server.py" and "libri musica" not in p["cmdline"] and "libri musica" not in p["cwd"]:
                        continue
                    return True
    return False


class LauncherHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(404)
            return
        mime, _ = mimetypes.guess_type(str(path))
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{mime or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = unquote(self.path.split("?", 1)[0])

        if path == "/":
            self._send_file(UI_DIR / "index.html")
            return

        if path.startswith("/ui/"):
            rel = path[len("/ui/"):]
            target = (UI_DIR / rel).resolve()
            if UI_DIR.resolve() in target.parents or target == UI_DIR.resolve():
                self._send_file(target)
            else:
                self.send_error(403)
            return

        if path == "/api/apps":
            apps = load_apps()
            procs = collect_running_processes()
            result = []
            for item in apps:
                entry = dict(item)
                entry["active"] = is_app_active(item, procs)
                entry["exists"] = os.path.exists(item["path"])
                result.append(entry)
            self._send_json(result)
            return

        if path.startswith("/api/instructions/"):
            app_id = path[len("/api/instructions/"):]
            item = find_app(app_id)
            if not item:
                self._send_json({"detail": "App non trovata"}, 404)
                return

            app_dir = Path(item["path"])
            candidates = item.get("instructions_files", ["ISTRUZIONI.md", "README.md", "read.md"])
            chosen: Path | None = None
            for rel in candidates:
                p = app_dir / rel
                if p.is_file():
                    chosen = p
                    break

            if not chosen:
                self._send_json({
                    "title": item["name"],
                    "file": None,
                    "html": "<p>Nessun file di istruzioni trovato nella cartella.</p>",
                })
                return

            raw = chosen.read_text(encoding="utf-8", errors="replace")
            rendered = markdown.markdown(raw, extensions=["fenced_code", "tables"])
            self._send_json({
                "title": item["name"],
                "file": str(chosen),
                "html": rendered,
            })
            return

        self.send_error(404)

    def do_POST(self) -> None:
        path = unquote(self.path.split("?", 1)[0])

        if path.startswith("/api/launch/"):
            app_id = path[len("/api/launch/"):]
            item = find_app(app_id)
            if not item:
                self._send_json({"detail": "App non trovata"}, 404)
                return

            app_dir = Path(item["path"])
            target = app_dir / item["launch_target"]
            if not target.exists():
                self._send_json({"detail": f"File di avvio non trovato: {target}"}, 404)
                return

            launch_type = item.get("launch_type", "exe")
            if launch_type == "html":
                webbrowser.open(target.as_uri())
                self._send_json({"status": "opened", "target": str(target)})
                return

            if launch_type == "bat":
                proc = subprocess.Popen(
                    ["cmd.exe", "/c", str(target)],
                    cwd=str(app_dir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                LAUNCHED_PIDS.setdefault(app_id, []).append(proc.pid)
                self._send_json({"status": "launched", "pid": proc.pid})
                return

            proc = subprocess.Popen([str(target)], cwd=str(app_dir))
            LAUNCHED_PIDS.setdefault(app_id, []).append(proc.pid)
            self._send_json({"status": "launched", "pid": proc.pid})
            return

        if path.startswith("/api/open-folder/"):
            app_id = path[len("/api/open-folder/"):]
            item = find_app(app_id)
            if not item:
                self._send_json({"detail": "App non trovata"}, 404)
                return

            folder = Path(item["path"])
            if not folder.exists():
                self._send_json({"detail": f"Cartella non trovata: {folder}"}, 404)
                return

            os.startfile(str(folder))
            self._send_json({"status": "opened", "path": str(folder)})
            return

        self.send_error(404)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless-test", action="store_true", help="Avvia solo il server HTTP senza GUI")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    port = args.port or find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), LauncherHandler)

    if args.headless_test:
        server.serve_forever()
        return

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    import webview
    webview.create_window(
        "MUSIC SUITE — Launcher",
        f"http://127.0.0.1:{port}/",
        width=1320,
        height=860,
        min_size=(960, 640),
        background_color="#F5F5F4",
    )
    webview.start()


if __name__ == "__main__":
    main()
