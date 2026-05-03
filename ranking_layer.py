"""
Ranking Layer Module

This module handles robust ranking of documents based on relevance to query.
Implements proper title weighting, stopword filtering, and length normalization.
"""

import math
import re
from typing import List, Dict, Tuple
from config import (
    SPAM_WORD_RATIO_THRESHOLD, SPAM_PUNCTUATION_THRESHOLD, SPAM_PENALTY_CAP,
    REPETITION_CAP, MIN_DOCUMENTS_FOR_IDF, TITLE_WEIGHT, FIRST_PARA_WEIGHT,
    BODY_WEIGHT, STRUCTURED_REPETITION_PENALTY
)


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


def calculate_idf_scores(documents: List[str], keywords: List[str]) -> Dict[str, float]:
    """
    Calculate Inverse Document Frequency (IDF) scores for keywords.

    Args:
        documents: List of document contents
        keywords: List of keywords to calculate IDF for

    Returns:
        Dictionary mapping keyword to IDF score
    """
    if len(documents) < MIN_DOCUMENTS_FOR_IDF:
        # Not enough documents for meaningful IDF
        return {kw: 1.0 for kw in keywords}

    idf_scores = {}
    total_docs = len(documents)

    for keyword in keywords:
        doc_count = sum(1 for doc in documents if keyword.lower() in doc.lower())
        if doc_count == 0:
            idf_scores[keyword] = 1.0  # Avoid division by zero
        else:
            idf_scores[keyword] = math.log(total_docs / doc_count)

    return idf_scores


def detect_structured_repetition(content: str) -> float:
    """
    Detect structured repetition patterns (like lists/tables).

    Args:
        content: Document content

    Returns:
        Penalty score for structured repetition
    """
    penalty = 0.0

    # Detect repetitive patterns like "Download X Release notes"
    download_count = content.lower().count("download")
    release_count = content.lower().count("release")
    notes_count = content.lower().count("notes")

    # If we have many template-like repetitions
    if download_count > 20 and release_count > 20:
        penalty += STRUCTURED_REPETITION_PENALTY * 0.5

    # Detect uniform line patterns (possible tables/lists)
    lines = content.split('\n')
    if len(lines) > 10:
        # Check if many lines follow similar patterns
        similar_patterns = 0
        for i in range(1, min(len(lines), 20)):
            if len(lines[i]) > 20 and len(lines[i-1]) > 20:
                # Simple pattern detection: similar line lengths
                if abs(len(lines[i]) - len(lines[i-1])) < 10:
                    similar_patterns += 1

        if similar_patterns > 10:
            penalty += STRUCTURED_REPETITION_PENALTY * 0.3

    return min(penalty, STRUCTURED_REPETITION_PENALTY)


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

    # If any word appears more than threshold ratio of total words, apply penalty
    total_words = len(words)
    for word, count in word_counts.items():
        if count / total_words > SPAM_WORD_RATIO_THRESHOLD:
            penalty += count / total_words

    # Check for excessive punctuation (possible spam)
    punctuation_ratio = sum(1 for c in content if c in '!?.') / len(content) if content else 0
    if punctuation_ratio > SPAM_PUNCTUATION_THRESHOLD:  # More than threshold punctuation
        penalty += punctuation_ratio * 2

    is_spam = penalty > SPAM_PENALTY_CAP  # Threshold for spam detection
    return is_spam, penalty


