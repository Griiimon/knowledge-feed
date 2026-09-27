from __future__ import annotations
from dataclasses import dataclass
from datetime import date

REQUIRED_FIELDS = {"id", "title", "category", "date", "reading_time", "seed", "tags", "status"}
STATUSES = {"draft", "published", "rejected"}

@dataclass(frozen=True)
class Article:
    id: str; title: str; category: str; date: str; reading_time: int; seed: str; tags: list[str]; status: str; body: str; summary: str = ""; sources: list[dict[str, str]] | None = None

@dataclass(frozen=True)
class Topic:
    category: str; description: str; seed: str

def article_from_metadata(metadata: dict, body: str) -> Article:
    missing = REQUIRED_FIELDS - metadata.keys()
    if missing: raise ValueError(f"missing required frontmatter fields: {', '.join(sorted(missing))}")
    if metadata["status"] not in STATUSES: raise ValueError("status must be draft, published, or rejected")
    if not isinstance(metadata["tags"], list): raise ValueError("tags must be a list")
    try: date.fromisoformat(str(metadata["date"])); reading_time = int(metadata["reading_time"])
    except (TypeError, ValueError) as exc: raise ValueError("date must be ISO format and reading_time an integer") from exc
    if reading_time < 1: raise ValueError("reading_time must be positive")
    return Article(**{k: metadata[k] for k in REQUIRED_FIELDS}, body=body, summary=str(metadata.get("summary", "")), sources=metadata.get("sources"))
