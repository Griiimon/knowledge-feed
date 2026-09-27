from __future__ import annotations
from pathlib import Path
import os, yaml

def load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc: raise ValueError(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict): raise ValueError(f"{path} must contain a mapping")
    return data

def load_config(root: Path) -> dict:
    config = load_yaml(root / "config/config.yaml")
    config.setdefault("openrouter", {})["model"] = os.getenv("OPENROUTER_MODEL", config.get("openrouter", {}).get("model", "openrouter/free"))
    return config

def load_topics(root: Path) -> list[dict]:
    data = load_yaml(root / "config/topics.yaml")
    categories = data.get("categories")
    if not isinstance(categories, list) or not categories: raise ValueError("topics.yaml needs a non-empty categories list")
    for category in categories:
        if not isinstance(category, dict) or not all(category.get(k) for k in ("name", "description", "seeds")) or not isinstance(category["seeds"], list):
            raise ValueError("each category requires name, description, and a non-empty seeds list")
    return categories
