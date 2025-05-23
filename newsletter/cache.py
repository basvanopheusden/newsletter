"""Simple JSON-based caching utilities for newsletter."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

def _cache_file() -> Path | None:
    """Return path to the paper cache file or ``None`` if caching is disabled."""
    dir_ = os.getenv("NEWSLETTER_CACHE_DIR")
    if not dir_:
        return None
    return Path(dir_) / "papers.json"


def _load_cache(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = _cache_file()
    if path is None or not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError:
        return {}


def _save_cache(path: Path | None, data: dict[str, Any]) -> None:
    if path is None:
        path = _cache_file()
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


_paper_cache: dict[str, Any] | None = None
_cache_path: Path | None = None


def get_paper(url: str) -> dict[str, Any] | None:
    """Return cached paper data for ``url`` if available."""
    global _paper_cache
    path = _cache_file()
    if path is None:
        return None
    global _cache_path
    if _paper_cache is None or _cache_path != path:
        _paper_cache = _load_cache(path)
        _cache_path = path
    return _paper_cache.get(url)


def set_paper(url: str, data: dict[str, Any]) -> None:
    """Store ``data`` for ``url`` in the cache."""
    global _paper_cache
    path = _cache_file()
    if path is None:
        return
    global _cache_path
    if _paper_cache is None or _cache_path != path:
        _paper_cache = _load_cache(path)
        _cache_path = path
    _paper_cache[url] = data
    _save_cache(path, _paper_cache)
