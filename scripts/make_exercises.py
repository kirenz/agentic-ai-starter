"""Generate exercise folders from *_solution agent folders.

Usage: uv run python -m scripts.make_exercises
"""

import re
import shutil
from pathlib import Path

# The body may not cross another opener, so an unclosed opener never swallows
# the code up to the next block's closer. The closer may end the file.
BLOCK = re.compile(
    r"^(?P<indent>[ \t]*)# >>> EXERCISE: (?P<hint>[^\n]*)\n"
    r"(?:(?!# >>> EXERCISE).)*?"
    r"^[ \t]*# <<< EXERCISE[ \t]*(?:\n|\Z)",
    re.MULTILINE | re.DOTALL,
)
LEFTOVER = re.compile(r"(>>>|<<<) EXERCISE")


def strip_exercises(source: str) -> str:
    return BLOCK.sub(lambda m: f"{m['indent']}# TODO: {m['hint']}\n", source)


def build_all(agents_dir: Path) -> list[Path]:
    created = []
    for sol in sorted(agents_dir.glob("*_solution")):
        files = list(sol.rglob("*.py"))
        if not any(LEFTOVER.search(f.read_text()) for f in files):
            continue
        target = agents_dir / sol.name.removesuffix("_solution")
        # Build and validate every file before touching the target folder.
        generated = {}
        for f in files:
            if "__pycache__" in f.parts:
                continue
            text = strip_exercises(f.read_text())
            text = text.replace(f'name="{sol.name}"', f'name="{target.name}"')
            if LEFTOVER.search(text):
                raise ValueError(f"{f}: unbalanced EXERCISE marker")
            compile(text, str(f), "exec")
            generated[f.relative_to(sol)] = text
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(sol, target, ignore=shutil.ignore_patterns("__pycache__"))
        for rel, text in generated.items():
            (target / rel).write_text(text)
        created.append(target)
    return created


if __name__ == "__main__":
    for path in build_all(Path(__file__).resolve().parent.parent / "agents"):
        print(f"generated {path.name}")
