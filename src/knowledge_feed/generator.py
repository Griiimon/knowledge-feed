from __future__ import annotations
import json
from datetime import date
from .models import Article, Topic
from .content import slugify
from .prompts import generation_prompt, repair_prompt, review_prompt

def parse_generated(raw: str, topic: Topic, min_words: int, max_words: int) -> dict:
    try: data = json.loads(raw)
    except json.JSONDecodeError as exc: raise ValueError("model returned malformed JSON") from exc
    if not isinstance(data, dict) or not all(k in data for k in ("title", "summary", "body_markdown", "tags", "sources")): raise ValueError("model response missing required fields")
    words = len(str(data["body_markdown"]).split())
    if not min_words <= words <= max_words: raise ValueError(f"article has {words} words; expected {min_words}-{max_words}")
    if not isinstance(data["tags"], list) or not isinstance(data["sources"], list): raise ValueError("tags and sources must be lists")
    return data
def generate_article(client, topic: Topic, settings: dict, request_budget: int) -> Article:
    if request_budget < 1: raise RuntimeError("API request limit reached")
    raw = client.chat(generation_prompt(topic, settings["min_words"], settings["max_words"]))
    try: data = parse_generated(raw, topic, settings["min_words"], settings["max_words"])
    except ValueError:
        if request_budget < 2: raise
        data = parse_generated(client.chat(repair_prompt(raw)), topic, settings["min_words"], settings["max_words"])
    if settings.get("review_enabled", True):
        if request_budget < 2: raise RuntimeError("API request limit reached before review")
        review = json.loads(client.chat(review_prompt(data)))
        if not review.get("approved") or review.get("quality_score", 0) < settings.get("approval_threshold", 1): raise ValueError("editorial review rejected article")
    reading_time = max(1, round(len(data["body_markdown"].split()) / 200))
    return Article(slugify(data["title"]), data["title"], topic.category, date.today().isoformat(), reading_time, topic.seed, [str(x) for x in data["tags"]], "published", data["body_markdown"], data["summary"], data["sources"])
