"""Load and manage Assets Service configuration from JSON"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Load .env file from project root (go up from assets_service to project root)
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not available, continue without it


class AssetsConfig:
    """Load and manage Assets Service configuration from JSON"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.config_dir = config_path.parent

    def get_pixabay_config(self) -> Dict[str, Any]:
        """Get Pixabay API configuration with environment variable override"""
        config = self.config.get("pixabay_api", {}).copy()

        # Override API key from environment variable if available
        env_api_key = os.getenv("PIXABAY_API_KEY")
        if env_api_key:
            config["api_key"] = env_api_key

        return config

    def get_duckduckgo_config(self) -> Dict[str, Any]:
        """Get DuckDuckGo configuration"""
        return self.config.get("duckduckgo", {})

    def get_character_config(self) -> Dict[str, Any]:
        """Get character images configuration"""
        return self.config.get("character_images", {})

    def get_stock_videos_config(self) -> Dict[str, Any]:
        """Get stock videos configuration"""
        return self.config.get("stock_videos", {})

    def get_download_config(self) -> Dict[str, Any]:
        """Get download settings configuration"""
        return self.config.get("download_settings", {})

    def get_output_config(self) -> Dict[str, Any]:
        """Get output settings configuration"""
        return self.config.get("output_settings", {})

    def get_characters_dir(self) -> Path:
        """Get characters directory path"""
        char_dir = self.get_character_config().get(
            "characters_dir", "assets/characters"
        )
        if Path(char_dir).is_absolute():
            return Path(char_dir)
        return (
            self.config_dir / char_dir
        )  # Assets are now within assets_service directory

    def get_stock_videos_dir(self) -> Path:
        """Get stock videos directory path"""
        videos_dir = self.get_stock_videos_config().get(
            "videos_dir", "assets/videos/gameplay_bg_videos"
        )
        if Path(videos_dir).is_absolute():
            return Path(videos_dir)
        return (
            self.config_dir / videos_dir
        )  # Assets are now within assets_service directory

    def get_character_mappings(self) -> Dict[str, str]:
        """Get character name to filename mappings"""
        return self.get_character_config().get("character_mappings", {})

    def get_supported_video_formats(self) -> List[str]:
        """Get supported video file formats"""
        return self.get_stock_videos_config().get(
            "supported_formats", ["mp4", "avi", "mov"]
        )

    def get_project_dir(self) -> Path:
        """Get project directory path"""
        project_dir = self.get_output_config().get("project_dir", "projects")
        if Path(project_dir).is_absolute():
            return Path(project_dir)
        return self.config_dir.parent.parent / project_dir  # Go up to project root
