import json
from pathlib import Path
from unittest.mock import patch

import pytest

from knowledge_feed.content import load_article, save_article
from knowledge_feed.config import load_config
from knowledge_feed.deduplication import is_duplicate
from knowledge_feed.models import Article
from knowledge_feed.openrouter import OpenRouterClient, OpenRouterError
from knowledge_feed.site import build_site
from knowledge_feed.topic_selector import select_topic


def article(**overrides):
    base = dict(
        id="roman-concrete",
        title="Why Roman Concrete Heals Cracks",
        category="Ancient Engineering",
        date="2026-09-01",
        reading_time=2,
        seed="Roman concrete",
        tags=["rome"],
        status="published",
        body="Hello **world**.",
        summary="A summary.",
        sources=[],
    )
    base.update(overrides)
    return Article(**base)


def test_duplicate_detection():
    assert is_duplicate("Roman concrete", "Different title", [article()])
    assert is_duplicate("Other", "How Roman Concrete Heals Cracks", [article()])
    assert not is_duplicate("Pulsars", "How Pulsars Keep Time", [article()])


def test_topic_rotation():
    categories = [
        {"name": "A", "description": "a", "seeds": ["used", "fresh"]},
        {"name": "B", "description": "b", "seeds": ["new"]},
    ]
    chosen = select_topic(categories, [article(category="A", seed="used")], 999)
    assert chosen.category == "B"


def test_article_validation(tmp_path):
    path = tmp_path / "x.md"
    path.write_text(
        '---\n{"id": "x", "title": "T", "category": "C", "date": "2026-01-01", '
        '"reading_time": 1, "seed": "S", "tags": ["x"], "status": "published"}'
        "\n---\n\nBody"
    )
    assert load_article(path).title == "T"


def test_save_article_uses_json_frontmatter(tmp_path):
    path = save_article(article(), tmp_path)
    frontmatter = path.read_text().split("---\n", 2)[1]
    assert json.loads(frontmatter)["title"] == "Why Roman Concrete Heals Cracks"
    assert load_article(path) == article()


def test_site_escapes_model_content(tmp_path):
    root = tmp_path
    (root / "config").mkdir()
    (root / "content/articles").mkdir(parents=True)
    (root / "templates").mkdir()
    (root / "static").mkdir()
    source = Path(__file__).parents[1]
    for filename in ("config/config.json",):
        (root / filename).write_text((source / filename).read_text())
    for directory in ("templates", "static"):
        for file in (source / directory).iterdir():
            (root / directory / file.name).write_text(file.read_text())
    (root / "content/articles/x.md").write_text(
        '---\n{"id": "x", "title": "<script>x</script>", "category": "C", '
        '"date": "2026-01-01", "reading_time": 1, "seed": "S", "tags": ["x"], '
        '"status": "published", "summary": "<b>bad</b>"}\n---\n\n<script>alert(1)</script>'
    )
    output = build_site(root)
    text = (output / "articles/x/index.html").read_text()
    assert "<script>alert" not in text and "&lt;script&gt;" in text


def test_generation_with_fake_client():
    from knowledge_feed.generator import generate_article
    from knowledge_feed.models import Topic

    class FakeClient:
        def __init__(self):
            self.calls = 0

        def chat(self, prompt):
            self.calls += 1
            if self.calls == 1:
                return json.dumps(
                    {
                        "title": "A focused topic",
                        "summary": "Brief summary",
                        "body_markdown": "word " * 300,
                        "tags": ["test"],
                        "sources": [{"title": "Reference", "url": "https://example.com"}],
                    }
                )
            return json.dumps(
                {"approved": True, "quality_score": 8, "issues": [], "suggested_changes": []}
            )

    result = generate_article(
        FakeClient(),
        Topic("Test", "test topic", "seed"),
        {"min_words": 300, "max_words": 700, "review_enabled": True, "approval_threshold": 1},
        5,
    )
    assert result.status == "published" and result.reading_time == 2


def test_openrouter_retries_when_response_has_no_message_content():
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def read(self):
            return json.dumps(self.payload).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    responses = [
        Response({"choices": [{"message": {"content": None}}]}),
        Response({"choices": [{"message": {"content": "valid response"}}]}),
    ]
    client = OpenRouterClient(api_key="test-key", model="test-model", retries=1)
    with patch("knowledge_feed.openrouter.request.urlopen", side_effect=responses) as urlopen, patch(
        "knowledge_feed.openrouter.time.sleep"
    ):
        assert client.chat("prompt") == "valid response"
    assert urlopen.call_count == 2


def test_openrouter_raises_clear_error_for_missing_message_content():
    class Response:
        def read(self):
            return b'{"choices": [{"message": {"content": null}}]}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    client = OpenRouterClient(api_key="test-key", model="test-model", retries=0)
    with patch("knowledge_feed.openrouter.request.urlopen", return_value=Response()):
        with pytest.raises(OpenRouterError, match="did not include assistant message content"):
            client.chat("prompt")


def test_load_config_reads_local_dotenv_without_overriding_environment(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "config/config.json").write_text(
        '{"openrouter": {"model": "configured-model"}}', encoding="utf-8"
    )
    (tmp_path / ".env").write_text(
        "# Local development credentials\n"
        "OPENROUTER_API_KEY='local-key'\n"
        "OPENROUTER_MODEL=local-model\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_MODEL", "shell-model")

    config = load_config(tmp_path)

    assert OpenRouterClient().api_key == "local-key"
    assert config["openrouter"]["model"] == "shell-model"
