import type {
  IngestRequest,
  IngestResponse,
  ArticleListItem,
  ArticleMetadata,
  ChunkListItem,
  DatasetResponse,
  IngestOptions,
  ConfigResponse,
  ValidationResponse,
} from '../types/api'

// Base API URL - Backend service accessible at the deployed IP address
const API_BASE_URL = 'http://localhost:8051'

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text()
    throw new ApiError(
      `API Error: ${response.status} ${response.statusText} - ${errorText}`,
      response.status
    )
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  
  return response as unknown as T
}

// Ingestion API
export async function startIngestion(request: IngestRequest): Promise<IngestResponse> {
  const response = await fetch(`${API_BASE_URL}/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  return handleResponse<IngestResponse>(response)
}

export async function uploadFiles(
  files: File[], 
  options: Partial<IngestOptions>
): Promise<IngestResponse[]> {
  const formData = new FormData()
  
  files.forEach(file => {
    formData.append('files', file)
  })
  
  // Append options
  if (options.chunk_size) formData.append('chunk_size', options.chunk_size.toString())
  if (options.chunk_overlap) formData.append('chunk_overlap', options.chunk_overlap.toString())
  if (options.split_strategy) formData.append('split_strategy', options.split_strategy)
  if (options.total_questions) formData.append('total_questions', options.total_questions.toString())
  if (options.reingest !== undefined) formData.append('reingest', options.reingest.toString())

  const response = await fetch(`${API_BASE_URL}/ingest/files`, {
    method: 'POST',
    body: formData,
  })
  
  return handleResponse<IngestResponse[]>(response)
}

// Articles API
export async function getArticles(): Promise<ArticleListItem[]> {
  const response = await fetch(`${API_BASE_URL}/articles`)
  return handleResponse<ArticleListItem[]>(response)
}

export async function getArticle(articleId: string): Promise<ArticleMetadata> {
  const response = await fetch(`${API_BASE_URL}/articles/${encodeURIComponent(articleId)}`)
  return handleResponse<ArticleMetadata>(response)
}

export async function getChunks(articleId: string): Promise<ChunkListItem[]> {
  const response = await fetch(`${API_BASE_URL}/articles/${encodeURIComponent(articleId)}/chunks`)
  return handleResponse<ChunkListItem[]>(response)
}

export async function exportArticle(articleId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/articles/${encodeURIComponent(articleId)}/export`)
  if (!response.ok) {
    throw new ApiError(
      `Failed to export article: ${response.status} ${response.statusText}`,
      response.status
    )
  }
  return response.blob()
}

export async function exportAllArticles(): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/articles/export/all`)
  if (!response.ok) {
    throw new ApiError(
      `Failed to export all articles: ${response.status} ${response.statusText}`,
      response.status
    )
  }
  return response.blob()
}

export async function deleteArticle(articleId: string): Promise<{ message: string; article_id: string }> {
  const response = await fetch(`${API_BASE_URL}/articles/${encodeURIComponent(articleId)}`, {
    method: 'DELETE',
  })
  return handleResponse<{ message: string; article_id: string }>(response)
}

// Dataset API
export async function getDataset(articleId: string): Promise<DatasetResponse> {
  const response = await fetch(`${API_BASE_URL}/dataset/${encodeURIComponent(articleId)}`)
  return handleResponse<DatasetResponse>(response)
}

export async function downloadDatasetJson(articleId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/dataset/${encodeURIComponent(articleId)}/download`)
  if (!response.ok) {
    throw new ApiError(
      `Failed to download dataset: ${response.status} ${response.statusText}`,
      response.status
    )
  }
  return response.blob()
}

// Files API
export async function downloadFile(articleId: string, filename: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/files/${encodeURIComponent(articleId)}/${filename}`)
  if (!response.ok) {
    throw new ApiError(
      `Failed to download file: ${response.status} ${response.statusText}`,
      response.status
    )
  }
  return response.blob()
}

// Legacy function - kept for compatibility but not used in current code
export async function getFileUrl(articleId: string, filename: string): Promise<string> {
  return `${API_BASE_URL}/files/${encodeURIComponent(articleId)}/${filename}`
}

// Server-Sent Events for ingestion progress
export function createIngestionEventSource(runId: string): EventSource {
  return new EventSource(`${API_BASE_URL}/ingest/stream/${runId}`)
}

// Configuration API
export async function getConfig(): Promise<ConfigResponse> {
  const response = await fetch(`${API_BASE_URL}/config`)
  return handleResponse<ConfigResponse>(response)
}

// Validation API
export async function validateArticle(articleId: string): Promise<ValidationResponse> {
  const response = await fetch(`${API_BASE_URL}/validate/${encodeURIComponent(articleId)}`, {
    method: 'POST',
  })
  return handleResponse<ValidationResponse>(response)
} 