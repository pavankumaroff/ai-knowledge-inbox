from typing import List
from app.core.config import settings
from app.core.logging import logger

def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> List[str]:
    """
    Splits text recursively based on paragraph -> sentence -> word boundaries
    to preserve semantic integrity while enforcing chunk_size and chunk_overlap.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    if len(clean_text) <= chunk_size:
        return [clean_text]

    separators = ["\n\n", "\n", ". ", "? ", "! ", " "]
    chunks: List[str] = []
    start = 0
    text_len = len(clean_text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # If we haven't reached the end of the text, try to find a natural break point
        if end < text_len:
            split_pos = -1
            search_window = clean_text[start:end]

            for sep in separators:
                last_idx = search_window.rfind(sep)
                # Ensure the break point isn't too close to the start (at least 30% of chunk_size)
                if last_idx >= int(chunk_size * 0.3):
                    split_pos = start + last_idx + len(sep)
                    break

            if split_pos != -1:
                end = split_pos

        chunk = clean_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward, stepping back by chunk_overlap to maintain cross-chunk continuity
        if end >= text_len:
            break
        
        step = max(1, end - start - chunk_overlap)
        start += step

    logger.debug(f"Chunked {text_len} chars into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks
