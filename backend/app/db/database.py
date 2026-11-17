import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.logging import logger

def get_db_path() -> str:
    path = Path(settings.DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    logger.info(f"Initializing SQLite database at: {get_db_path()}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                source_url TEXT,
                raw_content TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
            );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks(item_id);")
        conn.commit()
    logger.info("Database tables initialized successfully.")

def save_item(
    item_id: str,
    item_type: str,
    title: str,
    source_url: Optional[str],
    raw_content: str,
    char_count: int,
    chunks: List[Dict[str, Any]],
) -> None:
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO items (id, type, title, source_url, raw_content, char_count, chunk_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, item_type, title, source_url, raw_content, char_count, len(chunks), now_iso),
        )

        for c in chunks:
            # c['embedding'] is expected to be a numpy array or list of floats
            emb_array = np.array(c["embedding"], dtype=np.float32)
            emb_blob = emb_array.tobytes()
            cursor.execute(
                """
                INSERT INTO chunks (id, item_id, chunk_index, content, embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (c["id"], item_id, c["chunk_index"], c["content"], emb_blob, now_iso),
            )
        conn.commit()

def list_items() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, type, title, source_url, raw_content, char_count, chunk_count, created_at
            FROM items
            ORDER BY datetime(created_at) DESC
            """
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            preview = (r["raw_content"][:160] + "...") if len(r["raw_content"]) > 160 else r["raw_content"]
            result.append({
                "id": r["id"],
                "type": r["type"],
                "title": r["title"],
                "source_url": r["source_url"],
                "preview": preview.strip().replace("\n", " "),
                "char_count": r["char_count"],
                "chunk_count": r["chunk_count"],
                "created_at": r["created_at"],
            })
        return result

def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)

def delete_item(item_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_all_chunks_for_search() -> List[Dict[str, Any]]:
    """
    Returns all chunks joined with item title & source metadata,
    decoding binary embeddings back into numpy float32 arrays.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                c.id AS chunk_id,
                c.item_id,
                c.chunk_index,
                c.content,
                c.embedding,
                i.title,
                i.type AS source_type,
                i.source_url
            FROM chunks c
            JOIN items i ON c.item_id = i.id
            """
        )
        rows = cursor.fetchall()
        chunks = []
        for r in rows:
            emb_vector = np.frombuffer(r["embedding"], dtype=np.float32)
            chunks.append({
                "chunk_id": r["chunk_id"],
                "item_id": r["item_id"],
                "chunk_index": r["chunk_index"],
                "content": r["content"],
                "embedding": emb_vector,
                "title": r["title"],
                "source_type": r["source_type"],
                "source_url": r["source_url"],
            })
        return chunks
