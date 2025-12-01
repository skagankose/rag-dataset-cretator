"""Logging configuration."""

import logging
import sys
from typing import Any, Dict

from .config import settings


def setup_logging() -> None:
    """Setup application logging."""
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO if settings.is_development else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    
    # Set specific loggers
    loggers = {
        "app": logging.INFO,
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,
        "httpx": logging.WARNING,
        "openai": logging.WARNING,
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.{name}")


def log_llm_error(logger: logging.Logger, error_message: str, provider: str, response_data: Dict[str, Any] = None, exception: Exception = None) -> None:
    """Log LLM error with detailed response information."""
    import json
    
    msg_parts = [f"🚨 LLM ERROR ({provider.upper()}):", "", error_message, ""]
    
    if response_data:
        msg_parts.append("📄 RESPONSE DATA:")
        
        # Define key display priorities and formatting
        priority_keys = ["model", "finish_reason", "response_finish_reason", "candidate_finish_reason", "error_type", "error_code"]
        nested_keys = ["prompt_feedback", "candidate_safety_ratings", "safety_ratings"]
        
        # Display priority keys first
        for key in priority_keys:
            if key in response_data:
                msg_parts.append(f"   └─ {key}: {response_data[key]}")
        
        # Display nested structures with better formatting
        for key in nested_keys:
            if key in response_data and response_data[key]:
                msg_parts.append(f"   └─ {key}:")
                try:
                    formatted = json.dumps(response_data[key], indent=6)
                    for line in formatted.split('\n'):
                        msg_parts.append(f"      {line}")
                except Exception:
                    msg_parts.append(f"      {response_data[key]}")
        
        # Display other keys
        displayed_keys = set(priority_keys + nested_keys)
        for key, value in response_data.items():
            if key not in displayed_keys:
                if key == "content" and value:
                    # Truncate long content for readability
                    content = str(value)[:500] + "..." if len(str(value)) > 500 else str(value)
                    msg_parts.append(f"   └─ {key}: {content}")
                elif key == "prompt_preview" and value:
                    # Display prompt preview with proper truncation
                    msg_parts.append(f"   └─ {key}:")
                    msg_parts.append(f"      {value}")
                elif key in ["prompt_length", "response_parts_count", "candidates_count", "has_text", 
                           "candidate_has_content", "candidate_parts_count", "note"]:
                    msg_parts.append(f"   └─ {key}: {value}")
                elif isinstance(value, (list, dict)):
                    # Format complex structures
                    try:
                        formatted = json.dumps(value, indent=6)
                        msg_parts.append(f"   └─ {key}:")
                        for line in formatted.split('\n'):
                            msg_parts.append(f"      {line}")
                    except Exception:
                        msg_parts.append(f"   └─ {key}: {value}")
    
    if exception:
        msg_parts.append("")
        msg_parts.append(f"🔥 EXCEPTION: {type(exception).__name__}: {str(exception)}")
    
    # Log as error level to ensure it appears on terminal
    logger.error("\n".join(msg_parts))


class StructuredLogger:
    """Structured logger for ingestion progress."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_event(
        self,
        stage: str,
        message: str,
        level: str = "info",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Log a structured event and return the event dict."""
        import time
        
        event = {
            "timestamp": time.time(),
            "stage": stage,
            "message": message,
            "level": level,
            **kwargs,
        }
        
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(f"[{stage}] {message}", extra=kwargs)
        
        return event 