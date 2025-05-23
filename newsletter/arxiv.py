"""Fetch and parse listings from the arXiv website.

The primary entry point is :func:`get_recent_arxiv_urls` which returns the
fully-qualified URLs of papers appearing on the recent cs.AI listing page.
"""

import re
from urllib.parse import urljoin

import requests

BASE_URL = "https://arxiv.org"
RECENT_URL = f"{BASE_URL}/list/cs.AI/recent?skip=0&show=2000"
# Accept both single and double quoted href attributes
ABS_LINK_RE = re.compile(r"href=['\"](/abs/[^'\"]+)['\"]")

# User agent to avoid being blocked by arXiv when running outside tests
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; newsletter/1.0)"}


def get_recent_arxiv_urls() -> list[str]:
    """Return a sorted list of unique arXiv paper URLs from the cs.AI listing."""
    response = requests.get(RECENT_URL, timeout=10, headers=HEADERS)
    response.raise_for_status()
    matches = ABS_LINK_RE.findall(response.text)
    unique_paths = sorted(set(matches))
    return [urljoin(BASE_URL, path) for path in unique_paths]
