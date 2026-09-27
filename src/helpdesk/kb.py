"""Tiny keyword search over the Nimbus manual (no embeddings, runs offline)."""

import re
from dataclasses import dataclass
from functools import cache
from importlib import resources


@dataclass(frozen=True)
class Passage:
    source: str
    text: str


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


@cache
def load_passages() -> tuple[Passage, ...]:
    root = resources.files("helpdesk") / "data" / "manual"
    passages = []
    for f in sorted(root.iterdir(), key=lambda p: p.name):
        if not f.name.endswith(".md"):
            continue
        for block in f.read_text(encoding="utf-8").split("\n\n"):
            block = block.strip()
            if block and not block.startswith("#"):
                passages.append(Passage(source=f.name, text=block))
    return tuple(passages)


def search(query: str, k: int = 3) -> list[Passage]:
    """Return up to k passages ranked by the number of shared words."""
    q = _tokens(query)
    scored = [(len(q & _tokens(p.text)), p) for p in load_passages()]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: -s[0])
    return [p for _, p in scored[:k]]
