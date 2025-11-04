"""Server-Sent Events for streaming ingestion progress."""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, Optional
from collections import defaultdict

from ..core.logging import get_logger
from ..schemas.ingest import IngestProgress

logger = get_logger("ingest.sse")


class ProgressEvent:
    """Progress event for SSE streaming."""
    
    def __init__(
        self,
        run_id: str,
        stage: str,
        message: str,
        article_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.run_id = run_id
        self.stage = stage
        self.message = message
        self.timestamp = time.time()
        self.article_id = article_id
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "stage": self.stage,
            "message": self.message,
            "timestamp": self.timestamp,
            "article_id": self.article_id,
            "details": self.details,
        }
    
    def to_sse_data(self) -> str:
        """Convert to SSE data format."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class ProgressStreamer:
    """Manages progress streaming for ingestion runs."""
    
    def __init__(self):
        # Store event queues for each run_id
        self._run_queues: Dict[str, asyncio.Queue[ProgressEvent]] = defaultdict(asyncio.Queue)
        self._run_completed: Dict[str, bool] = defaultdict(bool)
    
    async def emit_event(
        self,
        run_id: str,
        stage: str,
        message: str,
        article_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit a progress event for a run."""
        event = ProgressEvent(
            run_id=run_id,
            stage=stage,
            message=message,
            article_id=article_id,
            details=details,
        )
        
        # Add event to queue
        await self._run_queues[run_id].put(event)
        
        # Log the event
        logger.info(f"[{run_id}] {stage}: {message}")
        
        # Mark run as completed for terminal stages
        if stage in ["DONE", "FAILED"]:
            self._run_completed[run_id] = True
    
    async def stream_progress(self, run_id: str) -> AsyncGenerator[str, None]:
        """Stream progress events for a specific run."""
        logger.info(f"Starting SSE stream for run: {run_id}")
        
        try:
            queue = self._run_queues[run_id]
            
            while True:
                try:
                    # Wait for next event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    
                    # Yield just the JSON data (EventSourceResponse handles SSE formatting)
                    yield event.to_sse_data()
                    
                    # Check if run is completed
                    if event.stage in ["DONE", "FAILED"]:
                        logger.info(f"SSE stream completed for run: {run_id}")
                        break
                        
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    heartbeat = json.dumps({'type': 'heartbeat'})
                    yield heartbeat
                    
                    # Check if run was completed elsewhere
                    if self._run_completed[run_id]:
                        break
                        
        except Exception as e:
            logger.error(f"Error in SSE stream for run {run_id}: {e}")
            # Send error event
            error_event = ProgressEvent(
                run_id=run_id,
                stage="FAILED",
                message=f"Stream error: {e}",
            )
            yield error_event.to_sse_data()
        
        finally:
            # Cleanup
            if run_id in self._run_queues:
                # Clear remaining events
                while not self._run_queues[run_id].empty():
                    try:
                        self._run_queues[run_id].get_nowait()
                    except asyncio.QueueEmpty:
                        break
                
                # Remove queue
                del self._run_queues[run_id]
            
            if run_id in self._run_completed:
                del self._run_completed[run_id]
            
            logger.info(f"Cleaned up SSE stream for run: {run_id}")
    
    def is_run_active(self, run_id: str) -> bool:
        """Check if a run is currently active."""
        return run_id in self._run_queues and not self._run_completed[run_id]
    
    def get_active_runs(self) -> list[str]:
        """Get list of currently active run IDs."""
        return [
            run_id for run_id in self._run_queues.keys()
            if not self._run_completed[run_id]
        ]


# Global progress streamer instance
progress_streamer = ProgressStreamer()


class ProgressLogger:
    """Context manager for logging progress events."""
    
    def __init__(self, run_id: str, streamer: ProgressStreamer = None):
        self.run_id = run_id
        self.streamer = streamer or progress_streamer
    
    async def log(
        self,
        stage: str,
        message: str,
        article_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a progress event."""
        await self.streamer.emit_event(
            run_id=self.run_id,
            stage=stage,
            message=message,
            article_id=article_id,
            details=details,
        )
    
    async def fetching(self, message: str, **kwargs) -> None:
        """Log FETCHING stage."""
        await self.log("FETCHING", message, **kwargs)
    
    async def cleaning(self, message: str, **kwargs) -> None:
        """Log CLEANING stage."""
        await self.log("CLEANING", message, **kwargs)
    
    async def splitting(self, message: str, **kwargs) -> None:
        """Log SPLITTING stage.""" 
        await self.log("SPLITTING", message, **kwargs)
    
    async def write_markdown(self, message: str, **kwargs) -> None:
        """Log WRITE_MARKDOWN stage."""
        await self.log("WRITE_MARKDOWN", message, **kwargs)
    
    async def question_gen(self, message: str, **kwargs) -> None:
        """Log QUESTION_GEN stage."""
        await self.log("QUESTION_GEN", message, **kwargs)
    
    async def write_dataset_md(self, message: str, **kwargs) -> None:
        """Log WRITE_DATASET_MD stage."""
        await self.log("WRITE_DATASET_MD", message, **kwargs)
    
    async def done(self, message: str, **kwargs) -> None:
        """Log DONE stage."""
        await self.log("DONE", message, **kwargs)
    
    async def failed(self, message: str, **kwargs) -> None:
        """Log FAILED stage."""
        await self.log("FAILED", message, **kwargs) 