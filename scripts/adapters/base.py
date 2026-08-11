from typing import List, Optional, Protocol

import requests

from scripts.common.models import Item

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AtashinchiWatch/1.0)",
}
DEFAULT_TIMEOUT = 15


class SiteAdapter(Protocol):
    SOURCE_ID: str
    SOURCE_LABEL: str

    def fetch(self) -> List[Item]:
        ...


def fetch_html(url: str, encoding: Optional[str] = None) -> str:
    """Shared HTTP fetch used by every adapter. Raises on non-2xx or network errors
    so the orchestrator can record the failure via common.health."""
    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    if encoding:
        resp.encoding = encoding
    return resp.text
