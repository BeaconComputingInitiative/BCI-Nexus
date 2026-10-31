# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Docker BCIBot Shell and Inference Agent v0.4.1
"""Authenticated container shell API over a private Unix-domain socket."""
from __future__ import annotations
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingUnixStreamServer
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import hmac
import json
import subprocess
import os
import stat

WORKSPACE = Path("/workspace")
SOCKET_FILE = WORKSPACE / "agent.sock"
TOKEN_FILE = Path("/run/secrets/agent.token")
OLLAMA_URL = "http://bci-bot-inference:11434/api/chat"
MODEL = "bci-secops:unified"
ACTIONS = {
    "container.identity": ["id"],
    "container.disk": ["df", "-h", "/workspace"],
    "container.processes": ["ps", "-eo", "pid,comm,%cpu,%mem"],
    "workspace.list": ["ls", "-lah", "/workspace"],
}

def validate_command(command: object) -> str:
    # Execute if and only if an operator supplies a bounded container command.
    if not isinstance(command, str) or not 1 <= len(command.strip()) <= 4000:
        raise ValueError("Command length must be between 1 and 4000")
    if "\x00" in command:
        raise ValueError("NUL bytes are not allowed")
    return command

def execute(argv: list[str], timeout: int = 25) -> dict:
    try:
        result = subprocess.run(
            argv, cwd=WORKSPACE, capture_output=True, check=False,
            text=True, errors="replace", timeout=timeout,
            env={"HOME": "/workspace", "PATH": "/usr/local/bin:/usr/bin:/bin"},
        )
        return {"scope": "CONTAINER_ONLY", "exit_code": result.returncode,
                "stdout": result.stdout[:32000], "stderr": result.stderr[:32000]}
    except subprocess.TimeoutExpired:
        return {"scope": "CONTAINER_ONLY", "exit_code": 124,
                "stdout": "", "stderr": "Execution exceeded 25 seconds"}

def shell(command: object) -> dict:
    command = validate_command(command)
    result = execute(["/bin/bash", "--noprofile", "--norc", "-c", command])
    digest = hashlib.sha256(command.encode()).hexdigest()
    with (WORKSPACE / "shell-audit.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps({"utc": datetime.now(timezone.utc).isoformat(),
            "developer_seal": "CJB-DEV-2026", "command_sha256": digest,
            "exit_code": result["exit_code"]}, sort_keys=True) + "\n")
    return {**result, "command_sha256": digest}

def ask(question: object) -> dict:
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
        raise ValueError("Question length must be between 1 and 2000")
    payload = json.dumps({"model": MODEL, "stream": False,
        "messages": [
            {"role": "system", "content":
             "You are BCIBot, a defensive systems analyst. No tools are attached "
             "to inference. Shell is a separate operator-approved operation. "
             "Never claim that analysis grants BCILock authorization."},
            {"role": "user", "content": question},
        ]}).encode()
    req = Request(OLLAMA_URL, data=payload, method="POST",
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=120) as response:
        raw = response.read(131073)
    if len(raw) > 131072:
        raise ValueError("Model response too large")
    obj = json.loads(raw)
    message = obj.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise ValueError("Model response malformed")
    return {"model": MODEL, "analysis": message["content"][:8000],
            "scope": "ADVISORY_ONLY"}

class Handler(BaseHTTPRequestHandler):
    key = ""
    def log_message(self, format, *args):
        return  # Keep commands, prompts and auth credentials out of HTTP logs.

    def response_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def authorized(self) -> bool:
        if not hmac.compare_digest(
            self.headers.get("Authorization", ""), "Bearer " + self.key
        ):
            self.response_json(401, {"error": "Unauthorized"})
            return False
        return True

    def read_body(self) -> dict:
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length") from exc
        if not 0 < size <= 8192:
            raise ValueError("Body outside 1–8192 bytes")
        data = json.loads(self.rfile.read(size))
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")
        return data

    def do_GET(self):
        if not self.authorized():
            return
        if self.path == "/health":
            self.response_json(200, {
                "initiative": "BEACON COMPUTING INITIATIVE",
                "developer_seal": "CJB-DEV-2026", "model": MODEL,
                "scope": "CONTAINER_ONLY", "shell": True, "host_shell": False})
        elif self.path == "/actions":
            self.response_json(200, {"actions": sorted(ACTIONS),
                                     "scope": "CONTAINER_ONLY"})
        else:
            self.response_json(404, {"error": "Unknown endpoint"})

    def do_POST(self):
        if not self.authorized():
            return
        if self.path not in {"/shell", "/ask", "/action"}:
            self.response_json(404, {"error": "Unknown endpoint"})
            return
        try:
            data = self.read_body()
            if self.path == "/shell":
                result = shell(data.get("command"))
            elif self.path == "/ask":
                result = ask(data.get("question"))
            else:
                action_id = data.get("id")
                if not isinstance(action_id, str) or action_id not in ACTIONS:
                    raise ValueError("Unregistered action")
                result = {"id": action_id, **execute(ACTIONS[action_id], 10)}
            self.response_json(200, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self.response_json(400, {"error": str(exc)})
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            self.response_json(503, {"error": type(exc).__name__ +
                                           ": " + str(exc)[:160]})

def main() -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    if TOKEN_FILE.is_symlink() or not TOKEN_FILE.is_file():
        raise RuntimeError("Missing mounted agent token")
    Handler.key = TOKEN_FILE.read_text(encoding="ascii").strip()
    if len(Handler.key) < 48:
        raise RuntimeError("Invalid agent token")
    # Bind if and only if the socket is absent or is a stale socket owned by us.
    if SOCKET_FILE.is_symlink():
        raise RuntimeError("Agent socket path is a symlink")
    if SOCKET_FILE.exists():
        previous = SOCKET_FILE.lstat()
        if not stat.S_ISSOCK(previous.st_mode) or previous.st_uid != os.getuid():
            raise RuntimeError("Refusing to replace untrusted socket path")
        SOCKET_FILE.unlink()
    old_umask = os.umask(0o077)
    try:
        server = ThreadingUnixStreamServer(str(SOCKET_FILE), Handler)
    finally:
        os.umask(old_umask)
    SOCKET_FILE.chmod(0o600)
    print("[BCI] Agent listening on Unix socket /workspace/agent.sock", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        if SOCKET_FILE.is_socket() and not SOCKET_FILE.is_symlink():
            SOCKET_FILE.unlink()

if __name__ == "__main__":
    main()
