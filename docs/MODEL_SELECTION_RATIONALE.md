# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026
**Component:** BCI Nexus model-selection architectural decision record (ADR-NX-2026-11-01)
**Decision date:** November 1, 2026
**Decision:** Adopt Qwen3-1.7B as the *new independently evaluated LoRA training foundation*, retaining the earlier Qwen2.5/SEC-OPS deployment until independent promotion criteria pass.
**Status:** Candidate selected and Stage-1/2 local fine-tuning completed; production promotion not authorized.

## Executive decision

BCI Nexus evolved from a lightweight local BCIBot/SEC-OPS assistant into a proposed evidence-aware multi-agent security engineering platform. The original Qwen2.5-0.5B-Instruct foundation was appropriate for validating CPU fine-tuning, JSON message formatting, local Ollama integration and repeatable checkpointing. It offered limited capacity for the more demanding future mix of network telemetry interpretation, cross-tool reasoning, agent task selection, structured incident narratives and code-generation assistance.

The user requested a different model and accepted Qwen3-1.7B after discussing alternatives. This was an **architectural fit and resource trade-off**, not the result of a recorded rigorous head-to-head benchmark. Qwen3 offered substantially more parameter capacity than the previous 0.5B family, native thinking/non-thinking instruction modes, and an explicit agent/tool-use orientation in Qwen's official model documentation. It remained a plausible *experimental* choice on the available CPU-only laptop, unlike larger models with greater full-precision resource demands.

**This is a model-candidate migration, not a production deployment migration.** Existing `bci-secops:unified`, the Docker inference gateway, the original Qwen2.5 adapters, and BCILock enforcement are deliberately preserved until a separately authorized validation/promotion process is implemented.

## Before and after

| Dimension | Historical Qwen2.5-0.5B-Instruct | Qwen3-1.7B candidate | Nexus implication |
|---|---|---|---|
| Approx. parameters | 0.49 billion | 1.7 billion | Approximately 3.47 times as many parameters; more capacity, not a guaranteed accuracy increase |
| Transformer layers | 24 | 28 | Different model architecture and checkpoint lineage |
| Native model-card context window | 32,768 tokens | 32,768 tokens | **No native context-length increase** from this particular switch |
| Thinking toggle | No Qwen3-style `enable_thinking` interface | `enable_thinking=True/False` | Enables selectable reasoning behavior in compatible templates; current BCI trainer uses `False` |
| Structured outputs | Instruction-tuned JSON/structured output | Tool-oriented instruction and agentic task emphasis | Candidate fit for machine-readable action proposals; requires testing |
| Approximate FP32 weight storage alone | 1.96 GB decimal | 6.8 GB decimal | Substantial CPU RAM and inference latency increase |
| Compatibility | Historical Qwen2.5 PEFT LoRA | New Qwen3-specific LoRA | Old adapters cannot be attached to the new base model directly |
| Deployment role | Earlier BCIBot/SEC-OPS ecosystem | Local experimental Nexus model | Keep operational model unchanged until independent qualification |

Numbers and capabilities come from the exact official model cards, not from a user-specific benchmark. Approximate FP32 weight memory is parameter count multiplied by four bytes and excludes activations, optimizer, tokenizer, Python, and OS overhead.

## Criteria used in selecting the new foundation

### 1. Increasing cognitive headroom for multi-agent coordination

Nexus aims to coordinate specialized components such as Sentinel (observation), Specter (protocol intelligence), Forge (engineering), Cipher (cryptographic tasks), Probe (authorized laboratory testing), Blackhole (controlled containment), Mesh (coordination) and Vault (audit). Larger model capacity was considered useful for nuanced context interpretation, structured tool choices and richer explanatory responses. **These are anticipated benefits** until tested with identical held-out examples; parameter count alone cannot establish they are achieved.

### 2. Matching agent-oriented data and response contracts

The fine-tuning roadmap uses Event Intelligence, Agent Actions and Agentic Engineering & Execution records. It emphasizes identifying the relevant tool, respecting network scope, marking evidence sources, distinguishing observation from inference, and producing JSON reports. Qwen3's published agent/tool-call positioning made it a reasonable candidate for this workflow. It does not itself provide network access, filesystem access, a Python executor, a container interface or permission checks. An external orchestrator must implement those capabilities.

