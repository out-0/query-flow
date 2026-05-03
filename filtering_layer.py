"""
Filtering Layer Module

This module handles filtering out invalid or low-quality documents.
"""

from typing import List, Optional


def filter_documents(documents: List[Optional[str]]) -> List[str]:
    """
    Filter out invalid or low-quality documents.
    
    Args:
        documents: List of extracted text content (None for failed extractions)
        
    Returns:
        List of filtered documents (only valid content)
    """
    filtered_documents = []
    
    for i, doc in enumerate(documents):
        if doc is None:
            continue
            
        # Basic filtering rules
        if len(doc.strip()) < 50:  # Too short
            print(f"⚠️  Filtered page {i+1}: content too short ({len(doc)} chars)")
            continue
            
        if doc.count(' ') < 10:  # Not enough words
            print(f"⚠️  Filtered page {i+1}: not enough words")
            continue
            
        filtered_documents.append(doc)
        print(f"✅ Validated page {i+1}: {len(doc)} chars")
    
    return filtered_documents
