export type ItemType = 'note' | 'url';

export interface KnowledgeItem {
  id: string;
  type: ItemType;
  title: string;
  source_url?: string | null;
  preview: string;
  char_count: number;
  chunk_count: number;
  created_at: string;
}

export interface IngestRequest {
  type: ItemType;
  content: string;
  title?: string;
}

export interface IngestResponse {
  id: string;
  type: ItemType;
  title: string;
  source_url?: string | null;
  char_count: number;
  chunk_count: number;
  created_at: string;
  message: string;
}

export interface SourceCitation {
  chunk_id: string;
  item_id: string;
  title: string;
  source_type: string;
  source_url?: string | null;
  snippet: string;
  similarity_score: number;
}

export interface QueryResponse {
  question: string;
  answer: string;
  sources: SourceCitation[];
  retrieved_count: number;
  model_used: string;
}
