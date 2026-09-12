# Repository instructions

- Preserve the project's central contract: deterministic tools first, bounded Hermes delegation second, authoritative reasoning only where needed.
- Treat `bin/hermes-worker`, `skills/local-worker/`, and `integrations/hermes/codex-worker-guard/` as the implementation surface.
- Keep routing, safety, and README claims synchronized with actual behavior.
- Do not claim a security boundary stronger than the code provides; the hook guard is defense-in-depth, not a sandbox.
- Do not publish benchmark savings without reproducible measurements.
- Tests in `tests/` must remain deterministic and must not invoke an LLM or remote mutation.
- Prefer small, reversible changes. Avoid unrelated framework or dependency additions.
- Never push, release, deploy, or mutate remote state without explicit user authorization.
