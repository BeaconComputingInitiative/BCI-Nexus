#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCIBot Docker Agent Installer v0.4.1
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"
command -v docker >/dev/null || { echo '[BCI] Docker not installed.'; exit 1; }
command -v python3 >/dev/null || { echo '[BCI] Python required.'; exit 1; }
(cd "$ROOT" && sha256sum -c SHA256SUMS &&
    python3 -m unittest discover -s tests -v)
if ! docker info >/dev/null 2>&1; then
    echo '[BCI] Docker daemon inaccessible. No changes made.'
    exit 1
fi
if ! docker container inspect bci-bot-inference >/dev/null 2>&1; then
    echo '[BCI] Existing bci-bot-inference container not found.'
    exit 1
fi
mkdir -p "$HOME/.config/bci-nexus" "$HOME/.local/share/bci-nexus/agent-workspace"
chmod 700 "$HOME/.config/bci-nexus" "$HOME/.local/share/bci-nexus/agent-workspace"
TOKEN="$HOME/.config/bci-nexus/agent.token"
if [[ ! -e "$TOKEN" ]]; then
    (umask 077; python3 -c 'import secrets,sys; open(sys.argv[1],"x").write(secrets.token_urlsafe(48)+"\n")' "$TOKEN")
fi
chmod 600 "$TOKEN"
export BCI_HOME="$HOME" BCI_UID="$(id -u)" BCI_GID="$(id -g)"
# Connect the model if and only if an internal network is required and available.
if ! docker network inspect bci-nexus-inference >/dev/null 2>&1; then
    docker network create --internal bci-nexus-inference
fi
if ! docker inspect -f '{{json .NetworkSettings.Networks}}' bci-bot-inference | grep -Fq '"bci-nexus-inference"'; then
    docker network connect bci-nexus-inference bci-bot-inference
fi
docker compose -f "$ROOT/docker/compose.agent.yml" up -d --build --force-recreate bci-nexus-agent
SOCKET="$HOME/.local/share/bci-nexus/agent-workspace/agent.sock"
# Report successful deployment if and only if the authenticated Unix API responds.
READY=0
for _attempt in $(seq 1 20); do
    if [[ -S "$SOCKET" ]] && python3 -c 'from nexus import agent_client; assert agent_client.health()["scope"] == "CONTAINER_ONLY"' >/dev/null 2>&1; then
        READY=1
        break
    fi
    sleep 0.5
done
if [[ "$READY" -ne 1 ]]; then
    echo '[BCI] FAIL: Agent Unix socket/API unavailable; inspect container logs.' >&2
    exit 1
fi
echo "[BCI] PASS: Authenticated Unix socket $SOCKET"
echo '[BCI] Inference stays on 11435. No host firewall or BLE changes.'
sha256sum "$ROOT/nexus/container_agent.py" "$ROOT/docker/compose.agent.yml"
