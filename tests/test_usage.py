from types import SimpleNamespace as NS

from helpdesk.usage import estimate_cost_eur, final_text, summarize


def _event(prompt, output):
    return NS(usage_metadata=NS(prompt_token_count=prompt, candidates_token_count=output))


def test_summarize_counts_only_events_with_usage():
    events = [_event(100, 20), NS(usage_metadata=None), _event(300, 50)]
    assert summarize(events) == {"model_calls": 2, "prompt_tokens": 400, "output_tokens": 70}


def test_estimate_cost():
    summary = {"model_calls": 1, "prompt_tokens": 1_000_000, "output_tokens": 500_000}
    assert estimate_cost_eur(summary, 0.30, 2.50) == 1.55


def _text_event(text, final=True):
    parts = [NS(text=t) for t in text] if isinstance(text, list) else [NS(text=text)]
    return NS(content=NS(parts=parts), is_final_response=lambda: final)


def test_final_text_joins_parts_of_last_final_response():
    events = [_text_event("First answer"), _text_event("thinking", final=False),
              _text_event(["Second ", "answer"]), _text_event("tool step", final=False)]
    assert final_text(events) == "Second answer"


def test_final_text_skips_parts_without_text_and_handles_no_answer():
    events = [NS(content=NS(parts=[NS(text=None), NS(text="Hi")]), is_final_response=lambda: True)]
    assert final_text(events) == "Hi"
    assert final_text([_text_event("tool step", final=False)]) == ""
    assert final_text([NS(content=None, is_final_response=lambda: True)]) == ""
