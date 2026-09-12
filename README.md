# codex-hermes-router

**Authority-aware local inference offload for Codex.**

Deterministic tools first. Local inference for bounded, verifiable work. Premium reasoning only where it matters.

The escalation hierarchy is deterministic tools -> Hermes/local worker -> Codex -> human/higher-level architecture.

> Public preview (`v0.1.0`). The router is policy-based, not a learned classifier. No token/cost savings are claimed until the benchmark plan is executed.

```text
                              task
                               |
                     +---------+---------+
                     |                   |
              deterministic?            no
                     |                   |
                     v                   v
               scripts/tools     bounded + low-risk
                                      + verifiable?
                                   /             \
                                 yes              no
                                  |                |
                                  v                v
                            Hermes/local        Codex
                           evidence worker   authoritative
                          /   |    |    \     engineering
                      scout research review prototype
                                           |
                                      isolated worktree
```

`codex-hermes-router` is a thin orchestration layer for developers who already use Codex and have Hermes Agent connected to a local or inexpensive model. Codex remains the authoritative engineer. Hermes absorbs bounded scouting, research, review, log triage, inventory, and speculative prototype work when the result is cheap to verify.

## Why

Strong/weak-model routing and LLM cascades are a well-studied way to trade inference cost against quality. FrugalGPT, RouteLLM, uncertainty-based two-tier selection, and later routing surveys all motivate selective escalation rather than spending the strongest model on every subtask. This project applies that idea to coding-agent workflows while adding two constraints that generic model routers usually do not model directly: **side-effect risk** and **engineering authority**.

The rule is deliberately conservative:

```text
Can deterministic code answer it?
  yes -> script/tool
  no  -> can a weaker local model do it, and can Codex cheaply verify it?
           yes -> Hermes
           no  -> Codex

Architecture, security-sensitive judgment, irreversible actions, and final correctness stay authoritative.
```

See [`docs/RESEARCH.md`](docs/RESEARCH.md) and [`docs/ROUTING_POLICY.md`](docs/ROUTING_POLICY.md).

## What ships

| Component | Role |
|---|---|
| `skills/local-worker/` | Global Codex skill that decides when local offload is appropriate |
| `bin/hermes-worker` | Bounded adapter around Hermes one-shot execution |
| `codex-worker-guard` | Hermes `pre_tool_call` hook for read-only and remote/destructive guardrails |
| `tests/test_guard.py` | Deterministic guard tests; no model calls |
| `docs/` | architecture, threat model, routing rationale, research, benchmark plan |

The worker uses the existing Hermes provider/model configuration; it does not duplicate API keys or credentials.

## Worker modes

| Mode | Tool surface | Writes | Use |
|---|---|---:|---|
| `scout` | file + terminal | blocked | repository/source/history mapping |
| `research` | web + file + terminal | blocked | external/local evidence gathering |
| `review` | web + file + terminal | blocked | first-pass diff/log/test review |
| `prototype` | file + terminal + web | isolated worktree | speculative implementation |

Every run receives a bounded turn budget, a compact output contract, `source=tool` tagging, and a JSON usage report.

## Install

Requirements:

- Linux/macOS/WSL-style shell environment
- `python3`
- Hermes Agent installed and configured
- Codex with user-skill discovery at `$HOME/.agents/skills`

```bash
git clone https://github.com/Denoax/codex-hermes-router.git
cd codex-hermes-router

./install.sh --dry-run
./install.sh

hermes plugins enable codex-worker-guard
# If Hermes asks for built-in tool override permission, answer NO.

hermes-worker doctor
```

Install locations:

```text
~/.local/bin/hermes-worker
~/.agents/skills/local-worker/
~/.hermes/plugins/codex-worker-guard/
```

Then add the rule in [`examples/codex-personalization.txt`](examples/codex-personalization.txt) to Codex Personalization. Codex should expose `$local-worker` in `/skills`.

## Use directly

Prefer stdin or task files so task text is not shell-interpreted:

```bash
printf '%s\n' 'Map the parser subsystem and relevant tests.' \
  | hermes-worker scout --repo "$PWD"

printf '%s\n' 'Collect authoritative evidence for this external API behavior.' \
  | hermes-worker research --repo "$PWD"

printf '%s\n' 'Review the current diff for correctness regressions.' \
  | hermes-worker review --repo "$PWD"

printf '%s\n' 'Prototype the smallest fix for issue #123.' \
  | hermes-worker prototype --repo "$PWD"
```

Or let Codex invoke `$local-worker` when its routing policy matches the task.

## Safety model

The guard is inactive during normal Hermes use and activates only when the wrapper sets `HERMES_CODEX_WORKER=1`. In read-only modes it blocks Hermes file-write tools plus common mutating shell commands. In every worker mode it blocks known push/merge/release/deploy/destructive operations. Prototype mode uses Hermes' Git worktree isolation and checkpoints.

This is **not a sandbox**. Hermes plugins run with the user's normal OS permissions, and command-pattern blocking cannot prove non-mutation against arbitrary indirect shell behavior. Use an actual OS/container/VM sandbox for hostile repositories or untrusted tasks. See [`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md).

## Deterministic validation

No model call is required to validate the guard:

```bash
bash -n bin/hermes-worker install.sh uninstall.sh
python -m unittest discover -s tests -v
```

The initial implementation was also exercised against a live Hermes installation with these control results:

```text
safe read command  -> allowed
read-only file write -> blocked
remote git push      -> blocked
```

These checks validate specific guard behavior, not complete sandbox security.

See [`docs/VALIDATION.md`](docs/VALIDATION.md) for the sanitized deterministic evidence recorded for `v0.1.0`.

## Usage accounting

Hermes one-shot runs write usage JSON into the local worker state directory. Aggregate it without an LLM call:

```bash
hermes-worker stats
```

By default state is stored under:

```text
${XDG_STATE_HOME:-$HOME/.local/state}/hermes-worker/
```

## Research and measurement

This project intentionally separates **motivation** from **measured claims**. Routing literature supports the general strong/weak-model and cascade idea; it does not prove this implementation saves tokens or preserves quality.

The reproducible evaluation design is in [`docs/BENCHMARK_PLAN.md`](docs/BENCHMARK_PLAN.md). Until those experiments are run, the README does not publish a percentage savings claim.

## Adjacent work

There are existing Hermes/Codex projects that make Hermes call or orchestrate Codex. `codex-hermes-router` focuses on the inverse relationship: **Codex is authoritative and selectively delegates low-authority work to Hermes/local inference**.

## Project status

`v0.1.0` is a small, inspectable prototype. The next meaningful work is empirical, not cosmetic:

1. run Codex-only vs routed benchmarks on representative engineering tasks;
2. measure false-offload and correction rates;
3. improve routing signals only where data shows a real failure mode;
4. consider a learned/uncertainty-aware router only after a useful labeled task set exists.

## References

- Chen, Zaharia, Zou — *FrugalGPT* (2023): https://arxiv.org/abs/2305.05176
- Ong et al. — *RouteLLM* (2024): https://arxiv.org/abs/2406.18665
- Ramírez, Birch, Titov — *Uncertainty-Based Two-Tier Selection* (2024): https://arxiv.org/abs/2405.02134
- Moslem, Kelleher — *Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey* (2026): https://arxiv.org/abs/2603.04445
- Hermes Agent: https://github.com/NousResearch/hermes-agent
- OpenAI Codex skills: https://developers.openai.com/codex/skills/

## License

MIT. See [`LICENSE`](LICENSE).

This is an independent project and is not affiliated with OpenAI or Nous Research. See [`NOTICE.md`](NOTICE.md).
