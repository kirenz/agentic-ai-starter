from pathlib import Path

from scripts.make_exercises import build_all, strip_exercises

SOLUTION = '''from helpdesk import tools

root_tools = [
    # >>> EXERCISE: add the order status tool
    tools.get_order_status,
    # <<< EXERCISE
]
'''


def test_strip_replaces_block_with_todo():
    out = strip_exercises(SOLUTION)
    assert "get_order_status" not in out
    assert "    # TODO: add the order status tool\n]" in out
    assert ">>>" not in out and "<<<" not in out
    compile(out, "exercise.py", "exec")


def test_build_all_creates_exercise_folder(tmp_path: Path):
    sol = tmp_path / "m03_demo_solution"
    sol.mkdir()
    (sol / "__init__.py").write_text("from . import agent\n")
    (sol / "agent.py").write_text(SOLUTION)
    (tmp_path / "m00_plain").mkdir()
    created = build_all(tmp_path)
    assert created == [tmp_path / "m03_demo"]
    assert "TODO" in (tmp_path / "m03_demo" / "agent.py").read_text()
    assert (tmp_path / "m03_demo" / "__init__.py").exists()


def test_build_all_renames_app(tmp_path: Path):
    sol = tmp_path / "m04_demo_solution"
    sol.mkdir()
    (sol / "agent.py").write_text('app_name = "x"\nname="m04_demo_solution"\n# >>> EXERCISE: hint\nx = 1\n# <<< EXERCISE\n')
    build_all(tmp_path)
    assert 'name="m04_demo"' in (tmp_path / "m04_demo" / "agent.py").read_text()
