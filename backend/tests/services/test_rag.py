from app.services.rag import retrieve_top_chunks, generate_rag_answer
from app.db.database import save_item
from app.services.embeddings import embedding_service
from app.services.chunker import chunk_text

def test_rag_with_empty_knowledge_base():
    answer, sources, model = generate_rag_answer("What is my secret key?", top_k=3)
    assert len(sources) == 0
    assert "couldn't find any relevant information" in answer.lower()

def test_rag_retrieval_and_answer_generation():
    doc_text = (
        "PostgreSQL supports pgvector extension for efficient vector search. "
        "SQLite can store float32 blobs directly with zero additional infrastructure."
    )
    chunks = chunk_text(doc_text)
    embs = embedding_service.embed_texts(chunks)
    chunk_records = [
        {"id": f"chunk-{i}", "chunk_index": i, "content": c, "embedding": e}
        for i, (c, e) in enumerate(zip(chunks, embs))
    ]

    save_item(
        item_id="db-doc-1",
        item_type="note",
        title="Database Vector Comparison",
        source_url=None,
        raw_content=doc_text,
        char_count=len(doc_text),
        chunks=chunk_records,
    )

    top_chunks = retrieve_top_chunks("How does SQLite store vectors?", top_k=2)
    assert len(top_chunks) >= 1
    assert top_chunks[0]["title"] == "Database Vector Comparison"
    assert top_chunks[0]["similarity_score"] > 0

    answer, sources, model = generate_rag_answer("How does SQLite store vectors?", top_k=2)
    assert len(sources) >= 1
    assert sources[0].title == "Database Vector Comparison"
    assert len(answer) > 0
