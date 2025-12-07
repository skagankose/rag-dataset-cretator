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
        temperature: float = 1.0,
        max_tokens: int = 1000,
        response_format: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        ...
    
    async def generate_json_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 1.0,
        max_tokens: int = 1000,
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
    elif provider == "ollama":
        from .ollama_chat import OllamaChat
        return OllamaChat()
    else:
        raise LLMError(f"Unsupported LLM provider: {provider}", provider=provider)


# Global instance
chat_provider = get_chat_provider() 