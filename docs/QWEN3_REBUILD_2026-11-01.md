# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026
**Component:** Nexus Qwen3 post-rebuild lineage and reproducibility register
**Evidence date:** 2026-11-01

## Provenance and scope

This register reflects operator-supplied local terminal output and SHA-256 verified archived scripts. It is not evidence that GitHub CI trained the model, that tools execute inside the standalone chat, or that any model has been deployed to a production security boundary.

## Verified training lineage

| Stage | Status | Checkpoint and hash |
|---|---|---|
| Historical custom-v1.2 | Referenced | Step 125 adapter SHA-256 1bf1c3f36555032db080094cc159fa5588a1616fede2cc1512298f846546055e |
| Stage 1 - bci_nexus_events_10k | 250/250 steps reported complete | Step 250 adapter SHA-256 782aa9fa557589d5ef579c4f2d521d0d90e186d0101a9265a7876cb4663d50b9 |
| Stage 2 - bci_nexus_agent_actions_10k | 250/250, complete.json PASS | Step 250 adapter SHA-256 20a0fe9f3c868e08597d3b3a3bb89caa9ea6980cf213040df4dab34db7f817b2 |
| Stage 3 - Agentic Engineering and Execution 10K | Compatible handoff developed; not confirmed trained | Next stage must use Stage-2 adapter as source |

The operator independently checked Stage-2 adapter_model.safetensors SHA-256 and found no remaining training process. Stage-2 evaluation: 16 examples, 4,085 labeled tokens, loss 2.4424719470513203. This small in-pipeline eval does not establish generalization or production readiness. Historical v1.4 controller begins Stage 1 from custom-v1.2 step125 after confirming interim-step100 prerequisite; Stage 2 continues from Stage 1 Step 250.

## Stage 3 dataset and compatibility problem

- Source ZIP: BCI-Nexus-Agentic-Engineering-Execution-10K-v3.0.0.zip
- ZIP SHA-256: 18b0563e6cdce3cefc7a464a47dcb1bbb4c1e20672848e6ec7300ab83e539802
- Original records: 9,000 train; 1,000 eval; multi-turn synthetic episodes including simulated tool observations.
- Original report is STRUCTURAL_PASS; the prior three-role controller demands a different report flag and strictly system/user/assistant roles.
- The v1.1 compatible handoff verifies the original archive, projects one labeled simulated assistant target per episode, checks hash manifests and runs Qwen3 tokenization coverage preflight. Projected records do not preserve complete multi-turn execution trajectories.
- Synthetic evidence must never be presented as real observed command execution. The projection is not expert semantic review. No verified Stage-3 tokenizer output or completed checkpoint was supplied in the evidence reviewed for this publication.

## Training configuration

The stage controller uses Qwen3-1.7B FP32 + PEFT LoRA, AdamW optimizer, CPU threads=4, seq=512, learning rate=0.00002, eval_count=16, 250 optimizer steps and saving every 25 steps. A 250-step run samples 250 shuffled examples from a nominal 9,000-record training set; this is NOT a full epoch.

## Reproducible local preparation

~~~bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
cd "$HOME/BCI/BCI-Nexus"
sha256sum -c SHA256SUMS
python3 -m compileall -q training/rebuild
install -m 644 training/rebuild/bci_nexus_post_interim_v1_4.py "$HOME/Documents/"
install -m 644 training/rebuild/BCI-Nexus-Stage3-Launcher-v1.0.py "$HOME/Documents/"
install -m 644 training/rebuild/BCI-Nexus-Stage3-Compatible-Handoff-v1.1.py "$HOME/Documents/"
"$HOME/BCI/BCI-Ollama-FineTune/.venv/bin/python" "$HOME/Documents/BCI-Nexus-Stage3-Compatible-Handoff-v1.1.py" prepare
~~~

Prepare operates if and only if source checkpoint, source ZIP, and dataset validation gates pass. It is not training approval. Training additionally requires an explicit semantic-review decision, sufficient tokenizer retention, and absence of competing FP32 processes. Source script checksums are listed in training/rebuild/SHA256SUMS.

## Separate runtime and agent security boundaries

The historical standalone chat code is archived as training/rebuild/bci_nexus_chat_v1_1.py. The operator subsequently modified their installed chat.py to add an attention mask and increase max_new_tokens to 256, but that modified local file was not retrieved for this publication. Archived v1.1 is therefore NOT identical to the locally patched runtime. Local inference exhibited CPU latency, truncated answers, and technical hallucinations (OSNT and unsupported tool-execution claims). Those remain evaluation findings. No model-generated text grants tool access or overrides BCILock, operator approval, or network scope.

## Publication restrictions

No binary weights, optimizer.pt, checkpoint state, dataset ZIPs, synthetic fixture records, credentials, internal logs, or private host observations are included. Stage-3 completion and production promotion are NOT claimed.

## Model-selection decision

The architectural rationale, historical alternatives, estimated project benefits, compute costs, and independent model-promotion gates are documented in [MODEL_SELECTION_RATIONALE.md](MODEL_SELECTION_RATIONALE.md). The move to Qwen3 is an independently evaluated local candidate, not proof that the deployed BCIBot/SEC-OPS model was replaced.

## Subsequent Stage-3 completion evidence (2026-11-01)

After this document's original evidence cutoff, the operator provided a passing local Stage-3 integrity-verification output. Baseline loss was `3.6284115075254117`, final loss was `1.694576641500351`, and the verified Step-250 adapter digest was `f8a50f1ba9b2a2b1df2a1d8f5f365ad090be641f463e2d9af0417b9a0805d78d`. The script wrote the local `STAGE3-SHA256SUMS` manifest. These later observations supersede earlier statements that Stage-3 completion was not yet reported. The [Stage-3 completion and Stage-4 handoff record](STAGE3_COMPLETION_2026-11-01.md) documents evidence limits and the next corpus's multi-turn schema compatibility requirement.
