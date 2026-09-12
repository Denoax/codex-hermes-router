# Architecture

`codex-hermes-router` is a policy-and-execution bridge, not a learned model router or API proxy. Codex remains the authoritative engineering agent. A global Codex skill decides when a bounded subtask is suitable for local offload and invokes `hermes-worker`.

```text
request
  |
  +-- deterministic? -----------------> scripts / native tools
  |
  +-- bounded + low-risk + verifiable? -> Hermes local worker
  |                                      |-- scout
  |                                      |-- research
  |                                      |-- review
  |                                      `-- prototype (isolated worktree)
  |
  +-- authoritative engineering? ------> Codex
  |
  `-- architecture / high-impact? ------> human / higher-level reasoning
```

## Components

### `skills/local-worker`
The Codex-side routing policy. It defines what is safe and useful to delegate and explicitly states that Hermes output is evidence rather than authority.

### `bin/hermes-worker`
A bounded CLI adapter. It selects toolsets, turn caps, read-only/prototype policy, a compact output contract, and JSON usage accounting. It reuses the user's existing Hermes provider/model configuration.

### `codex-worker-guard`
A Hermes `pre_tool_call` hook. It is inert during ordinary Hermes sessions and activates only when the wrapper sets `HERMES_CODEX_WORKER=1`. In read-only modes it blocks direct file writes and common mutating shell commands; in all modes it blocks a set of remote/destructive operations.

## Trust boundary

The guard is defense-in-depth, not a kernel sandbox. The local model and plugin execute with the user's OS permissions. Regex command filtering cannot prove non-mutation against arbitrary shell obfuscation or indirect scripts. Use containers/VMs or OS sandboxing when the repository or task is untrusted.

## Prototype worktrees

Prototype mode delegates through Hermes' native `--worktree` support. Current Hermes defaults to creating the worktree from a freshly fetched remote tip when possible; `worktree_sync: false` in Hermes config changes that behavior to local `HEAD`. Users who require an exact pinned local baseline should configure this deliberately and keep the main working tree clean.
