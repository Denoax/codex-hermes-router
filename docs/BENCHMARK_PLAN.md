# Benchmark plan

No cost or quality savings are claimed in v0.1. The repository needs measured evidence before publishing numbers.

## Question

Does local offload reduce authoritative-model token use without materially reducing task success or increasing correction work?

## Comparison

- **A — Codex-only:** complete each task without the local worker.
- **B — Routed:** deterministic tools first; Hermes for eligible bounded subtasks; Codex verifies and completes.

Use identical repositories, starting SHAs, tasks, model settings, and validation criteria. Randomize condition order when practical.

## Task strata

1. repository scouting
2. prior-art / artifact inventory
3. external technical research
4. log/test failure clustering
5. first-pass diff review
6. speculative implementation candidates

Do not route intentionally high-authority architecture/security tasks merely to inflate offload rates.

## Record

- Codex input/output/reasoning tokens where available
- Hermes/local tokens and API calls from `--usage-file`
- wall-clock duration
- task success under the same acceptance criteria
- number of Codex corrections to worker output
- worker findings accepted/rejected
- human intervention
- safety-policy blocks
- failures/abandoned runs

## Report

Report medians, tail behavior, success rate, and all adverse runs. Do not report only best cases. Any claim about savings must name the model pair, hardware/provider, task set, and measurement date.
