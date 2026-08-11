import logging

import requests

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
MAX_TEXT_LENGTH = 5000
TIMEOUT = 15

logger = logging.getLogger(__name__)


def get_access_token(channel_id: str, channel_secret: str) -> str:
    """Exchange channel ID + secret for a short-lived stateless access token.
    Used instead of a long-lived channel access token because newer LINE
    channels don't expose a simple "issue" button for one - this only needs
    values that are always on the Basic settings tab, no key-pair setup."""
    resp = requests.post(
        LINE_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": channel_id,
            "client_secret": channel_secret,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_access_token_or_dry_run(channel_id: str, channel_secret: str, dry_run: bool) -> str:
    """Skip the real token exchange in dry-run mode so local dev / smoke
    tests work without real LINE credentials configured at all."""
    if dry_run:
        return "dry-run"
    return get_access_token(channel_id, channel_secret)


def push_text(user_id: str, token: str, text: str, dry_run: bool = False) -> bool:
    """Send a single LINE push message. In dry-run mode, logs instead of calling
    the API so local dev / workflow_dispatch smoke tests never spend the
    monthly free quota. Returns True on success (dry-run always succeeds)."""
    text = text[:MAX_TEXT_LENGTH]
    if dry_run:
        logger.info("[DRY_RUN] LINE push skipped:\n%s", text)
        return True

    resp = requests.post(
        LINE_PUSH_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"to": user_id, "messages": [{"type": "text", "text": text}]},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return True
