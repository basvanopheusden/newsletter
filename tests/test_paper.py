import os, sys
from datetime import date
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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


def test_from_url_parses_paper_metadata():
    with patch("newsletter.paper.urllib.request.urlopen") as mock_get:
        mock_get.return_value.read.return_value = HTML_PAGE.encode()
        paper = Paper.from_url("http://arxiv.org/abs/1234.5678")
        mock_get.assert_called_once_with("http://arxiv.org/abs/1234.5678")

    assert paper.title == "X-MAS: Towards Building Multi-Agent Systems with Heterogeneous LLMs"
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
