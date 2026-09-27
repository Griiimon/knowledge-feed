from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import html, json, shutil
from urllib.parse import urlparse
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .content import slugify

def safe_url(value: str) -> str:
    return value if urlparse(value).scheme in {"http", "https"} else ""
def render_body(body: str) -> str:
    return markdown.markdown(html.escape(body), extensions=["extra"])
def build_site(root: Path) -> Path:
    from .config import load_config
    from .content import load_articles
    config = load_config(root); articles = [a for a in load_articles(root / "content/articles") if a.status == "published"]
    output = root / "site"; shutil.rmtree(output, ignore_errors=True); output.mkdir()
    shutil.copytree(root / "static", output / "assets")
    env = Environment(loader=FileSystemLoader(root / "templates"), autoescape=select_autoescape(["html", "xml"]))
    def write(template: str, relative: str, **ctx):
        p = output / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(env.get_template(template).render(site=config["site"], articles=articles, **ctx), encoding="utf-8")
    enriched = [{"article": a, "slug": slugify(a.id), "body_html": render_body(a.body), "sources": [{"title": str(s.get("title", "Source")), "url": safe_url(str(s.get("url", "")))} for s in (a.sources or [])]} for a in articles]
    write("index.html", "index.html", featured=enriched[:config["content"]["max_articles_homepage"]])
    write("archive.html", "archive/index.html", featured=enriched[:config["content"]["max_articles_archive_page"]])
    write("404.html", "404.html")
    categories = sorted({a.category for a in articles})
    for category in categories:
        selected = [x for x in enriched if x["article"].category == category]
        write("category.html", f"categories/{slugify(category)}/index.html", category=category, featured=selected)
    for item in enriched:
        related = [x for x in enriched if x["article"].category == item["article"].category and x["article"].id != item["article"].id][:3]
        write("article.html", f"articles/{item['slug']}/index.html", item=item, related=related)
    search = [{"id": a.id, "title": a.title, "category": a.category, "summary": a.summary, "tags": a.tags, "url": f"articles/{slugify(a.id)}/"} for a in articles]
    (output / "search.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")
    write("feed.xml", "feed.xml", generated=datetime.now(timezone.utc), entries=enriched)
    return output
