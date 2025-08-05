"""Articles API endpoints."""

import shutil
from typing import List

from fastapi import APIRouter, HTTPException

from ..core.errors import NotFoundError
from ..core.logging import get_logger
from ..schemas.articles import ArticleListItem, ArticleMetadata, ChunkListItem, ChunkDetail
from ..storage.index import article_index
from ..storage.md import read_markdown_file
from ..storage.paths import paths
from ..utils.text import count_tokens_estimate

logger = get_logger("api.articles")

router = APIRouter()


@router.get("/articles", response_model=List[ArticleListItem])
async def list_articles() -> List[ArticleListItem]:
    """List all articles."""
    try:
        entries = article_index.list_articles()
        return [
            ArticleListItem(
                id=entry.id,
                url=entry.url,
                title=entry.title,
                lang=entry.lang,
                created_at=entry.created_at,
            )
            for entry in entries
        ]
    except Exception as e:
        logger.error(f"Failed to list articles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list articles"
        ) from e


@router.get("/articles/{article_id}", response_model=ArticleMetadata)
async def get_article(article_id: str) -> ArticleMetadata:
    """Get article metadata."""
    try:
        # Get from index
        entry = article_index.get_article(article_id)
        
        # Read article file for additional metadata
        article_path = paths.article_file(article_id)
        front_matter, _ = read_markdown_file(article_path)
        
        return ArticleMetadata(
            id=entry.id,
            url=entry.url,
            title=entry.title,
            lang=entry.lang,
            created_at=entry.created_at,
            checksum=entry.checksum,
            options=front_matter.get("options", {}),
            stats=front_matter.get("stats", {}),
        )
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to get article {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get article"
        ) from e


@router.get("/articles/{article_id}/chunks", response_model=List[ChunkDetail])
async def list_chunks(article_id: str) -> List[ChunkDetail]:
    """List chunks for an article."""
    try:
        # Verify article exists
        article_index.get_article(article_id)
        
        # Get chunks directory
        chunks_dir = paths.chunks_dir(article_id)
        
        if not chunks_dir.exists():
            return []
        
        chunks = []
        
        # Read each chunk file (support both old and new formats)
        # Get new format files (article_id_c0001.md)
        new_format_files = list(chunks_dir.glob("*_c*.md"))
        # Get old format files (c0001.md) - only files that are exactly in old format
        old_format_files = [f for f in chunks_dir.glob("c*.md") 
                           if f.name.startswith("c") and "_" not in f.name]
        chunk_files = new_format_files + old_format_files
        for chunk_file in sorted(chunk_files):
            try:
                front_matter, content = read_markdown_file(chunk_file)
                
                chunk = ChunkDetail(
                    id=front_matter.get("id", chunk_file.stem),
                    article_id=article_id,
                    section=front_matter.get("section", ""),
                    heading_path=front_matter.get("heading_path", "Lead"),
                    start_char=front_matter.get("start_char", 0),
                    end_char=front_matter.get("end_char", 0),
                    content=content,
                    char_count=len(content),
                    token_estimate=count_tokens_estimate(content),
                    token_start=front_matter.get("token_start"),
                    token_end=front_matter.get("token_end"),
                )
                chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Failed to read chunk file {chunk_file}: {e}")
                continue
        
        return chunks
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to list chunks for {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list chunks"
        ) from e 


@router.delete("/articles/{article_id}")
async def delete_article(article_id: str) -> dict:
    """Delete an article and all related files."""
    try:
        # Verify article exists
        article_index.get_article(article_id)
        
        # Remove from index
        removed = article_index.remove_article(article_id)
        
        if not removed:
            raise HTTPException(
                status_code=404,
                detail=f"Article not found: {article_id}"
            )
        
        # Delete article directory and all contents
        article_dir = paths.article_dir(article_id)
        if article_dir.exists():
            shutil.rmtree(article_dir)
            logger.info(f"Deleted article directory: {article_dir}")
        
        logger.info(f"Successfully deleted article: {article_id}")
        return {"message": "Article deleted successfully", "article_id": article_id}
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to delete article {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete article"
        ) from e 