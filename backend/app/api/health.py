"""Health check endpoint."""

from fastapi import APIRouter

from ..core.config import settings
from ..schemas.health import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Health check endpoint."""
    
    # Check LLM provider configuration
    llm_status = "error"
    if settings.llm_provider == "openai":
        llm_status = "ok" if settings.openai_api_key and settings.openai_api_key != "your_key_here" and settings.openai_api_key != "your_secret" else "error"
    elif settings.llm_provider == "gemini":
        llm_status = "ok" if settings.gemini_api_key and settings.gemini_api_key != "your_key_here" and settings.gemini_api_key != "your_secret" else "error"
    elif settings.llm_provider == "ollama":
        # For Ollama, just check that the base URL is configured
        llm_status = "ok" if settings.ollama_api_base else "error"
    
    # Check data directory
    data_dir_status = "ok" if settings.data_dir.exists() else "error"
    
    # Determine overall status
    overall_status = "healthy" if all([
        llm_status == "ok",
        data_dir_status == "ok",
    ]) else "unhealthy"
    
    return HealthStatus(
        status=overall_status,
        environment=settings.app_env,
        services={
            "llm_provider": llm_status,
            "data_dir": data_dir_status,
        },
        message="Service is running" if overall_status == "healthy" else "Service has issues"
    ) 