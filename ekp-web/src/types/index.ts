export interface Document {
  id: number;
  title: string;
  file_path: string;
  file_size: number;
  file_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at?: string;
}

export interface DocumentChunk {
  id: number;
  document_id: number;
  content: string;
  chunk_index: number;
  token_count: number;
}

export interface QASource {
  chunk_id: number;
  document_id: number;
  document_title: string;
  content: string;
  relevance_score: number;
}

export interface QASession {
  id: number;
  question: string;
  answer: string;
  sources: QASource[];
  model_used: string;
  tokens_used: number;
  response_time_ms: number;
  created_at: string;
}

export interface QARequest {
  question: string;
  document_ids?: number[];
  top_k?: number;
}

export interface UploadResponse {
  id: number;
  title: string;
  status: string;
  message: string;
}

export interface HealthStatus {
  status: string;
  service?: string;
}
