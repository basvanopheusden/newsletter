#!/usr/bin/env python
"""Download recent arXiv cs.AI papers concurrently and save to JSONL."""
import asyncio
import json
import logging
import os
from dataclasses import asdict
from datetime import date

from newsletter.arxiv import get_recent_arxiv_urls
from newsletter.paper import Paper
import tweepy

logger = logging.getLogger(__name__)

OUTPUT_FILE = "papers.jsonl"


def _serialize_paper(paper: Paper) -> dict:
    """Return a JSON-serialisable representation of ``paper``."""

    data = asdict(paper)
    if isinstance(data.get("submission_date"), date):
        data["submission_date"] = data["submission_date"].isoformat()
    return data


def _create_twitter_client() -> tweepy.Client | None:
    """Return a Tweepy client initialized from ``TWITTER_BEARER_TOKEN``."""

    token = os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        logger.info("Twitter token not provided; skipping Twitter searches")
        return None
    return tweepy.Client(bearer_token=token)


async def fetch_paper(
    url: str,
    *,
    twitter_client: tweepy.Client | None = None,
    google_results: int = 10,
    twitter_results: int = 10,
) -> Paper:
    """Fetch a single paper concurrently and query search engines."""

    paper = await asyncio.to_thread(Paper.from_url, url)
    await asyncio.to_thread(paper.query_google, num_results=google_results)
    if twitter_client is not None:
        await asyncio.to_thread(paper.query_twitter, twitter_client, twitter_results)
    return paper


async def main(
    output_file: str | None = None,
    *,
    twitter_client: tweepy.Client | None = None,
) -> None:
    """Download recent papers and write them to ``output_file``."""

    if output_file is None:
        output_file = OUTPUT_FILE

    logger.info("Fetching recent arXiv URLs")
    urls = get_recent_arxiv_urls()
    logger.info("Retrieved %d URLs", len(urls))

    if twitter_client is None:
        twitter_client = _create_twitter_client()

    logger.info("Fetching paper metadata")
    tasks = [fetch_paper(url, twitter_client=twitter_client) for url in urls]
    papers = await asyncio.gather(*tasks)
    logger.info("Fetched %d papers", len(papers))
    Paper.compute_scores(papers)
    papers.sort(key=lambda p: p.combined_score, reverse=True)

    with open(output_file, "w", encoding="utf-8") as fh:
        for paper in papers:
            json.dump(_serialize_paper(paper), fh)
            fh.write("\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
