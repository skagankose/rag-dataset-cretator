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
    msg_parts = [f"🚨 LLM ERROR ({provider.upper()}):", error_message]
    
    if response_data:
        msg_parts.append("📄 RESPONSE DATA:")
        for key, value in response_data.items():
            if key == "content" and value:
                # Truncate long content for readability
                content = str(value)[:500] + "..." if len(str(value)) > 500 else str(value)
                msg_parts.append(f"   └─ {key}: {content}")
            elif key in ["model", "finish_reason", "usage", "error_type", "error_code"]:
                msg_parts.append(f"   └─ {key}: {value}")
    
    if exception:
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