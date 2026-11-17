def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_ingest_note_lifecycle(client):
    # Ingest Note
    payload = {
        "type": "note",
        "title": "FastAPI Async Routing",
        "content": "FastAPI is built on Starlette and Pydantic, enabling asynchronous request handling with standard Python async def endpoints."
    }
    res = client.post("/api/ingest", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "FastAPI Async Routing"
    assert data["chunk_count"] >= 1
    item_id = data["id"]

    # Verify in GET /api/items
    list_res = client.get("/api/items")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(it["id"] == item_id for it in items)

    # Query with POST /api/query
    q_res = client.post("/api/query", json={"question": "What is FastAPI built on?", "top_k": 3})
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert len(q_data["sources"]) >= 1
    assert q_data["sources"][0]["title"] == "FastAPI Async Routing"

    # Delete with DELETE /api/items/{id}
    del_res = client.delete(f"/api/items/{item_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == item_id

    # Verify deleted
    list_after = client.get("/api/items").json()
    assert not any(it["id"] == item_id for it in list_after)

def test_delete_nonexistent_item_returns_404(client):
    res = client.delete("/api/items/non-existent-uuid-1234")
    assert res.status_code == 404

def test_ingest_empty_content_returns_400(client):
    res = client.post("/api/ingest", json={"type": "note", "content": "    "})
    assert res.status_code == 400

def test_ingest_invalid_url_returns_400(client):
    res = client.post("/api/ingest", json={"type": "url", "content": "http://invalid-non-existent-domain-404.xyz"})
    assert res.status_code == 400
