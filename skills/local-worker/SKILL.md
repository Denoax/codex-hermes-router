---
name: local-worker
description: Delegate bounded, low-risk, easily verifiable scouting, research, first-pass review, or prototype work to Hermes. Use when deterministic scripts cannot answer the task directly and Codex can verify the result. Do not use for authoritative architecture, security decisions, irreversible actions, or final correctness claims.
---

# Local Worker

Use Hermes as a subordinate local worker, never as the authority.

## Routing

First ask:
1. Can deterministic tooling answer this reliably? If yes, use it instead.
2. Is the subtask bounded, low-risk, and straightforward to verify? If no, keep it in Codex.
3. Choose one mode:

- `scout`: repository/source/history mapping; mutation-guarded.
- `research`: web/source evidence gathering; mutation-guarded.
- `review`: first-pass diff/log/test/static-analysis review; mutation-guarded.
- `prototype`: speculative implementation only; Hermes edits an isolated Git worktree while Codex owns Git state.

Good delegation targets:
- map an unfamiliar subsystem
- inventory existing implementations/artifacts
- gather source-backed external research
- cluster logs or test failures
- first-pass code/diff review
- identify likely call sites/contracts
- try a bounded implementation experimentally

Do not delegate:
- final architecture or high-impact design decisions
- security/privacy-sensitive judgment
- credential/secret handling
- remote Git/release/deployment actions
- irreversible/destructive operations
- final correctness/visual/performance approval
- work that a deterministic script can perform directly

## Invocation

Prefer stdin or task files so task text is not shell-interpreted.

```bash
printf '%s\n' "<bounded task>" | hermes-worker scout --repo "$PWD"
printf '%s\n' "<research task>" | hermes-worker research --repo "$PWD"
printf '%s\n' "<review task>" | hermes-worker review --repo "$PWD"
printf '%s\n' "<prototype task>" | hermes-worker prototype --repo "$PWD"
```

Hermes output is evidence, not truth. Verify material claims against source/tests/authoritative docs before using them.

For `prototype`, inspect the produced worktree/diff and selectively integrate useful changes; never ask Hermes to commit or assume the prototype is correct.

Keep delegation prompts compact. Include only task, relevant scope/path, required baseline/constraints, desired evidence, and stop condition. Do not send giant conversation history to Hermes.
