from scripts.common.line_client import LINE_PUSH_URL, LINE_TOKEN_URL
from scripts.send_test_notification import run


def test_run_sends_given_message(requests_mock, monkeypatch):
    monkeypatch.setattr("scripts.send_test_notification.config.DRY_RUN", False)
    monkeypatch.setattr("scripts.send_test_notification.config.LINE_CHANNEL_ID", "channel-id")
    monkeypatch.setattr("scripts.send_test_notification.config.LINE_CHANNEL_SECRET", "channel-secret")
    monkeypatch.setattr("scripts.send_test_notification.config.LINE_USER_ID", "user123")
    requests_mock.post(LINE_TOKEN_URL, json={"access_token": "abc123"})
    requests_mock.post(LINE_PUSH_URL, json={})

    assert run("こんにちは") is True

    push_request = requests_mock.request_history[-1]
    assert push_request.json()["messages"] == [{"type": "text", "text": "こんにちは"}]


def test_run_dry_run_skips_network(requests_mock, monkeypatch):
    monkeypatch.setattr("scripts.send_test_notification.config.DRY_RUN", True)
    assert run("test") is True
    assert requests_mock.call_count == 0
