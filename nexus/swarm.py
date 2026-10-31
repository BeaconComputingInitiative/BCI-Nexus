# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Bounded BCIBot Agent Swarm v0.5.1
"""Single-host coordinator, observer, analyst, skeptic, verifier and auditor."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import ipaddress
import json
import os
import re
import shutil
import subprocess
import uuid

from . import agent_client

SEAL = "CJB-DEV-2026"
PHYSICAL = re.compile(r"^(?:wl[\w.-]*|en[\w.-]*|eth\d+|usb\d+)$")
PRIVATE = tuple(ipaddress.ip_network(x) for x in
    ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))

@dataclass(frozen=True)
class HostAction:
    name: str
    argv: tuple[str, ...]
    interface: str
    target: str

@dataclass(frozen=True)
class Job:
    id: str
    question: str
    kind: str
    roles: tuple[str, ...]
    host: HostAction | None = None

def classify(question: str) -> str | None:
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 500:
        return None
    q = question.lower().strip()
    if re.search(r"https?://|(?:\d{1,3}\.){3}\d{1,3}|/\d{1,2}\b|[;&|\x60]", q):
        return None
    if (re.search(r"\b(ssids?|wi-?fi|wireless networks?|access points?)\b", q)
            and re.search(r"\b(pull|show|list|find|scan|around|nearby)\b", q)):
        return "wifi.ssids"
    # Treat "check my network for endpoints" as an observation request,
    # never as evidence that an observation has already occurred.
    local_scope_requested = bool(re.search(
        r"\b(my network|local network|on my network|on the network)\b", q))
    explicit_discovery = bool(re.search(
        r"\b(nmap|network scan|scan (?:my|the|local) network)\b", q))
    endpoint_discovery = bool(re.search(
        r"\b(check|scan|find|discover|list|show|enumerate|identify)\b", q)
        and re.search(r"\b(endpoints?|hosts?|devices?|clients?|machines?)\b", q))
    if local_scope_requested and (explicit_discovery or endpoint_discovery):
        return "network.discover"
    return None

def _cmd(argv: list[str], timeout: int = 6) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, check=False,
                          errors="replace", timeout=timeout)

def local_scope() -> tuple[str, str]:
    route = _cmd(["ip", "-j", "-4", "route", "show", "default"])
    if route.returncode:
        raise RuntimeError("Could not read local IPv4 routes")
    candidates = [r for r in json.loads(route.stdout)
                  if isinstance(r, dict) and PHYSICAL.fullmatch(str(r.get("dev", "")))]
    if not candidates:
        raise ValueError("No eligible physical-interface route")
    metric = min(int(r.get("metric", 0)) for r in candidates)
    best = [r for r in candidates if int(r.get("metric", 0)) == metric]
    if len(best) != 1:
        raise ValueError("Ambiguous physical default route")
    iface = str(best[0]["dev"])
    address = _cmd(["ip", "-j", "-4", "address", "show", "dev", iface])
    if address.returncode:
        raise RuntimeError("Could not read interface address")
    subnets = set()
    for item in json.loads(address.stdout):
        for entry in item.get("addr_info", []):
            if entry.get("family") != "inet":
                continue
            try:
                net = ipaddress.ip_interface(
                    f"{entry['local']}/{entry['prefixlen']}").network
            except (KeyError, ValueError, TypeError):
                continue
            if (24 <= net.prefixlen <= 30 and
                    any(net.subnet_of(block) for block in PRIVATE)):
                subnets.add(str(net))
    if len(subnets) != 1:
        raise ValueError("One directly connected private /24-/30 subnet required")
    return iface, subnets.pop()

def host_plan(kind: str) -> HostAction:
    if kind == "wifi.ssids":
        return HostAction(kind, ("nmcli", "-t", "-f",
            "IN-USE,SSID,BSSID,CHAN,SIGNAL,SECURITY", "device", "wifi",
            "list", "--rescan", "yes"), "NetworkManager", "Nearby SSIDs")
    if kind == "network.discover":
        iface, subnet = local_scope()
        return HostAction(kind, ("nmap", "-sn", "-n", "--max-retries", "1", subnet),
                          iface, subnet)
    raise ValueError("Host action not registered")

def plan(question: str) -> Job:
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
        raise ValueError("Question length must be 1-2000")
    kind = classify(question) or "advisory"
    if kind == "advisory":
        return Job(uuid.uuid4().hex, question, kind,
            ("coordinator", "analyst", "skeptic", "verifier", "auditor"))
    return Job(uuid.uuid4().hex, question, kind,
        ("coordinator", "observer", "verifier", "auditor"), host_plan(kind))

def _observe(approved: HostAction) -> dict:
    # Execute iff the target still matches the operator-approved local plan.
    if approved != host_plan(approved.name):
        raise PermissionError("Network target or command changed since approval")
    if not shutil.which(approved.argv[0]):
        raise FileNotFoundError("Required Kali utility missing: " + approved.argv[0])
    try:
        proc = _cmd(list(approved.argv),
                    80 if approved.name == "network.discover" else 30)
        code, stdout, stderr = proc.returncode, proc.stdout[:32000], proc.stderr[:4000]
    except subprocess.TimeoutExpired:
        code, stdout, stderr = 124, "", "Observation timed out"
    return {"source": "ACTUAL_NATIVE_KALI_TOOL", "action": approved.name,
        "scope": approved.target, "interface": approved.interface,
        "exit_code": code, "stdout": stdout, "stderr": stderr}

def _model(role: str, question: str) -> dict:
    prompt = ("BCI " + role + " role. You have no tools, host shell, "
        "production database access or direct sensor data. Do not claim "
        "to have performed scans. Identify assumptions and missing evidence. "
        "User question: " + question)
    answer = agent_client.ask(prompt)
    return {"role": role, "model": answer.get("model"),
            "scope": answer.get("scope"),
            "text": str(answer.get("analysis") or "")[:6000]}

def _audit(job: Job, output: dict) -> None:
    folder = Path.home() / ".local/state/bci-nexus"
    if folder.is_symlink():
        raise PermissionError("Refusing symlink audit directory")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    folder.chmod(0o700)
    journal = folder / "swarm-audit.jsonl"
    if journal.is_symlink():
        raise PermissionError("Refusing symlink audit journal")
    record = {
        "developer_seal": SEAL,
        "utc": datetime.now(timezone.utc).isoformat(),
        "job_id": job.id,
        "kind": job.kind,
        "question_sha256": hashlib.sha256(job.question.encode()).hexdigest(),
        "response_sha256": hashlib.sha256(json.dumps(
            output, sort_keys=True).encode()).hexdigest(),
        "response_shape_valid": output.get("response_shape_valid", False),
        "execution_succeeded": output.get("execution_succeeded", False),
        "semantic_validation": False
    }
    fd = os.open(journal, os.O_CREAT | os.O_WRONLY | os.O_APPEND |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    journal.chmod(0o600)
    sidecar = folder / "swarm-audit.jsonl.sha256"
    if sidecar.is_symlink():
        raise PermissionError("Refusing symlink audit digest")
    sidecar.write_text(hashlib.sha256(journal.read_bytes()).hexdigest() +
                       "  " + journal.name + "\n", encoding="ascii")
    sidecar.chmod(0o600)

def execute(job: Job, approved: bool = False) -> dict:
    if not isinstance(job, Job) or not job.id:
        raise ValueError("Invalid job")
    if job.kind == "advisory":
        if job.host is not None:
            raise PermissionError("Advisory job cannot include host command")
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(_model, "analyst", job.question)
            s = pool.submit(_model, "skeptic", job.question)
            reports = [a.result(), s.result()]
        valid = all(r["model"] == "bci-secops:unified"
                    and r["scope"] == "ADVISORY_ONLY" and bool(r["text"].strip())
                    for r in reports)
        result = {"source": "LLM_ADVISORY", "reports": reports,
                  "verified": False, "response_shape_valid": valid,
                  "semantic_validation": False,
                  "notice": "No host observation performed; model facts unverified."}
    else:
        if not approved or job.host is None or job.kind != job.host.name:
            raise PermissionError("Explicit operator approval required")
        observation = _observe(job.host)
        result = {"source": "HOST_TOOL_OBSERVATION", "observation": observation,
                  "verified": False, "execution_succeeded": observation["exit_code"] == 0,
                  "semantic_validation": False,
                  "notice": "Exit status is not independent verification of findings."}
    result.update(job_id=job.id, roles=list(job.roles), developer_seal=SEAL)
    _audit(job, result)
    return result
