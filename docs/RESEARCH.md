# Research basis

The project combines two ideas: model routing/cascading for efficiency, and explicit authority/safety boundaries for software-engineering agents.

## Model routing and cascades

- **FrugalGPT** (Chen, Zaharia, Zou, 2023) describes prompt adaptation, approximation, and LLM cascades as ways to reduce inference cost while preserving task quality. https://arxiv.org/abs/2305.05176
- **RouteLLM** (Ong et al., 2024) learns routers between stronger and weaker models from preference data and studies the cost/quality trade-off. https://arxiv.org/abs/2406.18665
- **Uncertainty-Based Two-Tier Selection** (Ramírez, Birch, Titov, 2024) studies small/large-model escalation using uncertainty as the decision signal. https://arxiv.org/abs/2405.02134
- **Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey** (Moslem, Kelleher, 2026) surveys routing dimensions such as difficulty, uncertainty, preference, and cascades. https://arxiv.org/abs/2603.04445

These works motivate selective use of expensive models. They do **not** validate this repository's specific routing heuristic or safety properties.

## Runtime surfaces used

Hermes Agent currently documents one-shot/query-file execution, per-run model/provider overrides, selective toolsets, max-turn bounds, JSON usage reports, Git worktrees, checkpoints, and plugin hooks including blocking `pre_tool_call`.

- CLI reference: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/cli-commands.md
- Toolsets: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/tools.md
- Plugins: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/plugins.md
- Hooks: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/hooks.md
- Worktrees: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/git-worktrees.md

OpenAI Codex documents user-scoped skills at `$HOME/.agents/skills`, progressive disclosure of skill bodies, and `agents/openai.yaml` invocation metadata.

- Codex skills: https://developers.openai.com/codex/skills/
- AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md/

## Existing adjacent projects

GitHub already contains projects that make Hermes orchestrate Codex or route Hermes through Codex. This project intentionally targets the opposite direction: **Codex remains authoritative and selectively offloads bounded work to Hermes/local inference.** The differentiation is authority-aware offload, read-only modes, an explicit guard hook, and usage accounting.
