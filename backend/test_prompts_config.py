#!/usr/bin/env python3
"""Test script to verify prompts configuration is working correctly."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.llm.prompts import (
    get_question_generation_system_prompt,
    get_question_generation_user_prompt,
    get_multi_chunk_question_prompt,
    validate_question_response,
    _load_prompts_config,
)


def test_load_config():
    """Test that config loads successfully."""
    print("Testing config loading...")
    config = _load_prompts_config()
    
    assert "system_prompt" in config, "system_prompt not found in config"
    assert "single_chunk_prompt" in config, "single_chunk_prompt not found in config"
    assert "multi_chunk_prompt" in config, "multi_chunk_prompt not found in config"
    assert "categories" in config, "categories not found in config"
    
    print("✓ Config loaded successfully")
    print(f"  - Found {len(config['categories'])} categories: {config['categories']}")
    return config


def test_system_prompt():
    """Test system prompt retrieval."""
    print("\nTesting system prompt...")
    prompt = get_question_generation_system_prompt()
    
    assert isinstance(prompt, str), "System prompt is not a string"
    assert len(prompt) > 100, "System prompt seems too short"
    assert "RAG" in prompt, "System prompt doesn't mention RAG"
    assert "FACTUAL" in prompt, "System prompt doesn't mention FACTUAL category"
    assert "INTERPRETATION" in prompt, "System prompt doesn't mention INTERPRETATION category"
    assert "LONG_ANSWER" in prompt, "System prompt doesn't mention LONG_ANSWER category"
    
    print("✓ System prompt is valid")
    print(f"  - Length: {len(prompt)} characters")


def test_single_chunk_prompt():
    """Test single chunk prompt generation."""
    print("\nTesting single chunk prompt...")
    
    test_chunk_id = "test_chunk_001"
    test_content = "This is a test chunk content about machine learning."
    test_num_questions = 2
    
    prompt = get_question_generation_user_prompt(
        chunk_content=test_content,
        chunk_id=test_chunk_id,
        num_questions=test_num_questions,
        section="Test Section",
        heading_path="Main > Test Section"
    )
    
    assert isinstance(prompt, str), "Prompt is not a string"
    assert test_chunk_id in prompt, f"Chunk ID {test_chunk_id} not found in prompt"
    assert test_content in prompt, "Chunk content not found in prompt"
    assert str(test_num_questions) in prompt, f"Number of questions {test_num_questions} not found in prompt"
    assert "Test Section" in prompt, "Section not found in prompt"
    
    print("✓ Single chunk prompt generation works")
    print(f"  - Prompt length: {len(prompt)} characters")


def test_multi_chunk_prompt():
    """Test multi-chunk prompt generation."""
    print("\nTesting multi-chunk prompt...")
    
    test_chunk_ids = ["chunk_001", "chunk_002", "chunk_003"]
    test_contents = [
        "First chunk about AI.",
        "Second chunk about machine learning.",
        "Third chunk about neural networks."
    ]
    test_num_questions = 2
    
    prompt = get_multi_chunk_question_prompt(
        chunk_contents=test_contents,
        chunk_ids=test_chunk_ids,
        num_questions=test_num_questions
    )
    
    assert isinstance(prompt, str), "Prompt is not a string"
    
    # Check that all chunk IDs are present
    for chunk_id in test_chunk_ids:
        assert chunk_id in prompt, f"Chunk ID {chunk_id} not found in prompt"
    
    # Check that all contents are present
    for content in test_contents:
        assert content in prompt, f"Content '{content}' not found in prompt"
    
    assert str(test_num_questions) in prompt, f"Number of questions {test_num_questions} not found in prompt"
    
    print("✓ Multi-chunk prompt generation works")
    print(f"  - Prompt length: {len(prompt)} characters")


def test_validate_response():
    """Test response validation."""
    print("\nTesting response validation...")
    
    # Valid response
    valid_response = {
        "questions": [
            {
                "question": "What is machine learning?",
                "answer": "Machine learning is a subset of AI.",
                "related_chunk_ids": ["chunk_001"],
                "category": "FACTUAL"
            },
            {
                "question": "How does AI relate to neural networks?",
                "answer": "AI uses neural networks as a computational model.",
                "related_chunk_ids": ["chunk_001", "chunk_002"],
                "category": "INTERPRETATION"
            }
        ]
    }
    
    assert validate_question_response(valid_response), "Valid response failed validation"
    print("✓ Valid response passes validation")
    
    # Invalid response - missing category
    invalid_response1 = {
        "questions": [
            {
                "question": "What is AI?",
                "answer": "AI is artificial intelligence.",
                "related_chunk_ids": ["chunk_001"]
            }
        ]
    }
    
    assert not validate_question_response(invalid_response1), "Invalid response (missing category) passed validation"
    print("✓ Invalid response (missing category) correctly rejected")
    
    # Invalid response - invalid category
    invalid_response2 = {
        "questions": [
            {
                "question": "What is AI?",
                "answer": "AI is artificial intelligence.",
                "related_chunk_ids": ["chunk_001"],
                "category": "INVALID_CATEGORY"
            }
        ]
    }
    
    assert not validate_question_response(invalid_response2), "Invalid response (bad category) passed validation"
    print("✓ Invalid response (bad category) correctly rejected")
    
    # Invalid response - missing questions key
    invalid_response3 = {
        "data": []
    }
    
    assert not validate_question_response(invalid_response3), "Invalid response (missing questions) passed validation"
    print("✓ Invalid response (missing questions key) correctly rejected")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Prompts Configuration")
    print("=" * 60)
    
    try:
        test_load_config()
        test_system_prompt()
        test_single_chunk_prompt()
        test_multi_chunk_prompt()
        test_validate_response()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

