from __future__ import annotations
import argparse
from pathlib import Path
from .config import load_config, load_topics
from .content import load_articles, save_article
from .topic_selector import select_topic
from .deduplication import is_duplicate
from .site import build_site
from .openrouter import OpenRouterClient
from .generator import generate_article

def main() -> int:
    p=argparse.ArgumentParser(prog="python -m knowledge_feed"); p.add_argument("command", choices=["generate","build","generate-and-build","validate","list-topics"]); p.add_argument("--dry-run", action="store_true"); p.add_argument("--root", type=Path, default=Path.cwd()); args=p.parse_args(); root=args.root
    config=load_config(root); articles=load_articles(root/'content/articles')
    if args.command == 'build': print(build_site(root)); return 0
    if args.command == 'validate': print(f"valid: {len(articles)} articles"); return 0
    if args.command == 'list-topics':
        for c in load_topics(root): print(f"{c['name']}: {', '.join(c['seeds'])}")
        return 0
    topic=select_topic(load_topics(root), articles, config['content']['avoid_recent_days']); print(f"Selected: {topic.category} — {topic.seed}")
    if args.dry_run: return 0
    article=generate_article(OpenRouterClient(model=config['openrouter']['model'], retries=config['generation']['max_retries']), topic, config['generation'], config['generation']['max_api_requests_per_run'])
    if is_duplicate(article.seed, article.title, articles): raise ValueError("generated article overlaps existing content")
    print(save_article(article, root/'content/articles'))
    if args.command == 'generate-and-build': print(build_site(root))
    return 0
if __name__ == '__main__': raise SystemExit(main())
