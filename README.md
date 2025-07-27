# RAG Dataset Creator

A web application that automatically creates RAG (Retrieval-Augmented Generation) datasets from Wikipedia articles. It fetches articles, processes them into chunks, generates questions using AI, and saves everything as structured files ready for machine learning workflows.

## What This Application Does

This tool automates the creation of question-answer datasets for training RAG systems:

1. **Fetches Wikipedia Articles** - Takes any Wikipedia URL and downloads the article content
2. **Processes Text** - Cleans the content and splits it into manageable chunks
3. **Generates Questions** - Uses OpenAI's GPT models to create relevant questions for each text chunk
4. **Saves Structured Output** - Exports everything as organized Markdown files with metadata

The result is a complete dataset with questions, source text chunks, and all the metadata needed for machine learning projects.

## Key Features

- **Simple Web Interface** - Easy-to-use React frontend for managing the process
- **Real-time Progress** - Watch articles being processed with live status updates
- **Flexible Configuration** - Customize chunk sizes, question counts, and AI models
- **Multiple Output Formats** - Structured Markdown files with YAML metadata
- **Production Ready** - Dockerized setup with proper error handling and logging
- **No Database Required** - File-based storage that's easy to backup and manage

## What You Need to Configure

### Required
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

### Optional Settings
- **Chunk Size** - How large each text segment should be (default: 1200 characters)
- **Question Count** - Total questions to generate per article (default: 10)
- **AI Model** - Which OpenAI model to use (default: gpt-4o-mini)
- **Text Processing** - How to split text (recursive or sentence-based)

## How to Run It

### Quick Start with Docker (Recommended)

1. **Get the Code**
   ```bash
   git clone <repository-url>
   cd rag_dataset_creator
   ```

2. **Set Your OpenAI API Key**
   ```bash
   cp env.template .env
   # Edit .env and add: OPENAI_API_KEY=your_api_key_here
   ```

3. **Start the Application**
   ```bash
   docker compose up --build
   ```

4. **Use the App**
   - Open http://localhost:5180 in your browser
   - Paste a Wikipedia URL and configure options
   - Watch the processing happen in real-time
   - Download your generated dataset files

### Development Setup

If you want to run it without Docker:

**Backend (Python/FastAPI):**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend (React/TypeScript):**
```bash
cd frontend
npm install
npm run dev
```

## Basic Usage

1. **Start Processing** - Enter a Wikipedia URL (like `https://en.wikipedia.org/wiki/Machine_learning`)
2. **Configure Options** - Set chunk size, question count, and other preferences
3. **Watch Progress** - Real-time updates show fetching, cleaning, chunking, and question generation
4. **Review Results** - Browse generated chunks and questions in the web interface
5. **Download Files** - Get your complete dataset as organized Markdown files

## What You Get

The application creates a structured dataset for each article:

```
DATA_DIR/
  articles/
    {article_id}/
      article.md          # Full article with metadata
      chunks/
        c0001.md         # Individual text chunks
        c0002.md
        ...
      dataset.md         # Generated questions dataset
      chunks_index.md    # Summary of all chunks
```

Each file includes YAML metadata with IDs, timestamps, and processing options, making it easy to track and use in ML pipelines.

## Configuration Options

Create a `.env` file (copy from `env.template`) with these settings:

**Required:**
```env
OPENAI_API_KEY=your_api_key_here
```

**Optional (with defaults):**
```env
OPENAI_CHAT_MODEL=gpt-4o-mini
DEFAULT_CHUNK_SIZE=1200
DEFAULT_CHUNK_OVERLAP=200
DEFAULT_TOTAL_QUESTIONS=10
BACKEND_PORT=8051
```

## API Access

The backend provides REST API endpoints if you want to integrate programmatically:

- `POST /ingest` - Start processing an article
- `GET /articles` - List all processed articles  
- `GET /dataset/{article_id}` - Get generated questions
- `GET /files/{article_id}/{filename}` - Download files

API documentation available at: http://localhost:8051/docs

## Development

**Code Formatting:**
```bash
# Backend
make fmt lint test

# Frontend  
npm run format lint
```

**Project Structure:**
- `backend/` - FastAPI Python application
- `frontend/` - React TypeScript application
- `docker-compose.yml` - Full application setup

## Troubleshooting

**Common Issues:**
- **OpenAI API errors**: Check your API key and billing status
- **Memory issues**: Try smaller chunk sizes for very large articles
- **File permissions**: Ensure the data directory is writable

**Getting Help:**
- Check the API documentation at `/docs`
- Review log files in the data directory
- Verify your `.env` configuration

## TODO

**Planned Improvements:**
- **Add Gemini CLI support** - Integrate Google's Gemini models as an alternative to OpenAI
- **Improve question generation prompting**:
  1. Each question should be related to more chunks (cross-chunk relationships)
  2. Generated items don't need to be questions (e.g. they can be commands, tasks, or other prompts)

## Author

Created by [Your Name] - feel free to contribute or report issues.

## License

This project is open source and available under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software for any purpose, including commercial use. See the LICENSE file for full details. 