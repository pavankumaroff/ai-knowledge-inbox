import pytest
from pydantic import ValidationError
from app.models.schemas import IngestRequest, ItemType, QueryRequest

def test_ingest_request_valid_note():
    req = IngestRequest(type=ItemType.NOTE, content="Valid note body", title="Sample")
    assert req.type == ItemType.NOTE
    assert req.content == "Valid note body"
    assert req.title == "Sample"

def test_ingest_request_valid_url():
    req = IngestRequest(type=ItemType.URL, content="https://example.com")
    assert req.type == ItemType.URL
    assert req.title is None

def test_ingest_request_invalid_type():
    with pytest.raises(ValidationError):
        IngestRequest(type="audio", content="hello")

def test_ingest_request_empty_content():
    with pytest.raises(ValidationError):
        IngestRequest(type=ItemType.NOTE, content="")

def test_query_request_validation():
    req = QueryRequest(question="How does RAG work?", top_k=5)
    assert req.question == "How does RAG work?"
    assert req.top_k == 5

    # Question too short
    with pytest.raises(ValidationError):
        QueryRequest(question="a")

    # top_k out of bounds
    with pytest.raises(ValidationError):
        QueryRequest(question="Valid question", top_k=50)
