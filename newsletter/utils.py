from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import date
from html import unescape
from typing import TYPE_CHECKING, Callable

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from .paper import Paper

logger = logging.getLogger(__name__)


def extract_meta(soup: BeautifulSoup, name: str) -> str | None:
    """Return the content of a ``citation_*`` meta tag if present."""

    tag = soup.find("meta", attrs={"name": name})
    if tag and tag.has_attr("content"):
        content = unescape(tag["content"])
        logger.debug("Extracted %s: %s", name, content)
        return content
    logger.debug("Meta tag %s not found", name)
    return None


def serialize_paper(paper: "Paper", *, asdict_fn: Callable = asdict) -> dict:
    """Return a JSON-serialisable representation of ``paper``."""

    data = asdict_fn(paper)
    if isinstance(data.get("submission_date"), date):
        data["submission_date"] = data["submission_date"].isoformat()
    return data
