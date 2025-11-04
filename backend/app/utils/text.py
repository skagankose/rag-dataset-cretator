"""Text processing utilities."""

import re
from typing import List


def clean_whitespace(text: str) -> str:
    """Clean and normalize whitespace in text."""
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we can truncate at a reasonable word boundary
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."


def extract_language_from_url(url: str) -> str:
    """Extract language code from Wikipedia URL."""
    # Match pattern: https://XX.wikipedia.org/...
    match = re.match(r'https?://([a-z]{2,3})\.wikipedia\.org/', url)
    if match:
        return match.group(1)
    return "en"  # Default to English


def normalize_title(title: str) -> str:
    """Normalize article title for file naming."""
    # Remove or replace problematic characters
    title = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Remove excessive whitespace
    title = clean_whitespace(title)
    # Limit length
    return truncate_text(title, 50)


def count_tokens_estimate(text: str) -> int:
    """Rough estimate of token count (4 chars per token average)."""
    return len(text) // 4


def split_into_sentences(text: str) -> List[str]:
    """Simple sentence splitting using regex."""
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def create_heading_path(headings: List[str]) -> str:
    """Create a heading path from a list of headings."""
    if not headings:
        return "Lead"
    return " > ".join(clean_whitespace(h) for h in headings if h.strip())


def extract_preview(text: str, max_length: int = 200) -> str:
    """Extract a preview of text content."""
    # Clean up the text first
    text = clean_whitespace(text)
    
    # If short enough, return as-is
    if len(text) <= max_length:
        return text
    
    # Try to break at sentence boundary
    sentences = split_into_sentences(text)
    if sentences:
        preview = sentences[0]
        if len(preview) <= max_length:
            return preview
    
    # Fallback to truncation
    return truncate_text(text, max_length) 