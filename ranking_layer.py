"""
Ranking Layer Module

This module handles robust ranking of documents based on relevance to query.
Implements proper title weighting, stopword filtering, and length normalization.
"""

import math
import re
from typing import List, Dict, Tuple


# Common stopwords that should be ignored in scoring
STOPWORDS = {
    "the", "is", "a", "how", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "by", "as", "from", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "can", "this", "that", "these", "those", "i", "you",
    "he", "she", "it", "we", "they", "what", "which", "who", "when", "where", "why",
    "an", "are", "am", "is", "was", "were", "be", "been", "being"
}


def clean_query(query: str) -> List[str]:
    """
    Clean query by removing stopwords and extracting meaningful keywords.
    
    Args:
        query: Original search query
        
    Returns:
        List of meaningful keywords
    """
    # Lowercase and split into words
    words = query.lower().split()
    
    # Filter out stopwords and short words (< 2 chars)
    keywords = [
        word.strip().strip('.,!?;:"()[]{}')
        for word in words
        if word not in STOPWORDS and len(word.strip('.,!?;:"()[]{}')) >= 2
    ]
    
    return keywords


def detect_spam(content: str) -> Tuple[bool, float]:
    """
    Basic spam detection based on repetition patterns.
    
    Args:
        content: Document content
        
    Returns:
        Tuple of (is_spam, penalty_score)
    """
    penalty = 0.0
    
    # Check for excessive repetition of the same word
    words = content.lower().split()
    word_counts = {}
    
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # If any word appears more than 10% of total words, apply penalty
    total_words = len(words)
    for word, count in word_counts.items():
        if count / total_words > 0.1:
            penalty += count / total_words
    
    # Check for excessive punctuation (possible spam)
    punctuation_ratio = sum(1 for c in content if c in '!?.') / len(content) if content else 0
    if punctuation_ratio > 0.05:  # More than 5% punctuation
        penalty += punctuation_ratio * 2
    
    is_spam = penalty > 0.5  # Threshold for spam detection
    return is_spam, penalty


def calculate_document_score(keywords: List[str], content: str, title: str = "") -> float:
    """
    Calculate robust document score with proper weighting and normalization.
    
    Args:
        keywords: Cleaned query keywords
        content: Document content
        title: Document title (if available)
        
    Returns:
        Calculated score
    """
    if not keywords or not content:
        return 0.0
    
    content_lower = content.lower()
    title_lower = title.lower()
    
    # Initialize scoring components
    title_matches = 0
    text_matches = 0
    full_query_bonus = 0
    
    # Count keyword matches in title (5x weight)
    for keyword in keywords:
        title_matches += title_lower.count(keyword)
    
    # Count keyword matches in text (1x weight)
    for keyword in keywords:
        text_matches += content_lower.count(keyword)
    
    # Check for full query match (10x bonus)
    full_query = " ".join(keywords)
    if full_query in content_lower:
        full_query_bonus = 10
    elif full_query in title_lower:
        full_query_bonus = 15  # Higher bonus for title match
    
    # Spam detection
    is_spam, spam_penalty = detect_spam(content)
    if is_spam:
        return 0.0  # Completely discard spam
    
    # Apply spam penalty
    spam_penalty = min(spam_penalty, 0.8)  # Cap penalty at 80%
    
    # Calculate raw score
    raw_score = (title_matches * 5 + text_matches * 1 + full_query_bonus)
    
    # Normalize by document length (using log to prevent long doc bias)
    length_normalizer = math.log(len(content) + 1)  # +1 to avoid log(0)
    
    # Apply normalization and spam penalty
    final_score = (raw_score / length_normalizer) * (1 - spam_penalty)
    
    return final_score


def rank_documents(query: str, documents: List[str]) -> List[Dict]:
    """
    Rank documents using robust scoring algorithm with proper weighting.
    
    Args:
        query: Original search query
        documents: List of filtered document content
        
    Returns:
        List of ranked documents with detailed scores
    """
    ranked_documents = []
    
    # Clean the query to extract meaningful keywords
    keywords = clean_query(query)
    print(f"🔍 Keywords extracted: {keywords}")
    
    for i, doc in enumerate(documents):
        if not doc or len(doc.strip()) < 50:
            print(f"⚠️  Document {i+1}: Too short ({len(doc)} chars)")
            continue
        
        # Extract title (first line or first 100 chars as fallback)
        lines = doc.split('\n')
        title = lines[0].strip() if lines else ""
        if len(title) > 100:  # If title is too long, truncate
            title = title[:100] + "..."
        
        # Calculate robust score
        score = calculate_document_score(keywords, doc, title)
        
        # Get detailed scoring breakdown for debugging
        content_lower = doc.lower()
        title_lower = title.lower()
        
        title_match_count = sum(title_lower.count(kw) for kw in keywords)
        text_match_count = sum(content_lower.count(kw) for kw in keywords)
        
        ranked_documents.append({
            'content': doc,
            'title': title,
            'score': score,
            'index': i,
            'title_matches': title_match_count,
            'text_matches': text_match_count,
            'length': len(doc),
            'keywords': keywords
        })
    
    # Sort by score (highest first)
    ranked_documents.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"📊 Ranked {len(ranked_documents)} documents with robust scoring")
    return ranked_documents
