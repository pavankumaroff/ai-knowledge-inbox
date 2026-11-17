import os
import re
import hashlib
import numpy as np
from typing import List, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren',
    'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his',
    'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my',
    'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our',
    'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than',
    'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what',
    'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'you', 'your', 'yours', 'yourself',
    'used', 'using'
}

class EmbeddingService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None
                )
                logger.info(f"Initialized OpenAI Embeddings client using model '{settings.EMBEDDING_MODEL}'")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Falling back to local hash-based embedder.")
        else:
            logger.info("No OPENAI_API_KEY found. Utilizing deterministic semantic hash embedder for zero-config offline testing.")

    @property
    def is_using_openai(self) -> bool:
        return self.client is not None

    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embeds a list of strings into normalized float32 numpy arrays.
        Uses OpenAI when available; falls back to an offline deterministic vectorizer.
        """
        if not texts:
            return []

        if self.client:
            try:
                # OpenAI embeddings API supports batching
                response = self.client.embeddings.create(
                    model=settings.EMBEDDING_MODEL,
                    input=texts,
                )
                vectors = []
                for item in response.data:
                    vec = np.array(item.embedding, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    vectors.append(vec)
                return vectors
            except Exception as e:
                logger.error(f"OpenAI embedding call failed: {e}. Falling back to deterministic offline vectorizer.")

        # Fallback offline deterministic dense embedding generator (dim=384)
        return [self._local_fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string.
        """
        results = self.embed_texts([query])
        return results[0]

    def _local_fallback_embed(self, text: str, dim: int = 384) -> np.ndarray:
        """
        Deterministic, token & n-gram frequency hash embedder with stopword suppression
        and subword n-gram hashing for robust keyword & semantic matching without external APIs.
        """
        vec = np.zeros(dim, dtype=np.float32)
        # Strip punctuation and tokenize
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        words = cleaned.split()
        if not words:
            return vec

        # Filter stopwords
        content_words = [w for w in words if w and w not in STOP_WORDS]
        # If text consists only of stopwords, retain words
        tokens = content_words if content_words else words

        for i, word in enumerate(tokens):
            # Weight content words by length (rare/specialized technical terms are longer)
            weight = 1.0 + min(len(word) * 0.1, 1.2)
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % dim
            vec[h] += weight

            # Subword character trigrams for word stems / inflection robustness
            if len(word) >= 4:
                for j in range(len(word) - 2):
                    tri = word[j:j+3]
                    h_tri = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16) % dim
                    vec[h_tri] += 0.5

            # Word bigrams for multi-word phrase matching
            if i < len(tokens) - 1:
                bigram = f"{word}_{tokens[i+1]}"
                h2 = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16) % dim
                vec[h2] += 2.0

        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

embedding_service = EmbeddingService()
