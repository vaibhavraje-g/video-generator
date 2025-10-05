# services/image_download.py
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageDownloadService:
    @staticmethod
    def download_image(image_url: str, output_path: Path) -> bool:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; InfographicBot/1.0)"
        }
        try:
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/") or len(response.content) < 1000:
                logger.warning(f"Invalid image from {image_url}")
                return False

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Download failed for {image_url}: {e}")
            return False