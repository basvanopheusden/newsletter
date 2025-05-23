import json
from datetime import date
import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

import fetch_recent_papers
from newsletter.paper import Paper


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
        "fetch_recent_papers.asdict", lambda p: {
            "arxiv_url": p.arxiv_url,
            "title": p.title,
            "abstract": p.abstract,
            "authors": p.authors,
            "submission_date": p.submission_date.isoformat(),
            "twitter_results": p.twitter_results,
            "google_results": p.google_results,
        }
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
