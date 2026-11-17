import re
import httpx
from bs4 import BeautifulSoup
from typing import Tuple
from app.core.config import settings
from app.core.logging import logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 AI-Knowledge-Inbox/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

async def fetch_url_content(url: str) -> Tuple[str, str]:
    """
    Fetches web content server-side, strips navigational/script bloat,
    and returns (title, extracted_text).
    Raises ValueError on network failures or unreadable HTML.
    """
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    logger.info(f"Fetching URL server-side: {clean_url}")

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(clean_url)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                logger.warning(f"URL {clean_url} returned non-html content type: {content_type}")

            html_text = response.text
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching URL: {clean_url}")
        raise ValueError(f"Request timed out while trying to reach: {clean_url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} fetching URL: {clean_url}")
        raise ValueError(f"Server returned status {e.response.status_code} for URL: {clean_url}")
    except Exception as e:
        logger.error(f"Error fetching URL {clean_url}: {str(e)}")
        raise ValueError(f"Failed to fetch URL: {str(e)}")

    # Parse and clean HTML
    soup = BeautifulSoup(html_text, "html.parser")

    # Extract title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()
    if not title:
        title = clean_url

    # Remove script, style, navigation, footer, ads, etc.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Prioritize <article> or <main> if available
    main_container = soup.find("article") or soup.find("main") or soup.find("body") or soup
    raw_text = main_container.get_text(separator="\n")

    # Normalize whitespace: collapse 3+ newlines to 2, collapse repeated horizontal spaces
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw_text.splitlines()]
    cleaned_text = "\n".join(line for line in lines if line)

    if not cleaned_text:
        raise ValueError(f"No readable text content could be extracted from: {clean_url}")

    # Enforce maximum scrape length
    if len(cleaned_text) > settings.MAX_SCRAPE_LENGTH:
        cleaned_text = cleaned_text[: settings.MAX_SCRAPE_LENGTH]

    logger.info(f"Successfully scraped '{title}' ({len(cleaned_text)} chars) from {clean_url}")
    return title, cleaned_text
