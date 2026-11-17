import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.schemas import (
    IngestRequest,
    IngestResponse,
    ItemResponse,
    QueryRequest,
    QueryResponse,
    ItemType,
)
from app.services.scraper import fetch_url_content
from app.services.chunker import chunk_text
from app.services.embeddings import embedding_service
from app.services.rag import generate_rag_answer
from app.db.database import save_item, list_items, get_item, delete_item
from app.core.logging import logger

router = APIRouter()

@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a plain text note or a web URL",
    description="Fetches URL content if type is 'url', chunks text, creates embeddings, and stores in SQLite.",
)
async def ingest_content(payload: IngestRequest):
    item_id = str(uuid.uuid4())
    logger.info(f"Received ingest request: type={payload.type}")

    if payload.type == ItemType.URL:
        target_url = payload.content.strip()
        try:
            page_title, raw_content = await fetch_url_content(target_url)
            title = payload.title.strip() if payload.title else page_title
            source_url = target_url
        except ValueError as e:
            logger.error(f"URL scraping error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to ingest URL: {str(e)}",
            )
    elif payload.type == ItemType.NOTE:
        raw_content = payload.content.strip()
        if not raw_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note content cannot be empty.",
            )
        # Default title to first non-empty line (up to 60 chars) or user title
        first_line = raw_content.splitlines()[0][:60]
        title = payload.title.strip() if payload.title else (first_line or "Untitled Note")
        source_url = None
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type. Must be 'note' or 'url'.",
        )

    # 1. Chunking
    chunks_text = chunk_text(raw_content)
    if not chunks_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content could not be processed into meaningful text chunks.",
        )

    # 2. Embedding generation
    try:
        embeddings = embedding_service.embed_texts(chunks_text)
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate embeddings for content.",
        )

    # 3. Prepare chunk records
    chunk_records = []
    for idx, (txt, emb) in enumerate(zip(chunks_text, embeddings)):
        chunk_records.append({
            "id": f"{item_id}-c{idx}",
            "chunk_index": idx,
            "content": txt,
            "embedding": emb,
        })

    # 4. Save to Database
    try:
        save_item(
            item_id=item_id,
            item_type=payload.type.value,
            title=title,
            source_url=source_url,
            raw_content=raw_content,
            char_count=len(raw_content),
            chunks=chunk_records,
        )
    except Exception as e:
        logger.error(f"Database error saving item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save item to database.",
        )

    logger.info(f"Successfully ingested item {item_id}: '{title}' ({len(chunk_records)} chunks)")
    
    # Fetch created row for consistent response
    saved = get_item(item_id)

    return IngestResponse(
        id=item_id,
        type=payload.type.value,
        title=title,
        source_url=source_url,
        char_count=len(raw_content),
        chunk_count=len(chunk_records),
        created_at=saved["created_at"] if saved else "",
        message="Item ingested, chunked, and indexed successfully.",
    )

@router.get(
    "/items",
    response_model=List[ItemResponse],
    status_code=status.HTTP_200_OK,
    summary="List all saved knowledge items",
)
def get_items():
    try:
        return list_items()
    except Exception as e:
        logger.error(f"Error fetching items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve items.",
        )

@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a saved item and its chunks",
)
def remove_item(item_id: str):
    success = delete_item(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found.",
        )
    return {"message": "Item deleted successfully", "id": item_id}

@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question against your saved knowledge inbox",
)
def query_knowledge_inbox(payload: QueryRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    logger.info(f"Processing query: '{question}' (top_k={payload.top_k})")
    try:
        answer, sources, model_used = generate_rag_answer(
            question=question,
            top_k=payload.top_k or 4,
        )
        return QueryResponse(
            question=question,
            answer=answer,
            sources=sources,
            retrieved_count=len(sources),
            model_used=model_used,
        )
    except Exception as e:
        logger.error(f"Error during RAG execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying knowledge inbox: {str(e)}",
        )
