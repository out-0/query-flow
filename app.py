"""
Main Application Orchestrator

This module orchestrates the search and processing pipeline with proper
module separation and routing logic.
"""

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
    results = search_with_routing(query)
    
    if not results:
        print("❌ No search results found. Exiting.")
        exit()
    
    # Full pipeline using separate modules
    raw_html_pages = fetch_results(results)
    documents = extract_data(raw_html_pages)
    filtered_documents = filter_documents(documents)
    ranked_documents = rank_documents(query, filtered_documents)
    output_documents(ranked_documents)
