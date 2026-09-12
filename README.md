# codex-hermes-router

<img src="./showcase/assets/codex-x-hermes.png"
     alt="Codex x Hermes"
     width="100%">

Delegate bounded work to Hermes while Codex keeps final authority.

`codex-hermes-router` is a small, model-agnostic delegation layer. Codex uses
deterministic tools first, sends suitable work to a FAST or STRONG Hermes
worker, then verifies the evidence or candidate before acting on it.

![Authority-aware delegation route](showcase/assets/route.svg)

## The idea

```text
deterministic tools → FAST or STRONG worker → Codex verification → action
```

The worker handles bounded scouting, research, review, or prototyping. Codex
keeps architecture, security-sensitive judgment, Git integration, remote
actions, and final correctness. The design goal is to save authoritative-model
tokens where verification is cheaper than doing the whole task there. No
quantitative token, cost, latency, or quality savings are claimed yet.

Two independent controls keep routing explicit:

| Control | Meaning | Choices |
|---|---|---|
| Mode | authority and available tools | `scout`, `research`, `review`, `prototype` |
| Tier | worker capability | `inherit`, `fast`, `strong` |

There is no learned router, scoring service, or automatic FAST-to-STRONG
cascade. Codex chooses one path from the task and verifies what comes back.

## Quick start

Requirements: a Linux/macOS/WSL-style shell, Python 3, Git, Hermes Agent, and
Codex with user-skill discovery at `$HOME/.agents/skills`. Hermes Agent 0.21.x
is the currently tested line.

```bash
git clone https://github.com/Denoax/codex-hermes-router.git
cd codex-hermes-router
./install.sh --dry-run
./install.sh
hermes plugins enable codex-worker-guard
hermes-worker doctor
```

The installer refuses to overwrite an existing installation. It installs the
wrapper, the Codex skills, and the inert-by-default Hermes guard; it does not
install models, provider credentials, Iris, or a browser.

Configure generic FAST and STRONG targets in
`$HOME/.config/hermes-worker/models.json`:

```json
{
  "fast": {"provider": "YOUR_FAST_PROVIDER", "model": "YOUR_FAST_MODEL"},
  "strong": {"provider": "YOUR_STRONG_PROVIDER", "model": "YOUR_STRONG_MODEL"}
}
```

Protect the file and authenticate each provider through Hermes' normal
credential flow:

```bash
chmod 600 "$HOME/.config/hermes-worker/models.json"
```

`hermes-worker doctor` is deterministic and makes no model call. It verifies
Python, Git, the installed skill and guard, hook activation, least privilege,
and Hermes rule isolation.

## Use it

Ask Codex to route a bounded task:

```text
Use $local-worker with the fast tier to map the parser subsystem and relevant tests.
```

Or invoke the wrapper directly:

```bash
printf '%s\n' 'Map the parser subsystem and relevant tests.' \
  | hermes-worker scout --tier fast --repo "$PWD"

printf '%s\n' 'Review this change for cross-file inconsistencies.' \
  | hermes-worker review --tier strong --repo "$PWD"
```

Prefer stdin or `--task-file` so the shell does not interpret task text. Direct
execution checks worker safety prerequisites; `doctor` additionally checks the
complete Codex integration. Results and metadata are written below
`${XDG_STATE_HOME:-$HOME/.local/state}/hermes-worker/`.

## Modes

| Mode | Worker access | Use |
|---|---|---|
| `scout` | files + terminal, mutation-guarded | map repositories, source, and history |
| `research` | web, mutation-guarded | gather external evidence |
| `review` | files + terminal, mutation-guarded | first-pass review of diffs, logs, and tests |
| `prototype` | files + terminal in an exact-HEAD worktree; Git reads only | produce a speculative candidate |

All modes have bounded turn counts. Prototype mode requires a clean repository,
creates a detached worktree at the exact local `HEAD`, and leaves committed or
uncommitted candidates for Codex to inspect. Hermes may edit the candidate;
Codex owns staging, commits, refs, and integration.

## Worker tiers

| Tier | Behavior | Intended use |
|---|---|---|
| `inherit` | keep Hermes' current provider/model selection | direct-wrapper compatibility; the default |
| `fast` | load the configured FAST provider/model pair | work that is cheap to verify or redo |
| `strong` | load the configured STRONG provider/model pair | work where a better first pass materially matters |

Named tiers fail closed when their configuration is missing or invalid. They do
not silently fall back. Provider credentials stay in Hermes' credential store,
not in the tier file or run metadata. Codex may retry an inadequate FAST result
once with STRONG, but the wrapper never runs both automatically.

## Optional Iris camera

Iris is optional. It captures rendered pixels for Codex to inspect after web or
UI work; it is not a worker, browser-automation layer, or visual reviewer. Normal
Hermes routing does not depend on it.

1. Install [Iris](https://github.com/brijr/iris) and a supported Chrome-family
   browser using the upstream instructions. Ensure `iris` is on `PATH`.
2. The project installer already places
   [`$iris-camera`](skills/iris-camera/SKILL.md) in Codex's skill directory.
3. Check for an existing registration, then add Iris only if absent:

   ```bash
   codex mcp get iris
   codex mcp add iris -- iris mcp
   ```

4. Restart the Codex extension or session if the `capture` tool is not yet
   visible. Capture a small deterministic page or selector and have Codex
   inspect the returned pixels. CLI success alone does not prove in-session MCP
   success.

## Safety model

The Hermes hook and wrapper are defense-in-depth for trusted development tasks,
not an OS sandbox. They disable direct write tools in guarded modes and block
common mutation, destructive, and remote-action commands, but command-pattern
filtering cannot contain an adversarial worker or every indirect side effect.

Before a run, the wrapper fails closed unless the guard is enabled, its hook
passes Hermes validation, no unnecessary tool-override permission is granted,
and required isolation capabilities are present. Delegated sessions ignore
ambient Hermes rules, memory, and preloaded skills. Remote pushes, merges,
releases, deployments, credentials, production mutations, and final security
judgment remain outside worker authority.

Run records can contain task text, repository paths, results, and diagnostics;
retention is manual. See [SECURITY.md](SECURITY.md) and
[design](docs/design.md) for the exact boundary and prototype lifecycle.

## Development

Deterministic checks do not invoke a model:

```bash
bash -n bin/hermes-worker install.sh uninstall.sh
shellcheck bin/hermes-worker install.sh uninstall.sh
python -m unittest discover -s tests -v
```

CI runs the same checks.

## Evaluation

The current evidence covers deterministic behavior and runtime integration, not
comparative performance. See [evaluation](docs/evaluation.md) for the validation
record and benchmark plan. No quantitative token, cost, latency, or quality
savings are claimed.

## License

MIT. This independent integration project is not affiliated with, endorsed by,
or maintained by OpenAI or Nous Research. It does not redistribute Codex,
Hermes Agent, Iris, or provider models.
