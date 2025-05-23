from datetime import date
from unittest.mock import patch

import pytest

from newsletter.paper import Paper


HTML_PAGE = """\
<!DOCTYPE html>
<html>
<head>
<meta name="citation_title" content="X-MAS: Towards Building Multi-Agent Systems with Heterogeneous LLMs" />
<meta name="citation_author" content="Ye, Rui" />
<meta name="citation_author" content="Liu, Xiangrui" />
<meta name="citation_author" content="Wu, Qimin" />
<meta name="citation_author" content="Pang, Xianghe" />
<meta name="citation_author" content="Yin, Zhenfei" />
<meta name="citation_author" content="Bai, Lei" />
<meta name="citation_author" content="Chen, Siheng" />
<meta name="citation_date" content="2025/05/22" />
<meta name="citation_abstract" content="LLM-based multi-agent systems (MAS) extend the capabilities of single LLMs by enabling cooperation among multiple specialized agents." />
</head>
<body></body>
</html>
"""


def test_create_paper():
    paper = Paper(
        arxiv_url="http://arxiv.org/abs/1234.5678",
        title="A Great Paper",
        abstract="An abstract",
        authors=["Alice", "Bob"],
        submission_date=date(2023, 1, 1),
    )
    assert paper.title == "A Great Paper"
    assert paper.arxiv_url == "http://arxiv.org/abs/1234.5678"
    assert paper.authors == ["Alice", "Bob"]
    assert paper.google_results is None


def test_from_url_parses_paper_metadata():
    with patch("newsletter.paper.requests.get") as mock_get:
        mock_get.return_value.text = HTML_PAGE
        mock_get.return_value.raise_for_status = lambda: None
        paper = Paper.from_url("http://arxiv.org/abs/1234.5678")
        mock_get.assert_called_once_with("http://arxiv.org/abs/1234.5678", timeout=10)

    assert (
        paper.title
        == "X-MAS: Towards Building Multi-Agent Systems with Heterogeneous LLMs"
    )
    assert paper.authors == [
        "Ye, Rui",
        "Liu, Xiangrui",
        "Wu, Qimin",
        "Pang, Xianghe",
        "Yin, Zhenfei",
        "Bai, Lei",
        "Chen, Siheng",
    ]
    assert paper.abstract == (
        "LLM-based multi-agent systems (MAS) extend the capabilities of single LLMs by "
        "enabling cooperation among multiple specialized agents."
    )
    assert paper.submission_date == date(2025, 5, 22)


def test_from_url_missing_date_defaults_to_epoch():
    html = """\
<!DOCTYPE html>
<html>
<head>
<meta name="citation_title" content="No Date" />
<meta name="citation_author" content="Author" />
<meta name="citation_abstract" content="No date available" />
</head>
<body></body>
</html>
"""

    with patch("newsletter.paper.requests.get") as mock_get:
        mock_get.return_value.text = html
        mock_get.return_value.raise_for_status = lambda: None
        paper = Paper.from_url("http://arxiv.org/abs/0000.0000")

    assert paper.submission_date == date(1970, 1, 1)
    assert paper.authors == ["Author"]


def test_from_url_invalid_date_uses_today():
    today = date.today()
    html = """\
<!DOCTYPE html>
<html>
<head>
<meta name="citation_title" content="Bad Date" />
<meta name="citation_author" content="Author" />
<meta name="citation_date" content="invalid-date" />
<meta name="citation_abstract" content="Invalid" />
</head>
<body></body>
</html>
"""

    with patch("newsletter.paper.requests.get") as mock_get:
        mock_get.return_value.text = html
        mock_get.return_value.raise_for_status = lambda: None
        paper = Paper.from_url("http://arxiv.org/abs/0000.0000")

    assert paper.submission_date == today


def test_from_url_invalid_date_uses_patched_today():
    fallback = date(1999, 12, 31)

    class FakeDate(date):
        @classmethod
        def today(cls):
            return fallback

    html = """\
<!DOCTYPE html>
<html>
<head>
<meta name="citation_title" content="Patched" />
<meta name="citation_author" content="Author" />
<meta name="citation_date" content="bad-date" />
<meta name="citation_abstract" content="Invalid" />
</head>
<body></body>
</html>
"""

    with patch("newsletter.paper.requests.get") as mock_get, patch(
        "newsletter.paper.date", FakeDate
    ):
        mock_get.return_value.text = html
        mock_get.return_value.raise_for_status = lambda: None
        paper = Paper.from_url("http://arxiv.org/abs/0000.0000")

    assert paper.submission_date == fallback


def test_query_google_and_counts():
    paper = Paper(
        arxiv_url="http://arxiv.org/abs/9999.9999",
        title="Searchable Paper",
        abstract="Test",
        authors=["Author"],
        submission_date=date(2023, 1, 1),
    )

    with patch(
        "newsletter.paper.google_search", return_value=["g1", "g2"]
    ) as mock_google:
        results = paper.query_google(num_results=2)
        mock_google.assert_called_once()
        assert results == ["g1", "g2"]
        assert paper.google_results == ["g1", "g2"]

    counts = paper.search_result_counts()
    assert counts == {"google": 2}


def test_compute_combined_scores():
    p1 = Paper(
        arxiv_url="u1",
        title="p1",
        abstract="",
        authors=[],
        submission_date=date(2023, 1, 1),
    )
    p2 = Paper(
        arxiv_url="u2",
        title="p2",
        abstract="",
        authors=[],
        submission_date=date(2023, 1, 1),
    )
    p1.google_results = ["g1"]
    p2.google_results = ["g1", "g2", "g3"]

    Paper.compute_scores([p1, p2])

    mean_google = (1 + 3) / 2
    expected_p1 = 1 / mean_google
    expected_p2 = 3 / mean_google

    assert pytest.approx(p1.combined_score) == expected_p1
    assert pytest.approx(p2.combined_score) == expected_p2
