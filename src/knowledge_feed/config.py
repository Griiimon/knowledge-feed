from __future__ import annotations

import json
import os
from pathlib import Path


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE entries without replacing exported variables.

    GitHub Actions supplies secrets through its environment, while local runs
    commonly keep the same values in an ignored ``.env`` file.
    """
    if not path.is_file():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not key.isidentifier():
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def load_config(root: Path) -> dict:
    load_dotenv(root / ".env")
    config = load_json(root / "config/config.json")
    config.setdefault("openrouter", {})["model"] = os.getenv(
        "OPENROUTER_MODEL", config.get("openrouter", {}).get("model", "openrouter/free")
    )
    return config


def load_topics(root: Path) -> list[dict]:
    data = load_json(root / "config/topics.json")
    categories = data.get("categories")
    if not isinstance(categories, list) or not categories:
        raise ValueError("topics.json needs a non-empty categories list")
    for category in categories:
        if (
            not isinstance(category, dict)
            or not all(category.get(key) for key in ("name", "description", "seeds"))
            or not isinstance(category["seeds"], list)
        ):
            raise ValueError(
                "each category requires name, description, and a non-empty seeds list"
            )
    return categories
