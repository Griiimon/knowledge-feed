from __future__ import annotations
import json

def generation_prompt(topic, min_words: int, max_words: int) -> str:
    return f'''You write for a small independent knowledge publication. Write one factual, memorable article for an intelligent general audience about this specific angle: {topic.seed!r} ({topic.category}: {topic.description}). Find one surprising, focused angle; do not write a generic introduction or listicle. Use {min_words}-{max_words} words, concise prose, no clickbait, fake suspense, "imagine", filler, invented quotes, dates, statistics, or sources. Clearly mark uncertainty. Return ONLY JSON: {{"title":"...","category":"{topic.category}","summary":"...","body_markdown":"...","tags":["..."],"sources":[{{"title":"...","url":"https://..."}}]}}.'''
def repair_prompt(raw: str) -> str:
    return "Return valid JSON only for this malformed article response, preserving content where possible: " + raw
def review_prompt(article: dict) -> str:
    return """Act as an editorial reviewer. This is not independent fact-checking; assess factual plausibility, unsupported claims, invented citations, repetition, generic/clickbait writing, contradictions, and title accuracy. Return ONLY JSON: {\"approved\":true,\"quality_score\":8,\"issues\":[],\"suggested_changes\":[]}. Article:\n""" + json.dumps(article)
