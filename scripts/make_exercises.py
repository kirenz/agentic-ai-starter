"""Generate exercise folders from *_solution agent folders.

Usage: uv run python -m scripts.make_exercises
"""

import re
import shutil
from pathlib import Path

BLOCK = re.compile(
    r"^(?P<indent>[ \t]*)# >>> EXERCISE: (?P<hint>.*?)\n.*?^[ \t]*# <<< EXERCISE\n",
    re.MULTILINE | re.DOTALL,
)


def strip_exercises(source: str) -> str:
    return BLOCK.sub(lambda m: f"{m['indent']}# TODO: {m['hint']}\n", source)


def build_all(agents_dir: Path) -> list[Path]:
    created = []
    for sol in sorted(agents_dir.glob("*_solution")):
        files = list(sol.rglob("*.py"))
        if not any(BLOCK.search(f.read_text()) for f in files):
            continue
        target = agents_dir / sol.name.removesuffix("_solution")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(sol, target, ignore=shutil.ignore_patterns("__pycache__"))
        for f in target.rglob("*.py"):
            text = strip_exercises(f.read_text())
            text = text.replace(f'name="{sol.name}"', f'name="{target.name}"')
            f.write_text(text)
        created.append(target)
    return created


if __name__ == "__main__":
    for path in build_all(Path(__file__).resolve().parent.parent / "agents"):
        print(f"generated {path.name}")
