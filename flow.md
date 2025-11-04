# RAG Dataset Creator: Complete Flow Documentation

## Step-by-Step Flow: From URL Submission to Completion

### **Step 1: Frontend Form Submission**
**File:** `frontend/src/pages/HomePage.tsx` (lines 741-752)

1. User enters Wikipedia URL in the form
2. User clicks "Process Article" button  
3. `handleSubmit` function is triggered
4. Frontend calls `ingestMutation.mutate()` with the URL and options

### **Step 2: Frontend API Call**
**File:** `frontend/src/lib/api.ts` (lines 38-48)

1. `startIngestion()` function makes POST request to `http://localhost:8051/ingest`
2. Sends JSON payload with `wikipedia_url` and processing `options`

### **Step 3: Backend API Endpoint**  
**File:** `backend/app/api/ingest.py` (lines 31-58)

1. `/ingest` POST endpoint receives the request
2. Generates unique `run_id` using `generate_run_id()`
3. Adds background task to process the article
4. Immediately returns response with `run_id` and status "started"

### **Step 4: Backend Background Processing Starts**
**File:** `backend/app/api/ingest.py` (lines 22-28)

1. `run_ingestion_background()` function executes in background
2. Calls `ingestion_pipeline.ingest_article(url, options, run_id)`

### **Step 5: Frontend Sets Up Real-Time Monitoring**
**File:** `frontend/src/hooks/useIngestStream.ts` (lines 21-66)

1. Frontend receives the `run_id` from API response
2. Creates EventSource connection to `http://localhost:8051/ingest/stream/{run_id}`
3. Starts listening for Server-Sent Events (SSE)

### **Step 6: Backend SSE Stream Setup**
**File:** `backend/app/api/ingest.py` (lines 68-93)

1. `/ingest/stream/{run_id}` GET endpoint handles SSE connection
2. Uses `progress_streamer.stream_progress(run_id)` to yield events
3. Sets up EventSource response with proper headers

### **Step 7: Main Ingestion Pipeline Begins**
**File:** `backend/app/ingest/pipeline.py` (lines 40-127)

#### 7a. Check for Existing Article
- Computes URL checksum  
- Checks if article already exists in index
- If exists and not re-ingesting, returns early

#### 7b. **Stage: FETCHING** 
**File:** `backend/app/ingest/fetch.py` (lines 63-151)
- Uses `WikipediaFetcher` to call MediaWiki API
- Extracts language and title from URL  
- Fetches HTML content via API request to `{lang}.wikipedia.org/w/api.php`
- Saves raw HTML to `data/articles/{article_id}/raw.html`
- Progress: "Fetched article: {title}"

#### 7c. **Stage: CLEANING**
**File:** `backend/app/ingest/clean.py` (lines 33-80+)
- Uses `WikipediaHTMLCleaner` to process HTML
- Removes unwanted elements (navigation, infoboxes, etc.)
- Converts HTML to clean Markdown
- Extracts sections and heading hierarchy  
- Progress: "Cleaned content: {word_count} words"

#### 7d. **Stage: SPLITTING**  
**File:** `backend/app/ingest/split.py`
- Splits content into chunks using selected strategy (recursive/sentence/header_aware)
- Applies chunk size and overlap settings
- Creates `ChunkInfo` objects with metadata
- Progress: "Created {num_chunks} chunks"

#### 7e. **Stage: WRITE_MARKDOWN**
**File:** `backend/app/ingest/pipeline.py` (lines 232-300+)
- Writes `article.md` with front matter and content
- Writes individual chunk files as `chunk_{id}.md`
- Saves to `data/articles/{article_id}/` directory
- Progress: "Wrote article.md and {num_chunks} chunk files"

#### 7f. **Stage: QUESTION_GEN**
**File:** `backend/app/llm/questions.py`
- Uses configured LLM (OpenAI/Gemini) to generate questions
- Processes chunks in batches to create Q&A pairs
- Handles LLM errors gracefully, continues with empty dataset if needed
- Progress: "Generated {num_questions} questions"

#### 7g. **Stage: WRITE_DATASET_MD**
- Creates `dataset.md` with all generated Q&A pairs
- Saves to `data/articles/{article_id}/dataset.md`
- Progress: "Wrote dataset.md with {num_questions} questions"

### **Step 8: Finalization**
**File:** `backend/app/ingest/pipeline.py` (lines 190-210)

1. **Index Update**: Adds article entry to `article_index` 
2. **Logs**: Writes processing logs
3. **Final Progress**: Sends "DONE" event with final stats

### **Step 9: Frontend Completion**
**File:** `frontend/src/pages/HomePage.tsx` (lines 754-771)

1. Frontend receives "DONE" event via SSE
2. Closes EventSource connection
3. Invalidates React Query cache to refresh article list
4. Resets form and shows success toast
5. Article appears in the articles list

### **Step 10: Data Storage Structure**
**Files created in:** `backend/data/articles/{article_id}/`

```
data/articles/{article_id}/
├── raw.html           # Original Wikipedia HTML
├── article.md         # Cleaned markdown with metadata  
├── dataset.md         # Generated Q&A pairs
├── chunk_0001.md      # Individual content chunks
├── chunk_0002.md
└── ...
```

### **Real-Time Progress Updates**
Throughout steps 7a-7g, the backend continuously sends progress events via **Server-Sent Events**:

**File:** `backend/app/ingest/sse.py`
- `ProgressLogger` sends events for each stage
- `ProgressStreamer` manages event queues per run_id  
- Frontend displays real-time updates to user
- Events include stage name, message, and detailed metadata

This entire flow typically takes 30-60 seconds depending on article size and LLM response time, with the user seeing live progress updates throughout the process.

## Key Technologies Used

- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Backend**: FastAPI, Python, AsyncIO
- **Real-time**: Server-Sent Events (SSE)
- **Storage**: File system with markdown files
- **LLM Integration**: OpenAI GPT / Google Gemini APIs
- **Wikipedia API**: MediaWiki REST API

## Process Timeline

1. **Immediate** (< 1 second): Form submission → API call → Background task started
2. **FETCHING** (2-5 seconds): Wikipedia API call and HTML download
3. **CLEANING** (1-3 seconds): HTML parsing and markdown conversion  
4. **SPLITTING** (1-2 seconds): Text chunking with selected strategy
5. **WRITE_MARKDOWN** (1-2 seconds): File system operations
6. **QUESTION_GEN** (20-40 seconds): LLM API calls for Q&A generation
7. **WRITE_DATASET_MD** (1 second): Final file creation
8. **FINALIZATION** (< 1 second): Index update and cleanup 