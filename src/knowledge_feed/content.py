from __future__ import annotations
from pathlib import Path
import re, yaml
from .models import Article, article_from_metadata

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)
def load_article(path: Path) -> Article:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not match: raise ValueError(f"{path}: expected YAML frontmatter")
    try: metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc: raise ValueError(f"{path}: invalid frontmatter") from exc
    if not isinstance(metadata, dict): raise ValueError(f"{path}: frontmatter must be a mapping")
    return article_from_metadata(metadata, match.group(2).strip())
def load_articles(directory: Path) -> list[Article]:
    if not directory.exists(): return []
    return sorted((load_article(p) for p in directory.glob("*.md")), key=lambda a: a.date, reverse=True)
def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "article"
def save_article(article: Article, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {"id": article.id, "title": article.title, "category": article.category, "date": article.date, "reading_time": article.reading_time, "seed": article.seed, "tags": article.tags, "status": article.status, "summary": article.summary, "sources": article.sources or []}
    path = directory / f"{article.date}-{slugify(article.id)}.md"
    path.write_text("---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + article.body.strip() + "\n", encoding="utf-8")
    return path
