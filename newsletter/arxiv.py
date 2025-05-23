import re
from urllib.parse import urljoin

import requests

BASE_URL = "https://arxiv.org"
RECENT_URL = f"{BASE_URL}/list/cs.AI/recent?skip=0&show=2000"


def get_recent_arxiv_urls() -> list[str]:
    """Return a list of arXiv paper URLs from the recent cs.AI page."""
    response = requests.get(RECENT_URL)
    response.raise_for_status()
    pattern = re.compile(r'href="(/abs/[^\"]+)"')
    matches = pattern.findall(response.text)
    unique_paths = sorted(set(matches))
    return [urljoin(BASE_URL, path) for path in unique_paths]
