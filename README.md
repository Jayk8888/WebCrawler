# Concurrent Web Crawler

A small Python web crawler that uses `concurrent.futures.ThreadPoolExecutor` to fetch pages concurrently while keeping requests bounded by a configurable rate limit. It stays on the starting domain, follows HTML links, and reports crawl performance and failures.

## Features

- Concurrent page fetching with a configurable worker pool
- Separate limit for simultaneous HTTP requests
- Same-domain link filtering and duplicate URL prevention
- Configurable crawl depth and page cap
- Handles timeouts, HTTP errors, connection failures, and non-HTML responses
- Reports elapsed time, throughput, average fetch time, and error counts
- Includes a single-threaded versus multi-threaded comparison utility

## Requirements

- Python 3.9 or later
- [`requests`](https://pypi.org/project/requests/)
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)

Install the dependencies:

```bash
python -m pip install requests beautifulsoup4
```

## Usage

Run the crawler with the default target (`https://books.toscrape.com`):

```bash
python main.py
```

Or provide a URL and limits:

```bash
python main.py https://example.com --max-depth 2 --max-pages 30 --workers 8 --max-concurrent 4
```

Options:

| Option | Default | Description |
| --- | --- | --- |
| `url` | `https://books.toscrape.com` | Starting URL |
| `--max-depth` | `2` | Maximum link depth to crawl |
| `--max-pages` | `30` | Maximum number of unique URLs to visit |
| `--workers` | `8` | Number of threads in the worker pool |
| `--max-concurrent` | `4` | Maximum simultaneous HTTP requests |

The worker count controls available threads; `--max-concurrent` independently caps requests in flight. Keeping the latter modest helps avoid overloading a target website.

## Compare concurrency

Use `compare.py` to run the same crawl once with one worker and once with multiple workers:

```bash
python compare.py https://books.toscrape.com --max-depth 2 --max-pages 100 --workers 20 --max-concurrent 10
```

The comparison prints the elapsed time, crawled pages, and calculated speedup. With a page cap, concurrent and sequential runs can discover links in different orders, so their exact page counts may differ.

## Notes

- The crawler only follows links whose network location matches the start URL.
- Only `text/html` responses are parsed.
- URLs with fragment-only links, `mailto:`, `tel:`, JavaScript links, Wikipedia edit links, and red links are ignored.
- Please respect a site's terms of service and `robots.txt`; use conservative request limits.