### 3. Retaining local sovereignty and a feasible development process

The workstation used for the selection was an Intel Core i5-10210U laptop, approximately 15 GiB RAM and 12 GiB swap, with no CUDA-capable GPU. Qwen3-1.7B was a compromise between a very small model and the substantially higher memory costs of 4B-class alternatives. The candidate was trained using CPU FP32 with PEFT LoRA rather than attempting full-parameter fine-tuning. LoRA only optimizes a small adapter while loading the frozen base; optimizer state, activations and evaluation still consume memory and CPU.

The operator later observed local FP32 inference above 7 GB process RSS and CPU use above 300%, with responses sometimes taking minutes. Therefore **on-device feasibility is established only as a slow experimental workflow**, not a service-level latency guarantee. Q4_K_M GGUF is a possible separately tested deployment format after careful adapter merge/export, but the existing FP32 PEFT adapter cannot be trained directly as an Ollama GGUF. Keep original training weights and optimizer checkpoints.

### 4. Keeping model and policy separate

Nexus security principles require an explicit authorization gate, immutable evidence provenance, per-tool scope constraints, audit logging and human review for high-impact actions. The change of foundation improves the potential *reasoning layer* only. It must not move BLE authentication, BCILock nftables enforcement, incident decisions, endpoint containment or unrestricted shell privileges under model authority. Execute actions **if and only if** explicit approval, scope, verification and external policy constraints all pass. A fluent model response is never proof a command ran.

### 5. Preserving reproducibility without contaminating old models

Qwen2.5 LoRA weights were bound to the old base architecture and cannot be treated as reusable Qwen3 weights. The migration reused selected historical records and conversion logic, with new tokenizer formatting and checkpoint lineage. It preserved the existing Qwen2.5 model/service and wrote independently versioned Qwen3 training artifacts. Existing records require provenance, privacy and semantic review; syntactic validity alone does not make them ground truth.

## Alternatives discussed (not experimentally ranked)

| Candidate | Why it was considered | Trade-off in selection |
|---|---|---|
| Remain on Qwen2.5-0.5B-Instruct | Low RAM cost; historical adapters and SEC-OPS pipeline already exist | Small capacity for proposed multi-agent reasoning tasks; no migration |
| Gemma 3 1B | Smaller candidate with lower approximate weight-memory requirements | Different training/tokenizer path and less alignment with existing Qwen-oriented preparation; no measured comparative benchmark recorded |
| Qwen3-4B-Instruct-2507 | Larger potential reasoning and coding headroom | Substantially greater full-precision memory pressure and CPU inference cost for the available host |
| **Qwen3-1.7B** | Greater capacity than 0.5B; Qwen3 thinking/non-thinking and tool-oriented conventions; family continuity | CPU latency, RAM costs and separate adapters still require engineering work |

No controlled evaluation proving Qwen3-1.7B superior to these alternatives was found in the selection record. These comparisons document the **reasoning behind the decision**, not demonstrated performance rankings.

## Evidence from this Nexus rebuild

The independent local Qwen3 training lineage is recorded in [QWEN3_REBUILD_2026-11-01.md](QWEN3_REBUILD_2026-11-01.md).

- Stage 1, Events Intelligence: checkpoint Step 250 completed. Step-250 adapter SHA-256 `782aa9fa557589d5ef579c4f2d521d0d90e186d0101a9265a7876cb4663d50b9`.
- Stage 2, Agent Actions: checkpoint Step 250 completed. Operator independently verified adapter SHA-256 `20a0fe9f3c868e08597d3b3a3bb89caa9ea6980cf213040df4dab34db7f817b2`.
- Stage-2 evaluation: 16 examples, 4,085 labeled tokens, token-weighted loss `2.4424719470513203`. This is **not a head-to-head result against Qwen2.5** and cannot be compared to historical losses from a different evaluation set.
- Stage 3, Agentic Engineering & Execution: original synthetic 10K archive checksum verified, and a three-role compatibility handoff supplied. No confirmed operator output showing Stage-3 completed training is available as of this record.
- Inference acceptance gaps: a Qwen3 chat session loaded its checkpoint; initial OSNT explanations contained unsupported details, a generic capabilities answer incorrectly claimed executable tools, response lengths truncated, and FP32 latency was high.

