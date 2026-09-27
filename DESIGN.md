# Knowledge Feed

## 1. Project Summary

Build a small, zero-cost, AI-assisted personal knowledge website intended as an alternative to browsing Reddit for interesting things to learn.

The site should continuously accumulate short, high-quality knowledge articles about unusual, niche, surprising, or intellectually interesting subjects.

The intended user experience is:

> Open site → see something interesting → read for 2–5 minutes → learn something → optionally read another → leave.

This is explicitly **not** intended to become a social network, engagement-optimization system, or infinite-scroll addiction machine.

There are no:

* accounts
* comments
* likes
* followers
* notifications
* advertisements
* recommendation tracking
* user profiles
* infinite personalized feeds

The project should be completely usable by one person and optionally shared with a few friends.

The initial implementation must be free to operate using:

* GitHub
* GitHub Pages
* GitHub Actions
* OpenRouter free models

OpenRouter's `openrouter/free` router must be used rather than a potentially paid automatic router.

---

# 2. Primary Technical Architecture

Use this architecture:

```text
                         GitHub Repository
                               |
               +---------------+---------------+
               |                               |
               v                               v
       content/articles/                 config/topics.yaml
               |                               |
               +---------------+---------------+
                               |
                               v
                    GitHub Actions workflow
                               |
                               v
                         Python generator
                               |
                    +----------+----------+
                    |                     |
                    v                     v
             Topic selection        Existing article
                    |                deduplication
                    v
               OpenRouter
                    |
                    v
             Draft generation
                    |
                    v
             Editorial review
                    |
                    v
             Article JSON/MD
                    |
                    v
              Static site build
                    |
                    v
              GitHub Pages
```

The website itself must be completely static.

There must be no runtime Python server.

There must be no database server.

There must be no backend API.

All generated content should ultimately exist in the Git repository as static content.

---

# 3. Core Requirements

## 3.1 Content

Each generated article should generally be:

* 300–700 words
* readable in approximately 2–5 minutes
* about one clearly defined subject
* fact-oriented
* surprising or intellectually interesting
* accessible to an intelligent general audience
* concise
* free of filler

The content should favor:

* obscure historical events
* unusual scientific phenomena
* strange biological adaptations
* forgotten inventions
* failed technologies
* linguistic oddities
* surprising geographical facts
* archaeology
* mathematics
* engineering
* astronomy
* unusual cultural practices
* historical misconceptions
* unexpected connections between fields
* unusual origins of ordinary objects
* scientific discoveries
* extinct technologies
* strange natural phenomena
* obscure people whose work had interesting consequences
* unusual examples of human ingenuity

Avoid generic trivia such as:

* "Did you know octopuses have three hearts?"
* "The Eiffel Tower gets taller in summer."
* "Honey never spoils."

unless the article develops a genuinely less-obvious aspect of the subject.

The system should prefer depth and novelty over trivia quantity.

---

# 4. Topic System

Create:

```text
config/topics.yaml
```

The user should be able to edit this file without understanding the Python code.

Example:

```yaml
categories:

  - name: Ancient Engineering
    description: >
      Engineering, construction, materials, machines and infrastructure
      from ancient civilizations.
    seeds:
      - Roman concrete
      - ancient water clocks
      - Antikythera mechanism
      - ancient road construction
      - Roman surveying
      - ancient glassmaking

  - name: Strange Biology
    description: >
      Unusual adaptations, biological mechanisms and evolutionary solutions.
    seeds:
      - tardigrades
      - mimic octopus
      - axolotl regeneration
      - deep sea gigantism

  - name: Linguistics
    description: >
      Unusual properties of human languages and writing systems.
    seeds:
      - language isolates
      - unusual writing systems
      - linguistic number systems
      - disappearing languages

  - name: Forgotten Technology
    description: >
      Technologies that existed, disappeared, failed or were replaced.
    seeds:
      - pneumatic mail
      - mechanical television
      - Jacquard loom
      - early calculating machines
```

The user should only need to edit this file to customize the subject matter.

The topic selector must:

