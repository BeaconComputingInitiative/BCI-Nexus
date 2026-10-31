# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCI NEXUS
### Unified Cybersecurity Intelligence & Endpoint Defense Platform

**Observe. Analyze. Defend. One Sovereign Platform.**

BCI Nexus is the integration and orchestration platform
connecting three independent Beacon Computing Initiative systems:

- **BCILock:** Endpoint authentication and network egress enforcement.
- **BCIBot / SEC-OPS:** Local AI security analysis and evidence processing.
- **BCISentinel:** Network discovery, wireless monitoring, and telemetry.

## Architecture

BCISentinel → BCIBot → Evidence Analysis

BCILock → Read-only Telemetry → BCIBot

BCI Nexus coordinates the components without transferring
authentication or firewall authority to the language model.

## Integration Status

The platform is built around three separate projects. A verified BCILock-to-BCIBot read-only telemetry path and a Docker-hosted Ollama gateway exist on the developer workstation. The full BCISentinel-to-Nexus connection, evidence-gating upgrade, and operator dashboard are still pending.

| Project | Integrated responsibility | Current state |
|---|---|---|
| [BCILock](https://github.com/BeaconComputingInitiative/BCILock) | Endpoint authentication, egress observation and audit evidence | Read-only telemetry bridge tested locally |
| BCIBot / BCI SEC-OPS | Constrained read-only agent, unified local Ollama inference, evidence analysis | Shared agent routed to Docker port 11435; full grounding test pending |
| [BCISentinel](https://github.com/BeaconComputingInitiative/BCISentinel-) | Wireless observation, network indicators and PyQt6 Terminal Stream | Independent project; Nexus integration pending |
| BCI Nexus | Cross-project contracts, evidence correlation and operator orchestration | Documentation baseline; orchestration not deployed |

**Detailed [integration breakdown, trust boundaries and verification matrix](docs/INTEGRATIONS.md).**

## Executable integration foundation (v0.2.0)

Nexus provides a nonprivileged, read-only CLI for BCILock telemetry, Docker Ollama model health, Sentinel snapshot inspection, and a local IP/AP-change journal. The shared BCI SEC-OPS/BCILock integration remains independently installed. No firewall or BLE authentication authority is transferred to Nexus.

~~~sh
cd "$HOME/BCI/BCI-Nexus"
git pull --ff-only origin main
sha256sum -c SHA256SUMS
python3 -m unittest discover -s tests -v
bash scripts/install-user.sh
bci-nexus doctor
bci-nexus status
bci-nexus terminal
bci-nexus observe
~~~

The optional command bci-nexus ask-lock submits fresh BCILock evidence for advisory model analysis; its evidence-ID gate is structural only, not semantic verification. No automatic host scans, system services, Sentinel GUI modifications, or remote desktop configuration are included.

See [Runbook](docs/RUNBOOK.md) and [Security](SECURITY.md).

## Development Status

Integration in progress.

The containerized unified Ollama model and SEC-OPS gateway
have passed initial local connectivity and inference tests.

Evidence-gate validation, Sentinel integration, SQLite network
inventory, and Tailscale remote access remain development milestones.

## Security Principles

1. Observe accurately.
2. Preserve faithfully.
3. Analyze transparently.
4. Communicate securely.
5. Act deliberately.

## Integrity

Release artifacts and configuration files will be accompanied
by SHA-256 verification manifests.
