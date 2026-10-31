# BEACON COMPUTING INITIATIVE
Developer Seal: CJB-DEV-2026

# BCI Nexus BCIBot Swarm v0.5.0

Single-host role-specialized orchestration: Coordinator (deterministic intent routing), Observer (operator-approved Kali network tools), Analyst and Skeptic (independent concurrent role prompts to the same bci-secops:unified model), Verifier (checks exit status/response provenance, not semantic truth), and Auditor (SHA-256 job journal).

SSID surveys use NetworkManager nmcli. Nmap is host discovery only, unprivileged, and restricted to a directly connected private /24-/30 subnet. The GUI displays the exact command and scope and requires explicit operator approval. RFC1918 private addresses do not establish authorization to scan shared networks.

No model-generated commands run on Kali. The Docker shell remains independently isolated. The swarm cannot modify BCILock, nftables, model training jobs or production databases.

This is not yet a distributed swarm across multiple machines. Analyst and Skeptic share one model; agreement is not evidence of factual accuracy. Log: ~/.local/state/bci-nexus/swarm-audit.jsonl with SHA-256 sidecar.

## Observation routing and verification v0.5.1

"Check my network for endpoints", "discover hosts on my network" and
"list devices on my network" trigger an operator-reviewed bounded host
observation plan rather than an Ollama-only analysis. No scan runs absent
approval, and private-address range does not imply legal authorization.

Model advice always reports `verified=false` and separately
`response_shape_valid` when its transport and format are correct.
Observed command output separately reports `execution_succeeded` for
exit-code success. Neither flag certifies the substantive findings.
