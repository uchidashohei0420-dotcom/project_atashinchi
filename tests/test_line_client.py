import pytest

from scripts.common.line_client import (
    LINE_PUSH_URL,
    LINE_TOKEN_URL,
    get_access_token,
    get_access_token_or_dry_run,
    push_text,
)


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


def test_get_access_token_sends_client_credentials(requests_mock):
    requests_mock.post(LINE_TOKEN_URL, json={"access_token": "abc123", "expires_in": 1800})
    token = get_access_token("channel-id", "channel-secret")
    assert token == "abc123"
    body = requests_mock.request_history[0].text
    assert "grant_type=client_credentials" in body
    assert "client_id=channel-id" in body
    assert "client_secret=channel-secret" in body


def test_get_access_token_raises_on_http_error(requests_mock):
    requests_mock.post(LINE_TOKEN_URL, status_code=400, json={"error": "invalid_client"})
    with pytest.raises(Exception):
        get_access_token("bad-id", "bad-secret")


def test_get_access_token_or_dry_run_skips_network_when_dry_run(requests_mock):
    token = get_access_token_or_dry_run("channel-id", "channel-secret", dry_run=True)
    assert token == "dry-run"
    assert requests_mock.call_count == 0


def test_get_access_token_or_dry_run_calls_real_endpoint_when_not_dry_run(requests_mock):
    requests_mock.post(LINE_TOKEN_URL, json={"access_token": "real-token"})
    token = get_access_token_or_dry_run("channel-id", "channel-secret", dry_run=False)
    assert token == "real-token"
