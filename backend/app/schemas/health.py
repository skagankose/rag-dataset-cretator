"""Health check schemas."""

from typing import Dict, Literal

from pydantic import BaseModel


class HealthStatus(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy"]
    version: str = "1.0.0"
    environment: str
    services: Dict[str, Literal["ok", "error"]]
    message: str 