from datetime import datetime

"""Pure functions for the monthly LINE push counter. `is_throttled` is always
computed from `count`, never stored as its own flag, so the two can't drift
out of sync."""


def current_year_month(now: datetime) -> str:
    return now.strftime("%Y-%m")


def load_or_reset_month(quota: dict, now: datetime) -> dict:
    """Return quota state for the current calendar month, resetting the
    counter to 0 if the stored state belongs to a previous month."""
    ym = current_year_month(now)
    if quota.get("year_month") != ym:
        return {"year_month": ym, "count": 0}
    return dict(quota)


def is_throttled(quota: dict, threshold: int) -> bool:
    return quota.get("count", 0) >= threshold


def increment(quota: dict, by: int = 1) -> dict:
    updated = dict(quota)
    updated["count"] = updated.get("count", 0) + by
    return updated
