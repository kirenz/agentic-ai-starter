"""Tools for the Nimbus Support Assistant.

Plain Python functions with type hints and docstrings. ADK turns them into
function tools automatically; LangChain accepts them as tools as well.
"""

from itertools import count

from helpdesk import kb, orders

_ticket_ids = count(1001)
_tickets: list[dict] = []


def reset_state() -> None:
    """Reset in-memory tickets (used by tests)."""
    global _ticket_ids
    _ticket_ids = count(1001)
    _tickets.clear()


def search_manual(query: str) -> dict:
    """Search the Nimbus Home Hub manual.

    Args:
        query: Keywords describing the customer's question, e.g. "reset wifi".

    Returns:
        A dict with status and up to three matching manual passages.
    """
    hits = kb.search(query)
    if not hits:
        return {"status": "no_results", "passages": []}
    return {"status": "ok", "passages": [{"source": p.source, "text": p.text} for p in hits]}


def get_order_status(order_id: str) -> dict:
    """Look up the status of a Nimbus shop order.

    Args:
        order_id: The order number, e.g. "NH-1002".

    Returns:
        A dict with the order status and item, or status "not_found".
        Delivered orders also include days_since_delivery (for the 30-day return rule).
    """
    order = orders.get(order_id)
    if order is None:
        return {"status": "not_found", "order_id": order_id}
    result = {"status": "ok", "order_id": order_id.strip().upper(), "order_status": order["status"], "item": order["item"]}
    if order["delivered_days_ago"] is not None:
        result["days_since_delivery"] = order["delivered_days_ago"]
    return result


def create_ticket(subject: str, description: str, priority: str = "normal") -> dict:
    """Create a support ticket for a problem the assistant cannot solve.

    Args:
        subject: Short summary of the problem.
        description: What the customer reported and what was already tried.
        priority: "low", "normal" or "high".

    Returns:
        A dict with the new ticket id.
    """
    ticket = {"ticket_id": f"T-{next(_ticket_ids)}", "subject": subject, "description": description, "priority": priority}
    _tickets.append(ticket)
    return {"status": "created", **ticket}


def issue_refund(order_id: str, amount_eur: float, reason: str) -> dict:
    """Refund money for an order to the original payment method.

    Args:
        order_id: The order number, e.g. "NH-1001".
        amount_eur: Amount to refund in euros.
        reason: Why the refund is issued.

    Returns:
        A dict with status "refunded" or "rejected".
    """
    order = orders.get(order_id)
    if order is None:
        return {"status": "rejected", "reason": "unknown order"}
    if not (0 < amount_eur <= order["total_eur"]):  # also rejects NaN
        return {"status": "rejected", "reason": "amount must be between 0 and the order total"}
    return {"status": "refunded", "order_id": order_id.strip().upper(), "amount_eur": amount_eur, "reason": reason}
