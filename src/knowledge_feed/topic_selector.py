from __future__ import annotations
from datetime import date, timedelta
import random
from .models import Article, Topic

def select_topic(categories: list[dict], articles: list[Article], avoid_recent_days: int = 30, rng: random.Random | None = None) -> Topic:
    rng = rng or random.Random(0)
    cutoff = (date.today() - timedelta(days=avoid_recent_days)).isoformat()
    recent = [a for a in articles if a.date >= cutoff]
    used = {a.seed.casefold() for a in articles}
    recent_categories = [a.category for a in recent]
    ranked = sorted(categories, key=lambda c: (recent_categories.count(c["name"]), c["name"]))
    candidates = []
    for c in ranked:
        fresh = [s for s in c["seeds"] if s.casefold() not in used]
        if fresh: candidates.extend((c, s) for s in fresh)
    if not candidates: raise ValueError("no unexplored topic seeds available")
    lowest = min(recent_categories.count(c["name"]) for c, _ in candidates)
    candidates = [(c, s) for c, s in candidates if recent_categories.count(c["name"]) == lowest]
    c, seed = rng.choice(candidates)
    return Topic(c["name"], c["description"], seed)
