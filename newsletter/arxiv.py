"""Fetch and parse listings from the arXiv website.

The primary entry point is :func:`get_recent_arxiv_urls` which returns the
fully-qualified URLs of papers appearing on the recent cs.AI listing page.
"""

import re
from urllib.parse import urljoin

import requests

BASE_URL = "https://arxiv.org"
RECENT_URL = f"{BASE_URL}/list/cs.AI/recent?skip=0&show=2000"
ABS_LINK_RE = re.compile(r'href="(/abs/[^\"]+)"')


def get_recent_arxiv_urls() -> list[str]:
    """Return a sorted list of unique arXiv paper URLs from the cs.AI listing."""
    response = requests.get(RECENT_URL, timeout=10)
    response.raise_for_status()
    matches = ABS_LINK_RE.findall(response.text)
    unique_paths = sorted(set(matches))
    return [urljoin(BASE_URL, path) for path in unique_paths]
