import importlib

import pytest
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

CASES = [
    ("agents.m00_first_agent", "What is the Nimbus Home Hub?", None),
    ("agents.m02_core_solution", "Hello!", None),
    ("agents.m03_tools_solution", "Where is my order NH-1002?", "get_order_status"),
    ("agents.m03_mcp_solution", "My automation never runs, even though all devices are online. Please open a ticket.", "create_ticket"),
    ("agents.m04_context_solution", "How do I install a firmware update right now?", "search_manual"),
    ("agents.m06_multiagent_solution", "Where is my order NH-1002?", "get_order_status"),
    ("agents.m07_guardrails_solution", "How many automations does the hub support?", "search_manual"),
]


def _runner(package: str) -> InMemoryRunner:
    module = importlib.import_module(f"{package}.agent")
    app = getattr(module, "app", None)
    if isinstance(app, App):
        return InMemoryRunner(app=app)
    return InMemoryRunner(agent=module.root_agent, app_name=package.split(".")[-1])


@pytest.mark.live
@pytest.mark.parametrize("package,prompt,expected_tool", CASES)
async def test_agent_answers(package, prompt, expected_tool):
    events = await _runner(package).run_debug(prompt, quiet=True)
    final = [e for e in events if e.is_final_response() and e.content and e.content.parts]
    assert final, "agent produced no final answer"
    if expected_tool:
        called = {p.function_call.name for e in events if e.content for p in e.content.parts if p.function_call}
        assert expected_tool in called


def _calls(events):
    return [p.function_call.name for e in events if e.content for p in e.content.parts if p.function_call]


@pytest.mark.live
async def test_workflow_refund_pauses_for_approval():
    from agents.m05_workflow_solution.agent import root_agent

    runner = InMemoryRunner(node=root_agent, app_name="m05_workflow_solution")
    events = await runner.run_debug("My order NH-1001 arrived broken, I want my money back", quiet=True)
    assert "adk_request_input" in _calls(events)


@pytest.mark.live
async def test_workflow_order_status_answers_without_approval():
    from agents.m05_workflow_solution.agent import root_agent

    runner = InMemoryRunner(node=root_agent, app_name="m05_workflow_solution")
    events = await runner.run_debug("Where is my order NH-1002?", quiet=True)
    assert "adk_request_input" not in _calls(events)
    assert any("shipped" in str(e.output) for e in events if getattr(e, "output", None) is not None)
