from unittest.mock import Mock, patch

from newsletter.arxiv import get_recent_arxiv_urls, RECENT_URL


def test_get_recent_arxiv_urls_parses_links():
    html = """
    <html><body>
    <a href="/abs/1234.5678">paper1</a>
    <a href="/abs/2345.6789v2">paper2</a>
    <a href="/notabs/9999">ignore</a>
    </body></html>
    """
    mock_response = Mock()
    mock_response.text = html
    mock_response.raise_for_status = Mock()

    with patch("newsletter.arxiv.requests.get", return_value=mock_response) as mock_get:
        urls = get_recent_arxiv_urls()
        assert urls == [
            "https://arxiv.org/abs/1234.5678",
            "https://arxiv.org/abs/2345.6789v2",
        ]
        mock_get.assert_called_once_with(RECENT_URL, timeout=10)


def test_get_recent_arxiv_urls_dedup_and_sort():
    html = """
    <html><body>
    <a href="/abs/3456.7890v2">dup1</a>
    <a href="/abs/1234.5678">paper</a>
    <a href="/abs/3456.7890v2">dup2</a>
    </body></html>
    """
    mock_response = Mock()
    mock_response.text = html
    mock_response.raise_for_status = Mock()

    with patch("newsletter.arxiv.requests.get", return_value=mock_response):
        urls = get_recent_arxiv_urls()
        assert urls == [
            "https://arxiv.org/abs/1234.5678",
            "https://arxiv.org/abs/3456.7890v2",
        ]
