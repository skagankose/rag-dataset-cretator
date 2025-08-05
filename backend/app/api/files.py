"""File download API endpoints."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..core.errors import NotFoundError
from ..core.logging import get_logger
from ..storage.index import article_index
from ..storage.paths import paths

logger = get_logger("api.files")

router = APIRouter()


@router.get("/files/{article_id}/{filename}")
async def download_file(article_id: str, filename: str) -> FileResponse:
    """Download article files."""
    try:
        # Verify article exists
        article_index.get_article(article_id)
        
        # Map filename to file path
        file_path = _get_file_path(article_id, filename)
        
        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        # Determine media type
        media_type = _get_media_type(filename)
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
        )
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to download file {filename} for {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download file"
        ) from e


def _get_file_path(article_id: str, filename: str) -> Path | None:
    """Get the file path for a given filename."""
    
    # Map allowed filenames to their paths
    allowed_files = {
        "article.md": paths.article_file(article_id),
        "chunks_index.md": paths.chunks_index_file(article_id),
        "dataset.md": paths.dataset_file(article_id),
        "logs.ndjson": paths.logs_file(article_id),
        "raw.html": paths.raw_html_file(article_id),
    }
    
    # Check for chunk files (both old format c0001.md and new format article_id_c0001.md)
    if filename.endswith(".md"):
        # Try new format first (article_id_c0001.md)
        if "_c" in filename:
            chunk_id = filename[:-3]  # Remove .md extension
            chunk_path = paths.chunk_file(article_id, chunk_id)
            if chunk_path.exists():
                allowed_files[filename] = chunk_path
        # Try old format (c0001.md)
        elif filename.startswith("c"):
            chunk_id = filename[:-3]  # Remove .md extension
            chunk_path = paths.chunk_file(article_id, chunk_id)
            if chunk_path.exists():
                allowed_files[filename] = chunk_path
    
    return allowed_files.get(filename)


def _get_media_type(filename: str) -> str:
    """Get media type for file download."""
    
    if filename.endswith(".md"):
        return "text/markdown"
    elif filename.endswith(".json"):
        return "application/json"
    elif filename.endswith(".ndjson"):
        return "application/x-ndjson"
    elif filename.endswith(".html"):
        return "text/html"
    else:
        return "text/plain" 