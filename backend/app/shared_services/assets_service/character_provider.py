"""Character image provider for managing character assets"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CharacterProvider:
    """Character image provider for managing character assets"""

    def __init__(self, config: Dict[str, Any], characters_dir: Path):
        """
        Initialize Character provider

        Args:
            config: Character configuration dictionary
            characters_dir: Path to characters directory
        """
        self.characters_dir = characters_dir
        self.character_mappings = config.get("character_mappings", {})
        self.enabled = config.get("enabled", True)

    def get_character_image(
        self, character_name: str, mood_descriptor: Optional[str] = None
    ) -> str:
        """
        Get character image path based on character name and optional mood

        Args:
            character_name: Name of the character
            mood_descriptor: Optional mood or descriptor for the character

        Returns:
            Path to character image file

        Raises:
            ValueError: If character image not found
        """
        if not self.enabled:
            raise ValueError("Character provider is disabled")

        # Normalize character name
        key = character_name.lower().strip()
        key_no_griffin = key.replace("griffin", "").strip()

        # Try to find character in mappings
        filename = self.character_mappings.get(key) or self.character_mappings.get(
            key_no_griffin
        )

        if not filename:
            raise ValueError(f"No character mapping found for: {character_name}")

        # Build full path
        image_path = self.characters_dir / filename

        if not image_path.exists():
            raise ValueError(f"Character image file not found: {image_path}")

        logger.info(
            f"Found character image: {image_path} for character: {character_name}"
        )
        return str(image_path)

    def list_available_characters(self) -> Dict[str, str]:
        """
        List all available characters and their filenames

        Returns:
            Dictionary mapping character names to filenames
        """
        return self.character_mappings.copy()

    def get_character_info(self, character_name: str) -> Dict[str, Any]:
        """
        Get information about a character

        Args:
            character_name: Name of the character

        Returns:
            Dictionary with character information
        """
        key = character_name.lower().strip()
        key_no_griffin = key.replace("griffin", "").strip()

        filename = self.character_mappings.get(key) or self.character_mappings.get(
            key_no_griffin
        )

        if not filename:
            return {"error": f"Character not found: {character_name}"}

        image_path = self.characters_dir / filename

        return {
            "name": character_name,
            "filename": filename,
            "path": str(image_path),
            "exists": image_path.exists(),
            "size": image_path.stat().st_size if image_path.exists() else 0,
        }
