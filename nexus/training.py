# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Fine-tuning Inventory v0.4.0
"""Observe previous runs, datasets and adapters; do not replace production models."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import os

CATEGORIES = {
    "datasets": ("datasets", {".jsonl"}),
    "logs": ("logs", {".log"}),
    "adapters": ("output", {".safetensors"}),
    "checkpoints": ("output", {".pt", ".bin"}),
    "reports": ("output", {"training_report.json"}),
}

def root() -> Path:
    return Path(os.environ.get("BCI_TRAINING_ROOT",
        str(Path.home() / "BCI/BCI-Ollama-FineTune"))).expanduser()

def status() -> dict:
    base = root()
    if not base.is_dir():
        return {"available": False, "root": str(base),
                "reason": "Fine-tuning directory not found"}
    report = {"available": True, "root": str(base),
              "observed_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "INSPECT_ONLY", "automatic_promotion": False}
    for category, (directory, suffixes) in CATEGORIES.items():
        folder = base / directory
        found, scanned = [], 0
        if folder.is_dir():
            for current, subdirs, filenames in os.walk(folder):
                subdirs[:] = sorted(x for x in subdirs
                    if x not in {".git", ".venv", "__pycache__"})
                if len(Path(current).relative_to(folder).parts) >= 5:
                    subdirs[:] = []
                for name in sorted(filenames):
                    scanned += 1
                    if scanned > 5000:
                        break
                    if (Path(name).suffix not in suffixes
                        and name not in suffixes):
                        continue
                    p = Path(current) / name
                    if p.is_symlink():
                        continue
                    try:
                        st = p.stat()
                    except OSError:
                        continue
                    found.append({"path": str(p.relative_to(base)),
                        "size_bytes": st.st_size,
                        "modified_utc": datetime.fromtimestamp(
                            st.st_mtime, timezone.utc).isoformat()})
                if scanned > 5000:
                    break
        found.sort(key=lambda x: x["modified_utc"], reverse=True)
        report[category] = found[:12]
        report[category + "_scan_truncated"] = scanned > 5000
    return report

if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))
