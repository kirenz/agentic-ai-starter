"""Summarise token usage from ADK events and estimate cost."""


def summarize(events) -> dict[str, int]:
    with_usage = [e.usage_metadata for e in events if getattr(e, "usage_metadata", None)]
    return {
        "model_calls": len(with_usage),
        "prompt_tokens": sum(u.prompt_token_count or 0 for u in with_usage),
        "output_tokens": sum(u.candidates_token_count or 0 for u in with_usage),
    }


def estimate_cost_eur(summary: dict, eur_per_million_input: float, eur_per_million_output: float) -> float:
    """Prices come from the current Gemini pricing page; pass them in explicitly."""
    cost = (
        summary["prompt_tokens"] / 1_000_000 * eur_per_million_input
        + summary["output_tokens"] / 1_000_000 * eur_per_million_output
    )
    return round(cost, 4)
