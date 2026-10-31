# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCIBot Container Agent v0.4.0

The native GUI communicates with an authenticated **loopback-only** agent on port 11436. The agent owns a real Bash execution capability in an **isolated container workspace**. Ollama inference remains in the existing `bci-bot-inference` container, accessed over an internal Docker bridge by container name. BCILock and the Sentinel GUI remain native to Kali.

## Deployment

Run **only after verifying the project checksums and reviewing Docker network changes**:

```bash
cd "$HOME/BCI/BCI-Nexus"
git pull --ff-only origin main
sha256sum -c SHA256SUMS
bash scripts/install-docker-agent.sh
bash scripts/nexus-gui
```

The installer creates a 0600 token at `~/.config/bci-nexus/agent.token` and a persistent nonprivileged workspace at `~/.local/share/bci-nexus/agent-workspace`. It creates the internal Docker network `bci-nexus-inference` if absent and connects the already-existing inference container to that network. It then builds and starts `bci-nexus-agent` with dropped capabilities, a read-only root filesystem, and only the token and dedicated workspace mounted. The agent does **not** receive the Docker socket or arbitrary host paths.

A human approves every Bash command in the GUI. The shell executes each command in `/workspace` with a 25-second timeout; this first version is **not** a persistent TTY. Commands can modify the dedicated workspace. Do not put secrets into the workspace without separate encryption. Docker isolation should not be treated as a perfect security boundary, and membership in the docker group grants substantial host-level privilege to the user.

## Model training

The GUI's Model Training tab is a **read-only artifact inventory**, not a training executor. Existing LoRA datasets, logs, checkpoints and weights stay under `~/BCI/BCI-Ollama-FineTune`. Training jobs and model promotion are intentionally separate from production inference; this release does not start, resume or deploy training models.

## Validation

```bash
docker ps --filter name=bci-nexus-agent
docker exec bci-nexus-agent id
python3 -m unittest discover -s tests -v
```

**Authority:** Shell is container-only. BCILock nftables policy, BLE authentication and host shell are never delegated. Evaluation and explicit operator approval are required before replacing the production model.
