"""Hermes guardrails for Codex-delegated local worker runs.

Inert for normal Hermes sessions. Activates only when HERMES_CODEX_WORKER=1.
"""
from __future__ import annotations
import os
import re
from typing import Any

REMOTE_OR_DESTRUCTIVE = [
    r"\bgit\s+push\b", r"\bgit\s+merge\b", r"\bgit\s+rebase\b", r"\bgit\s+clean\b",
    r"\bgit\s+reset\b", r"\bgit\s+stash\b", r"\bgit\s+tag\b",
    r"\bgh\s+pr\s+merge\b", r"\bgh\s+release\b", r"\bgh\s+repo\s+(delete|archive|rename)\b",
    r"\bnpm\s+publish\b", r"\bpnpm\s+publish\b", r"\byarn\s+npm\s+publish\b",
    r"\bcargo\s+publish\b", r"\btwine\s+upload\b", r"\bdocker\s+push\b", r"\bpodman\s+push\b",
    r"\bkubectl\s+(apply|delete|patch|replace|rollout)\b", r"\bhelm\s+(install|upgrade|uninstall)\b",
    r"\bterraform\s+(apply|destroy)\b", r"\bvercel(\s+deploy)?\b", r"\bnetlify\s+deploy\b",
    r"\bfirebase\s+deploy\b", r"\bwrangler\s+(deploy|publish)\b", r"\bsudo\b", r"\bsu\s+-?\b",
    r"\bsystemctl\b",
]

READONLY_MUTATION = [
    r"(^|[;&|]\s*)rm\b", r"(^|[;&|]\s*)mv\b", r"(^|[;&|]\s*)cp\b", r"(^|[;&|]\s*)mkdir\b",
    r"(^|[;&|]\s*)touch\b", r"(^|[;&|]\s*)truncate\b", r"(^|[;&|]\s*)chmod\b", r"(^|[;&|]\s*)chown\b",
    r"(^|[;&|]\s*)ln\b", r"\bsed\s+-i\b", r"\btee\b",
    r"\bgit\s+(add|commit|restore|checkout|switch|cherry-pick|revert)\b",
    r"\b(pip|pip3|uv)\s+install\b", r"\b(npm|pnpm|yarn)\s+(install|add|remove|update)\b",
    r"\bcargo\s+(add|remove|update)\b", r"\b(go\s+get|go\s+mod\s+tidy)\b",
]

WRITE_REDIRECTION = re.compile(r"(^|[^<])>{1,2}\s*[^&]", re.M)

def _block(message: str) -> dict[str, str]:
    return {"action": "block", "message": message}

def _command_from_args(args: dict[str, Any]) -> str:
    for key in ("command", "cmd", "script"):
        value = args.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join(str(x) for x in value)
    return ""

def pre_tool_call(tool_name: str, args: dict, task_id: str = "", **kwargs):
    del task_id, kwargs
    if os.getenv("HERMES_CODEX_WORKER") != "1":
        return None

    mode = os.getenv("HERMES_WORKER_MODE", "")
    readonly = os.getenv("HERMES_WORKER_READONLY", "0") == "1"

    if readonly and tool_name in {"write_file", "patch"}:
        return _block(f"Codex worker mode '{mode}' is mutation-guarded; {tool_name} is disabled.")

    if tool_name != "terminal":
        return None

    cmd = _command_from_args(args)
    if not cmd:
        return None
    lowered = cmd.lower()

    for pattern in REMOTE_OR_DESTRUCTIVE:
        if re.search(pattern, lowered, flags=re.I):
            return _block("Blocked by codex-worker-guard: remote/destructive command is outside Hermes worker authority.")

    if re.search(r"\brm\s+(-[a-z]*r[a-z]*f[a-z]*|-[a-z]*f[a-z]*r[a-z]*)\s+(/|~|\$home)(\s|$)", lowered, re.I):
        return _block("Blocked by codex-worker-guard: destructive removal of root/home is forbidden.")

    if readonly:
        for pattern in READONLY_MUTATION:
            if re.search(pattern, lowered, flags=re.I):
                return _block(f"Codex worker mode '{mode}' is mutation-guarded; mutating terminal command blocked.")
        if WRITE_REDIRECTION.search(cmd):
            return _block(f"Codex worker mode '{mode}' is mutation-guarded; shell output redirection that may write files is blocked.")

    return None

def register(ctx):
    ctx.register_hook("pre_tool_call", pre_tool_call)
