"""Wikipedia article fetching using MediaWiki API."""

import re
from typing import Dict, Tuple
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.errors import FetchError
from ..core.logging import get_logger
from ..utils.text import extract_language_from_url

logger = get_logger("ingest.fetch")


class WikipediaFetcher:
    """Fetches Wikipedia articles using the MediaWiki API."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": "RAG-Dataset-Creator/1.0 (Educational Tool)"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    def extract_article_info(self, url: str) -> Tuple[str, str, str]:
        """Extract language, title from Wikipedia URL.
        
        Returns:
            Tuple of (language, title, api_base_url)
        """
        # Parse URL
        parsed = urlparse(url)
        
        # Extract language subdomain
        lang = extract_language_from_url(url)
        
        # Extract title from path
        path = parsed.path
        if path.startswith('/wiki/'):
            title = path[6:]  # Remove '/wiki/' prefix
        else:
            raise FetchError(f"Invalid Wikipedia URL format: {url}", url)
        
        # Construct API base URL
        api_base = f"https://{lang}.wikipedia.org/w/api.php"
        
        return lang, title, api_base
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_article(self, url: str) -> Dict[str, str]:
        """Fetch Wikipedia article content and metadata.
        
        Returns:
            Dict with keys: title, content, lang, extract, url
        """
        logger.info(f"Fetching Wikipedia article: {url}")
        
        try:
            # Extract article info
            lang, title, api_base = self.extract_article_info(url)
            
            # Query parameters for MediaWiki API
            params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts|pageprops",
                "exlimit": 1,
                "explaintext": False,  # Get HTML for better processing
                "exsectionformat": "wiki",
                "formatversion": 2,
            }
            
            # Make API request
            response = await self.session.get(api_base, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "error" in data:
                raise FetchError(f"MediaWiki API error: {data['error']}", url)
            
            # Extract page data
            pages = data.get("query", {}).get("pages", [])
            if not pages:
                raise FetchError("No pages found in API response", url)
            
            page = pages[0]
            
            # Check if page exists
            if "missing" in page:
                raise FetchError(f"Wikipedia page not found: {title}", url)
            
            # Extract content
            content = page.get("extract", "")
            if not content:
                raise FetchError("No content found in Wikipedia page", url)
            
            # Get actual title (may differ from URL title)
            actual_title = page.get("title", title)
            
            # Get extract for preview
            extract_params = {
                "action": "query",
                "format": "json",
                "titles": actual_title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "exsectionformat": "plain",
                "formatversion": 2,
            }
            
            extract_response = await self.session.get(api_base, params=extract_params)
            extract_data = extract_response.json()
            extract_pages = extract_data.get("query", {}).get("pages", [])
            extract_text = ""
            if extract_pages:
                extract_text = extract_pages[0].get("extract", "")[:500]
            
            result = {
                "title": actual_title,
                "content": content,
                "lang": lang,
                "extract": extract_text,
                "url": url,
            }
            
            logger.info(f"Successfully fetched article: {actual_title} ({len(content)} chars)")
            return result
            
        except httpx.RequestError as e:
            raise FetchError(f"Network error fetching Wikipedia page: {e}", url) from e
        except Exception as e:
            if isinstance(e, FetchError):
                raise
            raise FetchError(f"Unexpected error fetching Wikipedia page: {e}", url) from e


async def fetch_wikipedia_article(url: str) -> Dict[str, str]:
    """Convenience function to fetch a Wikipedia article."""
    async with WikipediaFetcher() as fetcher:
        return await fetcher.fetch_article(url) 