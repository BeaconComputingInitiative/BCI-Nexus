# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026
**Component:** Qwen3-1.7B rebuild scripts and handoff

This folder preserves known, integrity-checked source versions from the local model rebuild. The scripts are not enabled by the running Nexus integration service.

| Script | Role |
|---|---|
| bci_nexus_post_interim_v1_4.py | Guarded Stage-1/Stage-2 LoRA trainer, checkpoint hashes and resume |
| BCI-Nexus-Stage3-Launcher-v1.0.py | Original Stage-3 ZIP/source integrity and process gates; fails with multi-turn dataset |
| BCI-Nexus-Stage3-Compatible-Handoff-v1.1.py | Projects original synthetic multi-turn tool episodes to 3-role examples, preflights tokenizer, and resumes from Stage 2 |
| bci_nexus_chat_v1_1.py | Archived baseline chat; not the later locally modified chat.py |

Validate from repository root with sha256sum -c training/rebuild/SHA256SUMS.

The scripts intentionally require checkpoint assets in $HOME/Documents, a compatible base model at $HOME/BCI/models/Qwen3-1.7B, and the operator-installed Python environment. Copy controllers to $HOME/Documents if and only if their hashes pass. See ../../docs/QWEN3_REBUILD_2026-11-01.md for precise lineage and gate requirements.

The Stage-3 dataset is synthetic. Its tool messages contain fixtures, not real execution. Never bypass semantic review by editing validation flags. Do not run the v1.0 Stage-3 launcher on the unprojected tool-role dataset.
