import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from crawler import fetch_page, extract_links, is_same_domain, get_domain

class Crawler:

    def __init__(self, start_url, max_depth, max_pages, num_workers, max_concurrent):
        self.start_url = start_url
        self.allowed_domain = get_domain(start_url)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.num_workers = num_workers
        self.max_concurrent = max_concurrent
        self.visited = set()
        self.visited_lock = threading.Lock()
        self.rate_limiter = threading.Semaphore(max_concurrent)
        self.pages_crawled = 0
        self.pages_crawled_lock = threading.Lock()
        self.error_counts = {}
        self.error_counts_lock = threading.Lock()
        self.fetch_times = []
        self.fetch_times_lock = threading.Lock()

    def _try_visit(self, url):
        with self.visited_lock:
            if url in self.visited:
                return False
            if len(self.visited) >= self.max_pages:
                return False
            self.visited.add(url)
            return True

    def _crawl_one(self, url, depth):
        print(f'[depth {depth}] Crawling: {url}')
        fetch_start = time.time()
        with self.rate_limiter:
            result = fetch_page(url)
        fetch_duration = time.time() - fetch_start
        with self.fetch_times_lock:
            self.fetch_times.append(fetch_duration)
        with self.pages_crawled_lock:
            self.pages_crawled += 1
        if not result.ok:
            print(f'  [failed: {result.error_type}] {result.detail}')
            with self.error_counts_lock:
                self.error_counts[result.error_type] = self.error_counts.get(result.error_type, 0) + 1
            return []
        links = extract_links(result.html, url)
        return [link for link in links if is_same_domain(link, self.allowed_domain)]

    def run(self):
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {}
            if self._try_visit(self.start_url):
                fut = executor.submit(self._crawl_one, self.start_url, 0)
                futures[fut] = 0
            while futures:
                if len(self.visited) >= self.max_pages:
                    break
                done, _ = wait(list(futures.keys()), return_when=FIRST_COMPLETED)
                for fut in done:
                    parent_depth = futures.pop(fut)
                    child_depth = parent_depth + 1
                    try:
                        new_links = fut.result()
                    except Exception as e:
                        print(f'  [worker exception] {e}')
                        new_links = []
                    if child_depth > self.max_depth:
                        continue
                    for link in new_links:
                        if len(self.visited) >= self.max_pages:
                            break
                        if self._try_visit(link):
                            new_fut = executor.submit(self._crawl_one, link, child_depth)
                            futures[new_fut] = child_depth
        return (self.visited, self.pages_crawled)

    def print_stats(self, elapsed):
        print('\n--- Summary ---')
        print(f'Start URL: {self.start_url}')
        print(f'Pool size: {self.num_workers} | Max concurrent requests: {self.max_concurrent}')
        print(f'Pages crawled: {self.pages_crawled}')
        print(f'Unique URLs visited: {len(self.visited)}')
        print(f'Time elapsed: {elapsed:.2f}s')
        if self.fetch_times:
            avg_fetch = sum(self.fetch_times) / len(self.fetch_times)
            print(f'Avg time per page: {avg_fetch:.3f}s')
        if self.pages_crawled > 0 and elapsed > 0:
            print(f'Throughput: {self.pages_crawled / elapsed:.2f} pages/sec')
        total_errors = sum(self.error_counts.values())
        print(f'Total errors: {total_errors}')
        for error_type, count in sorted(self.error_counts.items()):
            print(f'  {error_type}: {count}')

def parse_args():
    parser = argparse.ArgumentParser(description='Web crawler using concurrent.futures.ThreadPoolExecutor.')
    parser.add_argument('url', nargs='?', default='https://books.toscrape.com', help='Start URL to crawl (default: %(default)s)')
    parser.add_argument('--max-depth', type=int, default=2)
    parser.add_argument('--max-pages', type=int, default=30)
    parser.add_argument('--workers', type=int, default=8, help='Thread pool size (default: 8)')
    parser.add_argument('--max-concurrent', type=int, default=4, help='Max concurrent HTTP requests, i.e. rate limit (default: 4)')
    return parser.parse_args()
if __name__ == '__main__':
    args = parse_args()
    start_time = time.time()
    crawler = Crawler(start_url=args.url, max_depth=args.max_depth, max_pages=args.max_pages, num_workers=args.workers, max_concurrent=args.max_concurrent)
    crawler.run()
    elapsed = time.time() - start_time
    crawler.print_stats(elapsed)
