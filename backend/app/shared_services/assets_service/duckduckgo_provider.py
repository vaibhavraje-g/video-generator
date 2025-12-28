"""DuckDuckGo search provider for images"""

import random
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DuckDuckGoProvider:
    """DuckDuckGo search provider for images"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DuckDuckGo provider

        Args:
            config: DuckDuckGo configuration dictionary
        """
        self.max_results = config.get("max_results", 5)
        self.delay_range = config.get("delay_range", [1, 2])
        self.timeout = config.get("timeout", 15)
        self.enabled = config.get("enabled", True)

    def search_images(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo for images using ddgs library

        Args:
            query: Search query
            max_results: Maximum number of results (overrides config)

        Returns:
            List of image results with 'image' and 'source' keys
        """
        if not self.enabled:
            logger.info("DuckDuckGo provider is disabled")
            return []

        max_results = max_results or self.max_results

        try:
            from ddgs import DDGS  # pip install duckduckgo-search

            # Add random delay to avoid rate limiting
            delay = random.uniform(self.delay_range[0], self.delay_range[1])
            time.sleep(delay)

            results = []
            with DDGS() as ddgs:
                for result in ddgs.images(query):
                    results.append(
                        {
                            "image": result["image"],
                            "source": "duckduckgo",
                            "title": result.get("title", ""),
                            "width": result.get("width", 0),
                            "height": result.get("height", 0),
                        }
                    )
                    if len(results) >= max_results:
                        break

            logger.info(f"DuckDuckGo found {len(results)} images for: {query}")
            return results

        except ImportError:
            logger.error(
                "ddgs library not installed. Install with: pip install duckduckgo-search"
            )
            return []
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            return []

    def search_assets(
        self, query: str, asset_type: str = "images", max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Search for assets (currently only supports images)

        Args:
            query: Search query
            asset_type: Type of asset (only 'images' supported)
            max_results: Maximum number of results

        Returns:
            List of asset results
        """
        if asset_type == "images":
            return self.search_images(query, max_results)
        else:
            logger.warning(f"DuckDuckGo only supports image search, not: {asset_type}")
            return []
