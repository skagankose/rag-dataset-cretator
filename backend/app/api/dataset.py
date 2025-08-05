"""Dataset API endpoints."""

import re
from typing import List

from fastapi import APIRouter, HTTPException, Response

from ..core.errors import NotFoundError
from ..core.logging import get_logger
from ..schemas.articles import DatasetItem, DatasetResponse
from ..storage.index import article_index
from ..storage.paths import paths
from ..utils.ids import parse_chunk_ids

logger = get_logger("api.dataset")

router = APIRouter()


@router.get("/dataset/{article_id}", response_model=DatasetResponse)
async def get_dataset(article_id: str) -> DatasetResponse:
    """Get dataset for an article."""
    try:
        # Verify article exists
        entry = article_index.get_article(article_id)
        
        # Read dataset file
        dataset_path = paths.dataset_file(article_id)
        
        if not dataset_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found for article: {article_id}"
            )
        
        # Parse dataset markdown file
        with open(dataset_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        items = _parse_dataset_markdown(content)
        
        return DatasetResponse(
            article_id=article_id,
            title=entry.title,
            created_at=entry.created_at,
            items=items,
            total_questions=len(items),
        )
        
    except NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Article not found: {article_id}"
        )
    except Exception as e:
        logger.error(f"Failed to get dataset for {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get dataset"
        ) from e


@router.get("/dataset/{article_id}/download")
async def download_dataset(article_id: str) -> Response:
    """Download dataset as JSON file."""
    try:
        # Get the dataset data
        dataset_response = await get_dataset(article_id)
        
        # Convert to JSON
        import json
        json_content = json.dumps(dataset_response.model_dump(), indent=2, ensure_ascii=False)
        
        # Create filename using article ID
        filename = f"{article_id}_dataset.json"
        
        # Return as downloadable file
        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from get_dataset
        raise
    except Exception as e:
        logger.error(f"Failed to download dataset for {article_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download dataset"
        ) from e


def _parse_dataset_markdown(content: str) -> List[DatasetItem]:
    """Parse dataset markdown content into DatasetItem objects."""
    items = []
    
    # Find the table section
    lines = content.split('\n')
    in_table = False
    header_passed = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check if this is a table row
        if line.startswith('|') and line.endswith('|'):
            if not in_table:
                in_table = True
                continue  # Skip header row
            
            if not header_passed:
                # Skip separator row (|---|---|---|)
                if all(c in '-|: ' for c in line):
                    header_passed = True
                    continue
            
            # Parse data row
            try:
                # Split by | and clean up
                parts = [part.strip() for part in line.split('|')[1:-1]]  # Remove empty first/last
                
                if len(parts) >= 5:
                    # New format: parts[0] is question number, parts[1] is question, parts[2] is answer, parts[3] is category, parts[4] is chunk IDs
                    question = parts[1]
                    answer = parts[2]
                    category = parts[3]
                    chunk_ids_str = parts[4]
                    
                    # Parse chunk IDs
                    chunk_ids = parse_chunk_ids(chunk_ids_str)
                    
                    if question and answer and chunk_ids:
                        items.append(DatasetItem(
                            question=question,
                            answer=answer,
                            related_chunk_ids=chunk_ids,
                            category=category
                        ))
                elif len(parts) >= 4:
                    # Backward compatibility: old format with answers but no category
                    question = parts[1]
                    answer = parts[2]
                    chunk_ids_str = parts[3]
                    
                    # Parse chunk IDs
                    chunk_ids = parse_chunk_ids(chunk_ids_str)
                    
                    if question and answer and chunk_ids:
                        items.append(DatasetItem(
                            question=question,
                            answer=answer,
                            related_chunk_ids=chunk_ids,
                            category="FACTUAL"  # Default category for backward compatibility
                        ))
                elif len(parts) >= 3:
                    # Backward compatibility: old format without answers or category
                    question = parts[1]
                    chunk_ids_str = parts[2]
                    
                    # Parse chunk IDs
                    chunk_ids = parse_chunk_ids(chunk_ids_str)
                    
                    if question and chunk_ids:
                        items.append(DatasetItem(
                            question=question,
                            answer="",  # Empty answer for backward compatibility
                            related_chunk_ids=chunk_ids,
                            category="FACTUAL"  # Default category for backward compatibility
                        ))
                        
            except Exception as e:
                logger.warning(f"Failed to parse dataset row: {line} - {e}")
                continue
        else:
            # Reset table parsing if we hit a non-table line
            if in_table:
                break
    
    return items 