from scripts.common.notify import format_digest, format_immediate


def test_format_immediate_includes_title_url_source_time():
    text = format_immediate("新商品発売", "https://example.com/x", "shopぬい", "2026-08-11T14:02:00+09:00")
    assert "新商品発売" in text
    assert "https://example.com/x" in text
    assert "shopぬい" in text
    assert "08/11 14:02" in text


def test_format_digest_empty_pending_returns_empty_string():
    assert format_digest([]) == ""


def test_format_digest_separates_high_and_low_tiers():
    pending = [
        {"tier": "high", "source": "shopnui", "source_label": "shopぬい", "title": "A", "url": "https://a"},
        {"tier": "low", "source": "google_search", "query": "あたしンち グッズ", "title": "B", "url": "https://b"},
    ]
    text = format_digest(pending)
    assert "熟した実" in text
    assert "青い実" in text
    assert "A" in text and "https://a" in text
    assert "B" in text and "検索: あたしンち グッズ" in text


def test_format_digest_omits_section_with_no_items():
    pending = [{"tier": "low", "source": "google_search", "query": "q", "title": "B", "url": "https://b"}]
    text = format_digest(pending)
    assert "熟した実" not in text
    assert "青い実" in text
