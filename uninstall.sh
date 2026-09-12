#!/usr/bin/env bash
set -euo pipefail
hermes plugins disable codex-worker-guard >/dev/null 2>&1 || true
rm -f "$HOME/.local/bin/hermes-worker"
rm -rf "$HOME/.agents/skills/local-worker"
rm -rf "$HOME/.agents/skills/iris-camera"
rm -rf "$HOME/.hermes/plugins/codex-worker-guard"
echo "Removed codex-hermes-router runtime files. Usage logs under ~/.local/state/hermes-worker were preserved."
