# Security model

## Goals

1. Read-oriented worker modes should not intentionally modify repository state.
2. Delegated workers should not push, merge, deploy, publish, tag, or perform known destructive remote actions.
3. Prototype writes should occur in an isolated Git worktree rather than the primary checkout.
4. The authoritative agent must verify material worker claims.

## Controls

- narrow Hermes toolsets per mode
- bounded `--max-turns`
- `--source tool` session tagging
- explicit worker policy in the delegated prompt
- `pre_tool_call` hook that blocks common mutations
- isolated Hermes worktree + checkpoints for prototypes
- no `tools.override` capability required
- usage/result logs stored locally for inspection

## What this does not provide

The hook is not a security sandbox. Hermes plugins run as normal Python under the user's account, and terminal-command regexes can be bypassed by sufficiently indirect or adversarial commands. The integration is intended for trusted local development tasks, not hostile code execution.

Do not delegate secrets, credential handling, authorization decisions, production mutations, or security-critical final judgment to a weaker worker.

## Reporting vulnerabilities

Do not include tokens, keys, private repository contents, or exploit payloads containing real secrets in public issues. Prefer GitHub private vulnerability reporting when enabled.
