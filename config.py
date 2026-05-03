"""
Configuration module for query-flow system.
"""

# Search and processing limits
MAX_SEARCH_RESULTS = 10  # Maximum number of search results to process
MAX_CONTENT_LENGTH = 50000  # Maximum content length per document (chars)
HTTP_TIMEOUT = 10.0  # HTTP request timeout in seconds

# Ranking thresholds
MIN_DOCUMENT_LENGTH = 50  # Minimum document length to be considered
MIN_WORD_COUNT = 10  # Minimum word count for valid documents

# Spam detection
SPAM_WORD_RATIO_THRESHOLD = 0.05  # Max ratio of single word to total words (reduced from 0.1)
SPAM_PUNCTUATION_THRESHOLD = 0.03  # Max ratio of punctuation characters (reduced from 0.05)
SPAM_PENALTY_CAP = 0.8  # Maximum spam penalty (80%)

# Improved ranking parameters
REPETITION_CAP = 3  # Maximum count for any single word in scoring
MIN_DOCUMENTS_FOR_IDF = 2  # Minimum documents needed for IDF calculation
TITLE_WEIGHT = 5.0  # Weight multiplier for title content
FIRST_PARA_WEIGHT = 2.0  # Weight multiplier for first paragraph
BODY_WEIGHT = 1.0  # Weight multiplier for rest of content
STRUCTURED_REPETITION_PENALTY = 0.3  # Penalty for template-like repetition

# Search routing
LOCAL_INSTANCE_URL = "http://localhost:8080/search"
PUBLIC_INSTANCES_FILE = "public_instances.json"  # JSON file with public instances
