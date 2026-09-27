from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.m05_workflow_solution.agent import Triage, build_workflow
from helpdesk import tools


def fake_classifier(category: str, order_id: str | None = None):
    def classify(node_input: str):
        return Triage(category=category, order_id=order_id)

    return classify


def _outputs(events):
    return [e.output for e in events if getattr(e, "output", None) is not None]


async def test_billing_route_pauses_for_approval_and_refunds_on_yes():
    tools.reset_state()
    runner = InMemoryRunner(node=build_workflow(fake_classifier("BILLING", "NH-1001")), app_name="wf")
    events = await runner.run_debug("I returned my hub, refund please", quiet=True)
    calls = [p.function_call for e in events if e.content for p in e.content.parts if p.function_call]
    assert calls and calls[0].name == "adk_request_input"

    reply = types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
        id=calls[0].id, name=calls[0].name, response={"result": "yes"}))])
    resumed = [e async for e in runner.run_async(user_id="debug_user_id", session_id="debug_session_id", new_message=reply)]
    assert any("refunded" in str(o) for o in _outputs(resumed))


async def test_billing_route_rejects_on_no():
    runner = InMemoryRunner(node=build_workflow(fake_classifier("BILLING", "NH-1001")), app_name="wf")
    events = await runner.run_debug("refund please", quiet=True)
    call = next(p.function_call for e in events if e.content for p in e.content.parts if p.function_call)
    reply = types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
        id=call.id, name=call.name, response={"result": "no"}))])
    resumed = [e async for e in runner.run_async(user_id="debug_user_id", session_id="debug_session_id", new_message=reply)]
    assert any("not approved" in str(o) for o in _outputs(resumed))
