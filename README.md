# AI Knowledge Inbox

A production-style, minimal RAG web application that lets users:
1. **Save short notes or URLs** (server-side text extraction & sanitization).
2. **Ask questions over their saved content** using semantic retrieval.
3. **Get answers powered by a grounded RAG pipeline** with verifiable source citations.

---

## Architecture & System Overview

- **Backend**: FastAPI (Python 3.10+) with Pydantic v2 schemas and structured logging.
- **Frontend**: React 19 (Vite) + Tailwind CSS + Lucide Icons.
- **Vector Storage**: SQLite storing raw IEEE 754 float32 embeddings as binary blobs.
- **RAG Pipeline**:
  - Intentional recursive character chunker (500 chars, 100 overlap).
  - Cosine-similarity vector search via NumPy.
  - LLM synthesis via OpenAI (`gpt-4o-mini` + `text-embedding-3-small`) with automatic zero-config offline fallback.

---

## Project Structure

```
ai-knowledge-inbox/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # /ingest, /items, /query, /items/{id}
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic BaseSettings & env configuration
│   │   │   └── logging.py        # Structured application logger
│   │   ├── db/
│   │   │   └── database.py       # SQLite connection, schemas, binary embeddings
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic request & response models
│   │   ├── services/
│   │   │   ├── scraper.py        # Server-side URL fetching & HTML cleaner
│   │   │   ├── chunker.py        # Recursive paragraph/sentence text splitter
│   │   │   ├── embeddings.py     # OpenAI embedding service + offline fallback
│   │   │   └── rag.py            # Cosine similarity retrieval & prompt synthesis
│   │   └── main.py               # FastAPI app lifecycle, CORS, health check
│   ├── tests/
│   │   ├── conftest.py           # Shared test fixtures (isolated SQLite DB & test client)
│   │   ├── api/
│   │   │   └── test_routes.py    # Tests /health, /ingest, /items, /query, delete & errors
│   │   ├── core/
│   │   │   └── test_config.py    # Tests configuration & settings defaults
│   │   ├── db/
│   │   │   └── test_database.py  # Tests SQLite CRUD, binary embedding blobs, cascade delete
│   │   ├── models/
│   │   │   └── test_schemas.py   # Tests Pydantic validation rules & types
│   │   └── services/
│   │       ├── test_chunker.py   # Tests recursive chunking, boundary splitting, overlap
│   │       ├── test_embeddings.py# Tests embedding dimensions, normalization, cosine similarity
│   │       ├── test_rag.py       # Tests top-k retrieval, context synthesis & citation grounding
│   │       └── test_scraper.py   # Tests HTML cleaning, tag decomposition, timeout handling
│   ├── pytest.ini
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx        # Top navigation & system status
│   │   │   ├── IngestForm.tsx    # Tabbed Note/URL capture form
│   │   │   ├── ItemsList.tsx     # Saved knowledge inbox feed
│   │   │   └── QueryPanel.tsx    # RAG search interface & cited sources
│   │   ├── services/
│   │   │   └── api.ts            # Typed API client
│   │   ├── types/
│   │   │   └── index.ts          # Shared TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── vite.config.ts
│   └── package.json
├── TRADEOFFS.md                  # Comprehensive architectural trade-off analysis
└── README.md
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your OpenAI API Key in .env
# If omitted, the application automatically uses a deterministic local semantic embedder
cp .env.example .env

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
FastAPI interactive Swagger docs will be available at: **http://127.0.0.1:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
The React application will be available at: **http://localhost:3000** (or http://localhost:5173).

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/ingest` | Ingests a plain text note or fetches and cleans a URL. Chunks and indexes vectors. |
| `GET` | `/api/items` | Lists all saved inbox items with chunk counts, preview, and timestamps. |
| `POST` | `/api/query` | Performs semantic search against stored chunks and synthesizes an answer with citations. |
| `DELETE` | `/api/items/{id}` | Deletes an item and its associated chunk embeddings. |
| `GET` | `/health` | Service health status. |

---

## Running Automated Tests

To run the mirrored backend test suite:

```bash
cd backend
pytest -v
```

All 24 unit and integration tests execute against an isolated temporary SQLite database and verify:
- API routing, status codes, and input validation
- Text chunking, sentence boundaries, and cross-chunk overlap
- Embedding vector shapes, unit normalization, and cosine similarity
- Server-side scraping and HTML sanitization
- Grounded RAG answer synthesis and source citations
- Database CRUD and foreign key cascade deletion

---

## Tradeoff Analysis & System Design

See [TRADEOFFS.md](file:///c:/Users/addme/Desktop/ai-knowledge-inbox/TRADEOFFS.md) for detailed discussion on:
1. **Chunking approach rationale** (500 chars / 100 overlap).
2. **Vector storage design** (SQLite binary blobs + NumPy).
3. **What breaks at scale** (in-memory scans, synchronous scraping, database concurrency).
4. **Production changes** (task queues, pgvector / Qdrant, hybrid search, RAGAS evals).
