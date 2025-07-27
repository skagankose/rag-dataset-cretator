"""Custom exceptions and error handling."""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error."""
    
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(AppError):
    """Configuration related error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class IngestionError(AppError):
    """Ingestion pipeline error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "INGESTION_ERROR", details)


class FetchError(IngestionError):
    """Wikipedia fetching error."""
    
    def __init__(self, message: str, url: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["url"] = url
        super().__init__(message, details)
        self.code = "FETCH_ERROR"


class CleaningError(IngestionError):
    """Content cleaning error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.code = "CLEANING_ERROR"


class SplittingError(IngestionError):
    """Text splitting error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.code = "SPLITTING_ERROR"


class LLMError(AppError):
    """LLM related error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "LLM_ERROR", details)


class StorageError(AppError):
    """Storage related error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "STORAGE_ERROR", details)


class NotFoundError(AppError):
    """Resource not found error."""
    
    def __init__(self, message: str, resource: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["resource"] = resource
        super().__init__(message, "NOT_FOUND", details) 