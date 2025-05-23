import datetime
from bs4 import BeautifulSoup

from newsletter.utils import extract_meta, serialize_paper
from newsletter.paper import Paper


def test_extract_meta_returns_unescaped():
    html = "<meta name='citation_title' content='A &amp; B'>"
    soup = BeautifulSoup(f"<html><head>{html}</head></html>", "html.parser")
    assert extract_meta(soup, "citation_title") == "A & B"


def test_extract_meta_missing_returns_none():
    soup = BeautifulSoup("<html></html>", "html.parser")
    assert extract_meta(soup, "citation_author") is None


def test_serialize_paper_converts_date():
    p = Paper(
        arxiv_url="u",
        title="t",
        abstract="a",
        authors=[],
        submission_date=datetime.date(2024, 1, 1),
    )
    p.google_results = ["g"]
    data = serialize_paper(p)
    assert data["submission_date"] == "2024-01-01"
    assert data["google_results"] == ["g"]
