# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCI Nexus v0.2.0 Operator Runbook

## Local setup

Requirements: Python 3.10+, Bash, sha256sum and Linux iproute2. The independently installed bci-lock-events command and loopback Ollama model are optional runtime inputs.

~~~sh
cd "$HOME/BCI/BCI-Nexus"
sha256sum -c SHA256SUMS
python3 -m unittest discover -s tests -v
bash scripts/install-user.sh
bci-nexus doctor
bci-nexus status
~~~

Install changes only a user-level CLI symlink at ~/.local/bin/bci-nexus. It does not call sudo, systemctl, nft, nmap, docker, or a remote API.

## Commands

~~~sh
bci-nexus doctor
bci-nexus status
bci-nexus terminal
bci-nexus observe
bci-nexus watch --interval 15
bci-nexus ask-lock "Explain L001 L002 L003 from current observations"
~~~

Local network observation records interface, addresses, default gateway, and associated SSID/BSSID into a private SQLite WAL DB at ~/.local/share/bci-nexus/network.sqlite3. A network-change event is inserted if and only if the fingerprint differs from the previous snapshot.

## Environment

- BCI_OLLAMA_URL: defaults to http://127.0.0.1:11435/api/chat; the host fallback http://127.0.0.1:11434/api/chat is allowed. All other URLs are rejected.
- BCI_SENTINEL_STATE: path to an existing local JSON snapshot, maximum 2MB.
- BCI_NEXUS_DB: alternate SQLite event database location.

## Recovery

Nexus never changes BCILock enforcement. Do not restart bci-egress.service merely for Nexus testing: its stop handler can apply a restrictive egress policy. A failed model endpoint is reported as unavailable. Remove the CLI symlink only if and only if it resolves to this repository's launcher.

## Verified and pending

The existing BCILock event bridge and SEC-OPS model routing were checked on the operator workstation separately. These tests do not claim end-to-end production security, semantic evidence adjudication, Sentinel UI embedding, authorized host scanning, or Tailscale remote console deployment. The initial integration release is a read-only foundation.
