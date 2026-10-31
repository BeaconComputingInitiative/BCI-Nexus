# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCI Nexus - Three-Project Integration Register
**Document revision:** 0.1.0  
**Recorded development status:** October 31, 2026  
**Repository:** [BeaconComputingInitiative/BCI-Nexus](https://github.com/BeaconComputingInitiative/BCI-Nexus)

## Mission

BCI Nexus coordinates **BCILock (endpoint enforcement)**, **BCIBot / SEC-OPS (AI-supported defensive analysis)**, and **BCISentinel (network and wireless observation)**. Each upstream project keeps its own repository, deployment lifecycle, permissions and operational authority.

**Core rule:** Observe accurately; preserve faithfully; analyze transparently; communicate securely; act deliberately.

## Integrated system at a glance

```text
  BCILock -- bci-lock-events read-only telemetry -----+
                                                       |
  BCISentinel -- wireless/network evidence (planned) -+--> BCI Nexus
                                                       |       |
  BCIBot / SEC-OPS -- Ollama agent --------------------+       +--> operator / terminal
                     127.0.0.1:11435 (Docker)          |
                                                       +--> correlation (planned)

  Enforcement authority: BCILock only. No firewall, unlock,
  scan, or authorization power is delegated to the LLM.
```

## Component responsibilities and source repositories

| Project | Source | Responsibility | Verified integration |
|---|---|---|---|
| BCILock | [BeaconComputingInitiative/BCILock](https://github.com/BeaconComputingInitiative/BCILock) | BLE challenge verification, endpoint posture, egress rule management, audit and signed shadow authorization testing | Published telemetry consumed by `bci-lock-events` locally |
| BCIBot / BCI SEC-OPS | Local installation `~/BCI/BCI-SEC-OPS/agent/`; no separate published BCIBot repository was identified | Unified Ollama model, deterministic read-only host inspection, evidence-assisted analysis | Shared Python agent core points to Docker Ollama |
| BCISentinel | [BeaconComputingInitiative/BCISentinel-](https://github.com/BeaconComputingInitiative/BCISentinel-) | Passive 802.11 observation, AP/station inventory, network indicators, flow-intelligence imports and PyQt6 operator console | Independent implementation present; Nexus bridge not yet deployed |
| BCI Nexus | [BeaconComputingInitiative/BCI-Nexus](https://github.com/BeaconComputingInitiative/BCI-Nexus) | Planned common contracts, event normalization, audit correlation and interface orchestration | Documentation repository initialized; no verified Nexus runtime release |

## 1. BCILock -> BCIBot: deployed read-only evidence bridge

The locally installed `bci-lock-events` command (reported version **v0.1.1**) reads a constrained BCILock telemetry snapshot. A separately invoked publisher can republish a snapshot via `bci-lock-events.service`. The evidence bridge provides deterministic fields and event IDs to the model, and does not authorize firewall changes.

### Evidence references

| Evidence ID | Meaning | Last reported observation |
|---|---|---|
| `L001` | v1.8 signed shadow lease and authorization state | `EXPIRED`, `lease_time_valid=false`, `enforcement=false` |
| `L002` | Local audit chain integrity | `valid=true`, five recorded events, `attested=false` |
| `L003` | v1.5 legacy egress guard | `BLUETOOTH_PRESENCE_NOT_CRYPTOGRAPHIC_LEASE`, `ACCEPT_RULE_PRESENT`, service active |

The five audit events were `AUTH_PENDING`, `DENIED`, `AUTH_PENDING`, `VERIFIED_SHADOW`, `EXPIRED`. The published record used schema `bci.bcilock.telemetry.v1` with **25-second TTL**; it must be refreshed and checked for freshness before current-state claims.

**Interpretation:** An expired signed *shadow* lease is not evidence of compromise. An nftables accept rule alone does not prove end-to-end connectivity. The local hash-linked audit is not externally attested.

### Authority separation

- The working BCILock v1.5 egress policy remains Bluetooth-connection based.
- The v1.8 signed challenge and time-limited lease were tested in a shadow broker without firewall enforcement authority.
- The model may explain these states; it cannot grant network access, approve a BLE challenge, or change nftables policy.
- Do not stop/restart `bci-egress.service` merely to test Nexus: the installed `ExecStopPost` can intentionally reapply restrictive networking.

## 2. BCIBot / SEC-OPS -> Docker Ollama: gateway routed

The original Ollama host instance operates on `127.0.0.1:11434`. A separate container `bci-bot-inference` serves the unified model at **`127.0.0.1:11435`**. The verified GGUF transfer SHA-256 is:

```text
2edacfdff5fee0b91dec4afd9878ab2f053b0d826fe8efd56759db5e592e7807
```

Model configuration fields `system`, `template`, `parameters`, `model_info`, and `messages` matched between host and container. The `details.parent_model` metadata differed by registration lineage (`bci-secops:v2` versus `bci-unified.gguf`), so the Ollama model IDs differ even though the checked GGUF source bytes match.

### Actual local Python entrypoints

```text
~/.local/bin/bci-secops-agent
  -> ~/BCI/BCI-SEC-OPS/agent/bci_secops_bridge.py
  -> ~/BCI/BCI-SEC-OPS/agent/bci_agent_core_v01.py

~/.local/bin/bci-lock-events
  -> ~/.local/share/bci-lock-events/bridge_client.py
  -> shared bci_agent_core_v01.py for the ask path
```

The shared core now reports `http://127.0.0.1:11435/api/chat`; the SEC-OPS `status` check successfully found the `bci-secops:unified` model. This establishes correct endpoint configuration and model availability; an end-to-end, evidence-validated `ask` response through the new route remains to be accepted.

**Pending:** v0.1.2 evidence-grounding correction is not confirmed installed. Raw LLM prose must remain advisory, not a validated threat verdict.

## 3. BCISentinel -> Nexus: planned integration, not yet deployed

The upstream Sentinel repository contains a PyQt6 `sentinel_gui.py` with a Terminal Stream and a NETSCOPE-era control center. Sentinel provides passive observations and its own local metrics. The proposed Nexus adapter will:

1. Consume a documented local snapshot or local-only API without changing capture state.
2. Preserve observed AP/BSSID, station, channel, signal and indicator provenance.
3. Distinguish Wi-Fi management beacons from independently sourced IP flow/C2-like periodicity.
4. Submit bounded, structured, untrusted observations for evidence-supported analysis.
5. Display read-only analysis alongside native Sentinel telemetry.

**Not yet verified:** An installed Nexus adapter, SQL-backed cross-project history, a modified Sentinel GUI, or end-to-end terminal rendering. No claim of active wireless monitoring follows merely from the existence of the repository.

## 4. BCI Nexus orchestration: target contracts

| Responsibility | Source of truth | Permitted Nexus action |
|---|---|---|
| Endpoint authorization | BCILock's independent cryptographic/policy authority | Read-only posture correlation |
| Legacy egress status | BCILock v1.5 | Observe and identify authorization basis |
| Wireless evidence | BCISentinel | Read and normalize with source timestamps |
| Local host inspection | BCIBot constrained tools | Request preapproved, read-only observations |
| Inference | Container Ollama | Submit bounded data; label model analysis |
| Network host inventory (future) | Operator-approved collection | Only when scope and authorization are independently validated |
| Audit and state history (future) | Versioned event contracts / SQLite | Store local observations with provenance and retention policy |
| Remote console (future) | Private Tailscale transport | Never expose VNC publicly by default |

A security-sensitive operation is enabled **if and only if** a separately implemented executor verifies both explicit operator authorization and the permitted scope at execution time. **No such Nexus executor is deployed or published.**

## 5. Milestone verification matrix

| Milestone | Status as of October 31, 2026 |
|---|---|
| BCILock event publisher and `bci-lock-events status` | **Verified locally** |
| BCIBot Docker inference runtime and model registration | **Verified locally** |
| Unified GGUF source transfer SHA-256 | **Verified locally** |
| Shared agent endpoint on Docker port 11435 | **Verified by configuration and status** |
| Docker-backed evidence answer with independent grounding gate | **Pending acceptance** |
| BCILock bridge v0.1.2 evidence-gate deployment | **Not confirmed** |
| Sentinel -> Nexus event adapter | **Not deployed** |
| Nexus SQLite AP/IP history and authorized host inventory | **Not deployed** |
| Nexus operator dashboard / Sentinel Terminal Stream plugin | **Not deployed** |
| Private Tailscale mobile console | **Not deployed** |
| Integrated production release and recovery tests | **Not completed** |

## 6. Planned release structure

```text
BCI-Nexus/
  README.md
  docs/
    ARCHITECTURE.md
    INTEGRATIONS.md
  contracts/      (future)
  integrations/   (future: bcilock, bcibot, sentinel)
  orchestration/  (future)
  database/       (future)
  dashboard/      (future)
  deployment/     (future)
  tests/          (future)
  SHA256SUMS
```

Do not interpret planned directories as shipped functionality. Continue component-level testing before an integration release. The initial target label **v1.0.0-alpha** is reserved for a future verified cross-project milestone, not assigned to the documentation baseline.

## Integrity and public-repository hygiene

Each tracked documentation artifact is covered by the root `SHA256SUMS` manifest (the manifest itself is excluded to avoid self-reference). All published files identify the initiative and developer seal **CJB-DEV-2026**. Exclude raw host inventories, phone identifiers, secrets, private BLE keys, local audit databases and model weight blobs from this public repository.
