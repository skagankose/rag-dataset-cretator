"""Question generation using OpenAI chat completion."""

import asyncio
import math
import random
from typing import List, Dict, Any, Tuple

from ..core.errors import LLMError
from ..core.logging import get_logger, log_llm_error
from ..ingest.split import ChunkInfo
from .factory import get_chat_provider
from .prompts import (
    get_question_generation_system_prompt,
    validate_question_response,
    _load_prompts_config,
)

logger = get_logger("llm.questions")


class QuestionGenerator:
    """Generates questions from text chunks using LLM providers."""
    
    def __init__(self, model: str = None):
        # Get the appropriate model based on the provider if none specified
        if model is None:
            from ..core.config import settings
            if settings.llm_provider == "openai":
                self.model = settings.openai_chat_model
            elif settings.llm_provider == "gemini":
                self.model = settings.gemini_chat_model
            else:
                self.model = None
        else:
            self.model = model
    
    def _create_chunk_groups(self, chunks: List[ChunkInfo], total_questions: int) -> List[Tuple[List[ChunkInfo], int]]:
        """Create groups of chunks and determine how many questions to generate for each group."""
        if not chunks:
            return []
        
        # Strategy: Create a mix of single-chunk and multi-chunk groups
        groups = []
        
        # Calculate distribution
        num_chunks = len(chunks)
        single_chunk_ratio = 0.6  # 60% single-chunk questions
        multi_chunk_ratio = 0.4   # 40% multi-chunk questions
        
        single_questions = max(1, int(total_questions * single_chunk_ratio))
        multi_questions = total_questions - single_questions
        
        # Create single-chunk groups
        if single_questions > 0:
            # Distribute single questions across chunks, prioritizing important chunks
            chunks_for_single = self._select_chunks_for_single_questions(chunks, single_questions)
            for chunk in chunks_for_single:
                groups.append(([chunk], 1))
        
        # Create multi-chunk groups
        if multi_questions > 0 and num_chunks >= 2:
            multi_groups = self._create_multi_chunk_groups(chunks, multi_questions)
            groups.extend(multi_groups)
        
        logger.info(f"Created {len(groups)} chunk groups for {total_questions} total questions")
        return groups
    
    def _select_chunks_for_single_questions(self, chunks: List[ChunkInfo], num_questions: int) -> List[ChunkInfo]:
        """Select chunks for single-chunk questions, prioritizing diverse content."""
        if num_questions >= len(chunks):
            return chunks
        
        # Prefer chunks from different sections and with substantial content
        selected = []
        sections_used = set()
        
        # Sort chunks by content length (prefer substantial chunks)
        sorted_chunks = sorted(chunks, key=lambda c: c.char_count, reverse=True)
        
        for chunk in sorted_chunks:
            if len(selected) >= num_questions:
                break
            
            # Prefer chunks from new sections
            if chunk.section not in sections_used or len(selected) < num_questions // 2:
                selected.append(chunk)
                sections_used.add(chunk.section)
        
        # Fill remaining slots if needed
        while len(selected) < num_questions and len(selected) < len(chunks):
            for chunk in chunks:
                if chunk not in selected:
                    selected.append(chunk)
                    break
        
        return selected
    
    def _create_multi_chunk_groups(self, chunks: List[ChunkInfo], num_questions: int) -> List[Tuple[List[ChunkInfo], int]]:
        """Create multi-chunk groups for generating questions that span multiple chunks."""
        groups = []
        
        if len(chunks) < 2:
            return groups
        
        # Strategy 1: Adjacent chunk pairs (2-3 chunks)
        adjacent_questions = max(1, num_questions // 2)
        
        # Strategy 2: Section-based groups (chunks from same section)
        section_questions = num_questions - adjacent_questions
        
        # Create adjacent chunk groups
        used_indices = set()
        for _ in range(adjacent_questions):
            if len(used_indices) >= len(chunks) - 1:
                break
            
            # Find consecutive chunks not yet used
            start_idx = None
            for i in range(len(chunks) - 1):
                if i not in used_indices and i + 1 not in used_indices:
                    start_idx = i
                    break
            
            if start_idx is not None:
                # Use 2-3 chunks depending on their size
                end_idx = min(start_idx + 2, len(chunks))
                if start_idx + 2 < len(chunks) and chunks[start_idx + 2].char_count > 500:
                    end_idx = start_idx + 3  # Include third chunk if substantial
                
                chunk_group = chunks[start_idx:end_idx]
                groups.append((chunk_group, 1))
                
                # Mark chunks as used
                for i in range(start_idx, end_idx):
                    used_indices.add(i)
        
        # Create section-based groups
        if section_questions > 0:
            section_groups = self._group_chunks_by_section(chunks)
            for section, section_chunks in section_groups.items():
                if len(section_chunks) >= 2 and section_questions > 0:
                    groups.append((section_chunks[:4], 1))  # Max 4 chunks per group
                    section_questions -= 1
        
        return groups
    
    def _group_chunks_by_section(self, chunks: List[ChunkInfo]) -> Dict[str, List[ChunkInfo]]:
        """Group chunks by their section."""
        sections = {}
        for chunk in chunks:
            section = chunk.section or "Lead"
            if section not in sections:
                sections[section] = []
            sections[section].append(chunk)
        return sections
    
    async def _generate_questions_for_group(
        self,
        chunk_group: List[ChunkInfo],
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate questions for a group of chunks."""
        try:
            # Prepare chunk information
            chunk_ids = [chunk.id for chunk in chunk_group]
            chunk_contents = [chunk.content for chunk in chunk_group]
            
            # Log chunk information for debugging
            total_chars = sum(len(content) for content in chunk_contents)
            logger.debug(f"Generating {num_questions} questions for {len(chunk_group)} chunk(s), total {total_chars} chars")
            logger.debug(f"Chunk IDs: {chunk_ids}")
            if chunk_group:
                sections = list(set(chunk.section for chunk in chunk_group if chunk.section))
                logger.debug(f"Sections: {sections if sections else ['Lead']}")
            
            # Create context information
            context_info = ""
            if len(chunk_group) == 1:
                chunk = chunk_group[0]
                if chunk.section or chunk.heading_path:
                    context_info = f"\n\nContext: This text is from the section '{chunk.section}' under '{chunk.heading_path}'."
            else:
                sections = list(set(chunk.section for chunk in chunk_group if chunk.section))
                if sections:
                    context_info = f"\n\nContext: These chunks are from sections: {', '.join(sections)}"
            
            # Create user prompt
            if len(chunk_group) == 1:
                user_prompt = self._create_single_chunk_prompt(chunk_group[0], num_questions, context_info)
            else:
                user_prompt = self._create_multi_chunk_prompt(chunk_group, num_questions, context_info)
            
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": get_question_generation_system_prompt()
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
            
            # Generate completion
            chat_provider = get_chat_provider()
            logger.debug(f"Calling LLM to generate {num_questions} questions...")
            response = await chat_provider.generate_json_completion(
                messages=messages,
                model=self.model,
                temperature=0.1,
                max_tokens=8192,  # Increased to allow for longer, more detailed responses
            )
            logger.debug(f"LLM response received: {response.get('usage', {})}")
            
            # Validate and extract questions
            parsed_response = response["parsed_content"]
            
            if not validate_question_response(parsed_response):
                response_data = {
                    "content": response.get("content"),
                    "parsed_content": parsed_response,
                    "model": response.get("model"),
                    "validation_error": "Invalid question response format"
                }
                log_llm_error(logger, "Invalid question response format", "unknown", response_data)
                raise LLMError("Invalid question response format", response_data=response_data)
            
            questions = parsed_response["questions"]
            
                        # Ensure chunk IDs are correct
            for question in questions:
                question["related_chunk_ids"] = chunk_ids

            logger.info(f"Generated {len(questions)} questions for chunk group of {len(chunk_group)} chunks")
            
            # Add 3-second delay to prevent rate limits
            logger.debug("Adding 3-second delay to prevent rate limits")
            await asyncio.sleep(3)
            
            return questions
            
        except LLMError as e:
            # Log detailed LLM error with chunk context
            logger.error(f"LLM Error for chunks {chunk_ids}: {e.get_detailed_message()}")
            logger.warning(f"Using fallback question for chunk group due to LLM error")
            # Return fallback question
            section = chunk_group[0].section if chunk_group else "this topic"
            return [{
                # "question": f"What information is provided about {section}?",
                # "answer": f"The text provides information about {section} as described in the relevant chunks.",
                # "related_chunk_ids": [chunk.id for chunk in chunk_group],
                # "category": "LONG_ANSWER"
                "question": "n/a",
                "answer": "n/a",
                "related_chunk_ids": [chunk.id for chunk in chunk_group],
                "category": "INTERPRETATION"
            }]
        except Exception as e:
            logger.error(f"Unexpected error generating questions for chunks {chunk_ids}: {type(e).__name__}: {e}")
            # Return fallback question
            section = chunk_group[0].section if chunk_group else "this topic"
            return [{
                # "question": f"What information is provided about {section}?",
                # "answer": f"The text provides information about {section} as described in the relevant chunks.",
                # "related_chunk_ids": [chunk.id for chunk in chunk_group],
                # "category": "LONG_ANSWER"
                "question": "n/a",
                "answer": "n/a",
                "related_chunk_ids": [chunk.id for chunk in chunk_group],
                "category": "INTERPRETATION"
            }]
    
    def _create_single_chunk_prompt(self, chunk: ChunkInfo, num_questions: int, context_info: str) -> str:
        """Create prompt for single-chunk questions."""
        config = _load_prompts_config()
        return config["single_chunk_prompt"].format(
            num_questions=num_questions,
            chunk_id=chunk.id,
            context_info=context_info,
            chunk_content=chunk.content
        )
    
    def _create_multi_chunk_prompt(self, chunks: List[ChunkInfo], num_questions: int, context_info: str) -> str:
        """Create prompt for multi-chunk questions."""
        config = _load_prompts_config()
        
        chunks_text = ""
        for chunk in chunks:
            chunks_text += f"\n\n--- Chunk {chunk.id} ---\n{chunk.content}"
        
        chunk_ids = [chunk.id for chunk in chunks]
        
        return config["multi_chunk_prompt"].format(
            num_questions=num_questions,
            chunks_text=chunks_text,
            context_info=context_info,
            chunk_ids=chunk_ids
        )
    
    async def generate_questions_for_chunks(
        self,
        chunks: List[ChunkInfo],
        total_questions: int = 10,
    ) -> List[Dict[str, Any]]:
        """Generate questions across multiple chunks with mixed single/multi-chunk approach."""
        logger.info(f"Generating {total_questions} questions across {len(chunks)} chunks")
        
        if not chunks:
            logger.warning("No chunks provided for question generation")
            return []
        
        all_questions = []
        failed_groups = 0
        successful_groups = 0
        
        # Create chunk groups
        chunk_groups = self._create_chunk_groups(chunks, total_questions)
        
        # Generate questions for each group
        for idx, (chunk_group, num_questions) in enumerate(chunk_groups, 1):
            try:
                logger.info(f"Processing chunk group {idx}/{len(chunk_groups)}...")
                questions = await self._generate_questions_for_group(chunk_group, num_questions)
                all_questions.extend(questions)
                successful_groups += 1
            except LLMError as e:
                # Log the detailed LLM error
                logger.error(f"LLM Error generating questions for chunk group {idx}/{len(chunk_groups)}: {e.get_detailed_message()}")
                failed_groups += 1
                continue
            except Exception as e:
                logger.error(f"Failed to generate questions for chunk group {idx}/{len(chunk_groups)}: {e}")
                failed_groups += 1
                continue
        
        logger.info(f"Generated {len(all_questions)} total questions from {successful_groups}/{len(chunk_groups)} groups (failed: {failed_groups})")
        return all_questions


async def generate_questions_for_chunks(
    chunks: List[ChunkInfo],
    total_questions: int = 10,
    model: str = None,
) -> List[Dict[str, Any]]:
    """Convenience function to generate questions for chunks."""
    generator = QuestionGenerator(model=model)
    return await generator.generate_questions_for_chunks(chunks, total_questions) 