def calculate_document_score(keywords: List[str], content: str, title: str = "", idf_scores: Dict[str, float] = None) -> float:
    """
    Calculate improved document score with repetition cap, IDF weighting, and position-based scoring.

    Args:
        keywords: Cleaned query keywords
        content: Document content
        title: Document title (if available)
        idf_scores: IDF scores for keywords (if available)

    Returns:
        Calculated score
    """
    if not keywords or not content:
        return 0.0

    content_lower = content.lower()
    title_lower = title.lower()

    # Split content into sections for position-based weighting
    lines = content.split('\n')
    title_text = title
    first_para = ' '.join(lines[:2]) if len(lines) > 2 else ''
    body_text = ' '.join(lines[2:]) if len(lines) > 2 else content

    # Initialize scoring components
    title_score = 0.0
    first_para_score = 0.0
    body_score = 0.0

    # Calculate scores with repetition cap and IDF weighting
    for keyword in keywords:
        # Title scoring (with repetition cap)
        title_count = min(title_lower.count(keyword), REPETITION_CAP)
        idf_weight = idf_scores.get(keyword, 1.0) if idf_scores else 1.0
        title_score += title_count * TITLE_WEIGHT * idf_weight

        # First paragraph scoring (with repetition cap)
        first_para_count = min(first_para.lower().count(keyword), REPETITION_CAP)
        first_para_score += first_para_count * FIRST_PARA_WEIGHT * idf_weight

        # Body text scoring (with repetition cap)
        body_count = min(body_text.lower().count(keyword), REPETITION_CAP)
        body_score += body_count * BODY_WEIGHT * idf_weight

    # Full query bonus (position-weighted)
    full_query = " ".join(keywords)
    if full_query in title_lower:
        title_score += 15 * TITLE_WEIGHT
    elif full_query in first_para.lower():
        first_para_score += 10 * FIRST_PARA_WEIGHT
    elif full_query in content_lower:
        body_score += 5 * BODY_WEIGHT

    # Spam detection
    is_spam, spam_penalty = detect_spam(content)
    if is_spam:
        return 0.0  # Completely discard spam

    # Structured repetition detection
    structured_penalty = detect_structured_repetition(content)

    # Apply spam penalty
    spam_penalty = min(spam_penalty + structured_penalty, SPAM_PENALTY_CAP)

    # Calculate total score
    total_score = title_score + first_para_score + body_score

    # Normalize by document length (using log to prevent long doc bias)
    length_normalizer = math.log(len(content) + 1)  # +1 to avoid log(0)

    # Apply normalization and penalties
    final_score = (total_score / length_normalizer) * (1 - spam_penalty)

    return final_score


def rank_documents(query: str, documents: List[str]) -> List[Dict]:
    """
    Rank documents using improved scoring algorithm with IDF, repetition cap, and position-based weighting.

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

    # Calculate IDF scores for keywords
    idf_scores = calculate_idf_scores(documents, keywords)
    print(f"📈 IDF scores: {idf_scores}")

    for i, doc in enumerate(documents):
        if not doc or len(doc.strip()) < 50:
            print(f"⚠️  Document {i+1}: Too short ({len(doc)} chars)")
            continue

        # Extract title (first line or first 100 chars as fallback)
        lines = doc.split('\n')
        title = lines[0].strip() if lines else ""
        if len(title) > 100:  # If title is too long, truncate
            title = title[:100] + "..."

        # Calculate improved score with IDF and position-based weighting
        score = calculate_document_score(keywords, doc, title, idf_scores)

        # Get detailed scoring breakdown for debugging
        content_lower = doc.lower()
        title_lower = title.lower()

        # Calculate capped counts for display
        title_match_count = sum(min(title_lower.count(kw), REPETITION_CAP) for kw in keywords)
        text_match_count = sum(min(content_lower.count(kw), REPETITION_CAP) for kw in keywords)

        # Check for structured repetition penalty
        structured_penalty = detect_structured_repetition(doc)

        ranked_documents.append({
            'content': doc,
            'title': title,
            'score': score,
            'index': i,
            'title_matches': title_match_count,
            'text_matches': text_match_count,
            'length': len(doc),
            'keywords': keywords,
            'structured_penalty': structured_penalty,
            'idf_scores': idf_scores
        })

    # Sort by score (highest first)
    ranked_documents.sort(key=lambda x: x['score'], reverse=True)

    print(f"📊 Ranked {len(ranked_documents)} documents with improved scoring (IDF + position + repetition cap)")
    return ranked_documents
