from types import SimpleNamespace as NS

from helpdesk.usage import estimate_cost_eur, summarize


def _event(prompt, output):
    return NS(usage_metadata=NS(prompt_token_count=prompt, candidates_token_count=output))


def test_summarize_counts_only_events_with_usage():
    events = [_event(100, 20), NS(usage_metadata=None), _event(300, 50)]
    assert summarize(events) == {"model_calls": 2, "prompt_tokens": 400, "output_tokens": 70}


def test_estimate_cost():
    summary = {"model_calls": 1, "prompt_tokens": 1_000_000, "output_tokens": 500_000}
    assert estimate_cost_eur(summary, 0.30, 2.50) == 1.55
