import importlib

import pytest
from google.adk.apps import App

AGENT_PACKAGES = [
    "agents.m00_first_agent",
    "agents.m02_core_solution",
    "agents.m03_tools_solution",
    "agents.m03_mcp_solution",
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
