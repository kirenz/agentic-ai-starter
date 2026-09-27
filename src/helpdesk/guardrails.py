"""Guardrails for the Nimbus Support Assistant."""

import re

from google.adk.models import LlmResponse
from google.adk.plugins import BasePlugin
from google.genai import types

_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"(reveal|show|print) (your )?(system prompt|instructions)",
    r"developer mode",
    r"you are now",
]

REFUND_LIMIT_EUR = 100.0


def looks_like_injection(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(p, lowered) for p in _INJECTION_PATTERNS)


def _last_user_text(llm_request) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user":
            return " ".join(p.text for p in content.parts or [] if p.text)
    return ""


class InjectionScreenPlugin(BasePlugin):
    """Runs before every model call of every agent in the app."""

    def __init__(self) -> None:
        super().__init__(name="injection_screen")

    async def before_model_callback(self, *, callback_context, llm_request) -> LlmResponse | None:
        if looks_like_injection(_last_user_text(llm_request)):
            return LlmResponse(content=types.Content(role="model", parts=[types.Part(
                text="Sorry, I can't help with that request. I can help with Nimbus products, orders and refunds.")]))
        return None


def refund_policy(tool, args: dict, tool_context) -> dict | None:
    """before_tool_callback: stop refunds above the limit before the tool runs."""
    if tool.name == "issue_refund" and float(args.get("amount_eur", 0)) > REFUND_LIMIT_EUR:
        return {"status": "blocked", "reason": f"Refunds above {REFUND_LIMIT_EUR:.0f} EUR need a supervisor. Create a ticket instead."}
    return None
