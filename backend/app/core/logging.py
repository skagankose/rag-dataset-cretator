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