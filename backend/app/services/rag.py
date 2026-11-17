import numpy as np
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.db.database import get_all_chunks_for_search
from app.services.embeddings import embedding_service
from app.models.schemas import SourceCitation

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))

def retrieve_top_chunks(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    Retrieves the top-k most semantically similar chunks for a given query
    by calculating cosine similarity across all stored chunk embeddings.
    """
    all_chunks = get_all_chunks_for_search()
    if not all_chunks:
        return []

    query_vec = embedding_service.embed_query(query)

    scored_chunks = []
    for c in all_chunks:
        chunk_vec = c["embedding"]
        # Handle dimension mismatch if embeddings were stored with a different embedder
        if chunk_vec.shape != query_vec.shape:
            continue
        score = cosine_similarity(query_vec, chunk_vec)
        scored_chunks.append({
            "chunk_id": c["chunk_id"],
            "item_id": c["item_id"],
            "title": c["title"],
            "source_type": c["source_type"],
            "source_url": c["source_url"],
            "snippet": c["content"],
            "similarity_score": round(score, 4),
        })

    # Sort descending by similarity score
    scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_chunks[:top_k]

def generate_rag_answer(question: str, top_k: int = 4) -> Tuple[str, List[SourceCitation], str]:
    """
    Executes the RAG pipeline:
    1. Embeds question and retrieves top_k chunks.
    2. Builds an augmented context prompt with clear source identifiers.
    3. Calls LLM (OpenAI) or deterministic synthesis fallback.
    4. Returns (answer, sources, model_used).
    """
    top_chunks = retrieve_top_chunks(question, top_k=top_k)
    
    if not top_chunks:
        return (
            "I couldn't find any relevant information in your knowledge inbox because no items match your question (or your inbox is currently empty). Try saving a note or URL first!",
            [],
            "none",
        )

    sources = [
        SourceCitation(
            chunk_id=c["chunk_id"],
            item_id=c["item_id"],
            title=c["title"],
            source_type=c["source_type"],
            source_url=c["source_url"],
            snippet=c["snippet"],
            similarity_score=c["similarity_score"],
        )
        for c in top_chunks
    ]

    # Build context string
    context_blocks = []
    for idx, c in enumerate(top_chunks, start=1):
        src_label = f"Source [{idx}] (Title: '{c['title']}', Type: {c['source_type']})"
        context_blocks.append(f"{src_label}\n{c['snippet']}")

    context_str = "\n\n---\n\n".join(context_blocks)

    system_prompt = (
        "You are an AI assistant for a personal Knowledge Inbox. "
        "Answer the user's question accurately and concisely, basing your response ONLY on the provided sources below.\n"
        "Guidelines:\n"
        "1. Cite your sources inline using [1], [2], etc., corresponding to the Source [x] indices provided in the context.\n"
        "2. If the context does not contain enough information to answer the question, clearly state that the saved notes/URLs do not cover this.\n"
        "3. Do not invent facts or cite nonexistent sources."
    )

    user_prompt = f"Context:\n{context_str}\n\nQuestion: {question}\n\nAnswer:"

    openai_error_msg = None

    # Check if OpenAI is available
    if embedding_service.client:
        try:
            logger.info(f"Calling OpenAI model '{settings.CHAT_MODEL}' for RAG completion")
            completion = embedding_service.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            answer = completion.choices[0].message.content.strip()
            return answer, sources, f"OpenAI ({settings.CHAT_MODEL})"
        except Exception as e:
            openai_error_msg = str(e)
            logger.error(f"OpenAI chat completion failed: {openai_error_msg}. Falling back to rule-based synthesis.")

    # Fallback synthesizer when no API key is present or when API call fails
    answer_lines = [
        f"Based on your saved items, here are the most relevant findings for: **\"{question}\"**\n"
    ]
    for idx, c in enumerate(top_chunks, start=1):
        preview = c['snippet'][:250].replace("\n", " ") + "..."
        answer_lines.append(f"- **[{idx}] {c['title']}**: \"{preview}\" *(Relevance score: {c['similarity_score']})*")

    if openai_error_msg:
        if "429" in openai_error_msg or "credits" in openai_error_msg:
            answer_lines.append(
                "\n*(Note: OpenAI returned Error 429 - Insufficient API credits in your OpenAI billing account. The app automatically fell back to the local extractive synthesizer so you still get answers!)*"
            )
        else:
            answer_lines.append(
                f"\n*(Note: OpenAI API error: {openai_error_msg[:120]}... Fell back to local extractive synthesizer)*"
            )
    else:
        answer_lines.append(
            "\n*(Note: Set `OPENAI_API_KEY` in backend `.env` for full generative LLM answers with GPT-4o-mini)*"
        )

    return "\n".join(answer_lines), sources, "Local Extractive Synthesizer"
