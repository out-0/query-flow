"""
Public SearXNG Provider Pool

This module provides public SearXNG instances pool with fallback routing.

Dependencies:
    - httpx: For making HTTP requests
    - beautifulsoup4: For parsing HTML content
    - time: For latency tracking

Usage:
    from PublicSearXNGProviderPool import PublicSearXNGPool
    pool = PublicSearXNGPool()
    results = pool.search("python programming")
"""

import httpx
from bs4 import BeautifulSoup
import time
import json
import os
from typing import List, Dict, Tuple
from config import PUBLIC_INSTANCES_FILE, HTTP_TIMEOUT


class SearXNGProvider:
    """Base class for SearXNG providers."""

    def __init__(self, url: str):
        self.url = url

    def search(self, query: str) -> Tuple[List[Dict], float]:
        """
        Perform search and return results with latency.

        Args:
            query: Search query string

        Returns:
            Tuple of (results_list, latency_ms)

        Raises:
            httpx.HTTPError: If request fails
        """
        start_time = time.time()

        try:
            response = httpx.get(
                f"{self.url}/search",
                params={"q": query},
                timeout=HTTP_TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()

            # Parse HTML response
            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for item in soup.select("article.result"):
                a = item.select_one("a[href]")
                if not a:
                    continue

                link = a.get("href")
                title = a.get_text(strip=True)

                if not link or not link.startswith("http"):
                    continue

                results.append({
                    "title": title,
                    "url": link
                })

            latency = (time.time() - start_time) * 1000  # Convert to ms
            return results, latency

        except httpx.HTTPError as e:
            raise e


class PublicSearXNGPool:
    """
    Public SearXNG instances pool with simple fallback routing.

    Manages multiple public SearXNG instances and provides fallback routing
    in the order they are defined.
    """

    def load_public_instances(self) -> List[str]:
        """
        Load public instances from JSON file.

        Returns:
            List of public instance URLs
        """
        try:
            if not os.path.exists(PUBLIC_INSTANCES_FILE):
                print(f"⚠️  Public instances file not found: {PUBLIC_INSTANCES_FILE}")
                return []

            with open(PUBLIC_INSTANCES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle simple list format
            if isinstance(data, list):
                instances = data
            else:
                print(f"⚠️  Invalid format in {PUBLIC_INSTANCES_FILE}. Expected list of URLs.")
                return []

            print(f"Loaded {len(instances)} public instances from {PUBLIC_INSTANCES_FILE}")
            return instances

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {PUBLIC_INSTANCES_FILE}: {e}")
            return []
        except Exception as e:
            print(f"❌ Error loading {PUBLIC_INSTANCES_FILE}: {e}")
            return []

    def __init__(self):
        # Load public instances from JSON file
        self.public_instances = self.load_public_instances()

    def search(self, query: str) -> List[Dict]:
        """
        Perform search using public instances in the order they appear.

        Args:
            query: Search query string

        Returns:
            List of search results (title, url dictionaries)
        """
        print("🔄 Using public instances pool...")

        # Try instances in order
        for url in self.public_instances:
            provider = SearXNGProvider(url)

            try:
                results, latency = provider.search(query)
                print(f"✅ Public instance {url} successful ({latency:.0f}ms)")
                return results

            except httpx.HTTPError as e:
                print(f"❌ Public instance {url} failed: {e}")
                continue

        # All instances failed
        print("💥 All public instances failed!")
        return []


# Test the public instances pool
if __name__ == "__main__":
    pool = PublicSearXNGPool()

    # Test search
    results = pool.search("python programming")

    # Display results
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['title']}")
