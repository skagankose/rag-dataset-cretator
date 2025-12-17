"""File download API endpoints."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from ..core.errors import NotFoundError
from ..core.logging import get_logger
from ..storage.index import article_index
from ..storage.paths import paths

logger = get_logger("api.files")

router = APIRouter()


@router.get("/files/{article_id}/{filename}")
async def download_file(article_id: str, filename: str) -> Response:
    """Download article files."""
    try:
        # Verify article exists (and normalize article_id to canonical stored ID)
        entry = article_index.get_article(article_id)
        article_id = entry.id
        
        # Map filename to file path
        file_path = _get_file_path(article_id, filename)
        
        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        # Determine media type
        media_type = _get_media_type(filename)
        
        # Try FileResponse first, but fallback to manual read if it fails
        # This handles edge cases with Unicode paths on some filesystems where FileResponse/stat might fail
        try:
            return FileResponse(
                path=file_path,
                media_type=media_type,
                filename=filename,
            )
        except Exception as e:
            logger.warning(f"FileResponse failed for {file_path}, falling back to manual read: {e}")
            
            async with aiofiles.open(file_path, mode='rb') as f:
                content = await f.read()
            
            return Response(
                content=content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
            
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file {filename} for {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download file"
        ) from e


def _get_file_path(article_id: str, filename: str) -> Optional[Path]:
    """Get the file path for a given filename."""
    
    # Map allowed filenames to their paths
    allowed_files = {
        "article.md": paths.article_file(article_id),
        "chunks_index.md": paths.chunks_index_file(article_id),
        "dataset.md": paths.dataset_file(article_id),
        "logs.ndjson": paths.logs_file(article_id),
        "raw.html": paths.raw_html_file(article_id),
    }
    
    # Check for chunk files (c0001.md, c0002.md, etc.)
    if filename.startswith("c") and filename.endswith(".md"):
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