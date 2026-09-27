import importlib

import pytest
from google.adk.apps import App

AGENT_PACKAGES = [
    "agents.m00_first_agent",
    "agents.m02_core_solution",
    "agents.m03_tools_solution",
    "agents.m03_mcp_solution",
    "agents.m04_context_solution",
    "agents.m05_workflow_solution",
    "agents.m06_multiagent_solution",
    "agents.m06_a2a_client_solution",
    "agents.m07_guardrails_solution",
]


@pytest.mark.parametrize("package", AGENT_PACKAGES)
def test_agent_package_exposes_root_agent_or_app(package):
    module = importlib.import_module(f"{package}.agent")
    app = getattr(module, "app", None)
    root = getattr(module, "root_agent", None)
    assert root is not None or isinstance(app, App)
    if isinstance(app, App):
        assert app.name == package.split(".")[-1]


def test_tools_agent_has_expected_tools():
    from agents.m03_tools_solution.agent import root_agent

    names = {getattr(t, "__name__", getattr(t, "name", None)) for t in root_agent.tools}
    assert {"search_manual", "get_order_status", "create_ticket", "web_search"} <= names


def test_context_app_has_compaction_and_memory_tool():
    from agents.m04_context_solution.agent import app

    assert app.events_compaction_config.compaction_interval == 5
    names = {getattr(t, "name", getattr(t, "__name__", None)) for t in app.root_agent.tools}
    assert "load_memory" in names


def test_triage_delegates_to_two_specialists():
    from agents.m06_multiagent_solution.agent import root_agent

    assert [a.name for a in root_agent.sub_agents] == ["technical_support", "billing_support"]
    assert all(a.parent_agent is root_agent for a in root_agent.sub_agents)


def test_a2a_server_builds_app():
    from scripts.a2a_billing_server import a2a_app

    assert a2a_app is not None


def test_gradio_app_builds():
    import gradio as gr

    from ui.gradio_app import demo

    assert isinstance(demo, gr.ChatInterface)


def test_core_agent_knows_the_product():
    from agents.m02_core.agent import root_agent as exercise
    from agents.m02_core_solution.agent import root_agent as solution

    for agent in (exercise, solution):
        assert "smart home hub that connects lights, plugs and sensors" in agent.instruction
