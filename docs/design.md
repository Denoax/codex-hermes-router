# Design

Codex is the router. This repository supplies a delegation policy, a bounded
Hermes adapter, and an accidental-mutation guard; it is not an independent
routing service or a learned model selector.

## Delegation policy

Use deterministic code or native tools when they can answer the question
directly. Otherwise, Hermes is suitable only when the subtask is bounded,
low-risk, and cheap for Codex to verify. Architecture, security-sensitive
judgment, irreversible actions, and final correctness remain with Codex or a
human reviewer.

The four worker modes are:

- `scout`: repository, source, and history mapping;
- `research`: external web evidence gathering;
- `review`: first-pass diff, log, test, or static-analysis review;
- `prototype`: a speculative candidate in an isolated worktree.

Worker output follows a compact result/evidence/uncertainty/next-action contract
and is never authoritative by itself.

## Components

`skills/local-worker/SKILL.md` describes when Codex should delegate. The
`hermes-worker` executable selects toolsets and turn limits, builds the delegated
prompt, calls Hermes once, and records results, metadata, and any usage data.
The Hermes `pre_tool_call` hook blocks common mutations and remote/destructive
operations while remaining inert during ordinary Hermes sessions.

Before a worker run, the wrapper requires an enabled guard, successful Hermes
hook validation, no tool-override grant, and the supported rule-isolation flag.
`doctor` additionally checks that the Codex skill is installed, so it reports
the full integration state while direct worker execution remains independent.

Worker sessions use `--ignore-rules`, which the tested Hermes runtime defines as
skipping automatic AGENTS/rules, memory, and preloaded-skill injection. The
prototype prompt instead tells the worker to read applicable repository
instructions deliberately from its exact workspace.

Provider and model configuration are inherited from Hermes, with optional
per-run overrides. Local or offline models are an intended use, not an enforced
invariant.

## Prototype baseline

Prototype mode requires a Git repository with no tracked or untracked changes.
The wrapper resolves local `HEAD`, creates a detached Git worktree at exactly
that commit, and invokes Hermes inside it without Hermes' native `--worktree`
mode. This avoids a remote fetch changing the prototype baseline. Metadata
records both the base SHA and workspace path. No-op worktrees are removed;
committed or uncommitted candidates remain available for review. If inspection
fails or a run is interrupted, the wrapper preserves the worktree rather than
assuming it is empty.

Linked worktrees share repository objects, refs, and configuration. Prototype
runs therefore block Git subcommands that mutate repository state: Hermes may
edit candidate files, but Codex owns staging, commits, refs, configuration, and
integration. Candidate-HEAD comparison remains a defensive recovery path.

## Guard boundary

Mutation-guarded modes disable direct Hermes write tools and block common shell
mutation patterns. Every mode blocks a set of push, merge, release, deployment,
privilege, and destructive commands. These checks reduce accidental side
effects in trusted tasks; regex filtering is not a security sandbox.

## Prior art

Strong/weak-model routing and cascades motivate selective escalation, but they
do not prove this project's quality, cost, or safety:

- [FrugalGPT](https://arxiv.org/abs/2305.05176)
- [RouteLLM](https://arxiv.org/abs/2406.18665)
- [Uncertainty-Based Two-Tier Selection](https://arxiv.org/abs/2405.02134)

Relevant implementation surfaces are documented by
[Hermes Agent](https://github.com/NousResearch/hermes-agent) and
[Codex skills](https://developers.openai.com/codex/skills/). Version-specific
behavior must be checked against the installed runtime before changing the
adapter.
