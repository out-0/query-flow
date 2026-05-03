"""
Output Layer Module

This module handles formatting and output of the final ranked results
with detailed scoring breakdown.
"""

from typing import List, Dict


def output_documents(ranked_documents: List[Dict]) -> None:
    """
    Format and output the final ranked results with detailed scoring.
    
    Args:
        ranked_documents: List of ranked documents with detailed scores
    """
    print(f"\n🎯 Top {len(ranked_documents)} Ranked Results:")
    print("=" * 100)
    
    for i, doc in enumerate(ranked_documents[:10], 1):  # Top 10 results
        print(f"\n{i}. Score: {doc['score']:.4f}")
        
        # Show title if available
        if 'title' in doc and doc['title']:
            print(f"   Title: {doc['title']}")
        
        # Show scoring breakdown
        if 'title_matches' in doc and 'text_matches' in doc:
            print(f"   Scoring: Title matches: {doc['title_matches']}, Text matches: {doc['text_matches']}")
        
        if 'length' in doc:
            print(f"   Length: {doc['length']} chars")
        
        # Show keywords if available
        if 'keywords' in doc and doc['keywords']:
            print(f"   Keywords: {', '.join(doc['keywords'])}")
        
        # Content preview
        content_preview = doc['content'][:200]
        if len(doc['content']) > 200:
            content_preview += "..."
        print(f"   Preview: {content_preview}")
        
        print("-" * 100)
