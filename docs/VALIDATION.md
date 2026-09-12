# Validation

Sanitized deterministic evidence for the `v0.1.0` publication candidate, recorded on 2026-09-12. No LLM or synthetic benchmark task was run.

## Repository checks

| Check | Result |
|---|---|
| `bash -n bin/hermes-worker install.sh uninstall.sh` | PASS |
| `python -m unittest discover -s tests -v` | PASS — 6 tests |
| README local-link target check | PASS — 8 targets resolved |
| sensitive-data pattern scan | PASS — no secrets, credentials, tokens, private keys, or machine-specific private paths detected |

## Installed-runtime checks

The validated installed runtime was inspected read-only. Because the validation shell did not inherit the user-local binary directory, that directory was temporarily prepended to `PATH`; no installed files or configuration were changed.

| Check | Result |
|---|---|
| `hermes-worker doctor` | PASS — Hermes discovered; wrapper, guard plugin, and Codex skill present; no LLM call |
| `hermes plugins doctor ~/.hermes/plugins/codex-worker-guard --ci` | PASS — manifest parsing, runtime discovery, import, and one hook registration |
| `hermes plugins capabilities codex-worker-guard` | PASS — no capabilities declared; `tools.override` not granted or required |

Validated environment: Hermes Agent `v0.21.0`, Python `3.11.16`, OpenAI SDK `2.24.0`. These versions record the tested environment; they are not asserted as the only supported versions.

## Reconciliation against installed files

- `skills/local-worker/` matches the installed validated skill byte-for-byte.
- The guard implementation matches byte-for-byte. Its repository manifest uses the public release version `0.1.0`; the installed pre-publication runtime carries an internal `1.0.0` label.
- The wrapper carries forward the installed tool surfaces and guard discovery fix. Its repository version is `0.1.0` for the first public release.
- The repository adds a deterministic doctor diagnostic for unnecessary `tools.override` grants. It passed against the installed runtime and reported that the override was not granted.

No token or cost savings are claimed. The benchmark plan remains unexecuted.
