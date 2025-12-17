"""Articles API endpoints."""

import io
import json
import shutil
import zipfile
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse

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
        article_id = entry.id
        
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
        entry = article_index.get_article(article_id)
        article_id = entry.id
        
        # Get chunks directory
        chunks_dir = paths.chunks_dir(article_id)
        
        if not chunks_dir.exists():
            return []
        
        chunks = []
        
        # Read each chunk file
        for chunk_file in sorted(chunks_dir.glob("c*.md")):
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


@router.get("/articles/{article_id}/export")
async def export_article(article_id: str) -> Response:
    """Export complete article data as JSON (content, chunks, and questions).
    
    This endpoint uses robust filesystem lookup to handle Unicode normalization
    differences between the article ID and the actual directory name on disk.
    """
    try:
        # Verify article exists and get canonical ID
        entry = article_index.get_article(article_id)
        canonical_id = entry.id
        
        logger.info(f"Exporting article: {canonical_id} ({entry.title})")
        
        # Find the actual article directory on disk (handles Unicode normalization)
        article_dir = paths.article_dir_readonly(canonical_id)
        
        if not article_dir:
            logger.error(f"Article directory not found for: {canonical_id}")
            # Return error response - directory doesn't exist on disk
            error_response = {
                "article": {
                    "id": entry.id,
                    "title": entry.title,
                    "url": entry.url,
                    "lang": entry.lang,
                    "created_at": entry.created_at,
                },
                "metadata": {
                    "export_date": datetime.utcnow().isoformat(),
                    "error": "Article directory not found on disk"
                }
            }
            return Response(
                content=json.dumps(error_response, indent=2, ensure_ascii=False).encode('utf-8'),
                media_type="application/json; charset=utf-8"
            )
        
        logger.info(f"Found article directory: {article_dir}")
        
        # Initialize response data with article metadata
        export_data: Dict[str, Any] = {
            "article": {
                "id": entry.id,
                "title": entry.title,
                "url": entry.url,
                "lang": entry.lang,
                "created_at": entry.created_at,
            },
            "metadata": {
                "export_date": datetime.utcnow().isoformat(),
            }
        }
        
        warnings_list = []
        
        # Try to read article content
        try:
            article_path = article_dir / "article.md"
            if article_path.exists():
                front_matter, content = read_markdown_file(article_path)
                export_data["article"]["content"] = content
                export_data["article"]["options"] = front_matter.get("options", {})
                export_data["article"]["stats"] = front_matter.get("stats", {})
                logger.info(f"✓ Article content loaded ({len(content)} chars)")
            else:
                logger.warning(f"Article file not found: {article_path}")
                warnings_list.append("Article content file not found")
        except Exception as e:
            logger.error(f"Failed to read article content: {e}", exc_info=True)
            warnings_list.append(f"Failed to read article content: {str(e)}")
        
        # Try to read chunks
        try:
            chunks_path = article_dir / "chunks"
            if chunks_path.exists() and chunks_path.is_dir():
                chunks = []
                for chunk_file in sorted(chunks_path.glob("c*.md")):
                    try:
                        front_matter, content = read_markdown_file(chunk_file)
                        chunks.append({
                            "id": front_matter.get("id", chunk_file.stem),
                            "section": front_matter.get("section", ""),
                            "heading_path": front_matter.get("heading_path", "Lead"),
                            "start_char": front_matter.get("start_char", 0),
                            "end_char": front_matter.get("end_char", 0),
                            "content": content,
                            "char_count": len(content),
                            "token_estimate": count_tokens_estimate(content),
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read chunk {chunk_file.name}: {e}")
                        continue
                
                export_data["chunks"] = chunks
                export_data["metadata"]["total_chunks"] = len(chunks)
                logger.info(f"✓ Loaded {len(chunks)} chunks")
            else:
                logger.warning(f"Chunks directory not found: {chunks_path}")
                export_data["chunks"] = []
                export_data["metadata"]["total_chunks"] = 0
        except Exception as e:
            logger.error(f"Failed to read chunks: {e}", exc_info=True)
            export_data["chunks"] = []
            export_data["metadata"]["total_chunks"] = 0
            warnings_list.append(f"Failed to read chunks: {str(e)}")
        
        # Try to read dataset
        try:
            dataset_path = article_dir / "dataset.md"
            if dataset_path.exists():
                # Parse dataset markdown
                from .dataset import _parse_dataset_markdown
                
                with open(dataset_path, "r", encoding="utf-8") as f:
                    dataset_content = f.read()
                
                items = _parse_dataset_markdown(dataset_content)
                
                # Convert items to dictionaries (support both Pydantic v1 and v2)
                items_list = []
                for item in items:
                    try:
                        # Try Pydantic v2 first
                        if hasattr(item, 'model_dump'):
                            items_list.append(item.model_dump())
                        # Fall back to Pydantic v1
                        elif hasattr(item, 'dict'):
                            items_list.append(item.dict())
                        # If neither, try to convert to dict manually
                        else:
                            items_list.append({
                                "question": getattr(item, 'question', ''),
                                "answer": getattr(item, 'answer', ''),
                                "related_chunk_ids": getattr(item, 'related_chunk_ids', []),
                                "category": getattr(item, 'category', 'FACTUAL')
                            })
                    except Exception as e:
                        logger.warning(f"Failed to serialize question item: {e}")
                        continue
                
                export_data["questions"] = {
                    "total_questions": len(items_list),
                    "items": items_list
                }
                logger.info(f"✓ Loaded {len(items_list)} questions")
            else:
                logger.warning(f"Dataset file not found: {dataset_path}")
                export_data["questions"] = {
                    "total_questions": 0,
                    "items": []
                }
        except Exception as e:
            logger.error(f"Failed to read dataset: {e}", exc_info=True)
            export_data["questions"] = {
                "total_questions": 0,
                "items": []
            }
            warnings_list.append(f"Failed to read dataset: {str(e)}")
        
        # Add warnings if any
        if warnings_list:
            export_data["metadata"]["warnings"] = warnings_list
        
        # Add description
        export_data["metadata"]["description"] = "Complete article dataset including content, chunks, and generated questions"
        export_data["metadata"]["content_format"] = "markdown"
        
        logger.info(f"✓ Export complete for {entry.title}")
        
        # Return as JSON
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Use a safe filename (ASCII only)
        safe_filename = "".join(c if c.isascii() and c.isalnum() else "_" for c in entry.title)[:50]
        if not safe_filename:
            safe_filename = "article"
        
        return Response(
            content=json_content.encode('utf-8'),
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_filename}_export.json"'
            }
        )
        
    except NotFoundError:
        logger.error(f"Article not found in index: {article_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to export article {article_id}: {e}", exc_info=True)
        # Return a graceful error response instead of 500
        try:
            error_response = {
                "article": {
                    "id": article_id,
                },
                "metadata": {
                    "export_date": datetime.utcnow().isoformat(),
                    "error": f"Export failed: {str(e)}"
                }
            }
            return Response(
                content=json.dumps(error_response, indent=2, ensure_ascii=False).encode('utf-8'),
                media_type="application/json; charset=utf-8"
            )
        except:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to export article: {str(e)}"
            ) from e
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to export article {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export article: {str(e)}"
        ) from e


