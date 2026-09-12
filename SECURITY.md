# Security policy

`codex-hermes-router` provides defense-in-depth controls for trusted development
tasks. It is not an OS sandbox.

## Security properties

- The guard is inert outside runs marked with `HERMES_CODEX_WORKER=1`.
- The worker fails closed unless Hermes reports the guard enabled and validates
  its hook registration.
- Mutation-guarded modes block direct file-write tools and common mutating shell
  patterns.
- All modes block known push, merge, release, publish, deploy, privilege, and
  destructive operations.
- Prototype changes occur in a wrapper-owned worktree pinned to the exact local
  `HEAD`; prototype mode refuses a dirty source worktree.
- Prototype runs block Git subcommands that mutate repository, ref, index, or
  configuration state; Codex owns Git integration.
- Prototype cleanup requires both an unchanged `HEAD` and an empty status;
  uncertain, committed, or uncommitted candidate state is preserved.
- Hermes output is evidence or a candidate. Codex must verify material claims.

The controls use prompts, restricted toolsets, and command-pattern filtering.
Hermes and its plugins still execute with the user's OS permissions, so indirect
or obfuscated commands can bypass the guard. Use a container, VM, or OS sandbox
for hostile repositories or untrusted tasks.

Provider/model selection is inherited from Hermes unless explicitly overridden.
Do not assume worker data stays local. Do not delegate secrets, credential
handling, authorization decisions, production mutations, or final
security-sensitive judgment.

Worker state under `${XDG_STATE_HOME:-$HOME/.local/state}/hermes-worker/` can
retain task text, repository paths, results, usage data, and diagnostics until
the user removes it. The uninstaller intentionally preserves this state.

## Reporting vulnerabilities

Do not include tokens, keys, private repository content, or real secret material
in public issues. Use GitHub private vulnerability reporting if it is enabled
for the repository.
