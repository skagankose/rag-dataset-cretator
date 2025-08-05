"""LLM provider factory for managing different chat completion providers."""

from typing import Protocol, Dict, List, Any

from ..core.config import settings
from ..core.errors import LLMError


class ChatProvider(Protocol):
    """Protocol for chat completion providers."""
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 100000,
        response_format: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        ...
    
    async def generate_json_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 100000,
    ) -> Dict[str, Any]:
        """Generate JSON-formatted completion."""
        ...


def get_chat_provider(provider: str = None):
    """Get a chat provider instance."""
    provider = provider or settings.llm_provider.lower()
    
    if provider == "openai":
        from .openai_chat import OpenAIChat
        return OpenAIChat()
    elif provider == "gemini":
        from .gemini_chat import GeminiChat
        return GeminiChat()
    else:
        raise LLMError(f"Unsupported LLM provider: {provider}", provider=provider)


# Global instance
chat_provider = get_chat_provider() 