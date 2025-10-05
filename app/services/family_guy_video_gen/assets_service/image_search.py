# services/image_search.py
import logging
import random
import time
import requests
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class ImageSearchService:
    def __init__(self):
        self.pixabay_api_key = "YOUR_PIXABAY_API_KEY"  # Get free key at https://pixabay.com/api/docs/

    def search_pixabay(self, query: str, max_results: int = 3) -> list[dict]:
        """Search Pixabay for relevant images (supports 'diagram', 'infographic' etc.)"""
        try:
            url = "https://pixabay.com/api/"
            params = {
                "key": self.pixabay_api_key,
                "q": query,
                "image_type": "illustration,photo",  # includes diagrams
                "per_page": max_results,
                "safesearch": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = [
                {"image": hit["largeImageURL"], "source": "pixabay"}
                for hit in data.get("hits", [])
                if hit.get("largeImageURL")
            ]
            logger.info(f"Pixabay found {len(results)} images for: {query}")
            return results
        except Exception as e:
            logger.warning(f"Pixabay search failed: {e}")
            return []

    def search_duckduckgo(self, query: str, max_results: int = 3) -> list[dict]:
        """Use ddgs (new duckduckgo-search)"""
        try:
            from ddgs import DDGS  # pip install ddgs
            time.sleep(random.uniform(1, 2))
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=query,
                    region="us-en",
                    safesearch="moderate",
                    size="Medium",
                    max_results=max_results
                ))
            return [{"image": r["image"], "source": "duckduckgo"} for r in results]
        except Exception as e:
            logger.warning(f"DuckDuckGo (ddgs) failed: {e}")
            return []

    def search_with_fallbacks(self, query: str, max_results: int = 3) -> list[dict]:
        """Try multiple sources in order of preference"""
        sources = [
            self.search_duckduckgo,
            self.search_pixabay,
            # Add Bing/Selenium later if needed
        ]
        for source_fn in sources:
            results = source_fn(query, max_results)
            if results:
                return results
        return []