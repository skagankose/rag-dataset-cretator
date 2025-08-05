"""Chunk filtering utilities."""

import re
from typing import List

from ..core.logging import get_logger
from ..core.config import settings
from ..ingest.split import ChunkInfo

logger = get_logger("utils.filtering")


def should_filter_chunk(chunk: ChunkInfo) -> bool:
    """
    Determine if a chunk should be filtered out based on various criteria.
    
    Args:
        chunk: The chunk to evaluate
        
    Returns:
        True if the chunk should be filtered out, False otherwise
    """
    # Check if filtering is disabled
    if not settings.enable_chunk_filtering:
        return False
    
    # Check if section contains unwanted keywords
    if settings.filter_unwanted_sections and _has_unwanted_section(chunk.section):
        logger.debug(f"Filtering chunk {chunk.id} due to unwanted section: {chunk.section}")
        return True
    
    # Check if heading_path contains unwanted keywords (as backup)
    if settings.filter_unwanted_sections and _has_unwanted_section(chunk.heading_path):
        logger.debug(f"Filtering chunk {chunk.id} due to unwanted heading_path: {chunk.heading_path}")
        return True
    
    # Check if content is too short
    # Strip whitespace and count words
    content_words = chunk.content.strip().split()
    word_count = len(content_words)
    if word_count < settings.min_chunk_words:
        logger.debug(f"Filtering chunk {chunk.id} due to short content: {word_count} words (min: {settings.min_chunk_words})")
        return True
    
    # Check if content is mostly whitespace or empty
    if not chunk.content.strip():
        logger.debug(f"Filtering chunk {chunk.id} due to empty content")
        return True
    
    return False


def _has_unwanted_section(section: str) -> bool:
    """
    Check if a section name contains unwanted keywords.
    
    Args:
        section: The section name to check
        
    Returns:
        True if the section contains unwanted keywords, False otherwise
    """
    if not section:
        return False
    
    # Convert to lowercase for case-insensitive matching
    section_lower = section.lower()
    
    # Keywords that indicate unwanted sections
    unwanted_keywords = [
        "references",
        "external links",
        "see also",
        "further reading",
        "bibliography",
        "notes",
        "footnotes",
        "citations",
        "sources",
        "external",
        "links",
        "related articles",
        "related topics",
        "additional",
        "resources",
        "web links",
        "online",
        "websites",
        "urls"
    ]
    
    # Check if any unwanted keyword is present in the section name
    for keyword in unwanted_keywords:
        if keyword in section_lower:
            return True
    
    return False


def filter_chunks(chunks: List[ChunkInfo]) -> List[ChunkInfo]:
    """
    Filter out unwanted chunks from a list of chunks.
    
    Args:
        chunks: List of chunks to filter
        
    Returns:
        List of chunks that passed the filtering criteria
    """
    original_count = len(chunks)
    filtered_chunks = []
    filtered_out_chunks = []
    
    for chunk in chunks:
        if should_filter_chunk(chunk):
            filtered_out_chunks.append(chunk)
        else:
            filtered_chunks.append(chunk)
    
    filtered_count = len(filtered_chunks)
    removed_count = original_count - filtered_count
    
    if removed_count > 0:
        logger.info(f"Filtered out {removed_count} chunks: {original_count} -> {filtered_count}")
        for chunk in filtered_out_chunks:
            logger.debug(f"Filtered out chunk {chunk.id}: section='{chunk.section}', words={len(chunk.content.strip().split())}")
    
    return filtered_chunks 