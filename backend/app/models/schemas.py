from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

class ItemType(str, Enum):
    NOTE = "note"
    URL = "url"

class IngestRequest(BaseModel):
    type: ItemType = Field(..., description="Type of content: 'note' or 'url'")
    content: str = Field(..., min_length=1, max_length=100000, description="Plain text note or target URL")
    title: Optional[str] = Field(None, max_length=200, description="Optional title or label")

class IngestResponse(BaseModel):
    id: str
    type: str
    title: str
    source_url: Optional[str] = None
    char_count: int
    chunk_count: int
    created_at: str
    message: str = "Content successfully ingested and indexed"

class ItemResponse(BaseModel):
    id: str
    type: str
    title: str
    source_url: Optional[str] = None
    preview: str
    char_count: int
    chunk_count: int
    created_at: str

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000, description="Question to ask over your saved content")
    top_k: Optional[int] = Field(4, ge=1, le=15, description="Number of top chunks to retrieve")

class SourceCitation(BaseModel):
    chunk_id: str
    item_id: str
    title: str
    source_type: str
    source_url: Optional[str] = None
    snippet: str
    similarity_score: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    retrieved_count: int
    model_used: str
