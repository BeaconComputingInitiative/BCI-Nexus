# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Authenticated Docker BCIBot Client v0.4.0
"""Loopback-only client for the Docker BCIBot shell and inference API."""
from __future__ import annotations
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "http://127.0.0.1:11436"
ROUTES = {("GET", "/health"), ("GET", "/actions"),
          ("POST", "/shell"), ("POST", "/ask"), ("POST", "/action")}

def token() -> str:
    path = Path(os.environ.get("BCI_AGENT_TOKEN_FILE",
        str(Path.home() / ".config/bci-nexus/agent.token"))).expanduser()
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise PermissionError("Missing/unsafe agent token; expected mode 0600")
    value = path.read_text(encoding="ascii").strip()
    if len(value) < 48:
        raise ValueError("Agent token too short")
    return value

def call(method: str, route: str, payload: dict | None = None,
         timeout: int = 30) -> dict:
    if (method, route) not in ROUTES:
        raise ValueError("Unapproved container API route")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(BASE + route, data=data, method=method,
        headers={"Authorization": "Bearer " + token(),
                 "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read(131073)
    except HTTPError as exc:
        raise RuntimeError("Container agent HTTP " + str(exc.code)) from exc
    except URLError as exc:
        raise RuntimeError("Container agent unavailable on port 11436") from exc
    if len(raw) > 131072:
        raise ValueError("Container response exceeded limit")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Container must return a JSON object")
    return value

def health() -> dict:
    return call("GET", "/health", timeout=5)

def actions() -> dict:
    return call("GET", "/actions", timeout=5)

def ask(question: str) -> dict:
    if not 1 <= len(question.strip()) <= 2000:
        raise ValueError("Question length must be 1-2000")
    return call("POST", "/ask", {"question": question}, timeout=130)

def shell(command: str) -> dict:
    if not 1 <= len(command.strip()) <= 4000:
        raise ValueError("Command length must be 1-4000")
    return call("POST", "/shell", {"command": command}, timeout=40)
