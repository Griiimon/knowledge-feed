from __future__ import annotations
import re
from .models import Article

def normalize(text: str) -> str: return " ".join(re.findall(r"[a-z0-9]+", text.lower()))
def tokens(text: str) -> set[str]: return {t for t in normalize(text).split() if len(t) > 2}
def is_duplicate(seed: str, title: str, articles: list[Article], threshold: float = .65) -> bool:
    candidate = tokens(title)
    for article in articles:
        if normalize(seed) == normalize(article.seed) or normalize(title) == normalize(article.title): return True
        other = tokens(article.title)
        if candidate and other and len(candidate & other) / min(len(candidate), len(other)) >= threshold: return True
    return False
