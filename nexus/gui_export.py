# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Self-Updating Sentinel Views Export v0.5.3
"""Export rendered, automatically refreshed Sentinel observations and their provenance."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

SEAL = "CJB-DEV-2026"
INITIATIVE = "BEACON COMPUTING INITIATIVE"
SECTIONS = (
    ("wireless_indicators", "Wireless Indicators"),
    ("dns_observation", "DNS Observation"),
    ("edge_flow_intelligence", "Edge Flow Intelligence"),
    ("prometheus_metrics", "Raw Prometheus Metrics"),
    ("terminal_stream", "Terminal Stream"),
)
SECTION_KEYS = frozenset(key for key, _ in SECTIONS)


def _table(table) -> dict:
    columns = []
    for col in range(table.columnCount()):
        header = table.horizontalHeaderItem(col)
        columns.append(str(header.text()) if header is not None else "Column " + str(col + 1))
    rows = []
    for row in range(table.rowCount()):
        rows.append([
            str(table.item(row, col).text()) if table.item(row, col) is not None else ""
            for col in range(table.columnCount())
        ])
    return {"columns": columns, "rows": rows, "row_count": len(rows)}


def _label(label) -> str:
    return str(label.text()) if label is not None else ""


def capture_views(window) -> dict:
    """Read live GUI widgets; hidden pages continue receiving Sentinel's timer updates."""
    return {
        "wireless_indicators": {
            "table": _table(window.indicators_table),
            "limitations": "Wireless indicators do not prove malicious activity.",
        },
        "dns_observation": {
            "summary": _label(window.dns_summary),
            "import_status": _label(window.dns_import_label),
            "table": _table(window.dns_table),
            "limitations": "Encrypted DNS and encrypted Wi-Fi traffic are not decoded.",
        },
        "edge_flow_intelligence": {
            "text": str(window.flow_text.toPlainText()),
            "limitations": "Imported flow evidence cannot be attributed to selected AP.",
        },
        "prometheus_metrics": {
            "table": _table(window.raw_table),
            "limitations": "API status and source timestamps determine freshness.",
        },
        "terminal_stream": {
            "text": str(window.terminal_out.toPlainText()),
            "limitations": "Session output is not a full system event log.",
        },
    }


def build_export(window, section: str = "all", at: datetime | None = None) -> dict:
    if section != "all" and section not in SECTION_KEYS:
        raise ValueError("Unsupported Sentinel export category")
    now = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    snapshot = getattr(window, "current_snapshot", None)
    snapshot = snapshot if isinstance(snapshot, dict) else {}
    data = capture_views(window)
    if section != "all":
        data = {section: data[section]}
    bssid = window.selected_bssid() if callable(getattr(window, "selected_bssid", None)) else None
    return {
        "initiative": INITIATIVE,
        "developer_seal": SEAL,
        "export_schema": "bci.sentinel.gui.export.v1",
        "exported_at_utc": now.isoformat(),
        "section": section,
        "source": "BCISentinel auto-refreshing GUI observation widgets",
        "source_state_version": snapshot.get("version"),
        "source_updated_at_utc": snapshot.get("updated_at_utc"),
        "gui_status": _label(getattr(window, "status_lbl", None)),
        "selected_bssid": bssid,
        "auto_refresh_interval_ms": 1500,
        "freshness_note": (
            "The GUI polls every 1.5 seconds unless frozen. "
            "Offline metrics or stale saved state may still be displayed. "
            "This file is a point-in-time export, not a continuously changing file."
        ),
        "data": data,
    }


def filename(section: str, at: datetime | None = None) -> str:
    if section != "all" and section not in SECTION_KEYS:
        raise ValueError("Unsupported Sentinel export category")
    now = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return "bci-sentinel-" + section.replace("_", "-") + "-" + now.strftime("%Y%m%dT%H%M%SZ") + ".json"


def _write_file(path: Path, payload: bytes) -> None:
    if path.is_symlink():
        raise PermissionError("Refusing symlink export destination")
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
    path.chmod(0o600)


def save_export(path: Path | str, content: dict) -> tuple[Path, Path, str]:
    path = Path(path).expanduser()
    if path.suffix.lower() != ".json":
        raise ValueError("Export destination must end in .json")
    if not path.parent.is_dir():
        raise FileNotFoundError("Export destination directory missing")
    digest_path = path.with_name(path.name + ".sha256")
    if path.is_symlink() or digest_path.is_symlink():
        raise PermissionError("Refusing symlink export paths")
    if content.get("initiative") != INITIATIVE or content.get("developer_seal") != SEAL:
        raise ValueError("BCI identity header missing")
    data = (json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    manifest = (
        "# BEACON COMPUTING INITIATIVE\n"
        "# Developer Seal: CJB-DEV-2026\n" +
        digest + "  " + path.name + "\n"
    ).encode("ascii")
    _write_file(path, data)
    _write_file(digest_path, manifest)
    return path, digest_path, digest
