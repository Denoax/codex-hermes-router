#!/usr/bin/env bash
set -euo pipefail
DRY=0
if [[ "${1:-}" == "--dry-run" ]]; then DRY=1; elif [[ $# -gt 0 ]]; then echo "Usage: $0 [--dry-run]" >&2; exit 2; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DST="${HOME}/.local/bin/hermes-worker"
SKILL_DST="${HOME}/.agents/skills/local-worker"
PLUGIN_DST="${HOME}/.hermes/plugins/codex-worker-guard"
command -v hermes >/dev/null 2>&1 || { echo "ERROR: hermes is not on PATH." >&2; exit 1; }
for p in "$BIN_DST" "$SKILL_DST" "$PLUGIN_DST"; do
  [[ ! -e "$p" ]] || { echo "ERROR: refusing to overwrite existing path: $p" >&2; exit 1; }
done
printf 'Will install:\n  %s\n  %s\n  %s\n' "$BIN_DST" "$SKILL_DST" "$PLUGIN_DST"
echo "The guard plugin is inert unless HERMES_CODEX_WORKER=1."
if [[ "$DRY" -eq 1 ]]; then echo "Dry run only; no files changed."; exit 0; fi
mkdir -p "$HOME/.local/bin" "$HOME/.agents/skills" "$HOME/.hermes/plugins"
install -m 0755 "$ROOT/bin/hermes-worker" "$BIN_DST"
cp -a "$ROOT/skills/local-worker" "$SKILL_DST"
cp -a "$ROOT/integrations/hermes/codex-worker-guard" "$PLUGIN_DST"
echo
echo "Files installed. Enable the guard with:"
echo "  hermes plugins enable codex-worker-guard"
echo "If Hermes asks to grant built-in tool override, answer NO; the plugin does not need it."
echo "Then run: hermes-worker doctor"
