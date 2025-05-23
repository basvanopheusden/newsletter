#!/usr/bin/env python
"""Download recent arXiv cs.AI papers concurrently and save to JSONL."""
import asyncio
import json
from dataclasses import asdict
from datetime import date

from newsletter.arxiv import get_recent_arxiv_urls
from newsletter.paper import Paper

OUTPUT_FILE = "papers.jsonl"


def _serialize_paper(paper: Paper) -> dict:
    """Return a JSON-serialisable representation of ``paper``."""

    data = asdict(paper)
    if isinstance(data.get("submission_date"), date):
        data["submission_date"] = data["submission_date"].isoformat()
    return data


async def fetch_paper(url: str) -> Paper:
    """Fetch a single paper concurrently."""
    return await asyncio.to_thread(Paper.from_url, url)


async def main(output_file: str | None = None) -> None:
    """Download recent papers and write them to ``output_file``."""

    if output_file is None:
        output_file = OUTPUT_FILE

    urls = get_recent_arxiv_urls()
    tasks = [fetch_paper(url) for url in urls]
    papers = await asyncio.gather(*tasks)
    Paper.compute_scores(papers)
    papers.sort(key=lambda p: p.combined_score, reverse=True)

    with open(output_file, "w", encoding="utf-8") as fh:
        for paper in papers:
            json.dump(_serialize_paper(paper), fh)
            fh.write("\n")


if __name__ == "__main__":
    asyncio.run(main())
