# GitHubScraper

A threaded GitHub repository scraper for fetching repository trees and content using multiple tokens to handle rate limits.

## Features

- Multi-threaded scraping of GitHub repositories.
- Handles GitHub API rate limits by cycling through provided tokens.
- Fetches repository trees and blobs.
- Saves structured tree data and content to disk.
- Customizable query, output directory, and threading options.

## Usage

```python
from ghtoolscraper_rchotacode import ThreadedScraper

tokens = ["ghp_XXXX", "ghp_YYYY"]  # List of GitHub tokens
scraper = ThreadedScraper(
    query="language:python",
    target="README.md",
    tokens=tokens,
    per_page=10,
    max_threads=5,
    output_dir="./repos"
)
scraper.scrape(page_start=1)
```

## Requirements

- Python 3.7+
- `ghtoolscraper_rchotacode` package installed through the pyproject.toml

## Configuration

- `query`: GitHub search query.
- `target`: File or directory to target in the repo tree.
- `tokens`: List of GitHub API tokens.
- `per_page`: Results per page (default: 10).
- `max_threads`: Number of concurrent threads (default: 5).
- `output_dir`: Directory to save results (default: `./repos`).
- `timeout`: Delay between requests (default: 1 second).

## Output

- Repository trees and content are saved in the specified output directory as JSON files.

## License

MIT
