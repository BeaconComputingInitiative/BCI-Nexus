# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Optional Sentinel terminal adapter v0.2.0
"""Formats Nexus observations for explicit future GUI inclusion.

This standalone module does not modify, start or patch Sentinel PyQt6.
"""
from nexus.core import overall_status


def terminal_lines() -> list[str]:
    status = overall_status()
    result = ["[NEXUS] BEACON COMPUTING INITIATIVE | CJB-DEV-2026"]
    for key in ("ollama", "bcilock", "sentinel"):
        component = status[key]
        result.append("[NEXUS][" + key.upper() + "] " +
                      ("AVAILABLE" if component["available"] else "UNAVAILABLE"))
        if key == "bcilock" and component["available"]:
            for entry in component["data"]["facts"]:
                result.append("[NEXUS][" + entry["id"] + "] " +
                              str(entry["value"])[:256])
    return result