The repository's Qwen3 scripts are archived and SHA-256 sealed. The operator's later edited `~/BCI/Nexus/chat.py` is **not** identical to the versioned historical chat source; do not claim its fixes are in this repository.

## Project benefits: expectation versus demonstrated result

| Project objective | Expected gain from Qwen3 selection | Demonstrated evidence | Remaining work |
|---|---|---|---|
| Security-event interpretation | More capacity for multi-signal explanation and uncertainty | Events training stage completed | Blind event-classification evaluation with analyst adjudication |
| Agent action selection | Better structured planning over tool schemas | Agent-actions stage completed | Operator-scoped tool-choice tests; unauthorized-action refusal |
| Engineering assistance | Better code/system design explanations | Stage-3 dataset handoff constructed | Correctness, sandbox compile/test and security reviews |
| Multi-agent coordination | More capable reasoning core for multiple specialist roles | Agent framework design and constrained agent code exist separately | Actual orchestrator integration and end-to-end trace tests |
| Reasoning control | Selectable thinking/non-thinking modes | Official Qwen3 interface supports them; trainer uses non-thinking | Benchmark speed, quality and token use per mode |
| Local operation | Retain full operator control over model weights and datasets | Local CPU adapter training and integrity checks | Quantized service benchmark, deployment gate and rollback |
| Provenance | Explicit adapter chain and SHA-256 checks | Stage-2 digest verified | Independent eval and model-promotion signed policy |

## Acceptance gate before replacing the previous operational model

Promotion may proceed **if and only if** all of these independent requirements are met:

1. **Reproducible lineage:** exact Qwen3 base revision, tokenizer revision, dataset manifests, model weights, PEFT config and checkpoint hashes recorded.
2. **Comparable evaluation:** Qwen2.5 operational baseline and Qwen3 candidate scored on the **same** held-out, group-isolated examples with appropriately aligned tasks and response contracts. Loss alone is insufficient; add technical-answer accuracy, tool-choice correctness, JSON validity, and hallucination rate.
3. **Policy tests:** unsafe/unapproved action requests denied; approved read-only actions only via real external tool adapters with logged approvals. Simulated outputs never represented as real.
4. **Resource tests:** realistic cold-load time, median/p95 generation latency, tokens/s, peak RAM, swap growth and offline resilience on the intended deployment host.
5. **Human review:** analyst acceptance of security findings, factual errors, sensitive data handling, and rollback plan.
6. **Separate deployment authorization:** approved model artifact promoted by an explicit versioned action, never by completion of training alone.

Do not report an unknown result as PASS. Stage-3 readiness and full dataset coverage must be measured with the actual tokenizer. The model-card context window is 32,768 tokens, but the current PEFT training sequence is truncated to 512; claiming 32K fine-tuned memory or long-context competence would be misleading.

## Primary sources and audit references

- [Qwen/Qwen2.5-0.5B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) — 0.49B, 24 layers, 32,768 context, instruction-tuned structured output.
- [Qwen/Qwen3-1.7B model card](https://huggingface.co/Qwen/Qwen3-1.7B) — 1.7B, 28 layers, 32,768 context, thinking/non-thinking templates and agent use.
- [Qwen3 official repository](https://github.com/QwenLM/Qwen3) — Qwen3 family release, thinking/non-thinking behavior and tooling descriptions.
- Local historical migration package: `Nexus Qwen3 Migration v2.0.0` documented candidate evaluation, CPU smoke-test limitations, immutable Qwen2.5 artifacts and no automatic promotion.
- BCI Nexus archived scripts and [rebuild evidence register](QWEN3_REBUILD_2026-11-01.md). This public repository does not include private logs or model weights.

**Decision outcome:** Qwen3-1.7B is the *preferred Nexus development and evaluation foundation* because it balances anticipated agentic reasoning headroom, Qwen training continuity and local controllability. It is **not yet a validated replacement for the production BCIBot/SEC-OPS model**.
