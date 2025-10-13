"""Download service for handling asset downloads"""

import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DownloadService:
    """Service for downloading assets from URLs"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Download service

        Args:
            config: Download configuration dictionary
        """
        self.user_agent = config.get(
            "user_agent", "Mozilla/5.0 (compatible; AssetsBot/1.0)"
        )
        self.min_file_size = config.get("min_file_size", 1000)
        self.max_file_size = config.get("max_file_size", 50000000)
        self.timeout = config.get("timeout", 15)
        self.retry_attempts = config.get("retry_attempts", 3)

    def download_image(
        self, image_url: str, output_path: Path, project_dir: Optional[Path] = None
    ) -> bool:
        """
        Download image from URL to specified path

        Args:
            image_url: URL of the image to download
            output_path: Path where to save the image
            project_dir: Project directory for validation (optional)

        Returns:
            True if download successful, False otherwise
        """
        headers = {"User-Agent": self.user_agent}

        try:
            response = requests.get(image_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                logger.warning(f"Invalid content type from {image_url}: {content_type}")
                return False

            content_length = len(response.content)
            if content_length < self.min_file_size:
                logger.warning(
                    f"File too small from {image_url}: {content_length} bytes"
                )
                return False

            if content_length > self.max_file_size:
                logger.warning(
                    f"File too large from {image_url}: {content_length} bytes"
                )
                return False

            # Validate output path is within project directory
            if project_dir:
                try:
                    output_path.resolve().relative_to(project_dir.resolve())
                except ValueError:
                    logger.error(f"Cannot download to non-project path: {output_path}")
                    return False

            # Create parent directories
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Downloaded image: {output_path} ({content_length} bytes)")
            return True

        except Exception as e:
            logger.error(f"Download failed for {image_url}: {e}")
            return False

    def download_video(
        self, video_url: str, output_path: Path, project_dir: Optional[Path] = None
    ) -> bool:
        """
        Download video from URL to specified path

        Args:
            video_url: URL of the video to download
            output_path: Path where to save the video
            project_dir: Project directory for validation (optional)

        Returns:
            True if download successful, False otherwise
        """
        headers = {"User-Agent": self.user_agent}

        try:
            response = requests.get(video_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("video/"):
                logger.warning(f"Invalid content type from {video_url}: {content_type}")
                return False

            content_length = len(response.content)
            if content_length < self.min_file_size:
                logger.warning(
                    f"File too small from {video_url}: {content_length} bytes"
                )
                return False

            if content_length > self.max_file_size:
                logger.warning(
                    f"File too large from {video_url}: {content_length} bytes"
                )
                return False

            # Validate output path is within project directory
            if project_dir:
                try:
                    output_path.resolve().relative_to(project_dir.resolve())
                except ValueError:
                    logger.error(f"Cannot download to non-project path: {output_path}")
                    return False

            # Create parent directories
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Downloaded video: {output_path} ({content_length} bytes)")
            return True

        except Exception as e:
            logger.error(f"Download failed for {video_url}: {e}")
            return False
