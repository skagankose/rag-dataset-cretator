"""Configuration endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from ..core.config import settings

router = APIRouter()


class ConfigResponse(BaseModel):
    """Configuration response."""
    prompt_language: str
    llm_provider: str
    llm_model: str
    default_chunk_size: int
    default_chunk_overlap: int
    default_total_questions: int


@router.get("/config", response_model=ConfigResponse)
async def get_config() -> ConfigResponse:
    """Get application configuration."""
    # Get the appropriate model based on the provider
    if settings.llm_provider == "openai":
        llm_model = settings.openai_chat_model
    elif settings.llm_provider == "gemini":
        llm_model = settings.gemini_chat_model
    elif settings.llm_provider == "ollama":
        llm_model = settings.ollama_chat_model
    else:
        llm_model = "unknown"
    
    return ConfigResponse(
        prompt_language=settings.prompt_language,
        llm_provider=settings.llm_provider,
        llm_model=llm_model,
        default_chunk_size=settings.default_chunk_size,
        default_chunk_overlap=settings.default_chunk_overlap,
        default_total_questions=settings.default_total_questions,
    )


