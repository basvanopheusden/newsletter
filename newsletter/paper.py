from __future__ import annotations

from dataclasses import dataclass
from datetime import date
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
        """Fetch paper metadata from the given URL and create a Paper.

        This is a stub implementation which performs the GET request but
        does not yet parse the response.
        """
        # Perform the request to retrieve the paper metadata
        urllib.request.urlopen(url)
        # Parsing of the response is not yet implemented
        raise NotImplementedError
