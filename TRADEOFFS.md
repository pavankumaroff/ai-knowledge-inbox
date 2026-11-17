# Architectural Tradeoffs & System Design Analysis

This document outlines the core engineering decisions, rationale, scaling bottlenecks, and production roadmap for the **AI Knowledge Inbox**.

---

## 1. Chunking Approach Rationale

### Choice: Recursive Character Chunking (~500 characters with 100-character overlap)
- **Why ~500 Characters?**
  - Raw plain-text notes and scraped web pages contain varying degrees of information density.
  - If chunks are too small (<200 chars), semantic embeddings lose broader contextual meaning and conversational nuances, leading to fragmented search results.
  - If chunks are too large (>1500 chars), the embedding vector averages out fine details ("dilution problem"), and passing large chunks consumes excessive LLM context tokens.
  - 500 characters (~100–120 words) aligns with a single coherent paragraph or thought unit.
- **Why 100-Character Overlap?**
  - Concepts and explanations frequently span paragraph or sentence boundaries. Overlapping windows ensure that semantic transitions and entity-verb relationships are not severed between adjacent chunks.
- **Hierarchical Separator Strategy:**
  - The chunker checks natural splits in descending order of semantic cohesion:
    `\n\n` (paragraphs) $\rightarrow$ `\n` (lines) $\rightarrow$ `. ` / `? ` / `! ` (sentences) $\rightarrow$ `" "` (words).
  - This avoids breaking words mid-syllable and maintains reader-friendly snippets for UI source inspection.

---

## 2. Vector Store Choice

### Choice: SQLite + NumPy Cosine Similarity Vector Search
- **Why SQLite + NumPy?**
  1. **Simplicity & Zero Infrastructure Debt**: For a personal "Knowledge Inbox" (typically hundreds to thousands of items), running external infrastructure like Pinecone, Milvus, or Qdrant adds network latency, operational overhead, and authentication gates without tangible benefits.
  2. **Single Source of Truth**: Metadata, raw content, and chunk vectors reside in the same relational SQLite database, guaranteeing ACID compliance and transactional cascade deletion (`ON DELETE CASCADE`).
  3. **Performance**: NumPy vectorized operations compute cosine similarity against 10,000 1536-dimensional float32 vectors in **< 15 milliseconds** on modern CPU cores.
- **Binary Blob Storage**:
  - Embeddings are serialized directly as raw IEEE 754 float32 byte arrays (`ndarray.tobytes()`). This avoids slow JSON string parsing and reduces storage size by ~60%.

---

## 3. What Breaks at Scale?

| Component | Scaling Bottleneck | Manifestation at High Scale |
| :--- | :--- | :--- |
| **In-Memory / NumPy Scan** | $O(N)$ linear scan over all chunk embeddings | Once total chunks exceed ~50,000–100,000, loading all vectors into RAM per query and performing brute-force dot products will cause CPU spikes and latency degradation (>200ms). |
| **Synchronous Scraping** | Web scraping executes during `POST /ingest` | If target websites have slow TTFB, Cloudflare challenges, or massive DOMs, the HTTP request blocks, causing client timeouts and starvation of FastAPI worker threads. |
| **Database Concurrency** | SQLite file locks on write | SQLite only supports a single concurrent writer (`database is locked` error under high write concurrency). |
| **Context Window Stuffing** | Naive top-$k$ concatenation | When retrieving multiple large chunks, token usage increases linearly. Without reranking, distracting or redundant chunks degrade LLM output precision. |

---

## 4. Production Changes & Evolution Roadmap

To transition this minimal prototype into an enterprise-grade, multi-tenant production system:

### A. Asynchronous Ingestion & Task Queues
- Move URL fetching, parsing, chunking, and embedding generation to an asynchronous worker queue (e.g., **Celery** or **ARQ** with **Redis**).
- `POST /ingest` immediately returns `202 Accepted` with a `task_id` and status `PROCESSING`.
- The frontend polls or uses WebSockets/SSE to update the item status when indexing is complete.

### B. Vector Database with Approximate Nearest Neighbor (ANN)
- Migrate vector storage to **pgvector** (PostgreSQL) or **Qdrant / Milvus**.
- Use **HNSW (Hierarchical Navigable Small World)** indexing for sub-10ms logarithmic $O(\log N)$ approximate nearest neighbor search over millions of chunks.

### C. Hybrid Search (Dense + Sparse) & Reranking
- Combine Dense Vector retrieval (semantic similarity) with Sparse BM25 / Full-Text Search (keyword exact matches).
- Apply a Cross-Encoder Reranker (e.g., `Cohere Rerank` or `bge-reranker-large`) on the top-20 retrieved candidates before sending the final top-4 to the LLM.

### D. Production Observability & Guardrails
- **OpenTelemetry / Langfuse**: Track LLM latency, token expenditure, and retrieval quality scores.
- **RAG Evaluation**: Integrate automated evaluation metrics (e.g., RAGAS for faithfulness and answer relevance).
- **Rate Limiting & Authentication**: Add JWT authentication and token-bucket rate limiters on `/ingest` and `/query`.
