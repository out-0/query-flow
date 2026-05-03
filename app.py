"""
Main Application Orchestrator

This module orchestrates the search and processing pipeline with proper
module separation and routing logic.
"""

from typing import List, Dict, Optional, Any
from LocalSearXNGProvider import send_request
from PublicSearXNGProviderPool import PublicSearXNGPool
from fetch_layer import fetch_results
from extraction_layer import extract_data
from filtering_layer import filter_documents
from ranking_layer import rank_documents
from output_layer import output_documents


def search_with_routing(query: str):
    """
    Hybrid search router that tries local instance first, falls back to public instances.

    Args:
        query: Search query string

    Returns:
        List of search results (title, url dictionaries)
    """
    # Strategy 1: Try local instance first
    try:
        results = send_request(query)
        print(f"✅ Local instance successful - found {len(results)} results")
        return results
    except Exception as e:
        print(f"❌ Local instance failed: {e}")

    # Strategy 2: Fallback to public instances pool
    print("🔄 Falling back to public instances...")
    public_pool = PublicSearXNGPool()
    results = public_pool.search(query)

    if results:
        print(f"✅ Public instances successful - found {len(results)} results")
    else:
        print("💥 All search instances failed!")

    return results


if __name__ == '__main__':
    # Get user query (hardcoded for demo)
    query = "python programming"
    print(f"🔍 Searching for: {query}")

    # Search with routing
    results: List[Dict[str, str]] = search_with_routing(query)  # Returns: List[{"title": str, "url": str}]

    if not results:
        print("❌ No search results found. Exiting.")
        exit()

    # Full pipeline using separate modules
    raw_html_pages: List[Optional[str]] = fetch_results(results)  # Returns: List[raw HTML or None]
    documents: List[Optional[str]] = extract_data(raw_html_pages)  # Returns: List[extracted text or None]
    filtered_documents: List[str] = filter_documents(documents)  # Returns: List[valid text content]
    ranked_documents: List[Dict[str, Any]] = rank_documents(query, filtered_documents)  # Returns: List[{"score": float, "content": str, ...}]
    #output_documents(ranked_documents)
    #print(ranked_documents[0]["content"])
    