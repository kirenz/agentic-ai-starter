"""Mock order database for the Nimbus shop."""

import json
from functools import cache
from importlib import resources


@cache
def _orders() -> dict:
    path = resources.files("helpdesk") / "data" / "orders.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get(order_id: str) -> dict | None:
    return _orders().get(order_id.strip().upper())
