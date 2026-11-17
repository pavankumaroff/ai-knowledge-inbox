import { IngestRequest, IngestResponse, KnowledgeItem, QueryResponse } from '../types';

const API_BASE = '/api';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // response wasn't JSON
    }
    throw new ApiError(errorDetail, res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  async getItems(): Promise<KnowledgeItem[]> {
    const res = await fetch(`${API_BASE}/items`);
    return handleResponse<KnowledgeItem[]>(res);
  },

  async ingest(data: IngestRequest): Promise<IngestResponse> {
    const res = await fetch(`${API_BASE}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<IngestResponse>(res);
  },

  async query(question: string, topK: number = 4): Promise<QueryResponse> {
    const res = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: topK }),
    });
    return handleResponse<QueryResponse>(res);
  },

  async deleteItem(id: string): Promise<{ message: string; id: string }> {
    const res = await fetch(`${API_BASE}/items/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<{ message: string; id: string }>(res);
  },
};
