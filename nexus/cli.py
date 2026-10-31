# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCI Nexus user CLI v0.2.0
"""Nonprivileged operator console for the read-only integration foundation."""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from . import DEVELOPER_SEAL, __version__
from . import core, network, agent


def display(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BCI Nexus defensive read-only console")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("doctor")
    sub.add_parser("status")
    sub.add_parser("terminal")
    sub.add_parser("observe")
    sub.add_parser("actions")
    direct = sub.add_parser("action")
    direct.add_argument("name")
    bot = sub.add_parser("agent-ask")
    bot.add_argument("--inspect", action="append", dest="inspections", required=True)
    bot.add_argument("question", nargs="+")
    watch = sub.add_parser("watch")
    watch.add_argument("--interval", type=int, default=15)
    ask = sub.add_parser("ask-lock")
    ask.add_argument("question", nargs="+")
    args = parser.parse_args(argv)
    try:
        if args.action == "doctor":
            display({
                "developer_seal": DEVELOPER_SEAL, "version": __version__,
                "ollama_endpoint": core.ollama_url(),
                "commands": {cmd: bool(shutil.which(cmd))
                             for cmd in ("ip", "iw", "bci-lock-events")},
                "network_scanning_enabled": False, "firewall_control_enabled": False,
            })
        elif args.action == "status":
            display(core.overall_status())
        elif args.action == "terminal":
            status = core.overall_status()
            print("BEACON COMPUTING INITIATIVE | " + DEVELOPER_SEAL)
            print("BCI NEXUS v" + __version__ + " | READ ONLY")
            for key in ("ollama", "bcilock", "sentinel"):
                item = status[key]
                print(key.upper() + ": " +
                      ("AVAILABLE" if item["available"] else "UNAVAILABLE"))
                if key == "bcilock" and item["available"]:
                    evidence = item["data"]["facts"]
                    for fact in evidence:
                        print(fact["id"] + " " + json.dumps(fact["value"], sort_keys=True))
        elif args.action == "actions":
            display(agent.catalog())
        elif args.action == "action":
            display(agent.execute(args.name))
        elif args.action == "agent-ask":
            result = agent.analyze(" ".join(args.question), args.inspections)
            display(result)
            return 0 if result["citation_gate_passed"] else 3
        elif args.action == "observe":
            display(network.observe_once())
        elif args.action == "watch":
            network.watch(args.interval)
        elif args.action == "ask-lock":
            payload = core._limited_status_command()
            # Model consultation is allowed iff the observation is fresh.
            if not core.telemetry_fresh(payload):
                print("[BCI] FAIL: BCILock telemetry stale. Republish first.",
                      file=sys.stderr)
                return 2
            result = core.ask_about_lock(" ".join(args.question), payload)
            display(result)
            return 0 if result["citation_check"]["passed"] else 3
        return 0
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, RuntimeError, PermissionError, json.JSONDecodeError) as exc:
        print("[BCI] FAIL: " + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
