"""Atomic file operations for safe concurrent access."""

import json
import os
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Union

import aiofiles

from ..core.errors import StorageError
from ..core.logging import get_logger

logger = get_logger("storage.atomic")

# Global lock for index operations
_index_lock = threading.Lock()


def atomic_write_text(file_path: Union[str, Path], content: str) -> None:
    """Atomically write text content to a file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temporary file first
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as tmp_file:
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Atomic move
        os.replace(tmp_path, file_path)
        logger.debug(f"Atomically wrote file: {file_path}")
    except Exception as e:
        # Clean up temp file on error
        tmp_path.unlink(missing_ok=True)
        raise StorageError(f"Failed to atomically write {file_path}: {e}") from e


def atomic_write_json(file_path: Union[str, Path], data: Any) -> None:
    """Atomically write JSON data to a file."""
    content = json.dumps(data, indent=2, ensure_ascii=False)
    atomic_write_text(file_path, content)


async def async_atomic_write_text(file_path: Union[str, Path], content: str) -> None:
    """Asynchronously atomically write text content to a file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temporary file first
    tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    
    try:
        async with aiofiles.open(tmp_path, "w", encoding="utf-8") as tmp_file:
            await tmp_file.write(content)
        
        # Atomic move
        os.replace(tmp_path, file_path)
        logger.debug(f"Atomically wrote file: {file_path}")
    except Exception as e:
        # Clean up temp file on error
        tmp_path.unlink(missing_ok=True)
        raise StorageError(f"Failed to atomically write {file_path}: {e}") from e


async def async_atomic_write_json(file_path: Union[str, Path], data: Any) -> None:
    """Asynchronously atomically write JSON data to a file."""
    content = json.dumps(data, indent=2, ensure_ascii=False)
    await async_atomic_write_text(file_path, content)


@contextmanager
def index_lock() -> Generator[None, None, None]:
    """Context manager for index file operations."""
    with _index_lock:
        logger.debug("Acquired index lock")
        try:
            yield
        finally:
            logger.debug("Released index lock")


def safe_read_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """Safely read JSON file with fallback to default."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to read JSON file {file_path}: {e}")
        return default


async def async_safe_read_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """Asynchronously safely read JSON file with fallback to default."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return default
    
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to read JSON file {file_path}: {e}")
        return default 