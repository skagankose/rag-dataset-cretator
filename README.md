# RAG Dataset Creator

A production-ready, dockerized web application for creating RAG (Retrieval-Augmented Generation) datasets from Wikipedia articles. The app fetches articles, processes them into chunks, generates questions using OpenAI, and outputs everything as structured Markdown files.

## Features

- **Wikipedia Integration**: Fetch articles via MediaWiki API with language detection
- **Smart Text Processing**: Clean HTML content and split into chunks using recursive or sentence-based strategies
- **AI-Powered Question Generation**: Generate contextual questions using OpenAI GPT models
- **Markdown Output**: All data saved as structured Markdown files with YAML front matter
- **Real-time Progress**: Live updates via Server-Sent Events during ingestion
- **Modern UI**: React + TypeScript frontend with TailwindCSS and dark mode
- **Production Ready**: Dockerized with proper error handling, logging, and health checks

## Architecture

### Backend (FastAPI + Python)
- **Ingestion Pipeline**: Fetch → Clean → Split → Generate Questions → Write Files
- **Storage**: File-based with atomic operations (no databases)
- **API**: RESTful endpoints with OpenAPI documentation
- **Streaming**: Server-Sent Events for real-time progress updates

### Frontend (React + TypeScript)
- **Modern Stack**: Vite, TailwindCSS, React Router, React Query
- **Real-time UI**: SSE integration for live progress tracking
- **File Management**: Browse chunks, view datasets, download files
- **Responsive Design**: Works on desktop and mobile

### Storage Structure
```
DATA_DIR/
  index.json                      # List of articles
  articles/
    {article_id}/
      article.md                  # Full article with metadata
      chunks/
        c0001.md                  # Individual chunks
        c0002.md
        ...
      chunks_index.md             # Chunk summary table
      dataset.md                  # Questions dataset
      logs.ndjson                 # Processing logs
      raw.html                    # Original HTML
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag_dataset_creator
   ```

2. **Configure environment**
   ```bash
   cp env.template .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start the application**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

All environment variables are documented in `env.template`. Copy it to `.env` and configure:

```bash
cp env.template .env
```

**Required Variables:**
- `OPENAI_API_KEY` - Your OpenAI API key (get from https://platform.openai.com/api-keys)

**OpenAI Configuration:**
- `OPENAI_CHAT_MODEL` - Model for question generation (default: gpt-4o-mini)
- `OPENAI_TIMEOUT` - Request timeout in seconds (default: 60)
- `OPENAI_MAX_RETRIES` - Max retries for failed requests (default: 5)

**Ingestion Defaults:**
- `DEFAULT_CHUNK_SIZE` - Text chunk size in characters (default: 1200)
- `DEFAULT_CHUNK_OVERLAP` - Overlap between chunks (default: 200)
- `DEFAULT_TOTAL_QUESTIONS` - Total questions to generate (default: 10)
- `STRIP_SECTIONS` - Remove Wikipedia sections like References (default: true)

**Optional Configuration:**
- `APP_ENV` - Environment (dev/prod, default: dev)
- `BACKEND_PORT` - Backend port (default: 8000)
- `DATA_DIR` - Data storage directory (default: /app/data)
- `VITE_API_URL` - Frontend API URL (default: http://localhost:8000)

### Ingestion Options

- **chunk_size**: Target size for text chunks (100-5000 characters)
- **chunk_overlap**: Overlap between consecutive chunks (0-1000 characters)
- **split_strategy**: "recursive" (default) or "sentence"
- **total_questions**: Total questions to generate across all chunks (1-50)
- **llm_model**: OpenAI model to use (default: gpt-4o-mini)
- **reingest**: Force re-processing of existing articles

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /ingest` - Start article ingestion
- `GET /ingest/stream/{run_id}` - Stream progress via SSE
- `GET /articles` - List all articles
- `GET /articles/{article_id}` - Get article metadata
- `GET /articles/{article_id}/chunks` - List article chunks
- `GET /dataset/{article_id}` - Get questions dataset
- `GET /files/{article_id}/{filename}` - Download files

### Example Usage

**Start Ingestion:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "wikipedia_url": "https://en.wikipedia.org/wiki/Machine_learning",
    "options": {
      "chunk_size": 1000,
      "total_questions": 15,
      "llm_model": "gpt-4o-mini"
    }
  }'
```

**Stream Progress:**
```bash
curl -N http://localhost:8000/ingest/stream/{run_id}
```

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../env.template ../.env  # Add your OpenAI API key
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
# Environment variables are automatically loaded from root .env
npm run dev
```

### Code Quality
```bash
# Backend
make fmt    # Format code
make lint   # Run linters
make test   # Run tests

# Frontend
npm run format  # Format code
npm run lint    # Run ESLint
```

## Output Format

### Article Markdown (`article.md`)
```yaml
---
id: article_12345
url: https://en.wikipedia.org/wiki/Machine_learning
title: Machine learning
lang: en
created_at: "2024-01-01T12:00:00Z"
options:
  chunk_size: 1200
  split_strategy: recursive
stats:
  word_count: 5000
  num_chunks: 10
---

# Machine learning

Machine learning is a subset of artificial intelligence...
```

### Chunk Files (`chunks/c0001.md`)
```yaml
---
id: c0001
article_id: article_12345
section: Introduction
heading_path: Lead > Introduction
start_char: 0
end_char: 1200
---

Machine learning is a subset of artificial intelligence...
```

### Dataset (`dataset.md`)
```markdown
# Dataset: Machine learning

Generated on: 2024-01-01T12:00:00Z
Total questions: 20

| # | Question | Related_Chunk_IDs |
|---|----------|------------------|
| 1 | What is machine learning? | c0001 |
| 2 | How does supervised learning work? | c0003 |
```

## Production Deployment

### Docker Compose (Recommended)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - APP_ENV=prod
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Environment-Specific Configurations
- **Development**: Live reload, debug logging, CORS enabled
- **Production**: Optimized builds, error monitoring, security headers

## Troubleshooting

### Common Issues

**OpenAI API Errors:**
- Verify your API key is correct
- Check rate limits and billing
- Ensure model availability

**Memory Issues:**
- Reduce chunk_size for large articles
- Lower total_questions
- Process articles sequentially

**File Permissions:**
- Ensure DATA_DIR is writable
- Check Docker volume mounts

### Monitoring
- Health check: `GET /health`
- Logs: Check `logs.ndjson` files
- Metrics: Monitor API response times

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks (`make lint test`)
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- API Documentation: http://localhost:8000/docs
- Issues: GitHub Issues
- Discussions: GitHub Discussions 