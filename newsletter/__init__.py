"""Public package API for :mod:`newsletter`."""

from .arxiv import get_recent_arxiv_urls
from .paper import Paper

__all__ = ["get_recent_arxiv_urls", "Paper"]
