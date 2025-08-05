"""Validation utilities for question and chunk data."""

import re
from typing import List, Dict, Any

from ..core.logging import get_logger

logger = get_logger("utils.validation")

# Regex pattern for valid chunk IDs
CHUNK_ID_PATTERN = re.compile(r'^[a-z0-9_]+_c\d{4}$', re.IGNORECASE)


def is_valid_chunk_id(chunk_id: str) -> bool:
    """
    Check if a chunk ID is valid.
    
    Args:
        chunk_id: The chunk ID to validate
        
    Returns:
        True if the chunk ID is valid, False otherwise
    """
    if not isinstance(chunk_id, str):
        return False
    
    return bool(CHUNK_ID_PATTERN.match(chunk_id.strip()))


def clean_question_chunk_ids(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and validate chunk IDs in a question.
    
    Args:
        question: The question dictionary to clean
        
    Returns:
        The cleaned question dictionary
    """
    if "related_chunk_ids" not in question:
        return question
    
    original_chunk_ids = question["related_chunk_ids"]
    
    if not isinstance(original_chunk_ids, list):
        logger.warning(f"Invalid related_chunk_ids format: {type(original_chunk_ids)}")
        question["related_chunk_ids"] = []
        return question
    
    # Filter out invalid chunk IDs
    valid_chunk_ids = []
    invalid_chunk_ids = []
    
    for chunk_id in original_chunk_ids:
        if is_valid_chunk_id(chunk_id):
            valid_chunk_ids.append(chunk_id)
        else:
            invalid_chunk_ids.append(chunk_id)
    
    if invalid_chunk_ids:
        logger.warning(f"Found invalid chunk IDs in question '{question.get('question', 'Unknown')}': {invalid_chunk_ids}")
    
    question["related_chunk_ids"] = valid_chunk_ids
    return question


def validate_and_clean_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and clean a list of questions.
    
    Args:
        questions: List of question dictionaries to clean
        
    Returns:
        List of cleaned question dictionaries
    """
    if not isinstance(questions, list):
        logger.error(f"Invalid questions format: {type(questions)}")
        return []
    
    cleaned_questions = []
    original_count = len(questions)
    
    for question in questions:
        if not isinstance(question, dict):
            logger.warning(f"Skipping invalid question format: {type(question)}")
            continue
        
        # Clean chunk IDs
        cleaned_question = clean_question_chunk_ids(question)
        
        # Only keep questions that have valid chunk IDs
        if cleaned_question.get("related_chunk_ids"):
            cleaned_questions.append(cleaned_question)
        else:
            logger.warning(f"Skipping question with no valid chunk IDs: {cleaned_question.get('question', 'Unknown')}")
    
    cleaned_count = len(cleaned_questions)
    removed_count = original_count - cleaned_count
    
    if removed_count > 0:
        logger.info(f"Cleaned questions: {original_count} -> {cleaned_count} (removed {removed_count})")
    
    return cleaned_questions 