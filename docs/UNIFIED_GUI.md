# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# Unified Native GUI and Docker Agent v0.4

**Execution boundary:** one native Kali PyQt6 window; Sentinel retains its existing tabs. Nexus extends the same QMainWindow with Overview, BCIBot + Container Shell, BCILock and Model Training tabs. The extension requires an updated Sentinel repository whose `main(nexus_extension=...)` hook exists.

```bash
cd "$HOME/BCI/BCISentinel-" && git pull --ff-only origin main
cd "$HOME/BCI/BCI-Nexus" && git pull --ff-only origin main
sha256sum -c SHA256SUMS
python3 -m unittest discover -s tests -v
bash scripts/nexus-gui
```

If Sentinel is installed elsewhere, export `BCI_SENTINEL_DIR` pointing to its source directory before launching. No host service or firewall configuration is changed by the GUI launcher.

The Docker BCIBot agent API is intended for authenticated loopback port 11436; its container shell is **not a Kali host shell**, and the GUI requires an explicit confirmation per shell command. The model inference container continues on host port 11435. BCILock remains native; the UI consumes only the existing read-only evidence bridge. The training tab inspects the existing local `~/BCI/BCI-Ollama-FineTune` directory, or an explicitly configured `BCI_TRAINING_ROOT`, and makes no edits or promotion decisions. Training itself remains a separate resumable workflow; no training run is started here.

**Acceptance criteria:** one QApplication/QMainWindow; all Sentinel tabs preserved; Docker agent offline state visible; BCILock read-only; training inventory present; no automatic host command execution, firewall modification, or model replacement.

## Docker agent installation

Provision the constrained Docker agent with `bash scripts/install-docker-agent.sh` after checking hashes and tests. See [Docker agent deployment](DOCKER_AGENT.md). This action creates an internal Docker network, connects the existing Ollama container, and starts `bci-nexus-agent`; it does not restart Ollama or alter BCILock. The Model Training tab remains observation-only.

## Keeping the live capture feed

The integrated GUI can use the updated `BCISentinel-` source checkout while reading the pre-existing live snapshot at `~/BCI/Docker Projects/orbital/captures/bci_state.json`. If the checkout's relative `captures/bci_state.json` does not exist, Nexus automatically uses that legacy capture path when present. Set `BCI_SENTINEL_STATE` explicitly if your live snapshot is elsewhere. No capture file is copied or deleted.