1. Load all categories.
2. Load all seeds.
3. Inspect previously generated articles.
4. Avoid recently used seeds.
5. Avoid topics with substantial semantic overlap with existing articles.
6. Prefer unexplored seeds.
7. Occasionally generate a topic related to an existing article.
8. Avoid repeatedly selecting the same category.

The selection system should be deterministic where practical so tests can be written around it.

---

# 5. Topic Expansion

A seed should not necessarily become the final article title.

For example:

```text
Seed:
Roman concrete
```

could result in:

```text
Why Some Roman Concrete Structures Became Stronger With Age
```

The generator should be encouraged to find a specific angle.

The prompt should explicitly discourage generic introductions and generic "10 facts" articles.

The article should answer:

> "What is the one thing about this subject that would make someone say 'I didn't know that'?"

---

# 6. Article Data Model

Store generated articles as Markdown with YAML frontmatter OR JSON.

Prefer Markdown because it is human-readable and easy to edit manually.

Example:

```text
content/articles/2026-09-27-roman-concrete.md
```

Example:

```yaml
---
id: roman-concrete-self-healing
title: "Why Some Roman Concrete Structures Became Stronger With Age"
category: "Ancient Engineering"
date: "2026-09-27"
reading_time: 4
seed: "Roman concrete"
tags:
  - engineering
  - rome
  - materials
status: published
---

Article body...

## Sources

- Source title — URL
- Source title — URL
```

The parser should validate the required fields.

Required metadata:

* `id`
* `title`
* `category`
* `date`
* `reading_time`
* `seed`
* `tags`
* `status`

Allowed status values:

```text
draft
published
rejected
```

Only `published` articles should appear on the website.

---

# 7. Article Generation Pipeline

Implement the following pipeline:

```text
select topic
    ↓
check duplicate/overlap
    ↓
generate article
    ↓
validate structure
    ↓
editorial review
    ↓
accept/reject
    ↓
save article
    ↓
build site
```

The generator should make separate LLM requests for generation and editorial review.

Do not combine everything into one enormous prompt.

---

# 8. OpenRouter Integration

Use the OpenRouter HTTP API.

Use:

```text
openrouter/free
```

as the default model.

Do not use:

```text
openrouter/auto
```

because the project requirement is zero-cost operation.

The API key must never be committed to the repository.

Read it from:

```text
OPENROUTER_API_KEY
```

environment variable.

The implementation should also support:

```text
OPENROUTER_MODEL
```

as an optional environment variable.

Default:

```text
openrouter/free
```

This allows a specific model to be selected later without modifying source code.

---

# 9. OpenRouter Client

Create:

```text
src/knowledge_feed/openrouter.py
```

Implement a small API client using Python's standard HTTP facilities or a lightweight dependency.

Requirements:

* timeout
* retry with exponential backoff
* handling HTTP 429
* handling transient 5xx errors
* clear error messages
* JSON parsing
* API-key authentication
* configurable model
* configurable maximum tokens

Do not implement an elaborate SDK.

The application only needs chat completion functionality.

---

# 10. Generation Prompt

Create prompts in:

```text
src/knowledge_feed/prompts.py
```

Do not bury prompts throughout Python source files.

The generation prompt should communicate roughly:

```text
You are the writer for a small independent knowledge publication.

Write one short, genuinely interesting knowledge article.

The goal is not to maximize engagement.
The goal is to teach the reader one unusual and memorable thing.

Requirements:

- 300–700 words
- intelligent general audience
- one central subject
- specific rather than generic
- factual
- concise
- no filler
- no clickbait
- no fake suspense
- no motivational language
- no rhetorical "imagine..."
- no generic "throughout history..." introductions
- don't repeat common trivia unless adding a substantially less-known aspect
- clearly distinguish established facts from uncertainty
- do not invent quotations
- do not invent sources
- do not invent dates, names or statistics
- include useful source references
```

The exact final prompt should be implemented by Codex rather than copied verbatim if improvements are appropriate.

---

# 11. Structured Generation

Prefer structured JSON output from the LLM.

