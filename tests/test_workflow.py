import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import ValidationError

from agents.m05_workflow_solution.agent import Triage, build_workflow
from helpdesk import tools


def fake_classifier(category: str, order_id: str | None = None, request: str = "Customer request"):
    def classify(node_input: str):
        return Triage(category=category, order_id=order_id, request=request)

    return classify


def _outputs(events):
    return [e.output for e in events if getattr(e, "output", None) is not None]


def _calls(events):
    return [p.function_call for e in events if e.content for p in e.content.parts if p.function_call]


def _reply(call, answer: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
        id=call.id, name=call.name, response={"result": answer}))])


async def test_refund_route_pauses_for_approval_and_refunds_on_yes():
    tools.reset_state()
    runner = InMemoryRunner(node=build_workflow(fake_classifier("REFUND", "NH-1001")), app_name="wf")
    events = await runner.run_debug("I returned my hub, refund please", quiet=True)
    calls = _calls(events)
    assert calls and calls[0].name == "adk_request_input"

    resumed = [e async for e in runner.run_async(
        user_id="debug_user_id", session_id="debug_session_id", new_message=_reply(calls[0], "yes"))]
    assert any("refunded" in str(o) for o in _outputs(resumed))


async def test_refund_route_rejects_on_no():
    tools.reset_state()
    runner = InMemoryRunner(node=build_workflow(fake_classifier("REFUND", "NH-1001")), app_name="wf")
    events = await runner.run_debug("refund please", quiet=True)
    call = next(c for c in _calls(events) if c.name == "adk_request_input")
    resumed = [e async for e in runner.run_async(
        user_id="debug_user_id", session_id="debug_session_id", new_message=_reply(call, "no"))]
    outputs = [str(o) for o in _outputs(resumed)]
    assert any("not approved" in o for o in outputs)
    assert not any("refunded" in o for o in outputs)


async def test_refund_without_valid_order_asks_for_order_number_only():
    runner = InMemoryRunner(node=build_workflow(fake_classifier("REFUND", None)), app_name="wf")
    events = await runner.run_debug("I want my money back", quiet=True)
    texts = [str(o) for o in _outputs(events) if isinstance(o, str)]
    assert texts == ["Please provide your order number (e.g. NH-1001)."]
    assert not any(c.name == "adk_request_input" for c in _calls(events))
    assert not any("not approved" in str(o) for o in _outputs(events))


async def test_order_status_route_answers_without_approval():
    runner = InMemoryRunner(node=build_workflow(fake_classifier("ORDER_STATUS", "NH-1002")), app_name="wf")
    events = await runner.run_debug("Where is my order NH-1002?", quiet=True)
    assert not any(c.name == "adk_request_input" for c in _calls(events))
    texts = [str(o) for o in _outputs(events)]
    assert any("NH-1002" in t and "shipped" in t for t in texts)
    assert not any("refund" in t.lower() for t in texts)


async def test_order_status_mentions_days_since_delivery():
    runner = InMemoryRunner(node=build_workflow(fake_classifier("ORDER_STATUS", "NH-1001")), app_name="wf")
    events = await runner.run_debug("Has NH-1001 arrived?", quiet=True)
    assert any("delivered" in str(o) and "17 days ago" in str(o) for o in _outputs(events))


async def test_order_status_without_valid_order_asks_for_order_number():
    runner = InMemoryRunner(node=build_workflow(fake_classifier("ORDER_STATUS", "NH-9999")), app_name="wf")
    events = await runner.run_debug("Where is my order NH-9999?", quiet=True)
    texts = [str(o) for o in _outputs(events) if isinstance(o, str)]
    assert texts == ["Please provide your order number (e.g. NH-1001)."]


async def test_other_route_answers_directly():
    runner = InMemoryRunner(node=build_workflow(fake_classifier("OTHER")), app_name="wf")
    events = await runner.run_debug("Do you sell coffee?", quiet=True)
    assert any("outside Nimbus support" in str(o) for o in _outputs(events))
    assert not _calls(events)


def test_triage_rejects_unknown_category():
    with pytest.raises(ValidationError):
        Triage(category="Billing", request="refund please")
