# Configuration Files

This directory contains configuration files for the RAG dataset creator application.

## prompts.yaml

This file contains all prompts used for LLM-based question generation.

### Structure

- **system_prompt**: The system prompt that defines the role and requirements for the LLM
- **single_chunk_prompt**: Template for generating questions from a single text chunk
- **multi_chunk_prompt**: Template for generating questions that span multiple chunks
- **categories**: List of valid question categories

### Template Variables

Templates use Python's `.format()` syntax with the following variables:

#### single_chunk_prompt variables:
- `{num_questions}`: Number of questions to generate
- `{chunk_id}`: ID of the chunk
- `{context_info}`: Optional context about the chunk's section/heading
- `{chunk_content}`: The actual text content of the chunk

#### multi_chunk_prompt variables:
- `{num_questions}`: Number of questions to generate
- `{chunks_text}`: Formatted text of all chunks with IDs
- `{context_info}`: Optional context about the chunks' sections
- `{chunk_ids}`: List of all chunk IDs

### Modifying Prompts

To modify prompts:

1. Edit the `prompts.yaml` file
2. Use the existing template variables
3. Ensure the prompt instructs the LLM to return valid JSON with the required structure
4. Restart the backend application for changes to take effect

The prompts are cached after first load for performance. During development, restart the application to reload changes.

### Question Categories

Three question types are supported:

1. **FACTUAL**: Direct recall questions (names, dates, numbers, specific facts)
2. **INTERPRETATION**: Comprehension questions requiring explanation or synthesis
3. **LONG_ANSWER**: Complex questions requiring multi-sentence explanations

These categories can be modified in the `categories` section, but ensure any changes are reflected in the prompt descriptions.

