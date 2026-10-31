# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Unix Socket BCIBot Client v0.4.1
"""Private Unix socket client. No Docker agent TCP port or external listener."""
from __future__ import annotations
from http.client import HTTPConnection
from pathlib import Path
import json
import os
import socket
import stat

SOCKET_FILE = Path.home() / ".local/share/bci-nexus/agent-workspace/agent.sock"
ROUTES = {("GET", "/health"), ("GET", "/actions"),
          ("POST", "/shell"), ("POST", "/ask"), ("POST", "/action")}

class UnixHTTPConnection(HTTPConnection):
    def __init__(self, path: Path, timeout: int):
        super().__init__("localhost", timeout=timeout)
        self.path = path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        try:
            self.sock.connect(str(self.path))
        except BaseException:
            self.sock.close()
            raise

def token() -> str:
    path = Path(os.environ.get("BCI_AGENT_TOKEN_FILE",
        str(Path.home() / ".config/bci-nexus/agent.token"))).expanduser()
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise PermissionError("Missing/unsafe agent token; expected mode 0600")
    if path.stat().st_uid != os.getuid():
        raise PermissionError("Agent token must belong to the current user")
    value = path.read_text(encoding="ascii").strip()
    if len(value) < 48:
        raise ValueError("Agent token too short")
    return value

def verify_socket(path: Path) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise RuntimeError("BCIBot agent socket not ready; restart agent") from exc
    # Connect if and only if this is our private Unix socket.
    if (not stat.S_ISSOCK(metadata.st_mode) or metadata.st_uid != os.getuid()
            or metadata.st_mode & 0o077 or path.parent.is_symlink()):
        raise PermissionError("BCIBot socket must be user-owned with mode 0600")

def call(method: str, route: str, payload: dict | None = None,
         timeout: int = 30) -> dict:
    if (method, route) not in ROUTES:
        raise ValueError("Unapproved container API route")
    verify_socket(SOCKET_FILE)
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    connection = UnixHTTPConnection(SOCKET_FILE, timeout)
    try:
        connection.request(method, route, body=body,
            headers={"Authorization": "Bearer " + token(),
                     "Content-Type": "application/json"})
        response = connection.getresponse()
        raw = response.read(131073)
        status = response.status
    except OSError as exc:
        raise RuntimeError("BCIBot Unix socket unavailable: " + str(exc)) from exc
    finally:
        connection.close()
    if len(raw) > 131072:
        raise ValueError("Container response exceeded 128 KiB")
    if status != 200:
        raise RuntimeError("Container agent HTTP status " + str(status))
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Container must return JSON object")
    return data

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
