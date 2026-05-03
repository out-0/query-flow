"""
Fetch Layer Module

This module handles fetching full HTML content for search result URLs.
"""

import httpx
from typing import List, Dict


def fetch_results(results: List[Dict]) -> List[str]:
    """
    Fetch full HTML content for each search result URL.
    
    Args:
        results: List of dictionaries with title and url
        
    Returns:
        List of raw HTML pages (None for failed requests)
    """
    raw_html_pages = []
    
    for result in results:
        try:
            response = httpx.get(result['url'], timeout=10.0)
            response.raise_for_status()
            raw_html_pages.append(response.text)
            print(f"✅ Fetched: {result['url']}")
        except httpx.HTTPError as e:
            print(f"❌ Failed to fetch {result['url']}: {e}")
            raw_html_pages.append(None)
    
    return raw_html_pages
