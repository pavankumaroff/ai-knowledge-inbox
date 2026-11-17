import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db

@pytest.fixture(autouse=True)
def isolated_test_db(monkeypatch):
    """
    Creates an isolated temporary SQLite database for each test run.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    monkeypatch.setattr("app.core.config.settings.DATABASE_PATH", db_path)
    # Ensure test suite runs 100% offline without hitting external OpenAI network/rate limits
    monkeypatch.setattr("app.services.embeddings.embedding_service.client", None)
    init_db()
    yield db_path
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

@pytest.fixture
def client():
    """
    TestClient instance bound to the FastAPI application.
    """
    with TestClient(app) as c:
        yield c
