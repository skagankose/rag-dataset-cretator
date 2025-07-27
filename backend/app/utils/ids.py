"""ID generation utilities."""

import re
import uuid
from typing import List


def generate_run_id() -> str:
    """Generate a unique run ID for ingestion tracking."""
    return f"run_{uuid.uuid4().hex[:8]}"


def generate_chunk_id(index: int) -> str:
    """Generate a deterministic chunk ID from index."""
    return f"c{index:04d}"


def parse_chunk_id(chunk_id: str) -> int:
    """Parse chunk index from chunk ID."""
    match = re.match(r'c(\d+)', chunk_id)
    if match:
        return int(match.group(1))
    raise ValueError(f"Invalid chunk ID format: {chunk_id}")


def validate_chunk_ids(chunk_ids: List[str]) -> bool:
    """Validate a list of chunk IDs."""
    for chunk_id in chunk_ids:
        try:
            parse_chunk_id(chunk_id)
        except ValueError:
            return False
    return True


def sort_chunk_ids(chunk_ids: List[str]) -> List[str]:
    """Sort chunk IDs numerically."""
    def sort_key(chunk_id: str) -> int:
        try:
            return parse_chunk_id(chunk_id)
        except ValueError:
            return float('inf')
    
    return sorted(chunk_ids, key=sort_key)


def format_chunk_ids(chunk_ids: List[str]) -> str:
    """Format chunk IDs as a comma-separated string."""
    sorted_ids = sort_chunk_ids(chunk_ids)
    return ", ".join(sorted_ids)


def parse_chunk_ids(chunk_ids_str: str) -> List[str]:
    """Parse chunk IDs from a comma-separated string."""
    if not chunk_ids_str:
        return []
    
    chunk_ids = [cid.strip() for cid in chunk_ids_str.split(',')]
    return [cid for cid in chunk_ids if cid] 