Expected structure:

```json
{
  "title": "...",
  "category": "...",
  "summary": "...",
  "body_markdown": "...",
  "tags": ["...", "..."],
  "sources": [
    {
      "title": "...",
      "url": "..."
    }
  ]
}
```

Validate this response before writing the article.

If the model returns malformed JSON:

1. retry once with a repair prompt
2. if still invalid, reject the generation

Never publish malformed content.

---

# 12. Editorial Review

Run a second LLM request against the generated article.

The reviewer should check:

* factual plausibility
* unsupported claims
* obvious hallucinations
* repetition
* generic content
* clickbait
* excessive verbosity
* invented citations
* contradictions
* whether the article actually contains something interesting
* whether the title accurately represents the article

The reviewer should return structured JSON:

```json
{
  "approved": true,
  "quality_score": 8,
  "issues": [],
  "suggested_changes": []
}
```

The score is internal only.

Do not expose the score publicly.

For the MVP:

```text
approved == true
```

is sufficient to publish.

However, the code should make the threshold configurable.

---

# 13. Important Factuality Limitation

The system must not pretend that an LLM editorial review constitutes factual verification.

The generated article should include its source URLs.

The application should clearly treat these as references, not guarantees of correctness.

If source verification cannot be performed automatically, do not claim that the article has been independently fact-checked.

Future versions may add actual source retrieval and verification.

---

# 14. Duplicate Detection

Create:

```text
src/knowledge_feed/deduplication.py
```

MVP duplicate detection should use:

1. exact seed matching
2. normalized title matching
3. token overlap
4. optionally an LLM similarity check

Do not introduce embeddings or a vector database in version 1.

The goal is simply to avoid obvious repetition.

Example:

Existing:

```text
Why Roman Concrete Could Repair Its Own Cracks
```

New candidate:

```text
How Roman Concrete Repaired Cracks by Itself
```

should be rejected or sent back for regeneration.

---

# 15. Article Selection

Implement:

```text
src/knowledge_feed/topic_selector.py
```

Selection should consider:

* category rotation
* seed age
* whether seed was already used
* recent category frequency
* related topics
* randomization

Configuration:

```yaml
generation:
  articles_per_run: 1
  min_words: 300
  max_words: 700
  avoid_recent_days: 30
```

Default generation should produce **one article per scheduled run**.

Do not generate multiple articles by default.

---

# 16. Site Generator

Create:

```text
src/knowledge_feed/site.py
```

Generate a completely static website.

No Flask.

No Django.

No server.

No JavaScript framework.

Prefer:

* Python
* HTML templates
* CSS
* minimal vanilla JavaScript where genuinely useful

A lightweight template dependency is acceptable, but minimize dependencies.

---

# 17. Website Structure

Generated output:

```text
site/
├── index.html
├── archive/
│   └── index.html
├── categories/
│   ├── science/
│   ├── history/
│   └── ...
├── articles/
│   ├── article-one/
│   │   └── index.html
│   └── article-two/
│       └── index.html
├── assets/
│   ├── style.css
│   └── app.js
├── search.json
└── 404.html
```

The exact structure can be adjusted if a simpler implementation is cleaner.

---

# 18. Homepage

The homepage should show:

* site title
* short description
* latest articles
* category navigation
* random article button
* archive link

Example concept:

```text
KNOWLEDGE FEED

Small things worth knowing.

[All] [Science] [History] [Technology] [Nature] [Language]

--------------------------------------------------

WHY SOME ROMAN CONCRETE GOT STRONGER WITH AGE

Ancient Engineering · 4 min

Short summary...

Read article →

--------------------------------------------------

THE MACHINE THAT COULD PREDICT ECLIPSES

Ancient Technology · 3 min

Short summary...

Read article →
```

Keep the design clean, editorial and calm.

Do not make it resemble Reddit.

Do not implement infinite scroll.

---

# 19. Article Page

Each article page should contain:

* title
* category
* date
* reading time
* tags
* article body
* sources
* link back to archive
* "Random article" button
* links to related articles

At the bottom:

