# Routing policy

The v0.1 router is deliberately heuristic and authority-aware. It does not claim to predict model quality with a learned classifier.

For a task `t`, reason about five properties:

- **Determinism D(t):** can normal code/tools answer it exactly?
- **Verifiability V(t):** can a stronger agent cheaply check the result?
- **Side-effect risk S(t):** can failure mutate important local/remote state?
- **Reasoning difficulty C(t):** how much genuine synthesis/debugging is required?
- **Authority A(t):** must the result itself be trusted as the final engineering decision?

Conceptually:

```text
D high                         -> deterministic tool/script
D low, V high, S low, A low   -> Hermes local worker
A high or C high               -> Codex
high-impact architecture       -> human / higher-level reasoning
```

This is related to strong/weak-model routing and cascades in the LLM-routing literature, but adds explicit software-engineering authority and side-effect constraints. The current implementation is policy-based; learned routing is future work.

## Modes

| Mode | Writes | Network research | Intended use | Authority |
|---|---:|---:|---|---|
| `scout` | no | no | repo/source/history mapping | evidence only |
| `research` | no | yes | external + local evidence gathering | evidence only |
| `review` | no | yes | first-pass diff/log/test review | evidence only |
| `prototype` | isolated worktree | yes | speculative implementation | candidate only |

## Non-goals

- replacing Codex with a local model
- autonomously publishing or deploying code
- claiming the local model is correct because it is cheaper
- hiding uncertainty from the authoritative agent
- learned routing in v0.1
