"""Main Assets Service - Unified interface for all asset providers"""

import random
from pathlib import Path
from typing import Literal, Optional, List, Dict

from .config import AssetsConfig
from .pixabay_provider import PixabayProvider
from .duckduckgo_provider import DuckDuckGoProvider
from .character_provider import CharacterProvider
from .download_service import DownloadService


class AssetsService:
    """
    Unified Assets Service supporting multiple providers:
    - Pixabay API for images and videos
    - DuckDuckGo for image search
    - Character images from local assets
    - Stock gameplay footage
    """

    def __init__(self, config_path: str = None, project_dir: Optional[Path] = None):
        """
        Initialize Assets Service

        Args:
            config_path: Path to config.json (default: same directory as this module)
            project_dir: Project directory where generated files should be stored
        """
        self.config = AssetsConfig(config_path)
        self.project_dir = project_dir or self.config.get_project_dir()

        # Initialize providers
        pixabay_config = self.config.get_pixabay_config()
        self.pixabay_provider = PixabayProvider(pixabay_config)

        duckduckgo_config = self.config.get_duckduckgo_config()
        self.duckduckgo_provider = DuckDuckGoProvider(duckduckgo_config)

        character_config = self.config.get_character_config()
        characters_dir = self.config.get_characters_dir()
        self.character_provider = CharacterProvider(character_config, characters_dir)

        download_config = self.config.get_download_config()
        self.download_service = DownloadService(download_config)

        # Initialize directories
        self.stock_videos_dir = self.config.get_stock_videos_dir()

    def get_stock_gameplay_footage(self, filename: Optional[str] = None) -> str:
        """
        Get stock gameplay footage (specific file or random)

        Args:
            filename: Specific video filename (optional)

        Returns:
            Path to video file

        Raises:
            FileNotFoundError: If no videos found
        """
        if filename:
            video_path = self.stock_videos_dir / filename
            if not video_path.exists():
                raise FileNotFoundError(f"Stock video not found: {video_path}")
            return str(video_path)

        # Get random video
        supported_formats = self.config.get_supported_video_formats()
        video_files = []
        for fmt in supported_formats:
            video_files.extend(self.stock_videos_dir.glob(f"*.{fmt}"))

        if not video_files:
            raise FileNotFoundError(f"No video files found in {self.stock_videos_dir}")

        selected_video = random.choice(video_files)
        return str(selected_video)

    def get_assets_infographics(
        self,
        query: str,
        sources: List[str] = None,
        output_path: Optional[Path] = None,
        max_results: int = 5,
    ) -> str:
        """
        Get assets/infographics using specified sources

        Args:
            query: Search query
            sources: List of sources to search (default: ["duckduckgo", "pixabay"])
            output_path: Output path for downloaded asset
            max_results: Maximum results to try

        Returns:
            Path to downloaded asset

        Raises:
            RuntimeError: If no assets found
        """
        if sources is None:
            sources = ["duckduckgo", "pixabay"]

        if output_path is None:
            output_path = (
                self.project_dir
                / "assets"
                / "infographics"
                / f"{query.replace(' ', '_')}.jpg"
            )
        else:
            # Ensure output_path is a Path object
            if isinstance(output_path, str):
                output_path = Path(output_path)

        # Ensure output path is within project directory
        try:
            output_path.resolve().relative_to(self.project_dir.resolve())
        except ValueError:
            output_path = (
                self.project_dir
                / "assets"
                / "infographics"
                / f"{query.replace(' ', '_')}.jpg"
            )

        # Try each source
        for source in sources:
            if source == "pixabay":
                results = self.pixabay_provider.search_images(query, max_results)
            elif source == "duckduckgo":
                results = self.duckduckgo_provider.search_images(query, max_results)
            else:
                continue

            # Try to download each result
            for result in results:
                image_url = result.get("image")
                if image_url and self.download_service.download_image(
                    image_url, output_path, self.project_dir
                ):
                    return str(output_path)

        raise RuntimeError(f"Failed to obtain infographic for: {query}")

    def get_videos_pixabay(
        self,
        query: str,
        api_key: Optional[str] = None,
        output_path: Optional[Path] = None,
        max_results: int = 5,
    ) -> str:
        """
        Get videos using Pixabay API

        Args:
            query: Search query
            api_key: Pixabay API key (optional, uses config if not provided)
            output_path: Output path for downloaded video
            max_results: Maximum results to try

        Returns:
            Path to downloaded video

        Raises:
            RuntimeError: If no videos found
        """
        if output_path is None:
            output_path = (
                self.project_dir
                / "assets"
                / "videos"
                / f"{query.replace(' ', '_')}.mp4"
            )
        else:
            # Ensure output_path is a Path object
            if isinstance(output_path, str):
                output_path = Path(output_path)

        # Ensure output path is within project directory
        try:
            output_path.resolve().relative_to(self.project_dir.resolve())
        except ValueError:
            output_path = (
                self.project_dir
                / "assets"
                / "videos"
                / f"{query.replace(' ', '_')}.mp4"
            )

        # Use provided API key or config
        if api_key:
            pixabay_config = self.config.get_pixabay_config().copy()
            pixabay_config["api_key"] = api_key
            pixabay_provider = PixabayProvider(pixabay_config)
        else:
            pixabay_provider = self.pixabay_provider

        results = pixabay_provider.search_videos(query, max_results)

        # Try to download each result
        for result in results:
            video_url = result.get("video")
            if video_url and self.download_service.download_video(
                video_url, output_path, self.project_dir
            ):
                return str(output_path)

        raise RuntimeError(f"Failed to obtain video for: {query}")

    def get_character_image(
        self, character_name: str, mood_descriptor: Optional[str] = None
    ) -> str:
        """
        Return character images from character map

        Args:
            character_name: Name of the character
            mood_descriptor: Optional mood descriptor

        Returns:
            Path to character image

        Raises:
            ValueError: If character not found
        """
        return self.character_provider.get_character_image(
            character_name, mood_descriptor
        )

    def search_assets(
        self,
        query: str,
        asset_type: Literal["images", "videos", "both"] = "images",
        sources: List[str] = None,
        max_results: int = 5,
    ) -> List[Dict[str, str]]:
        """
        Search for assets using multiple sources

        Args:
            query: Search query
            asset_type: Type of assets to search for
            sources: List of sources to search
            max_results: Maximum results per source

        Returns:
            List of asset results
        """
        if sources is None:
            sources = ["duckduckgo", "pixabay"]

        all_results = []

        for source in sources:
            if source == "pixabay":
                results = self.pixabay_provider.search_assets(
                    query, asset_type, max_results
                )
            elif source == "duckduckgo":
                results = self.duckduckgo_provider.search_assets(
                    query, asset_type, max_results
                )
            else:
                continue

            all_results.extend(results)

        return all_results

    def download_asset(
        self, url: str, output_path: Path, asset_type: str = "image"
    ) -> bool:
        """
        Download an asset from URL

        Args:
            url: URL of the asset
            output_path: Path to save the asset
            asset_type: Type of asset ("image" or "video")

        Returns:
            True if successful, False otherwise
        """
        if asset_type == "image":
            return self.download_service.download_image(
                url, output_path, self.project_dir
            )
        elif asset_type == "video":
            return self.download_service.download_video(
                url, output_path, self.project_dir
            )
        else:
            return False

    # Convenience methods for specific character images
    def get_peter_image(self, mood_descriptor: Optional[str] = None) -> str:
        """Get Peter Griffin's image"""
        return self.get_character_image("peter", mood_descriptor)

    def get_brian_image(self, mood_descriptor: Optional[str] = None) -> str:
        """Get Brian's image"""
        return self.get_character_image("brian", mood_descriptor)

    def get_stewie_image(self, mood_descriptor: Optional[str] = None) -> str:
        """Get Stewie's image"""
        return self.get_character_image("stewie", mood_descriptor)

    def get_lois_image(self, mood_descriptor: Optional[str] = None) -> str:
        """Get Lois's image"""
        return self.get_character_image("lois", mood_descriptor)

    def get_chris_image(self, mood_descriptor: Optional[str] = None) -> str:
        """Get Chris's image"""
        return self.get_character_image("chris", mood_descriptor)
