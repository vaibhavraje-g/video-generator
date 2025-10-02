import os
from datetime import datetime
from pathlib import Path
from typing import Dict


class ProjectManager:
    """Manages project directories and file paths for subliminal video generation."""

    def __init__(self, base_dir: str = "projects"):
        self.base_dir = Path(base_dir)

    def create_project(self, theme: str) -> Dict[str, str]:
        """Create a new project directory with subdirectories."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"subliminal_{theme}__{timestamp}"
        project_dir = self.base_dir / project_name

        # Create directory structure
        subdirs = ["assets", "audio", "output", "temp"]
        for subdir in subdirs:
            (project_dir / subdir).mkdir(parents=True, exist_ok=True)

        return {
            "project_dir": str(project_dir),
            "assets_dir": str(project_dir / "assets"),
            "audio_dir": str(project_dir / "audio"),
            "output_dir": str(project_dir / "output"),
            "temp_dir": str(project_dir / "temp"),
            "final_video": str(project_dir / "output" / "final.mp4"),
        }

    def get_audio_path(self, project_dir: str, index: int) -> str:
        """Get path for an affirmation audio file."""
        return str(Path(project_dir) / "audio" / f"affirmation_{index}.mp3")

    def get_frequency_path(self, project_dir: str) -> str:
        """Get path for the generated frequencies audio file."""
        return str(Path(project_dir) / "audio" / "frequencies.wav")

    def get_music_path(self, project_dir: str) -> str:
        """Get path for the background music file."""
        return str(Path(project_dir) / "audio" / "background_music.mp3")
