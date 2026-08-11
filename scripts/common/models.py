from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Item:
    """A single announcement/listing found by an adapter or the search client."""
    url: str
    title: str
    query: Optional[str] = None  # set for google_search results, which keyword matched
