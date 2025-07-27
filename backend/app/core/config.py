"""Application configuration using Pydantic settings."""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # App configuration
    app_env: Literal["dev", "prod"] = Field(default="dev")
    backend_port: int = Field(default=8051)
    data_dir: Path = Field(default=Path("./data"))
    
    # OpenAI configuration
    openai_api_key: str = Field(..., description="OpenAI API key is required")
    openai_chat_model: str = Field(default="gpt-4o-mini")
    openai_timeout: int = Field(default=60)
    openai_max_retries: int = Field(default=5)
    
    # Ingestion defaults
    default_chunk_size: int = Field(default=1200)
    default_chunk_overlap: int = Field(default=200)
    default_total_questions: int = Field(default=10)
    strip_sections: bool = Field(default=True)
    
    @validator("data_dir")
    def ensure_data_dir_exists(cls, v: Path) -> Path:
        """Ensure data directory exists."""
        v = v.resolve()
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key is provided."""
        if not v or v == "your_key_here":
            raise ValueError("OPENAI_API_KEY must be set to a valid API key")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "dev"


# Global settings instance
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


settings = get_settings() 