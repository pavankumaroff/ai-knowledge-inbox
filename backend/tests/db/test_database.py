import numpy as np
from app.db.database import (
    save_item,
    list_items,
    get_item,
    delete_item,
    get_all_chunks_for_search,
)

def test_save_and_list_items():
    fake_embedding = np.random.randn(384).astype(np.float32)
    fake_chunks = [
        {"id": "item-1-c0", "chunk_index": 0, "content": "Chunk zero content", "embedding": fake_embedding},
        {"id": "item-1-c1", "chunk_index": 1, "content": "Chunk one content", "embedding": fake_embedding},
    ]

    save_item(
        item_id="item-1",
        item_type="note",
        title="Test Database Item",
        source_url=None,
        raw_content="Chunk zero content. Chunk one content.",
        char_count=38,
        chunks=fake_chunks,
    )

    items = list_items()
    assert len(items) == 1
    assert items[0]["id"] == "item-1"
    assert items[0]["title"] == "Test Database Item"
    assert items[0]["chunk_count"] == 2

    # Verify single fetch
    item = get_item("item-1")
    assert item is not None
    assert item["title"] == "Test Database Item"

def test_cascade_delete_chunks():
    fake_embedding = np.ones(384, dtype=np.float32)
    save_item(
        item_id="item-to-delete",
        item_type="note",
        title="Delete Me",
        source_url=None,
        raw_content="Content to delete",
        char_count=17,
        chunks=[{"id": "del-c0", "chunk_index": 0, "content": "Content", "embedding": fake_embedding}],
    )

    # Chunks exist
    chunks_before = get_all_chunks_for_search()
    assert any(c["item_id"] == "item-to-delete" for c in chunks_before)

    # Delete item
    success = delete_item("item-to-delete")
    assert success is True

    # Chunks are cascade deleted
    chunks_after = get_all_chunks_for_search()
    assert not any(c["item_id"] == "item-to-delete" for c in chunks_after)
    assert get_item("item-to-delete") is None
