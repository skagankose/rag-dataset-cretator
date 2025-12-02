"""Configuration endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from ..core.config import settings

router = APIRouter()


class ConfigResponse(BaseModel):
    """Configuration response."""
    prompt_language: str
    llm_provider: str
    default_chunk_size: int
    default_chunk_overlap: int
    default_total_questions: int


@router.get("/config", response_model=ConfigResponse)
async def get_config() -> ConfigResponse:
    """Get application configuration."""
    return ConfigResponse(
        prompt_language=settings.prompt_language,
        llm_provider=settings.llm_provider,
        default_chunk_size=settings.default_chunk_size,
        default_chunk_overlap=settings.default_chunk_overlap,
        default_total_questions=settings.default_total_questions,
    )

