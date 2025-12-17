"""Index management for articles."""

import hashlib
import time
import unicodedata
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ..core.errors import NotFoundError, StorageError
from ..core.logging import get_logger
from .atomic import atomic_write_json, index_lock, safe_read_json
from .paths import paths

logger = get_logger("storage.index")


class ArticleIndexEntry(BaseModel):
    """Article index entry model."""
    id: str
    url: str
    title: str
    lang: str
    created_at: str
    checksum: str


class ArticleIndex:
    """Manages the main article index."""
    
    def __init__(self):
        self.file_path = paths.index_file
    
    def _load_index(self) -> List[ArticleIndexEntry]:
        """Load the index from disk."""
        data = safe_read_json(self.file_path, [])
        return [ArticleIndexEntry(**entry) for entry in data]
    
    def _save_index(self, entries: List[ArticleIndexEntry]) -> None:
        """Save the index to disk."""
        data = [entry.dict() for entry in entries]
        atomic_write_json(self.file_path, data)
    
    def list_articles(self) -> List[ArticleIndexEntry]:
        """List all articles in the index."""
        with index_lock():
            return self._load_index()
    
    def get_article(self, article_id: str) -> ArticleIndexEntry:
        """Get a specific article by ID."""
        with index_lock():
            entries = self._load_index()
            for entry in entries:
                if entry.id == article_id:
                    return entry
            
            # Fallback: Unicode normalization-insensitive match.
            # This fixes cases where the same visible ID is represented using a different
            # normalization form (e.g., Turkish dotted-i and combining marks) between
            # browser URL decoding, JSON, and filesystem.
            target_nfc = unicodedata.normalize("NFC", article_id)
            target_casefold = target_nfc.casefold()
            for entry in entries:
                entry_nfc = unicodedata.normalize("NFC", entry.id)
                if entry_nfc == target_nfc or entry_nfc.casefold() == target_casefold:
                    return entry
            raise NotFoundError(f"Article not found: {article_id}", "article")
    
    def find_by_checksum(self, checksum: str) -> Optional[ArticleIndexEntry]:
        """Find article by URL checksum."""
        with index_lock():
            entries = self._load_index()
            for entry in entries:
                if entry.checksum == checksum:
                    return entry
            return None
    
    def add_article(
        self,
        article_id: str,
        url: str,
        title: str,
        lang: str,
        checksum: str,
    ) -> ArticleIndexEntry:
        """Add a new article to the index."""
        with index_lock():
            entries = self._load_index()
            
            # Check if article already exists
            for entry in entries:
                if entry.id == article_id:
                    raise StorageError(f"Article already exists: {article_id}")
            
            # Create new entry
            new_entry = ArticleIndexEntry(
                id=article_id,
                url=url,
                title=title,
                lang=lang,
                created_at=datetime.utcnow().isoformat(),
                checksum=checksum,
            )
            
            entries.append(new_entry)
            self._save_index(entries)
            
            logger.info(f"Added article to index: {article_id}")
            return new_entry
    
    def remove_article(self, article_id: str) -> bool:
        """Remove an article from the index."""
        with index_lock():
            entries = self._load_index()
            
            # Find and remove entry
            for i, entry in enumerate(entries):
                if entry.id == article_id:
                    del entries[i]
                    self._save_index(entries)
                    logger.info(f"Removed article from index: {article_id}")
                    return True
            
            return False
    
    def update_article(
        self,
        article_id: str,
        **updates: str,
    ) -> ArticleIndexEntry:
        """Update an article in the index."""
        with index_lock():
            entries = self._load_index()
            
            # Find and update entry
            for entry in entries:
                if entry.id == article_id:
                    # Update allowed fields
                    for field, value in updates.items():
                        if hasattr(entry, field):
                            setattr(entry, field, value)
                    
                    self._save_index(entries)
                    logger.info(f"Updated article in index: {article_id}")
                    return entry
            
            raise NotFoundError(f"Article not found: {article_id}", "article")


def compute_url_checksum(url: str) -> str:
    """Compute SHA-256 checksum of URL for duplicate detection."""
    return hashlib.sha256(url.encode()).hexdigest()


def generate_article_id(url: str, title: str) -> str:
    """Generate a unique article ID from URL and title.
    
    Only uses ASCII characters to avoid URL encoding issues and filesystem compatibility problems.
    """
    # Combine URL and timestamp for uniqueness
    timestamp = str(int(time.time()))
    combined = f"{url}_{title}_{timestamp}"
    hash_part = hashlib.sha256(combined.encode()).hexdigest()[:8]
    
    # Create readable ID using only ASCII alphanumeric characters
    # This avoids URL encoding issues with non-ASCII characters like Turkish characters
    title_part = "".join(c for c in title if c.isascii() and c.isalnum())[:20].lower()
    if not title_part:
        title_part = "article"
    
    return f"{title_part}_{hash_part}"


# Global index instance
article_index = ArticleIndex() 