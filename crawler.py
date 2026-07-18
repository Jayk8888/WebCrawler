import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; SimpleCrawler/1.0)'}
REQUEST_TIMEOUT = 5

class FetchResult:

    def __init__(self, html=None, error_type=None, detail=''):
        self.html = html
        self.error_type = error_type
        self.detail = detail

    @property
    def ok(self):
        return self.html is not None

def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            return FetchResult(error_type='wrong_content_type', detail=content_type)
        return FetchResult(html=response.text)
    except requests.exceptions.Timeout as e:
        return FetchResult(error_type='timeout', detail=str(e))
    except requests.exceptions.HTTPError as e:
        return FetchResult(error_type='http_error', detail=str(e))
    except requests.exceptions.ConnectionError as e:
        return FetchResult(error_type='connection_error', detail=str(e))
    except requests.RequestException as e:
        return FetchResult(error_type='other', detail=str(e))

def extract_links(html, base_url):
    if html is None:
        return set()
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for tag in soup.find_all('a', href=True):
        href = str(tag['href'])
        if href.startswith(('#', 'mailto:', 'javascript:', 'tel:')):
            continue
        if 'redlink=1' in href or 'action=edit' in href:
            continue
        absolute_url = urljoin(base_url, href)
        absolute_url = absolute_url.split('#')[0]
        links.add(absolute_url)
    return links

def is_same_domain(url, allowed_domain):
    return urlparse(url).netloc == allowed_domain

def get_domain(url):
    return urlparse(url).netloc
