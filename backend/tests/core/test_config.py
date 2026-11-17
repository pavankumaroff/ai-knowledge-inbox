from app.core.config import settings

def test_settings_defaults():
    assert settings.APP_NAME == "AI Knowledge Inbox API"
    assert settings.CHUNK_SIZE == 500
    assert settings.CHUNK_OVERLAP == 100
    assert settings.DEFAULT_TOP_K == 4
    assert settings.MAX_SCRAPE_LENGTH > 0
    assert "http://localhost:3000" in settings.CORS_ORIGINS
