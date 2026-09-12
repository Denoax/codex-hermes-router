---
name: iris-camera
description: Capture trustworthy rendered web UI evidence with Iris when actual pixels matter. Use for frontend/UI verification, responsive layouts, dark mode, selected components, or documentation screenshots. Iris is a camera, not a reviewer. Do not use when source/tests are sufficient.
---

# Iris Camera

Use Iris only when rendered visual state materially affects the task.

## Routing

Use for:
- frontend or UI changes
- responsive/mobile validation
- dark-mode validation
- CSS/layout regressions
- selected component inspection
- README/documentation screenshots

Do not use for:
- backend-only work
- source questions that do not depend on rendering
- final visual approval without Codex inspecting the pixels
- browser interaction/automation

## Capture policy

Prefer the Iris MCP `capture` tool when it is available.

For routine verification:
- capture the smallest relevant selector when possible
- use scale 1
- capture only the relevant viewport
- request dark/mobile variants only when the task requires them
- omit `output` so MCP returns pixels inline unless a persistent artifact is needed

Use full-page/high-scale capture only when page-level composition or a committed
documentation asset requires it.

## Evidence

A successful capture proves only that Iris rendered/captured the requested state.

Codex must inspect the returned pixels and decide whether the UI is correct.

If the UI was produced by a Hermes worker, Iris evidence returns to Codex; it does
not give the worker final visual authority.

## CLI fallback

If the MCP tool is unavailable, the `iris` CLI may be used for a targeted file capture.

Do not claim MCP success from a CLI-only smoke test.
