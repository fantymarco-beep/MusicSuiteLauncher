import argparse
import json
import os
import socket
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any

import markdown
import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
APPS_FILE = BASE_DIR / "apps.json"
UI_DIR = BASE_DIR / "ui"

app = FastAPI(title="Music Suite Launcher")
LAUNCHED_PIDS: dict[str, list[int]] = {}


def load_apps() -> list[dict[str, Any]]:
    with open(APPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_app(app_id: str) -> dict[str, Any]:
    for item in load_apps():
        if item["id"] == app_id:
            return item
    raise HTTPException(status_code=404, detail=f"App '{app_id}' non trovata")


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

    # Check tracked PIDs (excluding html-only launchers)
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
            # Avoid false positives if multiple apps share generic names like main.py
            if all(tok in p["cmdline"] or tok in p["cwd"] for tok in cmd_tokens):
                return True
            for tok in cmd_tokens:
                if tok in p["cmdline"] and (app_path in p["cmdline"] or app_path in p["cwd"] or tok != "main.py"):
                    if tok == "server.py" and "libri musica" not in p["cmdline"] and "libri musica" not in p["cwd"]:
                        continue
                    return True
    return False


@app.get("/api/apps")
def api_get_apps() -> JSONResponse:
    apps = load_apps()
    procs = collect_running_processes()
    result = []
    for item in apps:
        entry = dict(item)
        entry["active"] = is_app_active(item, procs)
        entry["exists"] = os.path.exists(item["path"])
        result.append(entry)
    return JSONResponse(result)


@app.post("/api/launch/{app_id}")
def api_launch(app_id: str) -> JSONResponse:
    item = find_app(app_id)
    app_dir = Path(item["path"])
    target = app_dir / item["launch_target"]

    if not target.exists():
        raise HTTPException(status_code=404, detail=f"File di avvio non trovato: {target}")

    launch_type = item.get("launch_type", "exe")

    if launch_type == "html":
        webbrowser.open(target.as_uri())
        return JSONResponse({"status": "opened", "target": str(target)})

    if launch_type == "bat":
        proc = subprocess.Popen(
            ["cmd.exe", "/c", str(target)],
            cwd=str(app_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        LAUNCHED_PIDS.setdefault(app_id, []).append(proc.pid)
        return JSONResponse({"status": "launched", "pid": proc.pid})

    # exe
    proc = subprocess.Popen(
        [str(target)],
        cwd=str(app_dir),
    )
    LAUNCHED_PIDS.setdefault(app_id, []).append(proc.pid)
    return JSONResponse({"status": "launched", "pid": proc.pid})


@app.post("/api/open-folder/{app_id}")
def api_open_folder(app_id: str) -> JSONResponse:
    item = find_app(app_id)
    folder = Path(item["path"])
    if not folder.exists():
        raise HTTPException(status_code=404, detail=f"Cartella non trovata: {folder}")
    os.startfile(str(folder))
    return JSONResponse({"status": "opened", "path": str(folder)})


@app.get("/api/instructions/{app_id}")
def api_instructions(app_id: str) -> JSONResponse:
    item = find_app(app_id)
    app_dir = Path(item["path"])
    candidates = item.get("instructions_files", ["ISTRUZIONI.md", "README.md", "read.md"])

    chosen: Path | None = None
    for rel in candidates:
        p = app_dir / rel
        if p.is_file():
            chosen = p
            break

    if not chosen:
        return JSONResponse({
            "title": item["name"],
            "file": None,
            "html": "<p>Nessun file di istruzioni trovato nella cartella.</p>",
        })

    raw = chosen.read_text(encoding="utf-8", errors="replace")
    rendered = markdown.markdown(raw, extensions=["fenced_code", "tables"])
    return JSONResponse({
        "title": item["name"],
        "file": str(chosen),
        "html": rendered,
    })


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def start_server(port: int) -> None:
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless-test", action="store_true", help="Avvia solo il server HTTP senza GUI")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    port = args.port or find_free_port()

    if args.headless_test:
        start_server(port)
        return

    t = threading.Thread(target=start_server, args=(port,), daemon=True)
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
