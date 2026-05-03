"""
Local SearXNG Provider Module

This module provides functionality to search the web using a local SearXNG instance
and extract search results from the HTML response.

Dependencies:
    - httpx: For making HTTP requests
    - beautifulsoup4: For parsing HTML content

Usage:
    from LocalSearXNGProvider import send_request
    results = send_request("python programming")
"""

import httpx
from bs4 import BeautifulSoup
from config import LOCAL_INSTANCE_URL


def send_request(query: str):
    """
    Send a search query to the local SearXNG instance and extract search results.

    This function makes an HTTP GET request to localhost:8080 (default SearXNG port),
    parses the HTML response, and extracts relevant search results including
    titles and URLs.

    Args:
        query (str): The search query to send to SearXNG

    Returns:
        list[dict]: A list of dictionaries containing search results with:
            - title (str): The title of the search result
            - url (str): The URL of the search result

    Raises:
        httpx.HTTPError: If the HTTP request fails (4xx, 5xx status codes)

    Example:
        >>> results = send_request("python programming")
        >>> for result in results:
        ...     print(f"{result['title']}: {result['url']}")
    """
    # SearXNG endpoint URL (from config)
    url = LOCAL_INSTANCE_URL

    # Make HTTP GET request with search query parameter
    r = httpx.get(url, params={"q": query})
    r.raise_for_status()  # Raise exception for HTTP errors

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")

    # Initialize list to store extracted results
    results = []

    # Extract search results from semantic HTML structure
    # SearXNG uses <article class="result"> for each search result
    for item in soup.select("article.result"):
        # Find the main link within each result article
        a = item.select_one("a[href]")
        if not a:
            continue  # Skip if no link found

        # Extract URL and title from the link element
        link = a.get("href")
        title = a.get_text(strip=True)

        # Validate that we have a proper HTTP/HTTPS URL
        if not link or not link.startswith("http"):
            continue  # Skip invalid or relative URLs

        # Add the valid result to our results list
        results.append({
            "title": title,
            "url": link
        })

    return results


# Test the function with a sample search query
if __name__ == "__main__":
    test_results = send_request("python")
    print([result.get("title") for result in test_results])
