"""Validation API endpoints for checking question-answer correctness."""

import json
from typing import List

from fastapi import APIRouter, HTTPException

from ..core.errors import NotFoundError, LLMError
from ..core.logging import get_logger
from ..llm.factory import chat_provider
from ..llm.prompts import get_validation_system_prompt, get_validation_prompt
from ..schemas.articles import DatasetItem
from ..storage.index import article_index
from ..storage.md import read_markdown_file
from ..storage.paths import paths

logger = get_logger("api.validation")

router = APIRouter()


@router.post("/validate/{article_id}")
async def validate_article(article_id: str) -> dict:
    """Validate all question-answer pairs for an article."""
    try:
        # Verify article exists
        entry = article_index.get_article(article_id)
        
        # Read dataset file
        dataset_path = paths.dataset_file(article_id)
        
        if not dataset_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found for article: {article_id}"
            )
        
        # Import the dataset parsing function
        from .dataset import _parse_dataset_markdown
        
        # Parse dataset markdown file
        with open(dataset_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        items = _parse_dataset_markdown(content)
        
        if not items:
            return {
                "article_id": article_id,
                "is_correct": True,
                "reason": "No questions to validate",
                "validated_count": 0,
            }
        
        # Get chunks directory
        chunks_dir = paths.chunks_dir(article_id)
        
        if not chunks_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Chunks not found for article: {article_id}"
            )
        
        # Load all chunks into a dictionary for quick access
        chunks_dict = {}
        for chunk_file in chunks_dir.glob("c*.md"):
            try:
                front_matter, content = read_markdown_file(chunk_file)
                chunk_id = front_matter.get("id", chunk_file.stem)
                chunks_dict[chunk_id] = content
            except Exception as e:
                logger.warning(f"Failed to read chunk file {chunk_file}: {e}")
                continue
        
        # Validate each question-answer pair
        all_correct = True
        first_error_reason = None
        validated_count = 0
        
        logger.info(f"🔍 Starting validation for article '{entry.title}' - {len(items)} questions to validate")
        
        for idx, item in enumerate(items, start=1):
            # Get the content of related chunks
            chunks_content = ""
            for chunk_id in item.related_chunk_ids:
                if chunk_id in chunks_dict:
                    chunks_content += f"\n\n--- Chunk {chunk_id} ---\n{chunks_dict[chunk_id]}"
                else:
                    logger.warning(f"Chunk {chunk_id} not found for validation")
            
            if not chunks_content:
                all_correct = False
                first_error_reason = f"No chunk content found for question: {item.question}"
                logger.error(f"❌ Question {idx}/{len(items)}: FAILED - No chunk content found")
                logger.error(f"   Question: {item.question[:100]}{'...' if len(item.question) > 100 else ''}")
                break
            
            # Validate with LLM
            try:
                validation_result = await _validate_single_qa(
                    question=item.question,
                    answer=item.answer,
                    chunks_content=chunks_content
                )
                
                validated_count += 1
                
                # Log the validation result with details
                is_correct = validation_result["is_correct"]
                reason = validation_result["reason"]
                
                if is_correct:
                    logger.info(f"✅ Question {idx}/{len(items)}: CORRECT")
                    logger.info(f"   Question: {item.question[:100]}{'...' if len(item.question) > 100 else ''}")
                    logger.info(f"   Reason: {reason}")
                else:
                    logger.warning(f"❌ Question {idx}/{len(items)}: INCORRECT")
                    logger.warning(f"   Question: {item.question[:100]}{'...' if len(item.question) > 100 else ''}")
                    logger.warning(f"   Answer: {item.answer[:100]}{'...' if len(item.answer) > 100 else ''}")
                    logger.warning(f"   Reason: {reason}")
                    all_correct = False
                    # Store the first error reason
                    if first_error_reason is None:
                        first_error_reason = reason
                        
            except Exception as e:
                logger.error(f"❌ Question {idx}/{len(items)}: ERROR - {str(e)}")
                logger.error(f"   Question: {item.question[:100]}{'...' if len(item.question) > 100 else ''}")
                all_correct = False
                if first_error_reason is None:
                    first_error_reason = f"Validation failed: {str(e)}"
        
        # Log summary
        logger.info(f"📊 Validation Complete: {validated_count}/{len(items)} questions validated")
        if all_correct:
            logger.info(f"✅ Result: ALL {validated_count} QUESTIONS ARE CORRECT")
        else:
            logger.warning(f"❌ Result: VALIDATION FAILED - Some questions are incorrect")
            logger.warning(f"   First error: {first_error_reason}")
        
        return {
            "article_id": article_id,
            "is_correct": all_correct,
            "reason": first_error_reason if not all_correct else "All question-answer pairs are correct",
            "validated_count": validated_count,
            "total_questions": len(items),
        }
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to validate article {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate article: {str(e)}"
        ) from e


async def _validate_single_qa(
    question: str,
    answer: str,
    chunks_content: str,
) -> dict:
    """Validate a single question-answer pair with LLM."""
    try:
        # Get prompts
        system_prompt = get_validation_system_prompt()
        user_prompt = get_validation_prompt(
            question=question,
            answer=answer,
            chunks_content=chunks_content
        )
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call LLM with higher token limit to prevent truncation
        llm_response = await chat_provider.generate_json_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
        )
        
        # Extract the parsed content from the response
        # The response contains: content, usage, model, finish_reason, parsed_content
        if "parsed_content" in llm_response:
            response = llm_response["parsed_content"]
        else:
            # Fallback: try to parse content if parsed_content is not available
            logger.warning("parsed_content not in response, attempting to parse content")
            content = llm_response.get("content", "")
            
            # Try to fix incomplete JSON by completing it
            content = content.strip()
            if not content.endswith("}"):
                # Try to complete the JSON by adding closing braces
                open_braces = content.count("{")
                close_braces = content.count("}")
                if open_braces > close_braces:
                    # Add missing closing brace and close the string if needed
                    if '"reason":' in content and not content.rstrip().endswith('"'):
                        content += '"'
                    content += "}" * (open_braces - close_braces)
                    logger.warning(f"Attempted to fix incomplete JSON by adding closing braces")
            
            response = json.loads(content)
        
        # Log the response for debugging (at debug level to reduce verbosity)
        logger.debug(f"Validation response: {response}")
        
        # Validate response format
        if not isinstance(response, dict):
            logger.error(f"Response is not a dict, got: {type(response)} - {response}")
            raise ValueError("Invalid response format from LLM")
        
        if "is_correct" not in response or "reason" not in response:
            logger.error(f"Missing fields in response. Keys present: {list(response.keys())}, Response: {response}")
            raise ValueError("Missing required fields in validation response")
        
        if not isinstance(response["is_correct"], bool):
            logger.error(f"is_correct is not a boolean: {type(response['is_correct'])} - {response['is_correct']}")
            raise ValueError("is_correct must be a boolean")
        
        if not isinstance(response["reason"], str):
            logger.error(f"reason is not a string: {type(response['reason'])} - {response['reason']}")
            raise ValueError("reason must be a string")
        
        return response
        
    except LLMError as e:
        logger.error(f"LLM error during validation: {e}")
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise ValueError(f"Validation failed: {str(e)}") from e

