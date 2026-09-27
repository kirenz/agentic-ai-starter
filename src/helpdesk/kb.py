"""Tiny keyword search over the Nimbus manual (no embeddings, runs offline)."""

import re
from dataclasses import dataclass
from functools import cache
from importlib import resources


@dataclass(frozen=True)
class Passage:
    source: str
    text: str


STOPWORDS = {
    "the", "a", "an", "is", "are", "i", "my", "me", "how", "do", "does", "what", "to", "of",
    "and", "or", "can", "it", "in", "on", "for", "with", "this", "that", "you", "your", "be",
}
SUFFIXES = ("ing", "ed", "s")  # "connected" -> "connect", "devices" -> "device"


def _stem(word: str) -> str:
    """Strip one common suffix from longer words so word forms match."""
    if len(word) > 4:
        for suffix in SUFFIXES:
            if word.endswith(suffix):
                return word[: -len(suffix)]
    return word


def _tokens(text: str) -> set[str]:
    """Lowercase words without stopwords; "Wi-Fi" becomes "wifi"."""
    words = re.findall(r"[a-z0-9]+", text.lower().replace("-", ""))
    return {_stem(w) for w in words if w not in STOPWORDS}


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
