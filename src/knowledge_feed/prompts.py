from __future__ import annotations
import json


def generation_prompt(topic, min_words: int, max_words: int) -> str:
    schema = {
        "title": "string",
        "summary": "string",
        "body_markdown": "string",
        "tags": ["string", "string"],
        "sources": [{"title": "string", "url": "https://example.com/source"}],
    }
    return f"""You write for a small independent knowledge publication. Write one factual, memorable article for an intelligent general audience about this specific angle: {topic.seed!r} ({topic.category}: {topic.description}). Find one surprising, focused angle; do not write a generic introduction or listicle. Use {min_words}-{max_words} words, concise prose, no clickbait, fake suspense, "imagine", filler, invented quotes, dates, statistics, or sources. Clearly mark uncertainty.

You MUST return ONLY one valid JSON object. Do not include a preamble, explanation, reasoning, thinking process, Markdown code fence, or any text before or after the JSON.

The response MUST use this exact structure and value types:
{json.dumps(schema, ensure_ascii=False)}

`tags` MUST be an array of strings, never a single string. `sources` MUST be an array of objects, never Markdown or text within `body_markdown`; every source object MUST contain string `title` and `url` fields. Return only the JSON object."""


def repair_prompt(raw: str, validation_error: str) -> str:
    schema = {
        "title": "string",
        "summary": "string",
        "body_markdown": "string",
        "tags": ["string", "string"],
        "sources": [{"title": "string", "url": "https://example.com/source"}],
    }
    return f"""Repair the article response below. Return ONLY one valid JSON object: no explanation, reasoning, thinking process, or Markdown code fence.

It failed validation because: {validation_error}

Required structure and value types:
{json.dumps(schema, ensure_ascii=False)}

Preserve valid article content where possible. `tags` must be an array of strings. `sources` must be an array of objects, and every object must have string `title` and `url` fields.

Malformed response:
{raw}"""


def review_prompt(article: dict) -> str:
    return """Act as an editorial reviewer. This is not independent fact-checking; assess factual plausibility, unsupported claims, invented citations, repetition, generic/clickbait writing, contradictions, and title accuracy. Return ONLY JSON: {\"approved\":true,\"quality_score\":8,\"issues\":[],\"suggested_changes\":[]}. Article:\n""" + json.dumps(article)
