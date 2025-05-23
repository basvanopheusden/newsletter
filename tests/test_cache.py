import json
import os
from newsletter import cache
from pathlib import Path
from unittest.mock import patch


def test_cache_file_env_none(monkeypatch):
    monkeypatch.delenv("NEWSLETTER_CACHE_DIR", raising=False)
    assert cache._cache_file() is None


def test_cache_file_returns_path(tmp_path, monkeypatch):
    monkeypatch.setenv("NEWSLETTER_CACHE_DIR", str(tmp_path))
    assert cache._cache_file() == tmp_path / "papers.json"


def test_load_cache_invalid_json(tmp_path):
    f = tmp_path / "papers.json"
    f.write_text("{ bad json")
    assert cache._load_cache(f) == {}


def test_set_and_get_paper_roundtrip(tmp_path):
    env = {"NEWSLETTER_CACHE_DIR": str(tmp_path)}
    data = {"title": "T", "submission_date": "2024-01-01"}
    with patch.dict(os.environ, env):
        cache.set_paper("u", data)
        assert cache.get_paper("u") == data
