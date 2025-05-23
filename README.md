# newsletter

Utilities for working with arXiv papers.

## Getting recent cs.AI URLs

```
from newsletter.arxiv import get_recent_arxiv_urls

urls = get_recent_arxiv_urls()
print(urls[:5])
```

## Development

Install the package in editable mode and run the tests:

```bash
pip install -e .[test]
pytest -q
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
