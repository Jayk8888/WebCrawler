import argparse
import time

from main import Crawler


def run_once(url, max_depth, max_pages, num_workers, max_concurrent):
    start = time.time()
    crawler = Crawler(
        start_url=url,
        max_depth=max_depth,
        max_pages=max_pages,
        num_workers=num_workers,
        max_concurrent=max_concurrent,
    )
    visited, pages_crawled = crawler.run()
    elapsed = time.time() - start
    return elapsed, pages_crawled, crawler.error_counts


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare single-threaded (workers=1) vs multi-threaded crawling."
    )
    parser.add_argument("url", nargs="?", default="https://books.toscrape.com")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--workers", type=int, default=20,
                         help="Worker count for the multi-threaded run (default: 20)")
    parser.add_argument("--max-concurrent", type=int, default=10,
                         help="Rate limit for the multi-threaded run (default: 10)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print(f"Comparing on: {args.url}")
    print(f"max_depth={args.max_depth}, max_pages={args.max_pages}\n")

    print("=" * 60)
    print("Run 1: single-threaded (workers=1, max_concurrent=1)")
    print("=" * 60)
    single_elapsed, single_pages, single_errors = run_once(
        args.url, args.max_depth, args.max_pages,
        num_workers=1, max_concurrent=1,
    )
    print(f"\nTime elapsed: {single_elapsed:.2f}s | Pages: {single_pages}\n")

    print("=" * 60)
    print(f"Run 2: multi-threaded (workers={args.workers}, max_concurrent={args.max_concurrent})")
    print("=" * 60)
    multi_elapsed, multi_pages, multi_errors = run_once(
        args.url, args.max_depth, args.max_pages,
        num_workers=args.workers, max_concurrent=args.max_concurrent,
    )
    print(f"\nTime elapsed: {multi_elapsed:.2f}s | Pages: {multi_pages}\n")

    print("=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Single-threaded : {single_elapsed:.2f}s  ({single_pages} pages)")
    print(f"Multi-threaded  : {multi_elapsed:.2f}s  ({multi_pages} pages)")

    if multi_elapsed > 0:
        speedup = single_elapsed / multi_elapsed
        print(f"\nSpeedup: {speedup:.2f}x faster with {args.workers} workers")

    if single_pages != multi_pages:
        print(
            f"\nNote: page counts differ ({single_pages} vs {multi_pages}). "
            "Expected -- concurrent crawling discovers/visits links in a "
            "different order than strict single-threaded order, so with "
            "the same max_pages cap the exact set of pages can differ "
            "slightly. Not a bug."
        )
