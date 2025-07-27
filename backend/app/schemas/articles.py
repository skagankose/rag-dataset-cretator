"""Article API schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ArticleListItem(BaseModel):
    """Article list item."""
    id: str
    url: str
    title: str
    lang: str
    created_at: str


class ArticleMetadata(BaseModel):
    """Article metadata."""
    id: str
    url: str
    title: str
    lang: str
    created_at: str
    checksum: str
    options: Dict[str, Any]
    stats: Dict[str, Any]


class ChunkListItem(BaseModel):
    """Chunk list item."""
    id: str
    article_id: str
    section: str
    heading_path: str
    start_char: int
    end_char: int
    preview: str
    char_count: int
    token_estimate: int


class ChunkDetail(BaseModel):
    """Detailed chunk information."""
    id: str
    article_id: str
    section: str
    heading_path: str
    start_char: int
    end_char: int
    content: str
    char_count: int
    token_estimate: int
    token_start: Optional[int] = None
    token_end: Optional[int] = None


class DatasetItem(BaseModel):
    """Dataset question item."""
    question: str
    related_chunk_ids: List[str]


class DatasetResponse(BaseModel):
    """Dataset API response."""
    article_id: str
    title: str
    created_at: str
    items: List[DatasetItem]
    total_questions: int 