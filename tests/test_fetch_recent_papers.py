import asyncio
import json
from datetime import date
from unittest.mock import patch

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

    with patch.object(fetch_recent_papers, "OUTPUT_FILE", str(out)), \
         patch.object(fetch_recent_papers, "get_recent_arxiv_urls", return_value=["u1", "u2"]), \
         patch("fetch_recent_papers.Paper.from_url", side_effect=[p1, p2]):
        asyncio.run(fetch_recent_papers.main())

    lines = out.read_text().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["arxiv_url"] == "u2"