@router.get("/articles/export/all")
async def export_all_articles() -> StreamingResponse:
    """Export all articles as a ZIP file containing JSON exports for each article.
    
    This endpoint generates a complete export of all articles in the database,
    with each article as a separate JSON file inside a ZIP archive.
    """
    try:
        # Get all articles from the index
        all_articles = article_index.list_articles()
        
        if not all_articles:
            raise HTTPException(
                status_code=404,
                detail="No articles found in the database"
            )
        
        logger.info(f"Exporting all {len(all_articles)} articles as ZIP")
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            success_count = 0
            failure_count = 0
            
            for entry in all_articles:
                try:
                    # Export each article using the same logic as single export
                    canonical_id = entry.id
                    article_dir = paths.article_dir_readonly(canonical_id)
                    
                    if not article_dir:
                        logger.warning(f"Directory not found for {canonical_id}, skipping")
                        failure_count += 1
                        continue
                    
                    # Build export data
                    export_data: Dict[str, Any] = {
                        "article": {
                            "id": entry.id,
                            "title": entry.title,
                            "url": entry.url,
                            "lang": entry.lang,
                            "created_at": entry.created_at,
                        },
                        "metadata": {
                            "export_date": datetime.utcnow().isoformat(),
                        }
                    }
                    
                    # Read article content
                    article_path = article_dir / "article.md"
                    if article_path.exists():
                        try:
                            front_matter, content = read_markdown_file(article_path)
                            export_data["article"]["content"] = content
                            export_data["article"]["options"] = front_matter.get("options", {})
                            export_data["article"]["stats"] = front_matter.get("stats", {})
                        except Exception as e:
                            logger.warning(f"Failed to read article content for {canonical_id}: {e}")
                    
                    # Read chunks
                    chunks_path = article_dir / "chunks"
                    if chunks_path.exists() and chunks_path.is_dir():
                        chunks = []
                        for chunk_file in sorted(chunks_path.glob("c*.md")):
                            try:
                                front_matter, content = read_markdown_file(chunk_file)
                                chunks.append({
                                    "id": front_matter.get("id", chunk_file.stem),
                                    "section": front_matter.get("section", ""),
                                    "heading_path": front_matter.get("heading_path", "Lead"),
                                    "start_char": front_matter.get("start_char", 0),
                                    "end_char": front_matter.get("end_char", 0),
                                    "content": content,
                                    "char_count": len(content),
                                    "token_estimate": count_tokens_estimate(content),
                                })
                            except Exception:
                                continue
                        export_data["chunks"] = chunks
                        export_data["metadata"]["total_chunks"] = len(chunks)
                    else:
                        export_data["chunks"] = []
                        export_data["metadata"]["total_chunks"] = 0
                    
                    # Read dataset
                    dataset_path = article_dir / "dataset.md"
                    if dataset_path.exists():
                        try:
                            from .dataset import _parse_dataset_markdown
                            
                            with open(dataset_path, "r", encoding="utf-8") as f:
                                dataset_content = f.read()
                            
                            items = _parse_dataset_markdown(dataset_content)
                            items_list = []
                            for item in items:
                                try:
                                    if hasattr(item, 'model_dump'):
                                        items_list.append(item.model_dump())
                                    elif hasattr(item, 'dict'):
                                        items_list.append(item.dict())
                                    else:
                                        items_list.append({
                                            "question": getattr(item, 'question', ''),
                                            "answer": getattr(item, 'answer', ''),
                                            "related_chunk_ids": getattr(item, 'related_chunk_ids', []),
                                            "category": getattr(item, 'category', 'FACTUAL')
                                        })
                                except Exception:
                                    continue
                            
                            export_data["questions"] = {
                                "total_questions": len(items_list),
                                "items": items_list
                            }
                        except Exception as e:
                            logger.warning(f"Failed to read dataset for {canonical_id}: {e}")
                            export_data["questions"] = {"total_questions": 0, "items": []}
                    else:
                        export_data["questions"] = {"total_questions": 0, "items": []}
                    
                    export_data["metadata"]["description"] = "Complete article dataset"
                    export_data["metadata"]["content_format"] = "markdown"
                    
                    # Create safe filename (ASCII only)
                    safe_filename = "".join(c if c.isascii() and c.isalnum() else "_" for c in entry.title)[:50]
                    if not safe_filename:
                        safe_filename = entry.id
                    
                    # Add to ZIP
                    json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
                    zip_file.writestr(f"{safe_filename}.json", json_content.encode('utf-8'))
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to export article {entry.id}: {e}")
                    failure_count += 1
                    continue
            
            # Add a manifest file
            manifest = {
                "export_date": datetime.utcnow().isoformat(),
                "total_articles": len(all_articles),
                "successful_exports": success_count,
                "failed_exports": failure_count,
                "description": "Complete database export - all articles"
            }
            zip_file.writestr("_manifest.json", json.dumps(manifest, indent=2))
        
        logger.info(f"✓ Exported {success_count}/{len(all_articles)} articles successfully")
        
        # Prepare the ZIP for download
        zip_buffer.seek(0)
        
        # Create filename with current date
        current_date = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"all_articles_export_{current_date}_{success_count}_files.zip"
        
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export all articles: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export all articles: {str(e)}"
        ) from e


@router.delete("/articles/{article_id}")
async def delete_article(article_id: str) -> dict:
    """Delete an article and all related files."""
    try:
        # Verify article exists
        entry = article_index.get_article(article_id)
        article_id = entry.id
        
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