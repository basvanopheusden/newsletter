# newsletter

Utilities for working with arXiv papers.

## Getting recent cs.AI URLs

```
from newsletter.arxiv import get_recent_arxiv_urls

urls = get_recent_arxiv_urls()
print(urls[:5])
```

## Downloading recent papers

The script :mod:`fetch_recent_papers` downloads the latest cs.AI papers,
computes simple search scores and writes the results to ``papers.jsonl``:

```bash
python fetch_recent_papers.py
```

## Development

Install the package in editable mode and run the tests:

```bash
pip install -e .[test]
black -q .
pytest -q
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
