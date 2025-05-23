"""Representation of arXiv papers and helpers to retrieve their metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from html import unescape
from typing import List, Optional

import logging
import re
import requests


def _extract_meta(html: str, name: str) -> str | None:
    """Return the content of a ``citation_*`` meta tag if present."""

    pattern = rf'<meta[^>]+name=["\']{name}["\'][^>]+content=["\']([^"\']+)["\']'
    m = re.search(pattern, html, flags=re.IGNORECASE)
    return unescape(m.group(1)) if m else None


from googlesearch import search as google_search
import tweepy

logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """Metadata for an arXiv paper.

    Parameters
    ----------
    arxiv_url : str
        URL of the arXiv ``abs`` page.
    title : str
        Title of the paper.
    abstract : str
        Paper abstract.
    authors : List[str]
        List of author names.
    submission_date : date
        Date the paper was submitted.

    Instances are typically created via :meth:`from_url` which scrapes these
    fields from an arXiv HTML page.
    """

    arxiv_url: str
    title: str
    abstract: str
    authors: List[str]
    submission_date: date
    twitter_results: Optional[List[str]] = field(default=None)
    google_results: Optional[List[str]] = field(default=None)
    combined_score: float = field(default=0.0, init=False)

    @classmethod
    def from_url(cls, url: str) -> "Paper":
        """Fetch paper metadata from the given URL and return a :class:`Paper`.

        The function downloads the HTML from the arXiv ``abs`` page and
        extracts information from the ``citation_*`` meta tags which are
        consistently provided on arXiv pages.  Only a very small subset of
        fields are parsed (title, authors, abstract and submission date) as
        required by the :class:`Paper` dataclass.
        """

        # Retrieve the page content.  Tests patch ``requests.get`` to avoid
        # network access during unit tests.
        logger.info("Fetching %s", url)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
        logger.debug(
            "Received response (status %s) with %d characters",
            getattr(resp, "status_code", "unknown"),
            len(html),
        )

        # Title
        title = _extract_meta(html, "citation_title") or ""
        logger.debug("Parsed title: %s", title)

        # Abstract
        abstract = _extract_meta(html, "citation_abstract") or ""

        # Authors can appear multiple times. ``re.findall`` will collect them.
        authors_pattern = (
            r'<meta[^>]+name=["\']citation_author["\'][^>]+content=["\']([^"\']+)["\']'
        )
        authors = [
            unescape(a) for a in re.findall(authors_pattern, html, flags=re.IGNORECASE)
        ]
        logger.debug("Parsed %d authors", len(authors))

        # Submission date in format YYYY/MM/DD
        date_str = _extract_meta(html, "citation_date") or "1970/01/01"
        try:
            submission_date = date.fromisoformat(date_str.replace("/", "-"))
        except ValueError:
            submission_date = date.today()
        logger.debug("Parsed submission date: %s", submission_date)

        return cls(
            arxiv_url=url,
            title=title,
            abstract=abstract,
            authors=authors,
            submission_date=submission_date,
        )

    # ------------------------------------------------------------------
    # Search utilities
    # ------------------------------------------------------------------
    def query_twitter(self, client: tweepy.Client, max_results: int = 10) -> List[str]:
        """Search Twitter for the paper title or URL.

        Parameters
        ----------
        client:
            Initialized :class:`tweepy.Client` used to perform the search.
        max_results:
            Maximum number of tweets to retrieve.
        """

        query = f'"{self.title}" OR "{self.arxiv_url}"'
        response = client.search_recent_tweets(query=query, max_results=max_results)
        tweets = response.data or []
        self.twitter_results = [t.text for t in tweets]
        return self.twitter_results

    def query_google(self, num_results: int = 10) -> List[str]:
        """Search Google for the paper title or URL and store the results."""

        query = f'"{self.title}" OR "{self.arxiv_url}"'
        # ``google_search`` returns an iterator over result URLs
        results = list(google_search(query, num_results=num_results))
        self.google_results = results
        return results

    def search_result_counts(self) -> dict[str, int]:
        """Return a dictionary with the number of search results."""

        return {
            "twitter": len(self.twitter_results or []),
            "google": len(self.google_results or []),
        }

    # ------------------------------------------------------------------
    # Scoring utilities
    # ------------------------------------------------------------------
    def compute_score(self, mean_twitter: float, mean_google: float) -> float:
        """Compute and store the combined search score for this paper."""

        counts = self.search_result_counts()
        score = 0.0
        if mean_twitter:
            score += counts["twitter"] / mean_twitter
        if mean_google:
            score += counts["google"] / mean_google
        self.combined_score = score
        return score

    @classmethod
    def compute_scores(cls, papers: List["Paper"]) -> None:
        """Compute combined scores for all given papers."""

        if not papers:
            return

        total_twitter = sum(p.search_result_counts()["twitter"] for p in papers)
        total_google = sum(p.search_result_counts()["google"] for p in papers)
        mean_twitter = total_twitter / len(papers) if papers else 0
        mean_google = total_google / len(papers) if papers else 0

        for p in papers:
            p.compute_score(mean_twitter, mean_google)
