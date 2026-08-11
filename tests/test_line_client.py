import pytest

from scripts.common.line_client import LINE_PUSH_URL, push_text


def test_dry_run_does_not_call_api(requests_mock):
    ok = push_text("user123", "token123", "hello", dry_run=True)
    assert ok is True
    assert requests_mock.call_count == 0


def test_push_text_sends_expected_payload(requests_mock):
    requests_mock.post(LINE_PUSH_URL, json={}, status_code=200)
    ok = push_text("user123", "token123", "新着があります", dry_run=False)
    assert ok is True
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.headers["Authorization"] == "Bearer token123"
    body = request.json()
    assert body["to"] == "user123"
    assert body["messages"] == [{"type": "text", "text": "新着があります"}]


def test_push_text_raises_on_http_error(requests_mock):
    requests_mock.post(LINE_PUSH_URL, status_code=401, json={"message": "invalid token"})
    with pytest.raises(Exception):
        push_text("user123", "bad-token", "hello", dry_run=False)


def test_push_text_truncates_overlong_message(requests_mock):
    requests_mock.post(LINE_PUSH_URL, json={}, status_code=200)
    push_text("user123", "token123", "a" * 6000, dry_run=False)
    body = requests_mock.request_history[0].json()
    assert len(body["messages"][0]["text"]) == 5000
