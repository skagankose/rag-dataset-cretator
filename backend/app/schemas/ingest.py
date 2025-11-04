"""Ingestion API schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, model_validator


class IngestOptions(BaseModel):
    """Ingestion configuration options."""
    chunk_size: int = Field(default=1200, ge=100, le=5000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    split_strategy: Literal["recursive", "sentence", "header_aware"] = Field(default="header_aware")
    total_questions: int = Field(default=10, ge=1, le=50)
    llm_model: Optional[str] = Field(default=None)
    reingest: bool = Field(default=False)
    
    @model_validator(mode='after')
    def set_default_model(self):
        """Set default model based on the configured provider."""
        if self.llm_model is None:
            from ..core.config import settings
            if settings.llm_provider == "openai":
                self.llm_model = settings.openai_chat_model
            elif settings.llm_provider == "gemini":
                self.llm_model = settings.gemini_chat_model
            else:
                self.llm_model = "gpt-4o-mini"  # fallback
        return self


class IngestRequest(BaseModel):
    """Ingestion request payload."""
    wikipedia_url: HttpUrl
    options: Optional[IngestOptions] = None


class IngestResponse(BaseModel):
    """Ingestion response payload."""
    run_id: str
    article_id: Optional[str] = None
    message: str
    status: Literal["started", "existing", "failed"]


class IngestProgress(BaseModel):
    """Ingestion progress event."""
    run_id: str
    stage: Literal[
        "FETCHING",
        "CLEANING", 
        "SPLITTING",
        "WRITE_MARKDOWN",
        "QUESTION_GEN",
        "WRITE_DATASET_MD",
        "DONE",
        "FAILED"
    ]
    message: str
    timestamp: float
    article_id: Optional[str] = None
    details: Optional[dict] = None 