import asyncio
import json
from datetime import date
from unittest.mock import patch

from pathlib import Path

import pytest

import fetch_recent_papers
from newsletter.paper import Paper


def test_main_sorts_by_score(tmp_path):
    out = tmp_path / "out.jsonl"

    p1 = Paper(
        arxiv_url="u1",
        title="p1",
        abstract="",
        authors=[],
        submission_date=date(2023, 1, 1),
    )
    p2 = Paper(
        arxiv_url="u2",
        title="p2",
        abstract="",
        authors=[],
        submission_date=date(2023, 1, 1),
    )
    p1.twitter_results = ["t1", "t2"]
    p1.google_results = ["g1"]
    p2.twitter_results = ["t1"]
    p2.google_results = ["g1", "g2", "g3"]

    with patch.object(fetch_recent_papers, "OUTPUT_FILE", str(out)), patch.object(
        fetch_recent_papers, "get_recent_arxiv_urls", return_value=["u1", "u2"]
    ), patch("fetch_recent_papers.Paper.from_url", side_effect=[p1, p2]):
        asyncio.run(fetch_recent_papers.main())

    lines = out.read_text().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["arxiv_url"] == "u2"


def test_fetch_paper_calls_from_url():
    sample = Paper(
        arxiv_url="u",
        title="t",
        abstract="",
        authors=[],
        submission_date=date(2024, 1, 1),
    )
    with patch("fetch_recent_papers.Paper.from_url", return_value=sample) as mock:
        result = asyncio.run(fetch_recent_papers.fetch_paper("u"))
    assert result is sample
    mock.assert_called_once_with("u")


def test_main_writes_jsonl(tmp_path: Path):
    outfile = tmp_path / "out.jsonl"

    sample = Paper(
        arxiv_url="url1",
        title="Title",
        abstract="Abst",
        authors=["A"],
        submission_date=date(2024, 1, 1),
    )

    with patch("fetch_recent_papers.OUTPUT_FILE", str(outfile)), patch(
        "fetch_recent_papers.get_recent_arxiv_urls", return_value=["url1"]
    ) as mock_urls, patch(
        "fetch_recent_papers.Paper.from_url", return_value=sample
    ) as mock_from, patch(
        "fetch_recent_papers.asdict",
        lambda p: {
            "arxiv_url": p.arxiv_url,
            "title": p.title,
            "abstract": p.abstract,
            "authors": p.authors,
            "submission_date": p.submission_date.isoformat(),
            "twitter_results": p.twitter_results,
            "google_results": p.google_results,
        },
    ):
        asyncio.run(fetch_recent_papers.main())

    mock_urls.assert_called_once()
    mock_from.assert_called_once_with("url1")

    data = [json.loads(line) for line in outfile.read_text().splitlines()]
    assert data == [
        {
            "arxiv_url": "url1",
            "title": "Title",
            "abstract": "Abst",
            "authors": ["A"],
            "submission_date": "2024-01-01",
            "twitter_results": None,
            "google_results": None,
        }
    ]
