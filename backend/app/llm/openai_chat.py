"""OpenAI chat completion integration."""

import json
from typing import Any, Dict, List

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import settings
from ..core.errors import LLMError
from ..core.logging import get_logger, log_llm_error

logger = get_logger("llm.openai")


class OpenAIChat:
    """OpenAI chat completion client."""
    
    def __init__(self):
        self.client = None
    
    def _ensure_client(self):
        """Ensure OpenAI client is initialized."""
        if self.client is None:
            if not settings.openai_api_key:
                raise LLMError("OPENAI_API_KEY is required for OpenAI provider", provider="openai")
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
        response_data = {}
        
        try:
            # Ensure client is initialized
            self._ensure_client()
            
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
            # Capture response data if available
            if hasattr(e, 'response') and e.response:
                try:
                    error_response = e.response.json()
                    response_data = {
                        "error_type": error_response.get("error", {}).get("type"),
                        "error_code": error_response.get("error", {}).get("code"),
                        "error_message": error_response.get("error", {}).get("message"),
                        "status_code": getattr(e.response, 'status_code', None),
                    }
                except:
                    response_data = {"raw_error": str(e)}
            else:
                response_data = {"raw_error": str(e)}
                
            response_data.update({
                "model": model,
                "request_params": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "message_count": len(messages)
                }
            })
            
            # Log detailed error with response data
            log_llm_error(logger, f"Failed to generate completion: {e}", "openai", response_data, e)
            
            raise LLMError(f"Failed to generate completion: {e}", response_data=response_data, provider="openai") from e
    
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
                # Log the problematic response content
                response_data = {
                    "content": content,
                    "model": response.get("model"),
                    "finish_reason": response.get("finish_reason"),
                    "usage": response.get("usage"),
                    "parse_error": str(e)
                }
                log_llm_error(logger, f"Failed to parse JSON response: {e}", "openai", response_data, e)
                raise LLMError(f"Failed to parse JSON response: {e}", response_data=response_data, provider="openai") from e
                
        except LLMError:
            raise
        except Exception as e:
            response_data = {"raw_error": str(e)}
            log_llm_error(logger, f"Failed to generate JSON completion: {e}", "openai", response_data, e)
            raise LLMError(f"Failed to generate JSON completion: {e}", response_data=response_data, provider="openai") from e


# Global client instance
openai_chat = OpenAIChat() 