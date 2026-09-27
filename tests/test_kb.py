from helpdesk import kb


def test_search_finds_wifi_reset_passage_first():
    hits = kb.search("how do I reset the wifi settings")
    assert hits, "expected at least one passage"
    assert hits[0].source == "wifi.md"
    assert "10 seconds" in hits[0].text


def test_search_returns_at_most_k_and_skips_headings():
    hits = kb.search("hub", k=2)
    assert len(hits) == 2
    assert all(not h.text.startswith("#") for h in hits)


def test_search_without_overlap_returns_empty():
    assert kb.search("zzzz qqqq") == []
