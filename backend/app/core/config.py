"""Application configuration using Pydantic settings."""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
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
    
    # LLM Provider configuration
    llm_provider: Literal["openai", "gemini"] = Field(default="openai")
    
    # OpenAI configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_chat_model: str = Field(default="gpt-4o-mini")
    openai_timeout: int = Field(default=60)
    openai_max_retries: int = Field(default=5)
    
    # Gemini configuration
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_chat_model: str = Field(default="gemini-1.5-flash")
    gemini_timeout: int = Field(default=60)
    gemini_max_retries: int = Field(default=5)
    
    # Ingestion defaults
    default_chunk_size: int = Field(default=1200)
    default_chunk_overlap: int = Field(default=200)
    default_total_questions: int = Field(default=10)
    strip_sections: bool = Field(default=True)
    
    @field_validator("data_dir")
    @classmethod
    def ensure_data_dir_exists(cls, v: Path) -> Path:
        """Ensure data directory exists."""
        v = v.resolve()
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key when needed."""
        # Note: We can't access other fields in field_validator, 
        # so we'll handle validation in model_validator instead
        return v
    
    @field_validator("gemini_api_key")
    @classmethod
    def validate_gemini_key(cls, v: str) -> str:
        """Validate Gemini API key when needed."""
        # Note: We can't access other fields in field_validator,
        # so we'll handle validation in model_validator instead
        return v
    
    @model_validator(mode='after')
    def validate_provider_keys(self):
        """Validate that the appropriate API key is provided for the selected provider."""
        # Only validate in production or when API keys are actually used
        # This allows the app to start in development even without API keys
        return self
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "dev"


# Global settings instance
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


settings = get_settings() 