# Knowledge Feed

A small, static, AI-assisted knowledge publication: short articles about unusual things worth knowing, without accounts, tracking, advertisements, or infinite scrolling. It uses GitHub Pages and OpenRouter's free router (`openrouter/free`) by default. Free-tier limits can change.

## Setup

1. Create a GitHub repository and add this project.
2. Add `OPENROUTER_API_KEY` under **Settings → Secrets and variables → Actions**. Never commit this key.
3. Customize `config/topics.json` and `config/config.json`.
4. In repository Pages settings, select **GitHub Actions** as the source.
5. Run the **Knowledge Feed** workflow once; it generates an article, commits it, builds `site/`, and deploys it.

GitHub Pages may log visitor information under GitHub's own infrastructure and privacy policies; this project adds no analytics, cookies, or tracking.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
cp .env.example .env             # Windows PowerShell: Copy-Item .env.example .env
# Add your OpenRouter key to .env (this file is gitignored).
python -m knowledge_feed build
python -m knowledge_feed generate-and-build
```

Local generation reads `OPENROUTER_API_KEY` and the optional `OPENROUTER_MODEL` from `.env`; shell environment variables take precedence. Other commands are `generate`, `generate --dry-run`, `validate`, and `list-topics`. The dry run selects and prints a topic without calling OpenRouter or modifying files. The generator has a configured request cap and uses separate generation and editorial-review requests. LLM review is not independent fact-checking; published source links are references.

## Customize

- `config/topics.json`: editable categories and seeds.
- `config/config.json`: site settings and generation limits.
- `src/knowledge_feed/prompts.py`: generation and review prompts.
- `templates/` and `static/`: static site design.

Generated Markdown uses JSON frontmatter and belongs in `content/articles/`. Only `published` articles are rendered. The website is entirely static and requires no server, database, paid hosting, paid search, or user accounts.
