#!/usr/bin/env python
"""Download recent arXiv cs.AI papers concurrently and save to JSONL."""
import asyncio
import json
import logging
from dataclasses import asdict

from newsletter.arxiv import get_recent_arxiv_urls
from newsletter.paper import Paper
from newsletter.utils import serialize_paper

logger = logging.getLogger(__name__)

OUTPUT_FILE = "papers.jsonl"



async def fetch_paper(
    url: str,
    *,
    google_results: int = 10,
) -> Paper:
    """Fetch a single paper concurrently and query search engines."""

    paper = await asyncio.to_thread(Paper.from_url, url)
    await asyncio.to_thread(paper.query_google, num_results=google_results)
    return paper


async def main(
    output_file: str | None = None,
) -> None:
    """Download recent papers and write them to ``output_file``."""

    if output_file is None:
        output_file = OUTPUT_FILE

    logger.info("Fetching recent arXiv URLs")
    urls = get_recent_arxiv_urls()
    logger.info("Retrieved %d URLs", len(urls))

    logger.info("Fetching paper metadata")
    tasks = [fetch_paper(url) for url in urls]
    papers = await asyncio.gather(*tasks)
    logger.info("Fetched %d papers", len(papers))
    logger.info("Computing scores")
    Paper.compute_scores(papers)
    papers.sort(key=lambda p: p.combined_score, reverse=True)
    logger.debug("Top paper: %s", papers[0].arxiv_url if papers else "none")

    with open(output_file, "w", encoding="utf-8") as fh:
        for paper in papers:
            json.dump(serialize_paper(paper, asdict_fn=asdict), fh)
            fh.write("\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
