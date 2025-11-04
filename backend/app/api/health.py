"""Health check endpoint."""

from fastapi import APIRouter

from ..core.config import settings
from ..schemas.health import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Health check endpoint."""
    
    # Check OpenAI API key
    openai_status = "ok" if settings.openai_api_key != "your_key_here" else "error"
    
    # Check data directory
    data_dir_status = "ok" if settings.data_dir.exists() else "error"
    
    # Determine overall status
    overall_status = "healthy" if all([
        openai_status == "ok",
        data_dir_status == "ok",
    ]) else "unhealthy"
    
    return HealthStatus(
        status=overall_status,
        environment=settings.app_env,
        services={
            "openai": openai_status,
            "data_dir": data_dir_status,
        },
        message="Service is running" if overall_status == "healthy" else "Service has issues"
    ) 