```text
Read another
```

should lead to a randomly selected article.

---

# 20. Search

Implement client-side search.

Generate:

```text
search.json
```

containing:

```json
[
  {
    "id": "...",
    "title": "...",
    "category": "...",
    "summary": "...",
    "tags": [...]
  }
]
```

Use vanilla JavaScript to search this dataset.

Search should work without a backend.

---

# 21. Random Article

Implement a simple random article feature.

Do not make it personalized.

The same random pool should be available to every visitor.

---

# 22. RSS

Generate an RSS feed:

```text
feed.xml
```

containing recent published articles.

This is useful because the project is conceptually an alternative to a social feed.

The user should be able to subscribe through any RSS reader.

---

# 23. Configuration

Create:

```text
config/config.yaml
```

Example:

```yaml
site:
  title: "Knowledge Feed"
  description: "Small things worth knowing."
  author: "Knowledge Feed"
  base_url: ""

generation:
  articles_per_run: 1
  min_words: 300
  max_words: 700
  max_retries: 3
  review_enabled: true

openrouter:
  model: "openrouter/free"

content:
  avoid_recent_days: 30
  max_articles_homepage: 20
  max_articles_archive_page: 50
```

Environment variables should override secrets and machine-specific settings.

---

# 24. CLI

Create a CLI:

```text
python -m knowledge_feed
```

Support:

```text
python -m knowledge_feed generate
python -m knowledge_feed build
python -m knowledge_feed generate-and-build
python -m knowledge_feed validate
python -m knowledge_feed list-topics
```

Also support:

```text
python -m knowledge_feed generate --dry-run
```

Dry run should:

* select a topic
* print the selected topic
* call the LLM if explicitly requested
* not modify content files

Provide useful logging.

---

# 25. Local Development

Create:

```text
requirements.txt
```

or `pyproject.toml`.

Prefer modern `pyproject.toml`.

Support:

```text
python -m venv .venv
pip install -e .
```

Create:

```text
.env.example
```

containing:

```text
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
```

Do not commit `.env`.

Include `.gitignore`.

---

# 26. GitHub Actions

Create:

```text
.github/workflows/generate.yml
.github/workflows/deploy.yml
```

However, combine them into one workflow if that results in a cleaner architecture.

The preferred workflow is:

```text
scheduled/manual trigger
        ↓
checkout repository
        ↓
install Python
        ↓
install dependencies
        ↓
run generation
        ↓
commit generated content
        ↓
build site
        ↓
deploy GitHub Pages
```

Use a scheduled trigger.

Example:

```yaml
on:
  schedule:
    - cron: "0 7 * * *"
  workflow_dispatch:
```

Do not assume the exact cron time is important.

Allow manual execution from the GitHub Actions UI.

---

# 27. GitHub Secrets

The workflow must read:

```text
OPENROUTER_API_KEY
```

from:

```text
${{ secrets.OPENROUTER_API_KEY }}
```

Never print it.

Never write it to files.

Never commit it.

The README must explicitly explain how to create the secret.

---

# 28. GitHub Pages Deployment

Use GitHub's official Pages Actions:

```text
actions/configure-pages
actions/upload-pages-artifact
actions/deploy-pages
```

Use appropriate permissions:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

The generated website should be deployed as a Pages artifact.

Do not use a custom server.

GitHub Pages supports static files directly and is available on GitHub Free for public repositories. GitHub recommends Actions when using a custom build process.

---

# 29. Generated Content Commits

After successfully generating an article, commit it automatically.

Commit message format:

```text
content: add <slug>
```

Example:

```text
content: add roman-concrete-self-healing
```

Do not commit anything if generation fails.

Do not commit rejected articles unless they are explicitly stored for debugging.

---

# 30. Failure Handling

If OpenRouter is unavailable:

* workflow should fail clearly
* existing website should remain deployable
* do not destroy existing content
* do not create partial article files

If article generation fails:

* retry
* if retries fail, exit non-zero

If editorial review rejects the article:

* attempt regeneration
* do not publish the rejected article

