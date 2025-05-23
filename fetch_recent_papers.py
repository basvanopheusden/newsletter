#!/usr/bin/env python
"""Download recent arXiv cs.AI papers concurrently and save to JSONL."""
import asyncio
import json
from dataclasses import asdict

from newsletter.arxiv import get_recent_arxiv_urls
from newsletter.paper import Paper

OUTPUT_FILE = "papers.jsonl"

async def fetch_paper(url: str) -> Paper:
    """Fetch a single paper concurrently."""
    return await asyncio.to_thread(Paper.from_url, url)

async def main() -> None:
    urls = get_recent_arxiv_urls()
    tasks = [fetch_paper(url) for url in urls]
    papers = await asyncio.gather(*tasks)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        for paper in papers:
            json.dump(asdict(paper), fh)
            fh.write("\n")

if __name__ == "__main__":
    asyncio.run(main())
