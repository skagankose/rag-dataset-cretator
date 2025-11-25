"""Ingestion API endpoints."""

import asyncio
from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from ..core.errors import IngestionError
from ..core.logging import get_logger
from ..ingest.pipeline import ingestion_pipeline
from ..ingest.sse import progress_streamer
from ..schemas.ingest import IngestRequest, IngestResponse, IngestOptions
from ..utils.ids import generate_run_id

logger = get_logger("api.ingest")

router = APIRouter()


async def run_ingestion_background(url: str, options, run_id: str) -> None:
    """Run ingestion in background task."""
    try:
        await ingestion_pipeline.ingest_article(url, options, run_id)
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}")
        # The progress logger in the pipeline will handle the failure event


async def run_file_ingestion_background(content: str, filename: str, options: IngestOptions, run_id: str) -> None:
    """Run file ingestion in background task."""
    try:
        await ingestion_pipeline.ingest_file(content, filename, options, run_id)
    except Exception as e:
        logger.error(f"Background file ingestion failed: {e}")
        # The progress logger in the pipeline will handle the failure event


@router.post("/ingest", response_model=IngestResponse)
async def start_ingestion(
    request: IngestRequest,
    background_tasks: BackgroundTasks
) -> IngestResponse:
    """Start article ingestion process."""
    try:
        # Generate run ID
        run_id = generate_run_id()
        
        # Use default options if not provided
        options = request.options or IngestRequest.model_validate({"wikipedia_url": request.wikipedia_url}).options
        
        logger.info(f"Starting ingestion for URL: {request.wikipedia_url}")
        
        # Start background task
        background_tasks.add_task(
            run_ingestion_background,
            str(request.wikipedia_url),
            options,
            run_id
        )
        
        return IngestResponse(
            run_id=run_id,
            message="Ingestion started",
            status="started"
        )
        
    except Exception as e:
        logger.error(f"Failed to start ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start ingestion: {str(e)}"
        ) from e


@router.post("/ingest/files", response_model=List[IngestResponse])
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(1200),
    chunk_overlap: int = Form(200),
    split_strategy: str = Form("header_aware"),
    total_questions: int = Form(10),
    reingest: bool = Form(False),
) -> List[IngestResponse]:
    """Upload and process Markdown files."""
    responses = []
    
    try:
        # Create options object
        options = IngestOptions(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            split_strategy=split_strategy,
            total_questions=total_questions,
            reingest=reingest
        )
        
        for file in files:
            try:
                content = await file.read()
                content_str = content.decode("utf-8")
                filename = file.filename
                
                run_id = generate_run_id()
                
                background_tasks.add_task(
                    run_file_ingestion_background,
                    content_str,
                    filename,
                    options,
                    run_id
                )
                
                responses.append(IngestResponse(
                    run_id=run_id,
                    message=f"Ingestion started for {filename}",
                    status="started"
                ))
                
            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {e}")
                responses.append(IngestResponse(
                    run_id=generate_run_id(),
                    message=f"Failed to process file {file.filename}: {str(e)}",
                    status="failed"
                ))
                
        return responses
        
    except Exception as e:
        logger.error(f"Failed to start file ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start file ingestion: {str(e)}"
        ) from e



@router.get("/ingest/stream/{run_id}")
async def stream_ingestion_progress(run_id: str) -> StreamingResponse:
    """Stream ingestion progress via Server-Sent Events."""
    
    async def generate_events() -> AsyncGenerator[str, None]:
        """Generate SSE events for ingestion progress."""
        try:
            async for event in progress_streamer.stream_progress(run_id):
                yield event
        except Exception as e:
            logger.error(f"Error streaming progress for {run_id}: {e}")
            # Send error event
            import json
            error_data = json.dumps({"error": f"Stream error: {str(e)}"})
            yield error_data
    
    return EventSourceResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    ) 