If the GitHub Actions workflow fails after content generation but before deployment:

* the repository should remain in a consistent state
* avoid partially written files

---

# 31. Rate Limit Awareness

The free OpenRouter tier currently permits 50 requests/day.

The default workflow should require only a small number of requests per run.

Target:

```text
1 generation request
1 editorial request
```

Potentially:

```text
1 repair request
```

if structured output fails.

Never implement an uncontrolled generation loop.

Set a hard maximum number of API requests per run.

Example:

```yaml
generation:
  max_api_requests_per_run: 5
```

The program must stop when this limit is reached.

---

# 32. No Cost Requirement

The project must not require:

* paid hosting
* paid database
* paid search API
* paid analytics
* paid CDN
* paid AI API

Do not add dependencies that silently require payment.

The system should function with OpenRouter's free models.

The README must state that third-party free-tier limits can change.

---

# 33. Privacy

The website should not collect user data.

Do not add:

* Google Analytics
* tracking pixels
* advertising scripts
* fingerprinting
* cookies

Do not build user accounts.

No personally identifiable information should be stored.

Note in the README that GitHub Pages itself may log visitor information as part of GitHub's infrastructure/privacy policies.

---

# 34. Accessibility

The generated site should:

* use semantic HTML
* support keyboard navigation
* have visible focus states
* use proper heading hierarchy
* have sufficient contrast
* use responsive layouts
* work on mobile
* not depend on JavaScript for reading articles

---

# 35. Design Direction

Visual style:

* minimal
* editorial
* calm
* slightly academic
* modern
* readable

Avoid:

* Reddit-like cards everywhere
* social-media styling
* engagement counters
* excessive animations
* gamification
* huge hero images
* infinite scrolling
* clickbait typography

The article itself should be the visual focus.

---

# 36. Testing

Create tests using Python's standard testing framework or pytest.

At minimum test:

### Topic selection

* loads valid YAML
* rejects malformed configuration
* avoids recently used seeds
* rotates categories
* handles empty topic pools

### Article parsing

* valid frontmatter
* required fields
* invalid status
* malformed article

### Deduplication

* exact duplicate
* normalized duplicate
* obvious title duplicate
* unrelated titles

### Site generation

* homepage generated
* article page generated
* archive generated
* category pages generated
* RSS generated
* search index generated
* special HTML characters escaped

### OpenRouter client

Mock HTTP responses.

Test:

* successful request
* malformed response
* 429 retry
* 500 retry
* timeout
* missing API key

### End-to-end

Use a fake LLM response and verify:

```text
topic
→ generated article
→ validation
→ saved Markdown
→ static site
```

No test should make a real OpenRouter request.

---

# 37. Security

The code must:

* never expose API keys
* never execute generated content
* escape generated HTML
* sanitize URLs where practical
* avoid arbitrary file paths generated by the LLM
* generate slugs in Python rather than trusting model output
* prevent path traversal
* never execute Markdown as code

Treat all LLM output as untrusted input.

---

# 38. README

Generate a comprehensive but concise `README.md`.

It should explain:

## What this is

A small AI-generated knowledge feed.

## Requirements

* GitHub account
* OpenRouter account/API key
* Python 3.x for local development

## Initial setup

1. Create GitHub repository.
2. Copy repository contents.
3. Add `OPENROUTER_API_KEY` as GitHub Actions secret.
4. Edit `config/topics.yaml`.
5. Edit `config/config.yaml`.
6. Enable GitHub Pages with GitHub Actions.
7. Run workflow manually once.
8. Site will subsequently generate according to schedule.

## Local development

Show:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

and Windows equivalent.

Show:

```bash
python -m knowledge_feed build
```

and:

```bash
python -m knowledge_feed generate-and-build
```

## Customization

Explain where to edit:

```text
config/topics.yaml
config/config.yaml
src/knowledge_feed/prompts.py
site templates
CSS
```

---

# 39. Example Initial Topic Pool

Include a reasonably diverse starter `topics.yaml` so the project works immediately.

Categories should include approximately:

