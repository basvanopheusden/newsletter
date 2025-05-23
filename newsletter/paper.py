from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import unescape
from typing import List

import urllib.request


@dataclass
class Paper:
    arxiv_url: str
    title: str
    abstract: str
    authors: List[str]
    submission_date: date

    @classmethod
    def from_url(cls, url: str) -> "Paper":
        """Fetch paper metadata from the given URL and return a :class:`Paper`.

        The function downloads the HTML from the arXiv ``abs`` page and
        extracts information from the ``citation_*`` meta tags which are
        consistently provided on arXiv pages.  Only a very small subset of
        fields are parsed (title, authors, abstract and submission date) as
        required by the :class:`Paper` dataclass.
        """

        # Retrieve the page content.  Tests patch ``urllib.request.urlopen`` so
        # we stick with ``urllib`` rather than using ``requests``.
        resp = urllib.request.urlopen(url)
        html = resp.read().decode("utf-8", errors="ignore")

        # Helper function to extract a single meta tag value using a regular
        # expression.  The meta tags of interest have the form:
        #   <meta name="citation_title" content="..." />
        import re

        def extract(name: str) -> str | None:
            pattern = rf'<meta[^>]+name=["\']{name}["\'][^>]+content=["\']([^"\']+)["\']'
            m = re.search(pattern, html, flags=re.IGNORECASE)
            return unescape(m.group(1)) if m else None

        # Title
        title = extract("citation_title") or ""

        # Abstract
        abstract = extract("citation_abstract") or ""

        # Authors can appear multiple times. ``re.findall`` will collect them.
        authors_pattern = r'<meta[^>]+name=["\']citation_author["\'][^>]+content=["\']([^"\']+)["\']'
        authors = [unescape(a) for a in re.findall(authors_pattern, html, flags=re.IGNORECASE)]

        # Submission date in format YYYY/MM/DD
        date_str = extract("citation_date") or "1970/01/01"
        try:
            submission_date = date.fromisoformat(date_str.replace("/", "-"))
        except ValueError:
            submission_date = date.today()

        return cls(
            arxiv_url=url,
            title=title,
            abstract=abstract,
            authors=authors,
            submission_date=submission_date,
        )
