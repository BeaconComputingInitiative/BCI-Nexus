# BEACON COMPUTING INITIATIVE
**Developer Seal:** `CJB-DEV-2026`  
**Component:** BCI-Nexus / BCIBot developer history register  
**Audit baseline:** October 31, 2026  
**Repository:** https://github.com/BeaconComputingInitiative/BCI-Nexus

## Scope and evidence rules

This log reconciles public Git commit history with relevant available BCI development conversations. Every reachable main-branch commit at this baseline receives a separate ledger entry. Chat-only drafts, operator tests and unresolved requirements are labeled independently. Commit presence means code or documentation was published; it does not certify security, deployed system state or hardware behavior. Workflow outcome is for the indicated commit, not for the entire software system. Dates are UTC unless noted.

### Baseline

- Audited main branch head before this documentation update: `f384baa2be31b8350c987c58d315383fd30c1f4a`.
- 33 historical commits, no published GitHub Release objects detected during audit.
- Last observed main-branch CI: [successful](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41244272327) for `f384baa2be3`.
- Nexus is the integration repository. BCIBot inference, capture observations and BCILock enforcement have separate trust boundaries.

## Historical GitHub development updates — each commit

| # | Timestamp | Commit | Published development update | CI for that SHA |
|---:|---|---|---|---|
| 01 | 2026-10-31 14:08:44 UTC | [`92b611ea908`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/92b611ea908488fd3526e2fec053a6e780b383a0) | Initial BCI Nexus integration architecture | no per-commit workflow evidence |
| 02 | 2026-10-31 14:22:43 UTC | [`8a1e3ed417a`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/8a1e3ed417abdf52d32f1f4340d22ebd971f537a) | docs: publish verified Nexus three-project integration register | no per-commit workflow evidence |
| 03 | 2026-10-31 14:30:19 UTC | [`b1a2bf7356f`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/b1a2bf7356f8b829f191a6a430fe42c322959f19) | feat: add Nexus read-only integration CLI, adapters, journal, and tests | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41210476241) |
| 04 | 2026-10-31 14:53:19 UTC | [`77978e63073`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/77978e63073590050cf80fde1e5980a0ba944781) | feat: add first-party BCIBot constrained agent foundation | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212214935) |
| 05 | 2026-10-31 14:53:37 UTC | [`9d68680ed1d`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/9d68680ed1dec3d84c521a8835f64d82193b201c) | test: add BCIBot agent allowlist and no-tool regression tests | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212237078) |
| 06 | 2026-10-31 14:53:51 UTC | [`1320f1894e2`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/1320f1894e2c25667edb76406f0f588707479682) | feat: expose BCIBot action registry and agent-ask CLI | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212252958) |
| 07 | 2026-10-31 14:54:59 UTC | [`b2ba546c089`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/b2ba546c0891c4c09e0904c75a49869e19260130) | docs: establish BCIBot first-party Nexus development foundation | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212337128) |
| 08 | 2026-10-31 14:55:16 UTC | [`09e84c83056`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/09e84c83056d8684bbf1a7a269220eae79799c6f) | docs: integrate BCIBot agent actions and development into Nexus | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212361859) |
| 09 | 2026-10-31 14:55:18 UTC | [`9dd65edb67e`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/9dd65edb67e5cc860f016faed4691a7672e39d9b) | docs: integrate BCIBot agent actions and development into Nexus | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212364478) |
| 10 | 2026-10-31 14:55:20 UTC | [`85c5d56329d`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/85c5d56329d7a39a699bf0c18daeaaf4b2c6069e) | docs: integrate BCIBot agent actions and development into Nexus | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212367391) |
| 11 | 2026-10-31 14:55:59 UTC | [`5911c14af57`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/5911c14af570a171dad419b523bfd6a68ed20608) | chore: hash BCIBot agent, tests, docs and CLI | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41212414498) |
| 12 | 2026-10-31 15:50:34 UTC | [`6a86281d8b6`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/6a86281d8b63e9bbda6573ddc67c456a7d3a1e9c) | branding: publish assets/BCI-Nexus-icon.png | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41216767275) |
| 13 | 2026-10-31 15:50:44 UTC | [`9d13ece37e0`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/9d13ece37e01ae88d1e13435ab7556d41bef3b62) | branding: publish assets/BCI-Nexus-platform-overview.png | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41216779982) |
| 14 | 2026-10-31 15:50:47 UTC | [`8c93daf64f0`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/8c93daf64f0d70328d4a89db635815926b8719bf) | docs: document Nexus artwork provenance | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41216783386) |
| 15 | 2026-10-31 15:50:48 UTC | [`54d1229c92b`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/54d1229c92b934e67d7c65810c7fa55f37cae7b4) | docs: showcase BCI Nexus platform and icon | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41216785363) |
| 16 | 2026-10-31 15:50:50 UTC | [`71b5dd725ac`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/71b5dd725ac72baf39662731f658ac2ab3ba75b3) | chore: update SHA256SUMS for Nexus artwork | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41216787197) |
| 17 | 2026-10-31 20:40:31 UTC | [`f3696392bca`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/f3696392bcafe515c349818fd99f322440fdb93a) | feat(gui): native unified Sentinel Nexus BCIBot BCILock and training inventory | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41240009428) |
| 18 | 2026-10-31 20:41:59 UTC | [`f97fc4b294a`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/f97fc4b294af19172e58121572d5edbaff09da62) | feat(agent): authenticated container shell and isolated Docker deployment | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41240124570) |
| 19 | 2026-10-31 20:42:57 UTC | [`67ed4e32c8b`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/67ed4e32c8b22f852d559c4818400389f8068e63) | fix(docker): confirm inference network membership and validate Bash launchers | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41240196802) |
| 20 | 2026-10-31 20:44:50 UTC | [`bab5ec67825`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/bab5ec6782516473f1945361523633efca9a996f) | fix(gui): preserve live Sentinel capture path across source checkout | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41240337506) |
| 21 | 2026-10-31 20:45:51 UTC | [`c83221910fa`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/c83221910fabe5e2ccb3d3bdfe8bfa2baf0aa830) | fix(integrity): correct SHA-256 manifest for GUI source and deployment notes | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41240418763) |
| 22 | 2026-10-31 21:02:25 UTC | [`39c717bee52`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/39c717bee52d75463d868ee0b7d1a88d9a03fc27) | fix(agent): use authenticated private Unix socket instead of internal-network published port | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41241695207) |
| 23 | 2026-10-31 21:15:49 UTC | [`8bc481adf5c`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/8bc481adf5c58bda5c6d1c182c57e2f0f3198319) | feat(swarm): role-based BCIBot orchestration and approved network observers | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41242764921) |
| 24 | 2026-10-31 21:16:13 UTC | [`b4e700fa259`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/b4e700fa2591e08e847f4f35ea318b1a20d3ded5) | chore(integrity): update SHA-256 manifest for swarm source, tests and docs | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41242795163) |
| 25 | 2026-10-31 21:17:01 UTC | [`3217366cc2a`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/3217366cc2a8f452b365cf334e4554a68304cb56) | test(swarm): correct local-interface JSON fixture and checksum | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41242859921) |
| 26 | 2026-10-31 21:20:17 UTC | [`91539a1b0d9`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/91539a1b0d982a8519ab836782a08da603f7c7ce) | fix(swarm): route endpoint surveys to approved observer and correct advisory verification semantics | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41243117680) |
| 27 | 2026-10-31 21:20:44 UTC | [`a9183804d51`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/a9183804d51781bc5436738c784a7f0eac0557c4) | fix(gui): select embeddable Sentinel checkout and label swarm provenance precisely | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41243157710) |
| 28 | 2026-10-31 21:21:09 UTC | [`0caff9e8783`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/0caff9e8783ad34aa32c531223078d2bc62db611) | chore(integrity): seal Sentinel selection and swarm endpoint intent changes | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41243188954) |
| 29 | 2026-10-31 21:21:47 UTC | [`77b6eb00a56`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/77b6eb00a56d4c7aa2a83750f59d9f59940d99da) | test(gui): allow existing temporary directory in Sentinel selection fixture | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41243240507) |
| 30 | 2026-10-31 21:26:56 UTC | [`f80f38ed209`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/f80f38ed20964aa271068be4570cb5ca3074657b) | fix(gui): clear and refocus BCIBot prompt on accepted dispatch | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41243636672) |
| 31 | 2026-10-31 21:33:29 UTC | [`ef718a8210c`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/ef718a8210c46fb24415f501f8838b710de968ba) | feat(gui): auto-updating hidden Sentinel data and consolidated JSON export menu | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41244155666) |
| 32 | 2026-10-31 21:34:37 UTC | [`5a4b5904a68`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/5a4b5904a68b2e4018afea33369183150794e7dc) | test(gui): cover auto-refreshed Sentinel exports and SHA256 manifest | [failure](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41244243384) |
| 33 | 2026-10-31 21:35:01 UTC | [`f384baa2be3`](https://github.com/BeaconComputingInitiative/BCI-Nexus/commit/f384baa2be31b8350c987c58d315383fd30c1f4a) | chore(integrity): update Sentinel live-export SHA256 manifest | [success](https://github.com/BeaconComputingInitiative/BCI-Nexus/actions/runs/41244272327) |

## Conversation-derived developer update record

The entries below are based on available BCI development conversations and user-supplied terminal/GUI output. They are *not* additional Git commits and should not be treated as proof of production readiness.

| Chat update | When (2026) | Request, observation, or decision | Evidence tier / outcome |
|---|---|---|---|
| NX-C01 | Oct 31 | Define BCI Nexus as the first-party integration point for BCILock, BCISentinel, and BCIBot/SEC-OPS; keep security enforcement native and model authority nonprivileged. | Design decision; initial architecture subsequently committed |
| NX-C02 | Oct 31 | Add a read-only CLI, evidence adapters, IP/AP-change journal, and a native single-window Sentinel extension with BCIBot, BCILock and training inventory tabs. | Git implementation plus GUI screenshots; live source connectivity not fully verified |
| NX-C03 | Oct 31 | BCIBot inference through local Ollama \`bci-secops:unified\`; operator needs an isolated container Bash shell. Initial Docker agent started but was inaccessible at host TCP port 11436. | Operator terminal diagnostics: container running, internal listener 8766, no published host port |
| NX-C04 | Oct 31 | Correct internal-only Docker networking by replacing published TCP transport with authenticated mode-0600 Unix socket. | Git/CI change; operator confirmed agent health \`CONTAINER_ONLY\`, \`/workspace\`, UID 1000, Linux, shell exit 0 |
| NX-C05 | Oct 31 | Verify local-model inference. Model answered but invented a production-database role; user commands for nearby SSIDs and Nmap initially returned synthetic advisory responses, not executed observations. | Operator output: inference PASS; tool-grounding GAP |
| NX-C06 | Oct 31 | Add operator-approved host observation broker and role swarm (Coordinator / Observer / Analyst / Skeptic / Verifier / Auditor). Keep BCILock authority separate. | Git implementation; role reviewers share one Ollama model, not distinct independently trained models |
| NX-C07 | Oct 31 | Repair intent routing for “check my network for endpoints,” prevent model replies from being labeled factually verified, and select embeddable Sentinel source checkout. | Git/CI update; GUI version tested with 40 passing regression tests |
| NX-C08 | Oct 31 | Operator-approved local Nmap host discovery: 256 IPv4 addresses surveyed, two hosts reported up; subsequent “pull their IPs” request incorrectly returned more model advice. | Operator-observed scan result; **persistent endpoint inventory and follow-up retrieval still pending**. Actual private IPs intentionally omitted from public log |
| NX-C09 | Oct 31 | Clear/refocus BCIBot prompt after accepted dispatch, preserve chat history and rejected/declined prompt text. | Git/CI and input regression test; actual GUI interaction should be rechecked |
| NX-C10 | Oct 31 | Consolidate Sentinel UI tabs 4–8 into an Export menu with individual/all JSON export and SHA-256 sidecars; retain the existing 1.5-second GUI poll. | Git/CI implementation; stale capture snapshots still possible |
| NX-C11 | Oct 31 | Screenshot review: native GUI running, model available, Sentinel snapshot stale/API offline, BCILock read-only telemetry publisher absent. User explained the capture adapter was unavailable. | Operator screenshot and chat; missing adapter explains unavailable live radio capture, not all possible metrics failures |
| NX-C12 | Oct 31 | Request universal interface selection, offline/idle capture, and a dedicated GUI interface dropdown; changes implemented in Sentinel repository, not by Nexus itself. | Cross-repository design requirement; Sentinel 4.6.15 CI still failing as of this audit |
| NX-C13 | Oct 31 | Adopt one consolidated GitHub publication per five **chat-driven development changes** per repository. | User release-process instruction; historical commits are logged independently of this future rule |

### Outstanding Nexus acceptance gates

- Persist and retrieve observed endpoint records by job ID, source and timestamp; never ask the language model to recall addresses it was not given.
- Bind the BCILock read-only runtime event publisher without altering phone authorization, nftables, BLE or systemd enforcement.
- Verify live Sentinel API and snapshot freshness only when an appropriate capture source exists; idle/stale data must remain explicitly labeled.
- Validate GUI export behavior and user interactions on the actual Kali workstation; passing offline tests is not proof of all runtime paths.
- Preserve Docker-local shell boundaries, no autonomous host shell, and explicit scope approval for active scans.
- Review model-training pipeline integration; inventory is read-only and job scheduling/promotion are not implemented.

## Five-chat-update publication policy (effective for future work)

A **development update** is a substantive chat-requested behavior or feature change with a recorded decision and acceptance evidence; a mechanical hash, test-fix or README commit is **not automatically** a separate chat update. Record revisions NX-NEXT-01 through NX-NEXT-05 in this log; keep them in a development branch or working tree. Publish **one consolidated GitHub update at update five**, if and only if requested changes are integrated and checks pass. Emergency security changes require operator authorization for early publication. The baseline-history/documentation consolidation itself is a one-time audit operation, not a retroactive five-update release or certified release tag.

## Reproducible checks

```bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
cd "$HOME/BCI/BCI-Nexus"
sha256sum -c SHA256SUMS
python3 -m unittest discover -s tests -v
```

For this document, verify `docs/DEVELOPERS_LOG.md.sha256` from the repository root with `sha256sum -c docs/DEVELOPERS_LOG.md.sha256`. The log is documentation and does not alter running services.

## November 1, 2026 - Post-rebuild Qwen3 handoff

**Source of evidence:** local operator terminal messages plus archived Python scripts, not a production deployment or a new independently trained model artifact on GitHub.

- Events Stage 1 completed 250/250; Agent Actions Stage 2 completed 250/250. The user verified the Stage-2 adapter SHA-256 20a0fe9f3c868e08597d3b3a3bb89caa9ea6980cf213040df4dab34db7f817b2; evaluation loss 2.4424719470513203 over 4,085 tokens / 16 examples.
- Stage-3 synthetic 10K ZIP passed integrity and source checkpoint checks but failed the original three-role trainer schema. A source-preserving synthetic projection and Qwen tokenizer preflight were added. Stage-3 execution and completion have NOT been demonstrated by the terminal output available here.
- Standalone chat loaded a LoRA checkpoint, but the local OSNT and general abilities tests showed factual overclaiming. FP32 CPU latency and output truncation were also observed; the subsequently patched local chat.py is not included in the historical source archive.
- This consolidated publication contains source, documentation, and hash manifests only. See docs/QWEN3_REBUILD_2026-11-01.md.

## November 1, 2026 - Nexus base-model decision record

- Documented why the earlier Qwen2.5-0.5B-Instruct model was used to establish the SEC-OPS pipeline and why Qwen3-1.7B was accepted as the next independent LoRA candidate for more complex Nexus security and multi-agent workflows.
- Recorded 0.49B versus 1.7B parameter counts, both model-card context windows of 32,768 tokens, thinking/non-thinking architecture differences, FP32 CPU memory costs, Gemma 3 1B and Qwen3 4B alternatives, and the incompatibility of historical Qwen2.5 adapters with Qwen3.
- Kept expected advantages separate from measured results: Stage-1/2 checkpoint status, Stage-2 16-example loss, the operator's slow FP32 inference and factual-error observations. No head-to-head model comparison or Stage-3 completion was inferred.
- Confirmed the production service, agent execution policy, BCILock enforcement and model-promotion authority are unchanged. See docs/MODEL_SELECTION_RATIONALE.md.
