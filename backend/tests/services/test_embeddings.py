import numpy as np
from app.services.embeddings import embedding_service
from app.services.rag import cosine_similarity

def test_embed_query_shape_and_norm():
    vec = embedding_service.embed_query("Semantic embedding test")
    assert isinstance(vec, np.ndarray)
    assert vec.dtype == np.float32
    # Verify vector is L2 unit normalized
    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-3)

def test_embed_batch_texts():
    texts = ["First document", "Second document", "Third document"]
    vectors = embedding_service.embed_texts(texts)
    assert len(vectors) == 3
    for v in vectors:
        assert isinstance(v, np.ndarray)

def test_cosine_similarity_properties():
    # Identical vectors should have similarity ~1.0
    v1 = embedding_service.embed_query("machine learning neural network")
    assert np.isclose(cosine_similarity(v1, v1), 1.0, atol=1e-3)

    # Semantically closer phrases have higher similarity than unrelated phrases
    v_related = embedding_service.embed_query("deep learning artificial intelligence")
    v_unrelated = embedding_service.embed_query("strawberry cheesecake pastry recipe")

    sim_rel = cosine_similarity(v1, v_related)
    sim_unrel = cosine_similarity(v1, v_unrelated)
    assert sim_rel > sim_unrel
