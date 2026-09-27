from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from .models import Article, Topic
from .content import slugify
from .prompts import generation_prompt, repair_prompt, review_prompt


class ResponseLogger:
    """Write untrusted model responses to a local JSON Lines debug file."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._file = path.open("w", encoding="utf-8")

    def log(self, stage: str, raw: str) -> None:
        json.dump({"stage": stage, "response": raw}, self._file, ensure_ascii=False)
        self._file.write("\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def parse_generated(raw: str, topic: Topic, min_words: int, max_words: int) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else ""
        if raw.rstrip().endswith("```"):
            raw = raw.rstrip()[:-3].rstrip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("model returned malformed JSON") from exc
    required_fields = ("title", "summary", "body_markdown", "tags", "sources")
    if not isinstance(data, dict) or not all(key in data for key in required_fields):
        raise ValueError("model response missing required fields")
    words = len(str(data["body_markdown"]).split())
    if not min_words <= words <= max_words:
        raise ValueError(f"article has {words} words; expected {min_words}-{max_words}")
    if not isinstance(data["tags"], list) or not isinstance(data["sources"], list):
        raise ValueError("tags and sources must be lists")
    return data


def generate_article(
    client, topic: Topic, settings: dict, request_budget: int, response_logger: ResponseLogger | None = None
) -> Article:
    review_enabled = settings.get("review_enabled", True)
    reserved_requests = 1 if review_enabled else 0
    if request_budget <= reserved_requests:
        raise RuntimeError("API request limit reached before generation")

    last_error = None
    requests_used = 0
    while requests_used < request_budget - reserved_requests:
        raw = client.chat(generation_prompt(topic, settings["min_words"], settings["max_words"]))
        if response_logger:
            response_logger.log("generation", raw)
        requests_used += 1
        try:
            data = parse_generated(raw, topic, settings["min_words"], settings["max_words"])
            break
        except ValueError as exc:
            last_error = exc

        if requests_used >= request_budget - reserved_requests:
            continue
        try:
            raw = client.chat(repair_prompt(raw))
            if response_logger:
                response_logger.log("repair", raw)
            data = parse_generated(
                raw, topic, settings["min_words"], settings["max_words"]
            )
            break
        except ValueError as exc:
            last_error = exc
            requests_used += 1
    else:
        raise ValueError("model did not return a valid article within the API request limit") from last_error

    if review_enabled:
        raw_review = client.chat(review_prompt(data))
        if response_logger:
            response_logger.log("review", raw_review)
        try:
            review = json.loads(raw_review)
        except json.JSONDecodeError as exc:
            raise ValueError("model returned malformed editorial review JSON") from exc
        if not review.get("approved") or review.get("quality_score", 0) < settings.get("approval_threshold", 1):
            raise ValueError("editorial review rejected article")
    reading_time = max(1, round(len(data["body_markdown"].split()) / 200))
    return Article(
        slugify(data["title"]), data["title"], topic.category, date.today().isoformat(),
        reading_time, topic.seed, [str(x) for x in data["tags"]], "published",
        data["body_markdown"], data["summary"], data["sources"],
    )
