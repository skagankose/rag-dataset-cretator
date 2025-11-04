"""Prompts for LLM question generation."""

from typing import Dict, List


def get_question_generation_system_prompt() -> str:
    """Get the system prompt for question generation."""
    return """You are an expert at generating high-quality question-answer pairs for RAG (Retrieval-Augmented Generation) datasets.

Your task is to generate concise, factual questions with accurate answers that can be answered from the provided text chunks. Questions can be based on:
1. Single chunks - questions answerable from one chunk alone
2. Multiple chunks - questions requiring information from multiple related chunks

Each question must be categorized into one of these three categories:
1. **FACTUAL**: Questions that test direct recall of specific details. The answer is a specific name, date, number, or short verbatim phrase found directly in the text.
2. **INTERPRETATION**: Questions that test comprehension by asking for explanations of causes, effects, or relationships between concepts in the text. The answer requires synthesizing information rather than just quoting it.
3. **LONG_ANSWER**: Questions that demand a comprehensive, multi-sentence summary or detailed explanation of a major topic, process, or event described across the text.

Requirements:
1. Questions and answers must be based ONLY on the provided text chunks
2. Do not invent facts or include information not in the text
3. Focus on key facts, concepts, relationships, and connections
4. For multi-chunk questions, focus on relationships, comparisons, or broader concepts that span chunks
5. Prefer specific questions over general ones
6. Avoid questions that require outside knowledge
7. Make questions clear and unambiguous
8. Provide complete, accurate answers based solely on the chunk content
9. Do not mention chunks in questions or answers (e.g. "as described in following chunks")
10. Categorize each question appropriately based on the type of cognitive task required

Return your response as a JSON object with this exact structure:
{
  "questions": [
    {"question": "Single-chunk question?", "answer": "Complete answer based on the chunk content.", "related_chunk_ids": ["chunk_id"], "category": "FACTUAL"},
    {"question": "Multi-chunk question requiring synthesis?", "answer": "Complete answer synthesizing information from multiple chunks.", "related_chunk_ids": ["chunk_id1", "chunk_id2"], "category": "INTERPRETATION"}
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

Each question must be categorized into one of these three categories:
1. **FACTUAL**: Questions that test direct recall of specific details. The answer is a specific name, date, number, or short verbatim phrase found directly in the text.
2. **INTERPRETATION**: Questions that test comprehension by asking for explanations of causes, effects, or relationships between concepts in the text. The answer requires synthesizing information rather than just quoting it.
3. **LONG_ANSWER**: Questions that demand a comprehensive, multi-sentence summary or detailed explanation of a major topic, process, or event described across the text.

Chunks:
{chunks_text}

Return valid JSON with this structure:
{{
  "questions": [
    {{"question": "Question requiring multiple chunks?", "answer": "Complete answer synthesizing information from multiple chunks.", "related_chunk_ids": {chunk_ids}, "category": "INTERPRETATION"}}
  ]
}}

The "related_chunk_ids" should include all chunk IDs that are needed to answer each question."""


def validate_question_response(response: Dict) -> bool:
    """Validate question generation response format."""
    if not isinstance(response, dict):
        return False
    
    if "questions" not in response:
        return False
    
    questions = response["questions"]
    if not isinstance(questions, list):
        return False
    
    valid_categories = {"FACTUAL", "INTERPRETATION", "LONG_ANSWER"}
    
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