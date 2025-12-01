"""Google Gemini chat completion integration."""

import json
from typing import Any, Dict, List
import asyncio
import time

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import settings
from ..core.errors import LLMError
from ..core.logging import get_logger, log_llm_error

logger = get_logger("llm.gemini")


class GeminiChat:
    """Google Gemini chat completion client."""
    
    def __init__(self):
        self._configured = False
        
        # Safety settings to allow more flexibility in content generation
        # Using HarmBlockThreshold.BLOCK_ONLY_HIGH to be less restrictive
        # BLOCK_NONE can sometimes cause issues with newer Gemini models
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        
        # Generation config
        self.generation_config = {
            "temperature": 0.1,
            "max_output_tokens": 2000,  # Increased for longer responses
        }
    
    def _ensure_configured(self):
        """Ensure Gemini is configured with API key."""
        if not self._configured:
            if not settings.gemini_api_key:
                raise LLMError("GEMINI_API_KEY is required for Gemini provider", provider="gemini")
            genai.configure(api_key=settings.gemini_api_key)
            self._configured = True
            
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt for Gemini.
        
        Gemini works better with simpler, more direct prompts without
        explicit role markers like 'User:' or 'Assistant:'.
        """
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                # System messages become instructions at the top
                prompt_parts.append(content)
            elif role == "user":
                # User messages are added directly, potentially with minimal formatting
                prompt_parts.append(content)
            elif role == "assistant":
                # Assistant messages are included for context
                prompt_parts.append(f"Previous response: {content}")
        
        return "\n\n".join(prompt_parts)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion with retry logic."""
        model_name = model or settings.gemini_chat_model
        response_data = {}
        
        try:
            # Ensure Gemini is configured
            self._ensure_configured()
            
            logger.debug(f"Generating completion with model: {model_name}")
            
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)
            
            # Add JSON format instruction if needed
            if response_format and response_format.get("type") == "json_object":
                prompt += "\n\nIMPORTANT: Your response must be valid JSON. Do not include any text outside the JSON object."
            
            # Log prompt preview for debugging
            logger.debug(f"Prompt preview (first 300 chars): {prompt[:300]}...")
            
            # Initialize model
            model_instance = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=self.safety_settings,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            # Generate content asynchronously
            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt
            )
            
            # Extract content and check for blocking
            if not response.parts or not response.text:
                # Collect detailed response information
                response_data = {
                    "model": model_name,
                    "prompt_text": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                    "response_parts": len(response.parts) if hasattr(response, 'parts') else 0,
                    "finish_reason": str(getattr(response, 'finish_reason', 'unknown')),
                    "prompt_feedback": str(getattr(response, 'prompt_feedback', None)),
                }
                
                # Check safety ratings
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    response_data["candidate_finish_reason"] = str(getattr(candidate, 'finish_reason', 'unknown'))
                    if hasattr(candidate, 'safety_ratings'):
                        response_data["safety_ratings"] = [
                            {
                                "category": str(rating.category),
                                "probability": str(rating.probability),
                                "blocked": getattr(rating, 'blocked', False)
                            }
                            for rating in candidate.safety_ratings
                        ]
                
                error_msg = "No content generated by Gemini"
                if response_data.get("candidate_finish_reason") == "FinishReason.SAFETY":
                    error_msg = "Content blocked by Gemini safety filters"
                elif response_data.get("prompt_feedback"):
                    error_msg = f"Prompt blocked: {response_data['prompt_feedback']}"
                
                log_llm_error(logger, error_msg, "gemini", response_data)
                raise LLMError(error_msg, response_data=response_data, provider="gemini")
            
            # Extract text content - use response.text property which is more reliable
            content = response.text
            
            # Calculate approximate usage (Gemini doesn't provide exact token counts)
            usage = {
                "prompt_tokens": len(prompt.split()) * 1.3,  # Rough estimate
                "completion_tokens": len(content.split()) * 1.3,  # Rough estimate
                "total_tokens": (len(prompt.split()) + len(content.split())) * 1.3,
            }
            
            result = {
                "content": content,
                "usage": usage,
                "model": model_name,
                "finish_reason": "stop",  # Gemini doesn't provide detailed finish reasons
            }
            
            logger.debug(f"Completion generated: {result['usage']}")
            return result
            
        except Exception as e:
            # Capture response data if available
            if hasattr(e, 'response') and e.response:
                response_data = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "response_data": str(e.response) if hasattr(e, 'response') else None
                }
            else:
                response_data = {"raw_error": str(e)}
                
            response_data.update({
                "model": model_name,
                "request_params": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "message_count": len(messages)
                }
            })
            
            # Log detailed error with response data
            log_llm_error(logger, f"Failed to generate completion: {e}", "gemini", response_data, e)
            
            raise LLMError(f"Failed to generate completion: {e}", response_data=response_data, provider="gemini") from e
    
    async def generate_json_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
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
                # Clean up content - Gemini sometimes wraps JSON in markdown code blocks
                content = content.strip()
                
                # Remove markdown code block markers if present
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                elif content.startswith("```"):
                    content = content[3:]  # Remove ```
                
                if content.endswith("```"):
                    content = content[:-3]  # Remove trailing ```
                
                content = content.strip()
                
                # If content doesn't start with {, try to find JSON object
                if not content.startswith("{"):
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start != -1 and end > start:
                        content = content[start:end]
                
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
                log_llm_error(logger, f"Failed to parse JSON from Gemini response", "gemini", response_data, e)
                raise LLMError(f"Failed to parse JSON response: {e}", response_data=response_data, provider="gemini") from e
                
        except LLMError:
            raise
        except Exception as e:
            response_data = {"raw_error": str(e)}
            log_llm_error(logger, f"Failed to generate JSON completion: {e}", "gemini", response_data, e)
            raise LLMError(f"Failed to generate JSON completion: {e}", response_data=response_data, provider="gemini") from e


# Global instance
gemini_chat = GeminiChat() 