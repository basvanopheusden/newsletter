import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import date
from unittest.mock import patch

import pytest

from newsletter.paper import Paper


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


def test_from_url_uses_get_and_raises_not_implemented():
    with patch("newsletter.paper.urllib.request.urlopen") as mock_get:
        mock_get.return_value.read.return_value = b""
        with pytest.raises(NotImplementedError):
            Paper.from_url("http://arxiv.org/abs/1234.5678")
        mock_get.assert_called_once_with("http://arxiv.org/abs/1234.5678")
