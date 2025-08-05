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
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(message, "LLM_ERROR", details)
        self.response_data = response_data or {}
        self.provider = provider
        
    def get_detailed_message(self) -> str:
        """Get detailed error message including response data for logging."""
        msg_parts = [f"LLM Error ({self.provider or 'unknown'}): {self.message}"]
        
        if self.response_data:
            msg_parts.append("Response data:")
            for key, value in self.response_data.items():
                if key == "content" and value:
                    # Truncate long content for readability
                    content = str(value)[:500] + "..." if len(str(value)) > 500 else str(value)
                    msg_parts.append(f"  {key}: {content}")
                elif key in ["model", "finish_reason", "usage", "error_type", "error_code"]:
                    msg_parts.append(f"  {key}: {value}")
                    
        if self.details:
            msg_parts.append("Additional details:")
            for key, value in self.details.items():
                msg_parts.append(f"  {key}: {value}")
                
        return "\n".join(msg_parts)


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