"""Pixabay API provider for images and videos"""

import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class PixabayProvider:
    """Pixabay API provider for searching images and videos"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Pixabay provider

        Args:
            config: Pixabay configuration dictionary
        """
        self.api_key = config.get("api_key", "")
        self.max_results = config.get("max_results", 5)
        self.image_type = config.get("image_type", "illustration,photo")
        self.safesearch = config.get("safesearch", True)
        self.timeout = config.get("timeout", 10)
        self.enabled = config.get("enabled", True)

        if not self.api_key and self.enabled:
            logger.warning("Pixabay API key not provided. Provider will be disabled.")
            self.enabled = False

    def search_images(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Search Pixabay for images

        Args:
            query: Search query
            max_results: Maximum number of results (overrides config)

        Returns:
            List of image results with 'image' and 'source' keys
        """
        if not self.enabled:
            logger.info("Pixabay provider is disabled")
            return []

        max_results = max_results or self.max_results

        try:
            url = "https://pixabay.com/api/"
            params = {
                "key": self.api_key,
                "q": query,
                "image_type": self.image_type,
                "per_page": max_results,
                "safesearch": "true" if self.safesearch else "false",
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = [
                {
                    "image": hit["largeImageURL"],
                    "source": "pixabay",
                    "title": hit.get("tags", ""),
                    "width": hit.get("imageWidth", 0),
                    "height": hit.get("imageHeight", 0),
                }
                for hit in data.get("hits", [])
                if hit.get("largeImageURL")
            ]

            logger.info(f"Pixabay found {len(results)} images for: {query}")
            return results

        except Exception as e:
            logger.warning(f"Pixabay image search failed: {e}")
            return []

    def search_videos(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Search Pixabay for videos

        Args:
            query: Search query
            max_results: Maximum number of results (overrides config)

        Returns:
            List of video results with 'video' and 'source' keys
        """
        if not self.enabled:
            logger.info("Pixabay provider is disabled")
            return []

        max_results = max_results or self.max_results

        try:
            url = "https://pixabay.com/api/videos/"
            params = {
                "key": self.api_key,
                "q": query,
                "per_page": max_results,
                "safesearch": "true" if self.safesearch else "false",
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get("hits", []):
                # Get the best quality video URL
                video_url = None
                if "videos" in hit:
                    videos = hit["videos"]
                    # Prefer large, then medium, then small
                    for size in ["large", "medium", "small"]:
                        if size in videos and "url" in videos[size]:
                            video_url = videos[size]["url"]
                            break

                if video_url:
                    results.append(
                        {
                            "video": video_url,
                            "source": "pixabay",
                            "title": hit.get("tags", ""),
                            "duration": hit.get("duration", 0),
                            "width": hit.get("videos", {})
                            .get("large", {})
                            .get("width", 0),
                            "height": hit.get("videos", {})
                            .get("large", {})
                            .get("height", 0),
                        }
                    )

            logger.info(f"Pixabay found {len(results)} videos for: {query}")
            return results

        except Exception as e:
            logger.warning(f"Pixabay video search failed: {e}")
            return []

    def search_assets(
        self, query: str, asset_type: str = "images", max_results: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Search for assets (images or videos) based on type

        Args:
            query: Search query
            asset_type: Type of asset ('images', 'videos', or 'both')
            max_results: Maximum number of results

        Returns:
            List of asset results
        """
        if asset_type == "images":
            return self.search_images(query, max_results)
        elif asset_type == "videos":
            return self.search_videos(query, max_results)
        elif asset_type == "both":
            images = self.search_images(query, max_results)
            videos = self.search_videos(query, max_results)
            return images + videos
        else:
            logger.warning(f"Unknown asset type: {asset_type}")
            return []
