import importlib
from pathlib import Path

import pytest

AGENTS = Path(__file__).parent.parent / "agents"
EXERCISES = sorted(
    p.name for p in AGENTS.iterdir()
    if p.is_dir() and p.name.startswith("m") and not p.name.endswith("_solution") and (AGENTS / f"{p.name}_solution").exists()
)


def test_every_solution_with_markers_has_an_exercise():
    assert EXERCISES == [
        "m02_core", "m03_mcp", "m03_tools", "m04_context", "m05_workflow",
        "m06_a2a_client", "m06_multiagent", "m07_guardrails",
    ]


@pytest.mark.parametrize("name", EXERCISES)
def test_exercise_imports(name):
    module = importlib.import_module(f"agents.{name}.agent")
    assert hasattr(module, "root_agent") or hasattr(module, "app")
