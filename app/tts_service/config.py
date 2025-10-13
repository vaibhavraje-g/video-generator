"""Load and manage TTS configuration from JSON"""

import json
from pathlib import Path
from typing import Dict, Any


class TTSConfig:
    """Load and manage TTS configuration from JSON"""

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

    def get_character_voices(self) -> Dict[str, str]:
        """Get character voice mappings"""
        return self.config.get("character_voices", {})

    def get_character_mappings(self) -> Dict[str, str]:
        """Get character name mappings"""
        return self.config.get("character_mappings", {})

    def get_voice_samples_dir(self) -> Path:
        """Get voice samples directory"""
        voice_dir = self.config.get("voice_samples_dir", "voices")
        if Path(voice_dir).is_absolute():
            return Path(voice_dir)
        return self.config_dir / voice_dir

    def get_outputs_dir(self) -> Path:
        """Get outputs directory"""
        output_dir = self.config.get("outputs_dir", "outputs")
        if Path(output_dir).is_absolute():
            return Path(output_dir)
        return self.config_dir / output_dir

    def get_gtts_config(self) -> Dict[str, Any]:
        """Get gTTS configuration"""
        return self.config.get("gtts", {})

    def get_tiktok_config(self) -> Dict[str, Any]:
        """Get TikTok API configuration"""
        return self.config.get("tiktok_api", {})

    def get_chatterbox_config(self) -> Dict[str, Any]:
        """Get ChatterboxTTS configuration"""
        return self.config.get("chatterbox", {})

    def get_device(self) -> str:
        """Get device configuration"""
        return self.config.get("device", "auto")

    def get_subtitle_config(self) -> Dict[str, Any]:
        """Get subtitle configuration"""
        return self.config.get("subtitles", {})
