"""OpenAI chat completion integration."""

import json
from typing import Any, Dict, List

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import settings
from ..core.errors import LLMError
from ..core.logging import get_logger

logger = get_logger("llm.openai")


class OpenAIChat:
    """OpenAI chat completion client."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout,
            max_retries=settings.openai_max_retries,
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        response_format: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion with retry logic."""
        model = model or settings.openai_chat_model
        
        try:
            logger.debug(f"Generating completion with model: {model}")
            
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Add response format if specified (for JSON mode)
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self.client.chat.completions.create(**kwargs)
            
            result = {
                "content": response.choices[0].message.content,
                "usage": response.usage.dict() if response.usage else {},
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }
            
            logger.debug(f"Completion generated: {result['usage']}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMError(f"Failed to generate completion: {e}") from e
    
    async def generate_json_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """Generate JSON-formatted completion."""
        try:
            response = await self.generate_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON content
            content = response["content"]
            try:
                parsed_content = json.loads(content)
                response["parsed_content"] = parsed_content
                return response
            except json.JSONDecodeError as e:
                raise LLMError(f"Failed to parse JSON response: {e}") from e
                
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Failed to generate JSON completion: {e}") from e


# Global client instance
openai_chat = OpenAIChat() 