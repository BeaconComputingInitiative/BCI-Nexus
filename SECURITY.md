# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCI Nexus Security Boundaries v0.2.0

BCILock exclusively owns BLE verification, signed leases, and nftables enforcement. Nexus only reads telemetry through bci-lock-events status.

The SEC-OPS Ollama model is advisory. Citation presence is checked, but citations alone do not prove an answer true. External JSON, packet data and model text are never instructions to execute commands.

Sentinel owns monitor mode, local radio capture, and scope selection. Nexus may inspect an existing local Sentinel JSON snapshot but does not start capture, modify the Sentinel GUI, or perform an nmap scan.

Local network observation is passive: it invokes only ip and iw to read interface state and writes to a private local SQLite database. The data may include personally sensitive network identifiers and must not be committed to public GitHub.

Only the loopback Ollama ports 11434 and 11435 are allowed. The software never enables Tailscale Funnel, VNC, open firewall rules or external model APIs.

Security-sensitive actions would be permitted if and only if a separately authorized executor checked explicit operator permission, precise permitted network scope and live policy. No such executor is shipped in this version.

Hash-linked logs and SHA-256 manifests are integrity aids, not independently attested evidence.
