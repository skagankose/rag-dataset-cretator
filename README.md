# RAG Dataset Creator

A web application that automatically creates RAG (Retrieval-Augmented Generation) datasets from Wikipedia articles. It fetches articles, processes them into chunks, generates questions using AI, and saves everything as structured files ready for machine learning workflows.

## What This Application Does

This tool automates the creation of question-answer datasets for training RAG systems:

1. **Fetches Wikipedia Articles** - Takes any Wikipedia URL and downloads the article content
2. **Processes Text** - Cleans the content and splits it into manageable chunks
3. **Generates Questions** - Uses AI models (OpenAI GPT or Google Gemini) to create relevant questions for each text chunk
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
- **LLM Provider** - Choose between OpenAI or Google Gemini
- **API Key** - Get one from:
  - [OpenAI Platform](https://platform.openai.com/api-keys) for OpenAI
  - [Google AI Studio](https://aistudio.google.com/app/apikey) for Gemini

### Optional Settings
- **Chunk Size** - How large each text segment should be (default: 1200 characters)
- **Question Count** - Total questions to generate per article (default: 10)
- **AI Model** - Which specific model to use:
  - OpenAI: gpt-4o-mini, gpt-4o, gpt-3.5-turbo, etc.
  - Gemini: gemini-1.5-flash, gemini-1.5-pro, gemini-pro, etc.
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

**Project Structure:**
- `backend/` - FastAPI Python application
- `frontend/` - React TypeScript application
- `docker-compose.yml` - Full application setup

## Configuration Options

Create a `.env` file (copy from `env.template`) with these settings:

**LLM Provider Selection:**
```env
# Choose your LLM provider: "openai" or "gemini"
LLM_PROVIDER=openai
```

**Required (choose one based on your provider):**

For OpenAI:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

For Google Gemini:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Important for Gemini users:**
1. **Enable the API**: Visit [Google Cloud Console](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com) and enable the "Generative Language API"
2. **Get API Key**: Create a new API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
3. **Wait**: After enabling the API, wait 2-3 minutes before testing

**Optional (with defaults):**
```env
# OpenAI Configuration
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=60
OPENAI_MAX_RETRIES=5

# Gemini Configuration
GEMINI_CHAT_MODEL=gemini-1.5-flash
GEMINI_TIMEOUT=60
GEMINI_MAX_RETRIES=5

# Processing Configuration
DEFAULT_CHUNK_SIZE=1200
DEFAULT_CHUNK_OVERLAP=200
DEFAULT_TOTAL_QUESTIONS=10
BACKEND_PORT=8051
```

## Customizing LLM Prompts

The prompts used to generate questions from text chunks are now configurable via a YAML file instead of being hard-coded. This makes it easy to experiment with different prompting strategies.

**Prompts Configuration File:** `backend/app/config/prompts.yaml`

This file contains:
- **system_prompt**: The system message that defines the LLM's role and requirements
- **single_chunk_prompt**: Template for generating questions from a single text chunk
- **multi_chunk_prompt**: Template for generating questions that span multiple chunks
- **categories**: Valid question categories (FACTUAL, INTERPRETATION, LONG_ANSWER)

**To Modify Prompts:**

1. Edit the `backend/app/config/prompts.yaml` file
2. Keep the template variables intact (e.g., `{num_questions}`, `{chunk_content}`, etc.)
3. Ensure prompts instruct the LLM to return valid JSON with the required structure
4. Restart the application for changes to take effect

For detailed documentation on prompt templates and available variables, see `backend/app/config/README.md`.

## Troubleshooting

**Common Issues:**
- **LLM API errors**: 
  - For OpenAI: Check your API key and billing status at https://platform.openai.com/
  - For Gemini: 
    - **403 Service Disabled**: Enable the [Generative Language API](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com)
    - **API Key Issues**: Get a new key at https://aistudio.google.com/app/apikey
    - **Recent Setup**: Wait 2-3 minutes after enabling the API
- **Provider configuration**: Ensure `LLM_PROVIDER` is set to either "openai" or "gemini"
- **Memory issues**: Try smaller chunk sizes for very large articles
- **File permissions**: Ensure the data directory is writable

**Getting Help:**
- Check the API documentation at `/docs`
- Review log files in the data directory
- Verify your `.env` configuration
- Test your LLM provider: `cd backend && python test_llm_providers.py factory`

## TODO

**Planned Improvements:**
- **Fix Bulk Processing Issue** - It sometimes stuck when processing articles in bulk and requires page refresh
- **Add Gemini CLI support** - Integrate Google's Gemini models as an alternative to OpenAI
- **Improve question generation prompting**:
  1. Each question should be related to more chunks (cross-chunk relationships)
  2. Generated items don't need to be questions (e.g. they can be commands, tasks, or other prompts)

## Author

Created by Kagan Kose - feel free to contribute or report issues.

## License

This project is open source and available under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software for any purpose, including commercial use. See the LICENSE file for full details. 