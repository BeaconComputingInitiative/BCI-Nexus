# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCI Nexus passive network journal v0.2.0
"""Observe the local host's interfaces. No active scanning or packet capture."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import time

from . import DEVELOPER_SEAL

IFACE = re.compile(r"^[A-Za-z0-9_.:-]{1,24}$")


def run_readonly(args: list[str]) -> str:
    completed = subprocess.run(
        args, check=False, capture_output=True, text=True, timeout=6,
    )
    if completed.returncode:
        raise OSError("Read-only command failed: " + args[0])
    return completed.stdout[:131072]


def get_local_network() -> dict:
    """Return local route, address and associated AP without probing hosts."""
    routes = json.loads(run_readonly(["ip", "-j", "route", "show", "default"]))
    addresses = json.loads(run_readonly(["ip", "-j", "address", "show"]))
    if not isinstance(routes, list) or not isinstance(addresses, list):
        raise ValueError("Unexpected ip command data")
    route = next((x for x in routes if isinstance(x, dict) and x.get("dev")), {})
    interface = route.get("dev")
    if interface is not None and not IFACE.fullmatch(str(interface)):
        raise ValueError("Invalid interface label")
    gateway = route.get("gateway")
    ips = []
    for group in addresses:
        if isinstance(group, dict) and group.get("ifname") == interface:
            for address in group.get("addr_info", []):
                if isinstance(address, dict) and address.get("local"):
                    ips.append(str(address["local"]))
    ssid = bssid = None
    if interface:
        try:
            link = run_readonly(["iw", "dev", interface, "link"])
            ssid_match = re.search(r"(?m)^\s*SSID:\s*(.*)$", link)
            bssid_match = re.search(r"(?im)^\s*Connected to\s+([0-9a-f:]{17})", link)
            ssid = ssid_match.group(1).strip()[:128] if ssid_match else None
            bssid = bssid_match.group(1).lower() if bssid_match else None
        except (OSError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
    return {
        "interface": interface, "gateway": str(gateway) if gateway else None,
        "addresses": sorted(set(ips)), "ssid": ssid, "bssid": bssid,
    }


def canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def event(snapshot: dict, observed_at: datetime | None = None) -> dict:
    return {
        "schema": "bci.nexus.network-change.v1",
        "developer_seal": DEVELOPER_SEAL,
        "observed_utc": (observed_at or datetime.now(timezone.utc)).isoformat(),
        "snapshot_sha256": hashlib.sha256(canonical(snapshot).encode("ascii")).hexdigest(),
        "snapshot": snapshot,
    }


def database_path() -> Path:
    return Path(os.environ.get(
        "BCI_NEXUS_DB",
        str(Path.home() / ".local/share/bci-nexus/network.sqlite3"),
    )).expanduser()


def insert_if_changed(record: dict, path: Path | None = None) -> bool:
    """Insert if and only if network state differs from the last recorded state."""
    target = path if path is not None else database_path()
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with sqlite3.connect(target, timeout=10) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE IF NOT EXISTS observations ("
                   "id INTEGER PRIMARY KEY, observed_utc TEXT NOT NULL, "
                   "snapshot_sha256 TEXT NOT NULL, event_json TEXT NOT NULL)")
        db.execute("BEGIN IMMEDIATE")
        latest = db.execute(
            "SELECT snapshot_sha256 FROM observations ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if latest is not None and latest[0] == record["snapshot_sha256"]:
            return False
        db.execute("INSERT INTO observations (observed_utc,snapshot_sha256,event_json) "
                   "VALUES (?,?,?)",
                   (record["observed_utc"], record["snapshot_sha256"], canonical(record)))
        db.commit()
    os.chmod(target, 0o600)
    return True


def observe_once(path: Path | None = None) -> dict:
    record = event(get_local_network())
    return {"changed": insert_if_changed(record, path), "event": record}


def watch(interval: int) -> None:
    if not 5 <= interval <= 3600:
        raise ValueError("Poll interval must be 5-3600 seconds")
    while True:
        try:
            outcome = observe_once()
            if outcome["changed"]:
                print(canonical(outcome["event"]), flush=True)
        except (OSError, ValueError, sqlite3.Error) as exc:
            print("[BCI] Local observation unavailable: " + str(exc), flush=True)
        time.sleep(interval)
