"""Prompts for LLM question generation."""

import os
from pathlib import Path
from typing import Dict, List
import yaml

from ..core.logging import get_logger

logger = get_logger("llm.prompts")

# Cache for loaded prompts
_prompts_cache = None


def _load_prompts_config() -> Dict:
    """Load prompts configuration from YAML file."""
    global _prompts_cache
    
    if _prompts_cache is not None:
        return _prompts_cache
    
    # Get language setting from environment
    lang = os.getenv("PROMPT_LANGUAGE", "en").lower()
    
    # Get the path to the prompts config file
    config_dir = Path(__file__).parent.parent / "config"
    
    # Select file based on language
    if lang == "tr":
        prompts_filename = "prompts.tr.yaml"
    else:
        prompts_filename = "prompts.yaml"
        
    prompts_file = config_dir / prompts_filename
    
    if not prompts_file.exists():
        # Fallback to default if language file missing (except for 'en' which must exist)
        if lang != "en":
            logger.warning(f"Prompts file for language '{lang}' not found at {prompts_file}. Falling back to English.")
            prompts_file = config_dir / "prompts.yaml"
            
        if not prompts_file.exists():
            logger.error(f"Prompts config file not found at: {prompts_file}")
            raise FileNotFoundError(f"Prompts config file not found: {prompts_file}")
    
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            _prompts_cache = yaml.safe_load(f)
        logger.info(f"Loaded prompts configuration from {prompts_file} (Language: {lang})")
        return _prompts_cache
    except Exception as e:
        logger.error(f"Failed to load prompts config: {e}")
        raise


def get_question_generation_system_prompt() -> str:
    """Get the system prompt for question generation."""
    config = _load_prompts_config()
    return config["system_prompt"]


def get_question_generation_user_prompt(
    chunk_content: str,
    chunk_id: str,
    num_questions: int,
    section: str = "",
    heading_path: str = "",
) -> str:
    """Get the user prompt for question generation (deprecated - kept for compatibility)."""
    config = _load_prompts_config()
    
    context_info = ""
    if section or heading_path:
        context_info = f"\n\nContext: This text is from the section '{section}' under '{heading_path}'."
    
    return config["single_chunk_prompt"].format(
        num_questions=num_questions,
        chunk_id=chunk_id,
        context_info=context_info,
        chunk_content=chunk_content
    )


def get_multi_chunk_question_prompt(
    chunk_contents: List[str],
    chunk_ids: List[str],
    num_questions: int = 1,
) -> str:
    """Get prompt for generating questions that span multiple chunks (deprecated - kept for compatibility)."""
    config = _load_prompts_config()
    
    chunks_text = ""
    for i, (chunk_id, content) in enumerate(zip(chunk_ids, chunk_contents)):
        chunks_text += f"\n\n--- Chunk {chunk_id} ---\n{content}"
    
    return config["multi_chunk_prompt"].format(
        num_questions=num_questions,
        chunks_text=chunks_text,
        context_info="",
        chunk_ids=chunk_ids
    )


def validate_question_response(response: Dict) -> bool:
    """Validate question generation response format."""
    if not isinstance(response, dict):
        return False
    
    if "questions" not in response:
        return False
    
    questions = response["questions"]
    if not isinstance(questions, list):
        return False
    
    # Load valid categories from config
    config = _load_prompts_config()
    valid_categories = set(config.get("categories", ["FACTUAL", "INTERPRETATION"]))
    
    for question in questions:
        if not isinstance(question, dict):
            return False
        
        # Check required fields
        if "question" not in question or "answer" not in question or "related_chunk_ids" not in question or "category" not in question:
            return False
        
        if not isinstance(question["question"], str):
            return False
            
        if not isinstance(question["answer"], str):
            return False
        
        if not isinstance(question["related_chunk_ids"], list):
            return False
        
        if not isinstance(question["category"], str):
            return False
        
        # Check that category is valid
        if question["category"] not in valid_categories:
            return False
        
        # Check that chunk IDs are strings
        if not all(isinstance(chunk_id, str) for chunk_id in question["related_chunk_ids"]):
            return False
    
    return True


def get_validation_system_prompt() -> str:
    """Get the system prompt for validating question-answer pairs."""
    config = _load_prompts_config()
    return config["validation_system_prompt"]


def get_validation_prompt(
    question: str,
    answer: str,
    chunks_content: str,
) -> str:
    """Get the user prompt for validating a question-answer pair with chunks."""
    config = _load_prompts_config()
    
    return config["validation_prompt"].format(
        question=question,
        answer=answer,
        chunks_content=chunks_content
    ) 