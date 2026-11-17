import pytest
from app.services.scraper import fetch_url_content

@pytest.mark.anyio
async def test_fetch_url_content_real_or_mock(monkeypatch):
    class MockResponse:
        status_code = 200
        headers = {"content-type": "text/html; charset=utf-8"}
        text = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Article Page</title></head>
        <body>
            <header><nav>Navigation Link</nav></header>
            <main>
                <h1>Article Main Heading</h1>
                <p>This is the real body content of the article that should be preserved.</p>
            </main>
            <footer>Footer Copyright 2026</footer>
            <script>console.log('strip me');</script>
        </body>
        </html>
        """
        def raise_for_status(self):
            pass

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient", MockAsyncClient)

    title, text = await fetch_url_content("https://example-test-url.org/page")
    assert title == "Test Article Page"
    assert "Navigation Link" not in text
    assert "Footer Copyright" not in text
    assert "console.log" not in text
    assert "This is the real body content of the article" in text

@pytest.mark.anyio
async def test_fetch_invalid_url_raises_value_error():
    with pytest.raises(ValueError):
        await fetch_url_content("http://this-domain-does-not-exist-at-all-xyz987.invalid")
