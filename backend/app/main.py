"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import articles, config, dataset, files, health, ingest
from .core.config import settings
from .core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    
    # Validate configuration
    try:
        # This will raise an exception if OpenAI key is invalid
        _ = settings.openai_api_key
    except ValueError as e:
        raise RuntimeError(f"Configuration error: {e}") from e
    
    yield
    
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="RAG Dataset Creator",
    description="Create RAG datasets from Wikipedia articles",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(config.router, tags=["Configuration"])
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(articles.router, tags=["Articles"])
app.include_router(dataset.router, tags=["Dataset"])
app.include_router(files.router, tags=["Files"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "RAG Dataset Creator",
        "version": "1.0.0",
        "description": "Create RAG datasets from Wikipedia articles",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "ingestion": "/ingest",
            "articles": "/articles",
            "dataset": "/dataset/{article_id}",
            "files": "/files/{article_id}/{filename}",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.is_development,
    ) 