```text
Ancient Engineering
Strange Biology
Obscure History
Forgotten Technology
Linguistics
Geography
Astronomy
Mathematics
Archaeology
Everyday Objects
Medicine and Biology
Computer History
Transportation
Materials Science
Psychology and Perception
Natural Phenomena
Unusual Inventions
Scientific Discoveries
```

Each category should have at least 5–10 seed topics.

The user can replace these later.

---

# 40. Architecture Principle

Keep the implementation deliberately boring.

Do NOT introduce:

* React
* Next.js
* Docker
* Kubernetes
* PostgreSQL
* Redis
* vector databases
* embeddings
* microservices
* cloud functions
* authentication
* complex frontend frameworks

unless a concrete requirement later makes one necessary.

The entire project should be understandable by one technically competent hobbyist.

---

# 41. Suggested Repository Layout

Implement approximately:

```text
knowledge-feed/
│
├── .github/
│   └── workflows/
│       └── knowledge-feed.yml
│
├── config/
│   ├── config.yaml
│   └── topics.yaml
│
├── content/
│   └── articles/
│
├── src/
│   └── knowledge_feed/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── models.py
│       ├── openrouter.py
│       ├── prompts.py
│       ├── generator.py
│       ├── reviewer.py
│       ├── topic_selector.py
│       ├── deduplication.py
│       ├── content.py
│       ├── site.py
│       ├── rss.py
│       └── utils.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── article.html
│   ├── archive.html
│   ├── category.html
│   └── 404.html
│
├── static/
│   ├── style.css
│   └── app.js
│
├── tests/
│   ├── test_config.py
│   ├── test_topics.py
│   ├── test_deduplication.py
│   ├── test_content.py
│   ├── test_site.py
│   ├── test_openrouter.py
│   └── test_generation.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── AGENTS.md
```

The implementation may alter this structure if there is a strong technical reason, but should preserve the separation of:

```text
configuration
content
generation
validation
site generation
deployment
```

---

# 42. AGENTS.md

Create an `AGENTS.md` file for future Codex sessions.

It should tell Codex:

```text
# Project Instructions

This is a small personal knowledge-feed project.

Priorities:

1. Keep the system free to operate.
2. Keep the architecture simple.
3. Do not introduce infrastructure unnecessarily.
4. Preserve static GitHub Pages deployment.
5. Never commit secrets.
6. Treat LLM output as untrusted input.
7. Prefer deterministic Python code over unnecessary abstractions.
8. Keep prompts in prompts.py.
9. Keep generated content human-readable.
10. Do not introduce paid APIs without explicit user approval.
11. Run tests before completing changes.
12. Do not modify existing published articles unless explicitly requested.
```

---

# 43. Definition of Done

The implementation is complete when a fresh clone can be configured with approximately:

```text
1. GitHub repository
2. OPENROUTER_API_KEY secret
3. topics.yaml customization
```

and then:

```text
GitHub Actions
    ↓
selects topic
    ↓
generates article
    ↓
reviews article
    ↓
writes Markdown
    ↓
builds static website
    ↓
deploys GitHub Pages
```

without manual intervention.

A manual workflow dispatch must also work.

The repository must contain enough starter topics that the first generation works immediately.

---

# 44. Codex Implementation Instructions

Implement the entire project described above.

Do not merely provide pseudocode.

Create all required source files, configuration files, templates, tests and GitHub workflows.

Before finishing:

1. Run the test suite.
2. Run a local static-site build.
3. Run the generation pipeline using a mocked OpenRouter response.
4. Verify that generated HTML contains no unescaped user/model content.
5. Verify that no API key is committed or written to generated files.
6. Verify GitHub Actions YAML syntax.
7. Verify the README describes the actual implementation.
8. Verify the project works without any paid service.
9. Verify the scheduled workflow cannot exceed the configured API request limit.
10. Verify an empty article directory still produces a valid website.

Do not make real OpenRouter requests during automated tests.

If a design decision is ambiguous, choose the simplest implementation that satisfies the requirements.

Do not add features merely because they might be useful later.
