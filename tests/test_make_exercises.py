from pathlib import Path

import pytest

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


UNCLOSED = '''a = 1
# >>> EXERCISE: first hint
b = 2
c = 3
# >>> EXERCISE: second hint
d = 4
# <<< EXERCISE
'''


def test_unclosed_opener_keeps_code_between_blocks():
    out = strip_exercises(UNCLOSED)
    assert "b = 2" in out and "c = 3" in out
    assert "d = 4" not in out


def test_build_all_rejects_unclosed_opener(tmp_path: Path):
    sol = tmp_path / "m05_demo_solution"
    sol.mkdir()
    (sol / "agent.py").write_text(UNCLOSED)
    with pytest.raises(ValueError, match="agent.py"):
        build_all(tmp_path)


def test_closer_at_eof_without_newline_is_stripped():
    out = strip_exercises("x = [\n    # >>> EXERCISE: hint\n    1,\n    # <<< EXERCISE")
    assert out == "x = [\n    # TODO: hint\n"
    out = strip_exercises("a = 1\n# >>> EXERCISE: hint\nb = 2\n# <<< EXERCISE")
    assert "EXERCISE" not in out and "b = 2" not in out
    compile(out, "exercise.py", "exec")


def test_build_all_rejects_invalid_python(tmp_path: Path):
    sol = tmp_path / "m06_demo_solution"
    sol.mkdir()
    (sol / "agent.py").write_text("def f(\n# >>> EXERCISE: hint\n    x):\n# <<< EXERCISE\n")
    with pytest.raises(SyntaxError):
        build_all(tmp_path)


def test_build_all_rejects_folder_with_only_unclosed_opener(tmp_path: Path):
    sol = tmp_path / "m07_demo_solution"
    sol.mkdir()
    (sol / "agent.py").write_text("# >>> EXERCISE: hint\nx = 1\n")
    with pytest.raises(ValueError, match="agent.py"):
        build_all(tmp_path)
