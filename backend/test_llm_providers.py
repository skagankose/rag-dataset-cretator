#!/usr/bin/env python3
"""
Test script to verify LLM providers are working correctly.
Run this script to test your OpenAI or Gemini configuration.

Usage:
    python test_llm_providers.py openai
    python test_llm_providers.py gemini
    python test_llm_providers.py factory
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

try:
    from app.core.config import settings
    from app.core.errors import LLMError
except ImportError as e:
    print(f"❌ Failed to import app modules: {e}")
    print("Make sure you're running this from the backend directory.")
    sys.exit(1)


async def test_openai():
    """Test OpenAI provider."""
    print("Testing OpenAI provider...")
    
    try:
        from app.llm.openai_chat import openai_chat
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds with valid JSON."},
            {"role": "user", "content": 'Generate a simple JSON object with a "test" field set to "success".'}
        ]
        
        print("Sending test request to OpenAI...")
        response = await openai_chat.generate_json_completion(messages)
        
        print(f"✅ OpenAI test successful!")
        print(f"Model: {response['model']}")
        print(f"Response: {response['content'][:100]}...")
        print(f"Usage: {response['usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False


async def test_gemini():
    """Test Gemini provider."""
    print("Testing Gemini provider...")
    
    try:
        from app.llm.gemini_chat import gemini_chat
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds with valid JSON."},
            {"role": "user", "content": 'Generate a simple JSON object with a "test" field set to "success".'}
        ]
        
        print("Sending test request to Gemini...")
        response = await gemini_chat.generate_json_completion(messages)
        
        print(f"✅ Gemini test successful!")
        print(f"Model: {response['model']}")
        print(f"Response: {response['content'][:100]}...")
        print(f"Usage: {response['usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False


async def test_factory():
    """Test the factory provider selection."""
    print(f"Testing factory with provider: {settings.llm_provider}")
    
    try:
        from app.llm.factory import chat_provider
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Respond with exactly: Hello from factory!"}
        ]
        
        print("Sending test request via factory...")
        response = await chat_provider.generate_completion(messages)
        
        print(f"✅ Factory test successful!")
        print(f"Provider: {settings.llm_provider}")
        print(f"Model: {response['model']}")
        print(f"Response: {response['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Factory test failed: {e}")
        return False


async def main():
    """Main test function."""
    if len(sys.argv) != 2:
        print("Usage: python test_llm_providers.py [openai|gemini|factory]")
        print("\nExamples:")
        print("  python test_llm_providers.py openai   # Test OpenAI directly")
        print("  python test_llm_providers.py gemini   # Test Gemini directly")
        print("  python test_llm_providers.py factory  # Test configured provider")
        sys.exit(1)
    
    provider = sys.argv[1].lower()
    
    print(f"RAG Dataset Creator - LLM Provider Test")
    print(f"=" * 40)
    print(f"Current settings:")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  OpenAI Model: {settings.openai_chat_model}")
    print(f"  Gemini Model: {settings.gemini_chat_model}")
    print(f"=" * 40)
    
    success = False
    
    if provider == "openai":
        if not settings.openai_api_key:
            print("❌ OPENAI_API_KEY not set in environment")
            sys.exit(1)
        success = await test_openai()
    elif provider == "gemini":
        if not settings.gemini_api_key:
            print("❌ GEMINI_API_KEY not set in environment")
            sys.exit(1)
        success = await test_gemini()
    elif provider == "factory":
        success = await test_factory()
    else:
        print(f"❌ Unknown provider: {provider}")
        print("Use: openai, gemini, or factory")
        sys.exit(1)
    
    if success:
        print(f"\n🎉 All tests passed! Your {provider} configuration is working correctly.")
    else:
        print(f"\n💥 Tests failed. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 