"""Main ingestion pipeline that coordinates all processing steps."""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.errors import IngestionError, LLMError
from ..core.logging import get_logger
from ..llm.questions import generate_questions_for_chunks
from ..schemas.ingest import IngestOptions
from ..storage.atomic import async_atomic_write_text
from ..storage.index import (
    ArticleIndexEntry,
    article_index,
    compute_url_checksum,
    generate_article_id,
)
from ..storage.md import (
    async_write_markdown_file,
    create_markdown_table,
)
from ..storage.paths import paths
from ..utils.ids import format_chunk_ids, generate_run_id
from ..utils.text import count_tokens_estimate, extract_preview, normalize_title
from .clean import clean_wikipedia_html
from .fetch import fetch_wikipedia_article
from .split import split_content, ChunkInfo
from .sse import ProgressLogger

logger = get_logger("ingest.pipeline")


class IngestionPipeline:
    """Main ingestion pipeline for processing Wikipedia articles."""
    
    def __init__(self):
        pass
    
    async def ingest_article(
        self,
        url: str,
        options: IngestOptions,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run the complete ingestion pipeline for a Wikipedia article."""
        run_id = run_id or generate_run_id()
        progress = ProgressLogger(run_id)
        
        try:
            logger.info(f"Starting ingestion for URL: {url}")
            
            # Check for existing article
            url_checksum = compute_url_checksum(url)
            existing_article = article_index.find_by_checksum(url_checksum)
            
            if existing_article and not options.reingest:
                await progress.done(
                    "Article already exists",
                    article_id=existing_article.id,
                    details={"existing": True}
                )
                return {
                    "article_id": existing_article.id,
                    "status": "existing",
                    "run_id": run_id,
                }
            
            # Step 1: Fetch article
            await progress.fetching("Fetching Wikipedia article...")
            article_data = await fetch_wikipedia_article(url)
            
            # Generate article ID
            article_id = generate_article_id(article_data["url"], article_data["title"])
            
            # Save raw HTML for debugging
            raw_html_path = paths.raw_html_file(article_id)
            await async_atomic_write_text(raw_html_path, article_data["content"])
            
            await progress.fetching(
                f"Fetched article: {article_data['title']}",
                article_id=article_id,
                details={
                    "title": article_data["title"],
                    "lang": article_data["lang"],
                    "content_length": len(article_data["content"])
                }
            )
            
            # Step 2: Clean content
            await progress.cleaning("Cleaning and converting HTML to Markdown...")
            cleaned_data = clean_wikipedia_html(
                article_data["content"],
                article_data["title"],
                strip_sections=options.strip_sections if hasattr(options, 'strip_sections') else True
            )
            
            await progress.cleaning(
                f"Cleaned content: {cleaned_data['word_count']} words",
                article_id=article_id,
                details={
                    "word_count": cleaned_data["word_count"],
                    "char_count": cleaned_data["char_count"],
                    "sections": len(cleaned_data["sections"])
                }
            )
            
            # Step 3: Split into chunks
            await progress.splitting(f"Splitting text with {options.split_strategy} strategy...")
            chunks = split_content(
                content=cleaned_data["content"],
                sections=cleaned_data["sections"],
                strategy=options.split_strategy,
                chunk_size=options.chunk_size,
                chunk_overlap=options.chunk_overlap,
            )
            
            await progress.splitting(
                f"Created {len(chunks)} chunks",
                article_id=article_id,
                details={
                    "num_chunks": len(chunks),
                    "strategy": options.split_strategy,
                    "chunk_size": options.chunk_size,
                    "chunk_overlap": options.chunk_overlap
                }
            )
            
            # Step 4: Write Markdown files
            await progress.write_markdown("Writing article and chunk files...")
            await self._write_article_files(
                article_id=article_id,
                article_data=article_data,
                cleaned_data=cleaned_data,
                chunks=chunks,
                options=options,
                url_checksum=url_checksum
            )
            
            await progress.write_markdown(
                f"Wrote article.md and {len(chunks)} chunk files",
                article_id=article_id
            )
            
            # Step 5: Generate questions
            await progress.question_gen("Generating questions with LLM, this may take a while...")
            try:
                questions = await generate_questions_for_chunks(
                    chunks=chunks,
                    total_questions=options.total_questions,
                    model=options.llm_model,
                )
                
                await progress.question_gen(
                    f"Generated {len(questions)} questions",
                    article_id=article_id,
                    details={
                        "num_questions": len(questions),
                        "model": options.llm_model,
                        "total_questions_requested": options.total_questions
                    }
                )
            except LLMError as e:
                # Log detailed LLM error and continue with empty questions
                logger.error(f"LLM Error during question generation: {e.get_detailed_message()}")
                await progress.question_gen(
                    f"Failed to generate questions due to LLM error, continuing with empty dataset",
                    article_id=article_id,
                    details={"error": str(e), "provider": e.provider}
                )
                questions = []
            except Exception as e:
                logger.error(f"Unexpected error during question generation: {e}")
                await progress.question_gen(
                    f"Failed to generate questions, continuing with empty dataset",
                    article_id=article_id,
                    details={"error": str(e)}
                )
                questions = []
            
            # Step 6: Write dataset file
            await progress.write_dataset_md("Writing dataset markdown file...")
            await self._write_dataset_file(article_id, article_data["title"], questions)
            
            await progress.write_dataset_md(
                f"Wrote dataset.md with {len(questions)} questions",
                article_id=article_id
            )
            
            # Step 7: Update index
            index_entry = article_index.add_article(
                article_id=article_id,
                url=url,
                title=article_data["title"],
                lang=article_data["lang"],
                checksum=url_checksum,
            )
            
            # Step 8: Write logs
            await self._write_logs(run_id, article_id, progress)
            
            await progress.done(
                f"Successfully ingested article: {article_data['title']}",
                article_id=article_id,
                details={
                    "total_chunks": len(chunks),
                    "total_questions": len(questions),
                    "processing_time": time.time()
                }
            )
            
            return {
                "article_id": article_id,
                "status": "completed",
                "run_id": run_id,
                "stats": {
                    "chunks": len(chunks),
                    "questions": len(questions),
                    "word_count": cleaned_data["word_count"],
                }
            }
            
        except LLMError as e:
            logger.error(f"LLM Error during ingestion for {url}: {e.get_detailed_message()}")
            await progress.failed(f"LLM Error: {str(e)}")
            raise IngestionError(f"Pipeline failed due to LLM error: {e}") from e
        except Exception as e:
            logger.error(f"Ingestion failed for {url}: {e}")
            await progress.failed(f"Ingestion failed: {str(e)}")
            raise IngestionError(f"Pipeline failed: {e}") from e
    
    async def _write_article_files(
        self,
        article_id: str,
        article_data: Dict[str, str],
        cleaned_data: Dict[str, Any],
        chunks: List[ChunkInfo],
        options: IngestOptions,
        url_checksum: str,
    ) -> None:
        """Write article.md and chunk files."""
        
        # Prepare article front matter
        article_front_matter = {
            "id": article_id,
            "url": article_data["url"],
            "title": article_data["title"],
            "lang": article_data["lang"],
            "created_at": datetime.utcnow().isoformat(),
            "checksum": url_checksum,
            "options": {
                "chunk_size": options.chunk_size,
                "chunk_overlap": options.chunk_overlap,
                "split_strategy": options.split_strategy,
                "total_questions": options.total_questions,
                "llm_model": options.llm_model,
            },
            "stats": {
                "word_count": cleaned_data["word_count"],
                "char_count": cleaned_data["char_count"],
                "num_chunks": len(chunks),
                "num_sections": len(cleaned_data["sections"]),
            }
        }
        
        # Write article.md
        article_path = paths.article_file(article_id)
        await async_write_markdown_file(
            article_path,
            article_front_matter,
            cleaned_data["content"]
        )
        
        # Write individual chunk files
        for chunk in chunks:
            chunk_front_matter = {
                "id": chunk.id,
                "article_id": article_id,
                "section": chunk.section,
                "heading_path": chunk.heading_path,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "char_count": chunk.char_count,
                "token_estimate": chunk.token_estimate,
            }
            
            chunk_path = paths.chunk_file(article_id, chunk.id)
            await async_write_markdown_file(
                chunk_path,
                chunk_front_matter,
                chunk.content
            )
        
        # Write chunks index
        await self._write_chunks_index(article_id, chunks)
    
    async def _write_chunks_index(self, article_id: str, chunks: List[ChunkInfo]) -> None:
        """Write chunks_index.md file."""
        headers = ["ID", "Section", "Heading Path", "Char Range", "Preview"]
        rows = []
        
        for chunk in chunks:
            char_range = f"{chunk.start_char}-{chunk.end_char}"
            preview = extract_preview(chunk.content, 100)
            
            rows.append([
                chunk.id,
                chunk.section,
                chunk.heading_path,
                char_range,
                preview
            ])
        
        table_content = create_markdown_table(
            headers=headers,
            rows=rows,
            title="Chunks Index"
        )
        
        chunks_index_path = paths.chunks_index_file(article_id)
        await async_atomic_write_text(chunks_index_path, table_content)
    
    async def _write_dataset_file(
        self,
        article_id: str,
        title: str,
        questions: List[Dict[str, Any]]
    ) -> None:
        """Write dataset.md file."""
        
        # Create table content
        headers = ["#", "Question", "Answer", "Category", "Related_Chunk_IDs"]
        rows = []
        
        for i, question in enumerate(questions, 1):
            chunk_ids_str = format_chunk_ids(question["related_chunk_ids"])
            rows.append([
                str(i),
                question["question"],
                question["answer"],
                question["category"],
                chunk_ids_str
            ])
        
        # Add metadata header
        metadata = f"""# Dataset: {title}

Generated on: {datetime.utcnow().isoformat()}
Total questions: {len(questions)}

"""
        
        table_content = create_markdown_table(headers=headers, rows=rows)
        full_content = metadata + table_content
        
        dataset_path = paths.dataset_file(article_id)
        await async_atomic_write_text(dataset_path, full_content)
    
    async def _write_logs(
        self,
        run_id: str,
        article_id: str,
        progress: ProgressLogger
    ) -> None:
        """Write ingestion logs in NDJSON format."""
        logs_path = paths.logs_file(article_id)
        
        # Create a simple log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": run_id,
            "article_id": article_id,
            "status": "completed",
            "message": "Ingestion completed successfully"
        }
        
        log_line = json.dumps(log_entry) + "\n"
        
        # Append to logs file
        with open(logs_path, "a", encoding="utf-8") as f:
            f.write(log_line)


# Global pipeline instance
ingestion_pipeline = IngestionPipeline() 