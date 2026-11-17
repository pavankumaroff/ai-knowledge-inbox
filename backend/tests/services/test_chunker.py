from app.services.chunker import chunk_text

def test_chunk_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []

def test_chunk_short_text_single_chunk():
    text = "A short note that fits inside one single chunk."
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_paragraph_boundary_splitting():
    p1 = "First paragraph discussing system design and FastAPI architecture."
    p2 = "Second paragraph discussing SQLite vector embeddings and NumPy dot product."
    p3 = "Third paragraph discussing React 19 frontend integration with Vite."
    full_text = f"{p1}\n\n{p2}\n\n{p3}"

    chunks = chunk_text(full_text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 3
    # Verify no chunk exceeds chunk_size by an unreasonable margin
    for c in chunks:
        assert len(c) <= 120

def test_chunk_overlap_preservation():
    words = [f"word{i}" for i in range(100)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=150, chunk_overlap=40)
    assert len(chunks) > 1

    # Overlap implies text from the end of chunk 0 appears in chunk 1
    chunk_0_end_tokens = set(chunks[0].split()[-3:])
    chunk_1_start_tokens = set(chunks[1].split()[:5])
    assert len(chunk_0_end_tokens.intersection(chunk_1_start_tokens)) > 0
