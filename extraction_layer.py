"""
Extraction Layer Module

This module handles extracting clean text content from raw HTML pages.
"""

from trafilatura import extract
from typing import List, Optional


def extract_data(raw_html_pages: List[Optional[str]]) -> List[Optional[str]]:
    """
    Extract clean text content from raw HTML pages.
    
    Args:
        raw_html_pages: List of raw HTML strings (None for failed requests)
        
    Returns:
        List of extracted documents (None for failed extractions)
    """
    documents = []
    
    for i, html in enumerate(raw_html_pages):
        if html is None:
            documents.append(None)
            continue
            
        try:
            # Use trafilatura to extract main content
            extracted = extract(html, include_links=False, include_formatting=False)
            documents.append(extracted)
            print(f"✅ Extracted content from page {i+1}")
        except Exception as e:
            print(f"❌ Failed to extract content from page {i+1}: {e}")
            documents.append(None)
    
    return documents
