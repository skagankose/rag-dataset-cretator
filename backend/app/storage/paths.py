"""File system path management."""

from pathlib import Path
from typing import Union

from ..core.config import settings


class StoragePaths:
    """Manages file system paths for the application."""
    
    def __init__(self, base_dir: Union[str, Path] = None):
        self.base_dir = Path(base_dir) if base_dir else settings.data_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    def article_dir(self, article_id: str) -> Path:
        """Path to a specific article directory."""
        path = self.articles_dir / article_id
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def article_file(self, article_id: str) -> Path:
        """Path to the article.md file."""
        return self.article_dir(article_id) / "article.md"
    
    def chunks_dir(self, article_id: str) -> Path:
        """Path to the chunks directory for an article."""
        path = self.article_dir(article_id) / "chunks"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def chunk_file(self, article_id: str, chunk_id: str) -> Path:
        """Path to a specific chunk file."""
        return self.chunks_dir(article_id) / f"{chunk_id}.md"
    
    def chunks_index_file(self, article_id: str) -> Path:
        """Path to the chunks_index.md file."""
        return self.article_dir(article_id) / "chunks_index.md"
    
    def dataset_file(self, article_id: str) -> Path:
        """Path to the dataset.md file."""
        return self.article_dir(article_id) / "dataset.md"
    
    def logs_file(self, article_id: str) -> Path:
        """Path to the logs.ndjson file."""
        return self.article_dir(article_id) / "logs.ndjson"
    
    def raw_html_file(self, article_id: str) -> Path:
        """Path to the raw HTML file."""
        return self.article_dir(article_id) / "raw.html"


# Global paths instance
paths = StoragePaths() 