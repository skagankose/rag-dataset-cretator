"""Prompts for LLM question generation."""

from typing import Dict, List


def get_question_generation_system_prompt() -> str:
    """Get the system prompt for question generation."""
    return """You are an expert at generating high-quality questions for RAG (Retrieval-Augmented Generation) datasets.

Your task is to generate concise, factual questions that can be answered from the provided text chunks. Questions can be based on:
1. Single chunks - questions answerable from one chunk alone
2. Multiple chunks - questions requiring information from multiple related chunks

Requirements:
1. Questions must be answerable from ONLY the provided text chunks
2. Do not invent facts or include information not in the text
3. Focus on key facts, concepts, relationships, and connections
4. For multi-chunk questions, focus on relationships, comparisons, or broader concepts that span chunks
5. Prefer specific questions over general ones
6. Avoid questions that require outside knowledge
7. Make questions clear and unambiguous
8. Do not include the answers in your response
9. Do not mention about chunk in questions (e.g. as described in following chunks)

Return your response as a JSON object with this exact structure:
{
  "questions": [
    {"question": "Single-chunk question?", "related_chunk_ids": ["chunk_id"]},
    {"question": "Multi-chunk question requiring synthesis?", "related_chunk_ids": ["chunk_id1", "chunk_id2"]}
  ]
}

Include ALL chunk IDs needed to answer each question in the "related_chunk_ids" array."""


def get_question_generation_user_prompt(
    chunk_content: str,
    chunk_id: str,
    num_questions: int,
    section: str = "",
    heading_path: str = "",
) -> str:
    """Get the user prompt for question generation."""
    context_info = ""
    if section or heading_path:
        context_info = f"\n\nContext: This text is from the section '{section}' under '{heading_path}'."
    
    return f"""Generate exactly {num_questions} question(s) that can be answered from this text chunk:

Chunk ID: {chunk_id}{context_info}

Text:
{chunk_content}

Remember:
- Only ask about information that is explicitly stated in this text
- Make questions specific and factual
- Each question should be answerable from this chunk alone
- Return valid JSON with the exact structure specified"""


def get_multi_chunk_question_prompt(
    chunk_contents: List[str],
    chunk_ids: List[str],
    num_questions: int = 1,
) -> str:
    """Get prompt for generating questions that span multiple chunks."""
    chunks_text = ""
    for i, (chunk_id, content) in enumerate(zip(chunk_ids, chunk_contents)):
        chunks_text += f"\n\n--- Chunk {chunk_id} ---\n{content}"
    
    return f"""Generate exactly {num_questions} question(s) that require information from multiple chunks below.

These chunks are consecutive and related. Generate questions that:
1. Require information from at least 2 of the provided chunks
2. Are about connections, relationships, or broader concepts across chunks
3. Cannot be answered from any single chunk alone

Chunks:
{chunks_text}

Return valid JSON with this structure:
{{
  "questions": [
    {{"question": "Question requiring multiple chunks?", "related_chunk_ids": {chunk_ids}}}
  ]
}}

The "related_chunk_ids" should include all chunk IDs that are needed to answer each question."""


def validate_question_response(response: Dict) -> bool:
    """Validate the structure of a question generation response."""
    if not isinstance(response, dict):
        return False
    
    if "questions" not in response:
        return False
    
    questions = response["questions"]
    if not isinstance(questions, list):
        return False
    
    for question in questions:
        if not isinstance(question, dict):
            return False
        
        if "question" not in question or "related_chunk_ids" not in question:
            return False
        
        if not isinstance(question["question"], str):
            return False
        
        if not isinstance(question["related_chunk_ids"], list):
            return False
        
        # Check that all chunk IDs are strings
        for chunk_id in question["related_chunk_ids"]:
            if not isinstance(chunk_id, str):
                return False
    
    return True 