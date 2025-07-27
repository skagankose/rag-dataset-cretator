"""Markdown utilities for front matter and content handling."""

import re
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from ..core.errors import StorageError
from ..core.logging import get_logger
from .atomic import atomic_write_text, async_atomic_write_text

logger = get_logger("storage.md")


def parse_front_matter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML front matter from markdown content.
    
    Returns:
        Tuple of (front_matter_dict, content_without_front_matter)
    """
    # Match front matter pattern
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    try:
        front_matter = yaml.safe_load(match.group(1)) or {}
        body = match.group(2)
        return front_matter, body
    except yaml.YAMLError as e:
        logger.warning(f"Failed to parse YAML front matter: {e}")
        return {}, content


def create_markdown_with_front_matter(
    front_matter: Dict[str, Any],
    content: str
) -> str:
    """Create markdown content with YAML front matter."""
    if not front_matter:
        return content
    
    try:
        # Convert front matter to YAML
        yaml_content = yaml.dump(
            front_matter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        
        # Combine with content
        return f"---\n{yaml_content}---\n{content}"
    except yaml.YAMLError as e:
        raise StorageError(f"Failed to serialize front matter: {e}") from e


def write_markdown_file(
    file_path: Union[str, Path],
    front_matter: Dict[str, Any],
    content: str,
) -> None:
    """Write markdown file with front matter."""
    markdown_content = create_markdown_with_front_matter(front_matter, content)
    atomic_write_text(file_path, markdown_content)


async def async_write_markdown_file(
    file_path: Union[str, Path],
    front_matter: Dict[str, Any],
    content: str,
) -> None:
    """Asynchronously write markdown file with front matter."""
    markdown_content = create_markdown_with_front_matter(front_matter, content)
    await async_atomic_write_text(file_path, markdown_content)


def read_markdown_file(file_path: Union[str, Path]) -> Tuple[Dict[str, Any], str]:
    """Read markdown file and extract front matter and content.
    
    Returns:
        Tuple of (front_matter_dict, content)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise StorageError(f"Markdown file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return parse_front_matter(content)
    except OSError as e:
        raise StorageError(f"Failed to read markdown file {file_path}: {e}") from e


def create_markdown_table(
    headers: list[str],
    rows: list[list[str]],
    title: Optional[str] = None,
) -> str:
    """Create a markdown table from headers and rows."""
    if not headers or not rows:
        return ""
    
    # Ensure all rows have the same number of columns
    max_cols = len(headers)
    normalized_rows = []
    for row in rows:
        normalized_row = list(row)
        while len(normalized_row) < max_cols:
            normalized_row.append("")
        normalized_rows.append(normalized_row[:max_cols])
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in normalized_rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Build table
    lines = []
    
    if title:
        lines.append(f"# {title}")
        lines.append("")
    
    # Header row
    header_row = "| " + " | ".join(
        header.ljust(col_widths[i]) for i, header in enumerate(headers)
    ) + " |"
    lines.append(header_row)
    
    # Separator row
    separator_row = "| " + " | ".join(
        "-" * col_widths[i] for i in range(len(headers))
    ) + " |"
    lines.append(separator_row)
    
    # Data rows
    for row in normalized_rows:
        data_row = "| " + " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        ) + " |"
        lines.append(data_row)
    
    return "\n".join(lines)


def escape_markdown(text: str) -> str:
    """Escape special markdown characters in text."""
    # Escape common markdown special characters
    special_chars = r"[\\`*_{}[\]()#+-.!|]"
    return re.sub(special_chars, r"\\\g<0>", text) 