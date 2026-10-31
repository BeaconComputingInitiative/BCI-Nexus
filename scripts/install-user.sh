#!/usr/bin/env bash
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Nonprivileged CLI installer v0.2.0
set -euo pipefail
ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
SOURCE="$ROOT/scripts/nexus"
TARGET="$HOME/.local/bin/bci-nexus"

# Install if and only if integrity and unit-test checks pass.
(cd "$ROOT" && sha256sum -c SHA256SUMS)
(cd "$ROOT" && python3 -m unittest discover -s tests -v)

mkdir -p "$HOME/.local/bin"
if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    if [[ "$(readlink -f "$TARGET")" != "$SOURCE" ]]; then
        echo "[BCI] FAIL: Existing command belongs to a different installation."
        exit 1
    fi
else
    ln -s "$SOURCE" "$TARGET"
fi
chmod +x "$SOURCE"
echo "[BCI] PASS: Installed local CLI link at $TARGET"
echo "[BCI] No firewall rules, network scans or privileged services changed."
sha256sum "$SOURCE"
