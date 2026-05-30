"""
Fetch Layer Module

This module handles fetching full HTML content for search result URLs.
"""

import httpx
from typing import List, Dict
from config import MAX_SEARCH_RESULTS, HTTP_TIMEOUT


def fetch_results(results: List[Dict]) -> List[str]:
    """
    Fetch full HTML content for each search result URL.

    Args:
        results: List of dictionaries with title and url

    Returns:
        List of raw HTML pages (None for failed requests)
    """
    raw_html_pages = []

    # Limit results to avoid overwhelming the system
    if len(results) > MAX_SEARCH_RESULTS:
        results = results[:MAX_SEARCH_RESULTS]

    for result in results:
        try:
            # High-Compatibility headers to mimic a real Firefox browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            }
            response = httpx.get(result['url'], timeout=HTTP_TIMEOUT, headers=headers, follow_redirects=True)
            response.raise_for_status()
            raw_html_pages.append(response.text)
            print(f"✅ Fetched: {result['url']}")
        except httpx.HTTPError as e:
            print(f"❌ Failed to fetch {result['url']}: {e}")
            raw_html_pages.append(None)

    return raw_html_pages
