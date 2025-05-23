"""Representation of arXiv papers and helpers to retrieve their metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from html import unescape
from typing import List, Optional

import logging
import requests
from bs4 import BeautifulSoup


def _extract_meta(soup: BeautifulSoup, name: str) -> str | None:
    """Return the content of a ``citation_*`` meta tag if present."""

    tag = soup.find("meta", attrs={"name": name})
    if tag and tag.has_attr("content"):
        content = unescape(tag["content"])
        logger.debug("Extracted %s: %s", name, content)
        return content
    logger.debug("Meta tag %s not found", name)
    return None


from googlesearch import search as google_search
from requests.exceptions import HTTPError

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
        soup = BeautifulSoup(html, "html.parser")
        logger.debug(
            "Received response (status %s) with %d characters",
            getattr(resp, "status_code", "unknown"),
            len(html),
        )

        # Title
        title = _extract_meta(soup, "citation_title") or ""
        logger.debug("Parsed title: %s", title)

        # Abstract
        abstract = _extract_meta(soup, "citation_abstract") or ""

        # Authors can appear multiple times.
        authors = [
            unescape(tag["content"])
            for tag in soup.find_all("meta", attrs={"name": "citation_author"})
            if tag.has_attr("content")
        ]
        logger.debug("Parsed %d authors", len(authors))

        # Submission date in format YYYY/MM/DD
        date_str = _extract_meta(soup, "citation_date") or "1970/01/01"
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

    def query_google(self, num_results: int = 10) -> List[str]:
        """Search Google for the paper title or URL and store the results."""

        query = f'"{self.title}" OR "{self.arxiv_url}"'
        logger.info("Searching Google for '%s'", self.title)
        try:
            # ``google_search`` returns an iterator over result URLs
            results = list(google_search(query, num_results=num_results))
        except HTTPError as exc:
            logger.warning("Google search failed for %s: %s", self.title, exc)
            results = []
        self.google_results = results
        logger.debug("Found %d Google results", len(results))
        return results

    def search_result_counts(self) -> dict[str, int]:
        """Return a dictionary with the number of search results."""
        counts = {
            "google": len(self.google_results or []),
        }
        logger.debug("Search result counts: %s", counts)
        return counts

    # ------------------------------------------------------------------
    # Scoring utilities
    # ------------------------------------------------------------------
    def compute_score(self, mean_google: float) -> float:
        """Compute and store the search score for this paper."""

        counts = self.search_result_counts()
        score = counts["google"] / mean_google if mean_google else 0.0
        self.combined_score = score
        logger.debug(
            "Computed score %.3f for %s (google=%d)",
            score,
            self.arxiv_url,
            counts["google"],
        )
        return score

    @classmethod
    def compute_scores(cls, papers: List["Paper"]) -> None:
        """Compute search scores for all given papers."""

        if not papers:
            return

        total_google = sum(p.search_result_counts()["google"] for p in papers)
        mean_google = total_google / len(papers) if papers else 0

        logger.info(
            "Computing scores for %d papers (mean_google=%.3f)",
            len(papers),
            mean_google,
        )

        for p in papers:
            p.compute_score(mean_google)
