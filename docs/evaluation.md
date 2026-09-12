# Evaluation

## Deterministic validation

The repository's required checks are:

```bash
bash -n bin/hermes-worker install.sh uninstall.sh
shellcheck bin/hermes-worker install.sh uninstall.sh
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

The local v2 refinement gate recorded on 2026-09-12 passed shell syntax, all 28
deterministic tests, and the repository wrapper's fail-closed doctor command
against the installed Hermes runtime. The tests include disabled/invalid guard
states, committed-candidate retention, missing-usage failure accounting, and
incomplete-run stats. README link and SVG XML/render checks also passed. No
model call was made.

The local v3 refinement gate recorded on 2026-09-12 passed shell syntax, all 34
deterministic tests, the repository wrapper's full integration doctor, README
link checks, canonical-hero checksum verification, and SVG XML/render checks.
The local host did not have ShellCheck installed; CI installs it from Ubuntu's
package repository before linting. No model call was made.

The local v4 refinement gate recorded on 2026-09-12 passed shell syntax, all 44
deterministic tests, repository and installed-plugin doctors, the installed
wrapper's live integration doctor, installed-file reconciliation, README link
checks, and canonical-hero checksum verification. Optional Iris setup also
passed a deterministic local-file capture through both the CLI and MCP protocol.
The local host still did not have ShellCheck installed; CI installs it before
linting. No model call was made.

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
