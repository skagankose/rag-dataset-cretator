// API types matching the backend schemas

export interface IngestOptions {
  chunk_size: number
  chunk_overlap: number
  split_strategy: 'recursive' | 'header_aware'
  total_questions: number
  llm_model: string
  reingest: boolean
}

export interface IngestRequest {
  wikipedia_url: string
  options?: Partial<IngestOptions>
}

export interface IngestResponse {
  run_id: string
  article_id?: string
  message: string
  status: 'started' | 'existing' | 'failed'
}

export interface IngestProgress {
  run_id: string
  stage: 'FETCHING' | 'CLEANING' | 'SPLITTING' | 'WRITE_MARKDOWN' | 'QUESTION_GEN' | 'WRITE_DATASET_MD' | 'DONE' | 'FAILED'
  message: string
  timestamp: number
  article_id?: string
  details?: Record<string, any>
}

export interface ArticleListItem {
  id: string
  url: string
  title: string
  lang: string
  created_at: string
}

export interface ArticleMetadata {
  id: string
  url: string
  title: string
  lang: string
  created_at: string
  checksum: string
  options: Record<string, any>
  stats: Record<string, any>
}

export interface ChunkListItem {
  id: string
  article_id: string
  section: string
  heading_path: string
  start_char: number
  end_char: number
  content: string
  char_count: number
  token_estimate: number
  token_start?: number
  token_end?: number
}

export interface DatasetItem {
  question: string
  answer: string
  related_chunk_ids: string[]
  category: string
}

export interface DatasetResponse {
  article_id: string
  title: string
  created_at: string
  items: DatasetItem[]
  total_questions: number
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy'
  version: string
  environment: string
  services: Record<string, 'ok' | 'error'>
  message: string
}

export interface ConfigResponse {
  prompt_language: string
  llm_provider: string
  default_chunk_size: number
  default_chunk_overlap: number
  default_total_questions: number
} 