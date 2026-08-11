from scripts.common.health import record_failure, record_success


def test_ok_to_error_raises_alert():
    health = {"shopnui": {"status": "ok", "last_error": None, "last_error_at": None}}
    updated, alert = record_failure(health, "shopnui", "shopぬい", "selector not found", "2026-08-11T12:00:00+09:00")
    assert alert is not None
    assert "shopぬい" in alert
    assert updated["shopnui"]["status"] == "error"
    assert updated["shopnui"]["last_error"] == "selector not found"


def test_error_to_error_stays_silent():
    health = {"shopnui": {"status": "error", "last_error": "old error", "last_error_at": "t0"}}
    updated, alert = record_failure(health, "shopnui", "shopぬい", "still broken", "t1")
    assert alert is None
    assert updated["shopnui"]["last_error"] == "still broken"


def test_error_to_ok_raises_recovery_alert():
    health = {"shopnui": {"status": "error", "last_error": "boom", "last_error_at": "t0"}}
    updated, alert = record_success(health, "shopnui", "shopぬい")
    assert alert is not None
    assert "復旧" in alert
    assert updated["shopnui"]["status"] == "ok"
    assert updated["shopnui"]["last_error"] is None


def test_ok_to_ok_stays_silent():
    health = {"shopnui": {"status": "ok", "last_error": None, "last_error_at": None}}
    updated, alert = record_success(health, "shopnui", "shopぬい")
    assert alert is None
    assert updated["shopnui"]["status"] == "ok"


def test_first_ever_failure_for_unknown_source_raises_alert():
    updated, alert = record_failure({}, "shopnui", "shopぬい", "boom", "t0")
    assert alert is not None
    assert updated["shopnui"]["status"] == "error"


def test_does_not_mutate_input_dict():
    health = {"shopnui": {"status": "ok", "last_error": None, "last_error_at": None}}
    record_failure(health, "shopnui", "shopぬい", "boom", "t0")
    assert health["shopnui"]["status"] == "ok"
