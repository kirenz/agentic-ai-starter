import pytest

from helpdesk import tools


@pytest.fixture(autouse=True)
def _reset():
    tools.reset_state()


def test_order_status_known_order():
    result = tools.get_order_status("NH-1002")
    assert result == {"status": "ok", "order_id": "NH-1002", "order_status": "shipped", "item": "Nimbus Home Hub"}


def test_order_status_unknown_order():
    assert tools.get_order_status("NH-9999")["status"] == "not_found"


def test_create_ticket_increments_ids():
    first = tools.create_ticket("Hub offline", "Light is solid orange")
    second = tools.create_ticket("Automation", "Does not run", priority="high")
    assert first["ticket_id"] == "T-1001"
    assert second["ticket_id"] == "T-1002"
    assert second["priority"] == "high"


def test_refund_within_order_total():
    result = tools.issue_refund("NH-1001", 129.0, "Returned within 30 days")
    assert result["status"] == "refunded"
    assert result["amount_eur"] == 129.0


def test_refund_above_order_total_is_rejected():
    assert tools.issue_refund("NH-1003", 100.0, "Too much")["status"] == "rejected"


def test_search_manual_wraps_passages():
    result = tools.search_manual("firmware update now")
    assert result["status"] == "ok"
    assert result["passages"][0]["source"] == "firmware.md"
