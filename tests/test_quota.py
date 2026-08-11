from datetime import datetime

from scripts.common.quota import current_year_month, increment, is_throttled, load_or_reset_month


def test_current_year_month_format():
    assert current_year_month(datetime(2026, 8, 11)) == "2026-08"


def test_load_or_reset_month_keeps_count_within_same_month():
    quota = {"year_month": "2026-08", "count": 42}
    result = load_or_reset_month(quota, datetime(2026, 8, 20))
    assert result == {"year_month": "2026-08", "count": 42}


def test_load_or_reset_month_resets_on_month_rollover():
    quota = {"year_month": "2026-07", "count": 190}
    result = load_or_reset_month(quota, datetime(2026, 8, 1))
    assert result == {"year_month": "2026-08", "count": 0}


def test_is_throttled_below_threshold():
    assert is_throttled({"count": 179}, threshold=180) is False


def test_is_throttled_at_threshold():
    assert is_throttled({"count": 180}, threshold=180) is True


def test_is_throttled_above_threshold():
    assert is_throttled({"count": 199}, threshold=180) is True


def test_increment_does_not_mutate_input():
    original = {"year_month": "2026-08", "count": 5}
    result = increment(original)
    assert result == {"year_month": "2026-08", "count": 6}
    assert original["count"] == 5


def test_increment_by_custom_amount():
    result = increment({"year_month": "2026-08", "count": 0}, by=3)
    assert result["count"] == 3
