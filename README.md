# RAG Dataset Creator

A simplified tool for generating Retrieval-Augmented Generation (RAG) datasets from Wikipedia articles and Markdown files. This application automates the workflow of content ingestion, text splitting, and question-answer pair generation to facilitate RAG system training and evaluation.

## Features

- **Multi-Source Ingestion**: Import content directly from Wikipedia URLs or upload Markdown files.
- **Intelligent Text Splitting**: Configurable strategies (including header-aware splitting) to preserve semantic context in chunks.
- **Automated QA Generation**: Uses LLMs to generate relevant questions and answers for each text chunk.
- **Dataset Validation**: Validates Q&A and chunk pairs using LLMs to ensure dataset quality.
- **Management**: View, manage, and export processed datasets as JSON.

## Tech Stack

- **Backend**: Python, FastAPI, AsyncIO
- **Frontend**: React, Vite, Tailwind CSS
- **Infrastructure**: Docker
- **AI/LLM**: OpenAI & Gemini integration

## Installation

### Prerequisites

- Docker and Docker Compose
- API Key for OpenAI or Google Gemini

### **Environment Setup**
   Copy the template configuration and update with your credentials:
   ```bash
   cp env.template .env
   ```
   Edit `.env` to add your `OPENAI_API_KEY` or other required variables.

### **Run the Application**
   Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

   The web interface will be available at `http://localhost:5173` (default Vite port).

## Usage

1. Navigate to the dashboard.
2. Enter a Wikipedia URL or upload Markdown files.
3. Configure chunking parameters (size, overlap) and generation settings.
4. Monitor the ingestion progress.
5. Once complete, explore the generated dataset and export it for your RAG pipeline.

Refer to the `Makefile` for common development commands if available.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
