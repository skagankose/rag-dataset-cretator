"""File system path management."""
from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Dict, Optional, Union

from ..core.config import settings


def _normalize_for_comparison(s: str) -> str:
    """Normalize a string for comparison (NFC + casefold)."""
    return unicodedata.normalize("NFC", s).casefold()


class StoragePaths:
    """Manages file system paths for the application."""
    
    def __init__(self, base_dir: Union[str, Path] = None):
        self.base_dir = Path(base_dir) if base_dir else settings.data_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Cache for resolved article directories
        self._dir_cache: Dict[str, Path] = {}
    
    @property
    def index_file(self) -> Path:
        """Path to the main index.json file."""
        return self.base_dir / "index.json"
    
    @property
    def articles_dir(self) -> Path:
        """Path to the articles directory."""
        path = self.base_dir / "articles"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _find_article_dir_on_disk(self, article_id: str) -> Optional[Path]:
        """Find the actual article directory on disk by scanning.
        
        This handles Unicode normalization differences between Python strings
        and the filesystem (macOS APFS uses NFD normalization).
        """
        # Check cache first
        cache_key = _normalize_for_comparison(article_id)
        if cache_key in self._dir_cache:
            cached = self._dir_cache[cache_key]
            if cached.exists():
                return cached
            else:
                # Cache is stale, remove it
                del self._dir_cache[cache_key]
        
        articles_path = self.articles_dir
        target_normalized = _normalize_for_comparison(article_id)
        
        # First try exact match (fast path)
        exact_path = articles_path / article_id
        if exact_path.exists() and exact_path.is_dir():
            self._dir_cache[cache_key] = exact_path
            return exact_path
        
        # Scan directory for a match using Unicode normalization
        try:
            for entry in articles_path.iterdir():
                if entry.is_dir():
                    entry_normalized = _normalize_for_comparison(entry.name)
                    if entry_normalized == target_normalized:
                        self._dir_cache[cache_key] = entry
                        return entry
        except OSError:
            pass
        
        return None
    
    def article_dir(self, article_id: str, create: bool = True) -> Path:
        """Path to a specific article directory.
        
        Args:
            article_id: The article ID
            create: If True, create the directory if it doesn't exist.
                    If False, return the expected path without creating.
        """
        # Try to find existing directory first
        existing = self._find_article_dir_on_disk(article_id)
        if existing:
            return existing
        
        # Directory doesn't exist - return expected path
        path = self.articles_dir / article_id
        if create:
            path.mkdir(parents=True, exist_ok=True)
        return path
    
    def article_dir_readonly(self, article_id: str) -> Optional[Path]:
        """Get article directory for reading (doesn't create if missing).
        
        Returns None if the directory doesn't exist.
        """
        return self._find_article_dir_on_disk(article_id)
    
    def article_file(self, article_id: str) -> Path:
        """Path to the article.md file."""
        return self.article_dir(article_id, create=False) / "article.md"
    
    def article_file_readonly(self, article_id: str) -> Optional[Path]:
        """Get article.md path for reading (returns None if dir doesn't exist)."""
        dir_path = self.article_dir_readonly(article_id)
        if dir_path:
            return dir_path / "article.md"
        return None
    
    def chunks_dir(self, article_id: str, create: bool = True) -> Path:
        """Path to the chunks directory for an article."""
        path = self.article_dir(article_id, create=create) / "chunks"
        if create:
            path.mkdir(parents=True, exist_ok=True)
        return path
    
    def chunks_dir_readonly(self, article_id: str) -> Optional[Path]:
        """Get chunks directory for reading (returns None if doesn't exist)."""
        dir_path = self.article_dir_readonly(article_id)
        if dir_path:
            chunks_path = dir_path / "chunks"
            if chunks_path.exists():
                return chunks_path
        return None
    
    def chunk_file(self, article_id: str, chunk_id: str) -> Path:
        """Path to a specific chunk file."""
        return self.chunks_dir(article_id, create=False) / f"{chunk_id}.md"
    
    def chunks_index_file(self, article_id: str) -> Path:
        """Path to the chunks_index.md file."""
        return self.article_dir(article_id, create=False) / "chunks_index.md"
    
    def dataset_file(self, article_id: str) -> Path:
        """Path to the dataset.md file."""
        return self.article_dir(article_id, create=False) / "dataset.md"
    
    def dataset_file_readonly(self, article_id: str) -> Optional[Path]:
        """Get dataset.md path for reading (returns None if dir doesn't exist)."""
        dir_path = self.article_dir_readonly(article_id)
        if dir_path:
            return dir_path / "dataset.md"
        return None
    
    def logs_file(self, article_id: str) -> Path:
        """Path to the logs.ndjson file."""
        return self.article_dir(article_id, create=False) / "logs.ndjson"
    
    def raw_html_file(self, article_id: str) -> Path:
        """Path to the raw HTML file."""
        return self.article_dir(article_id, create=False) / "raw.html"
    
    def clear_cache(self) -> None:
        """Clear the directory cache."""
        self._dir_cache.clear()


# Global paths instance
paths = StoragePaths() 