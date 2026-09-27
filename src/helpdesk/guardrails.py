"""Guardrails for the Nimbus Support Assistant.

Keyword screening is a first line of defence, not a complete one: it is easy
to bypass with rephrasing, typos or other languages. It also checks only the
user's messages, not tool results, so instructions hidden in a manual page or
a web search result (indirect prompt injection) pass unnoticed.
"""

import re

from google.adk.models import LlmResponse
from google.adk.plugins import BasePlugin
from google.genai import types

_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"(reveal|show|print) (your )?(system prompt|instructions)",
    r"developer mode",
    r"you are now (a|an|in) ",
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
    """Runs before every model call of every agent in the app.

    Screens only the last user message with keywords (see the module docstring
    for what this does not catch).
    """

    def __init__(self) -> None:
        super().__init__(name="injection_screen")

    async def before_model_callback(self, *, callback_context, llm_request) -> LlmResponse | None:
        if looks_like_injection(_last_user_text(llm_request)):
            return LlmResponse(content=types.Content(role="model", parts=[types.Part(
                text="Sorry, I can't help with that request. I can help with Nimbus products, orders and refunds.")]))
        return None


def refund_policy(tool, args: dict, tool_context) -> dict | None:
    """before_tool_callback: stop refunds above the limit before the tool runs."""
    if tool.name != "issue_refund":
        return None
    try:
        amount = float(args.get("amount_eur", 0))
    except (TypeError, ValueError):
        return {"status": "blocked", "reason": "The refund amount must be a number."}
    if amount > REFUND_LIMIT_EUR:
        return {"status": "blocked", "reason": f"Refunds above {REFUND_LIMIT_EUR:.0f} EUR need a supervisor. Create a ticket instead."}
    return None
