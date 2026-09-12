# Evaluation

## Deterministic validation

The repository's required checks are:

```bash
bash -n bin/hermes-worker install.sh uninstall.sh
python -m unittest discover -s tests -v
```

The tests use a fake Hermes executable and make no model calls. They cover guard
activation and command blocking plus worker mode routing, least-capability
toolsets, dirty prototype refusal, exact prototype base selection, worktree
retention/cleanup, metadata creation, Hermes exit propagation, and missing
dependency failure.

Documentation validation also checks local links, SVG XML parsing, stale paths,
overstrong security/provider claims, unmeasured savings claims, and accidental
credentials or machine-specific paths.

The local refinement gate recorded on 2026-09-12 passed shell syntax, all 13
deterministic tests, the repository wrapper's doctor command against the
installed Hermes runtime, README link checks, and SVG XML/render checks. No
model call was made.

## Benchmark plan

No cost, token, latency, or quality savings are claimed. A future evaluation
should compare Codex-only and delegated runs from identical repository SHAs,
tasks, model settings, and acceptance criteria.

Representative task groups should include repository scouting, artifact
inventory, external technical research, failure clustering, first-pass review,
and bounded prototype candidates. High-authority architecture or security tasks
must not be delegated merely to increase offload rates.

Record authoritative and worker token usage where available, wall time, task
success, worker findings accepted or rejected, verification and correction
work, human intervention, guard blocks, and every failed or abandoned run.
Report distributions and adverse results, not only best cases. Any eventual
claim must name the model pair, provider/hardware, task set, acceptance criteria,
and measurement date.
