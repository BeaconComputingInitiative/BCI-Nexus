# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCIBot / SEC-OPS — First-Party Nexus Development Foundation v0.3.0

BCIBot is maintained **within the BCI-Nexus repository** rather than in a separate BCIBot repository. BCILock and BCISentinel remain separate upstream repositories.

## First-party implementation

- nexus/agent.py — constrained BCIBot agent, seven read-only actions, bounded observation analysis and a hash-only local audit record.
- nexus/core.py — Ollama inference, BCILock evidence and Sentinel snapshot adapters.
- nexus/network.py — passive network-change observation with a private SQLite WAL database.
- nexus/cli.py — operator console, direct actions and agent analysis.
- tests/test_agent.py — regression tests for permissions, action selection and model tool isolation.

## Agent actions

| Action identifier | Source | Effect |
|---|---|---|
| host.summary | Python OS and disk utilities | Hostname, kernel, load and disk occupancy |
| network.interfaces | ip -j address show | Local addresses only |
| network.listeners | ss -H -lnt | Local TCP listening sockets |
| host.processes | ps -eo pid,comm,%cpu,%mem | Resource summary of local processes |
| bcilock.evidence | bci-lock-events status | Fresh L001-L003 BCILock evidence |
| sentinel.snapshot | Existing Sentinel local JSON | Observation snapshot metadata |
| ollama.health | Local /api/tags | Unified model registration |

Actions execute **if and only if** their exact identifiers are registered and all selected actions are allowed before execution. The model does not select actions or receive native executable tools.

Explicitly disabled: network.scan, firewall.modify, bcilock.authorize, shell.execute, service.restart, packet.inject and remote.desktop.expose. No Nexus module is granted firewall or cryptographic signing authority.

## CLI examples

    cd "$HOME/BCI/BCI-Nexus"
    git pull --ff-only origin main
    sha256sum -c SHA256SUMS
    python3 -m unittest discover -s tests -v
    bash scripts/install-user.sh
    bci-nexus actions
    bci-nexus action host.summary
    bci-nexus action ollama.health
    bci-nexus agent-ask --inspect host.summary --inspect ollama.health "Analyze and cite each observation."

The event publisher has a short TTL and is managed independently by BCILock. Nexus must not restart its enforcement service or claim an expired signed shadow lease authorizes network egress.

## Unified model foundation

The locally fine-tuned bci-secops:unified GGUF is accessed via Docker Ollama at 127.0.0.1:11435/api/chat, with localhost host instance 11434 reserved for fallback. Previously verified GGUF transfer SHA-256:

    2edacfdff5fee0b91dec4afd9878ab2f053b0d826fe8efd56759db5e592e7807

Existing SEC-OPS development includes Qwen2.5 fine-tuning, defensive botnet-related synthetic training data, LoRA adapter runs, evaluation staging and read-only host inspection prototypes. No private model files, training logs, phone secrets, local captured data, or host-specific network configurations are copied to this public repository. Additional training assets should be reviewed before importing.

A matching GGUF source file and a reachable inference endpoint do not establish reliable threat verdicts. Citation presence is a structural test, not semantic validation.

## Next milestones

1. Curate the defensive training/evaluation pipeline with published provenance and privacy reviews.
2. Benchmark hallucination, citation precision, false-positive and false-negative behavior.
3. Integrate deterministic evidence validation beyond the basic citation check.
4. Correlate Sentinel telemetry through source-timestamped local event contracts.
5. Add an operator console, without giving the model authority over BCILock.
6. Design any separately authorized executor with explicit scope and independently verified permissions.

Status: BCIBot first-party read-only agent foundation published; live end-to-end acceptance and production readiness remain unverified.
