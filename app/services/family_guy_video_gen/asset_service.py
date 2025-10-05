# services/asset_service.py
import random
from pathlib import Path
from typing import Optional

from app.services.family_guy_video_gen.image_search import ImageSearchService
from app.services.family_guy_video_gen.image_download import ImageDownloadService
from app.services.family_guy_video_gen.placeholder_service import create_placeholder

# Directories (relative to project root)
# Calculate the root directory by finding the directory containing 'app'
current_path = Path(__file__).resolve()
while current_path.name != "app":
    current_path = current_path.parent
BASE_DIR = current_path.parent  # Go one level up from 'app' to get to root
CHARACTER_IMAGES_DIR = BASE_DIR / "assets" / "characters"
BACKGROUND_VIDEOS_DIR = BASE_DIR / "assets" / "videos" / "gameplay_bg_videos"
INFOGRAPHICS_DIR = BASE_DIR / "assets" / "infographics"

# Character mapping
CHARACTER_MAP = {
    "peter griffin": "peter.png",
    "brian griffin": "brian.png",
    "stewie griffin": "stewie.png",
    "lois griffin": "lois.png",
    "chris griffin": "chris.png",
}


class AssetService:
    def __init__(self):
        self.character_dir = CHARACTER_IMAGES_DIR
        self.bg_video_dir = BACKGROUND_VIDEOS_DIR
        self.infographic_dir = INFOGRAPHICS_DIR
        self.infographic_dir.mkdir(parents=True, exist_ok=True)

        # Services for external assets
        self.image_search = ImageSearchService()
        self.image_download = ImageDownloadService()

    def get_character_image(self, character_name: str) -> str:
        """Return path to local character PNG."""
        key = character_name.lower().strip()
        filename = CHARACTER_MAP.get(key)
        if not filename:
            raise ValueError(f"No character mapping for: {character_name}")
        
        path = self.character_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Character image missing: {path}")
        return str(path)

    def get_background_video(self, filename: Optional[str] = None) -> str:
        """Return path to background video (specific or random)."""
        if filename:
            path = self.bg_video_dir / filename
            if not path.exists():
                raise FileNotFoundError(f"Background video not found: {path}")
            return str(path)
        
        video_files = list(self.bg_video_dir.glob("*.mp4"))
        if not video_files:
            raise FileNotFoundError(f"No .mp4 files in {self.bg_video_dir}")
        return str(random.choice(video_files))

    def generate_smart_search_query(
        self, topic: str, dialogue_text: str, infographic_hint: Optional[str] = None
    ) -> str:
        # (Keep your existing logic here — possibly move to a helper if complex)
        topic_clean = topic.replace("What is ", "").replace("?", "").strip()
        tech_terms = ["event", "loop", "queue", "call stack", "callback", "async", "diagram", "infographic"]
        keywords = [topic_clean]
        dialogue_lower = dialogue_text.lower()
        keywords.extend([term for term in tech_terms if term in dialogue_lower][:3])
        if infographic_hint:
            keywords.extend(infographic_hint.split()[:2])
        query = " ".join(keywords + ["diagram", "infographic"])
        return query[:80]

    def get_infographic(
        self,
        topic: str,
        dialogue_text: str,
        output_filename: str,
        infographic_hint: Optional[str] = None
    ) -> str:
        """Fetch or generate infographic; always returns a valid image path."""
        query = self.generate_smart_search_query(topic, dialogue_text, infographic_hint)
        output_path = self.infographic_dir / output_filename

        # Try external search
        results = self.image_search.search_with_fallbacks(query, max_results=5)
        for item in results:
            if self.image_download.download_image(item["image"], output_path):
                return str(output_path)

        # Fallback: placeholder
        placeholder_path = create_placeholder(query, output_path)
        if placeholder_path:
            return str(placeholder_path)

        # Last resort: return a default "missing" asset (optional)
        raise RuntimeError(f"Failed to obtain infographic for: {query}")
    
# --- Keep these at module level for backward compatibility ---

_asset_service_instance = None

def _get_asset_service():
    global _asset_service_instance
    if _asset_service_instance is None:
        _asset_service_instance = AssetService()
    return _asset_service_instance

def fetch_character_image(character: str) -> str:
    return _get_asset_service().get_character_image(character)

def fetch_background_video(filename: str = None) -> str:
    return _get_asset_service().get_background_video(filename)

def fetch_infographic(
    topic: str,
    dialogue_text: str,
    output_filename: str,
    infographic_hint: str = None
) -> str | None:
    return _get_asset_service().get_infographic(topic, dialogue_text, output_filename, infographic_hint)