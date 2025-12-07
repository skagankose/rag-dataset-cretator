"""Ollama chat completion integration."""

import json
from typing import Any, Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import settings
from ..core.errors import LLMError
from ..core.logging import get_logger, log_llm_error

logger = get_logger("llm.ollama")


class OllamaChat:
    """Ollama chat completion client."""
    
    def __init__(self):
        self.client = None
    
    def _ensure_client(self):
        """Ensure Ollama client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=settings.ollama_api_base,
                timeout=settings.ollama_timeout,
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
        model = model or settings.ollama_chat_model
        response_data = {}
        
        try:
            # Ensure client is initialized
            self._ensure_client()
            
            logger.debug(f"Generating completion with model: {model}")
            
            # Prepare request payload for Ollama API
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            # Add format specification for JSON mode if requested
            if response_format and response_format.get("type") == "json_object":
                payload["format"] = "json"
            
            # Make request to Ollama API
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            
            result_data = response.json()
            
            # Extract content from Ollama response
            content = result_data.get("message", {}).get("content", "")
            
            # Calculate usage statistics (Ollama provides token counts)
            usage = {
                "prompt_tokens": result_data.get("prompt_eval_count", 0),
                "completion_tokens": result_data.get("eval_count", 0),
                "total_tokens": result_data.get("prompt_eval_count", 0) + result_data.get("eval_count", 0),
            }
            
            result = {
                "content": content,
                "usage": usage,
                "model": result_data.get("model", model),
                "finish_reason": "stop" if result_data.get("done", False) else "unknown",
            }
            
            logger.debug(f"Completion generated: {result['usage']}")
            return result
            
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors from Ollama
            response_data = {
                "error_type": "http_error",
                "error_message": str(e),
                "status_code": e.response.status_code,
                "response_text": e.response.text,
                "model": model,
                "request_params": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "message_count": len(messages)
                }
            }
            
            log_llm_error(logger, f"HTTP error from Ollama: {e}", "ollama", response_data, e)
            raise LLMError(f"Failed to generate completion: {e}", response_data=response_data, provider="ollama") from e
            
        except Exception as e:
            # Handle other errors
            response_data = {
                "raw_error": str(e),
                "error_type": type(e).__name__,
                "model": model,
                "request_params": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "message_count": len(messages)
                }
            }
            
            log_llm_error(logger, f"Failed to generate completion: {e}", "ollama", response_data, e)
            raise LLMError(f"Failed to generate completion: {e}", response_data=response_data, provider="ollama") from e
    
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
                # Clean up content - Ollama sometimes includes extra whitespace
                content = content.strip()
                
                # Try to extract JSON if it's wrapped in markdown code blocks
                if content.startswith("```"):
                    # Remove markdown code block markers
                    lines = content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines).strip()
                
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
                log_llm_error(logger, f"Failed to parse JSON response: {e}", "ollama", response_data, e)
                raise LLMError(f"Failed to parse JSON response: {e}", response_data=response_data, provider="ollama") from e
                
        except LLMError:
            raise
        except Exception as e:
            response_data = {"raw_error": str(e)}
            log_llm_error(logger, f"Failed to generate JSON completion: {e}", "ollama", response_data, e)
            raise LLMError(f"Failed to generate JSON completion: {e}", response_data=response_data, provider="ollama") from e


# Global client instance
ollama_chat = OllamaChat()
