from datetime import datetime
from typing import Dict
from pathlib import Path


class ProjectManager:
    def __init__(self, base_projects_dir: str = "projects"):
        self.base_projects_dir = Path(base_projects_dir)

    def create_project(self, topic: str) -> Dict[str, str]:
        """
        Create a new project directory structure for a Family Guy video request.

        Args:
            topic: The topic of the video being generated

        Returns:
            Dict containing paths for various project assets
        """
        # Create a shorter, sanitized project name from the topic
        # Take first 30 chars of topic, replace spaces/special chars with underscore
        short_topic = "".join(c if c.isalnum() else "_" for c in topic.lower())[:30]
        timestamp = datetime.now().strftime("%y%m%d_%H%M")  # Shorter timestamp format
        project_name = f"fg_{short_topic}_{timestamp}"

        # Create project directory structure
        project_dir = self.base_projects_dir / project_name
        subdirs = {
            "audio": project_dir / "audio",
            "output": project_dir / "output",
            "assets": project_dir / "assets",
            "temp": project_dir / "temp",
        }

        # Create all directories
        for dir_path in subdirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Return paths dictionary
        paths = {
            "project_dir": str(project_dir),
            "audio_dir": str(subdirs["audio"]),
            "output_dir": str(subdirs["output"]),
            "assets_dir": str(subdirs["assets"]),
            "temp_dir": str(subdirs["temp"]),
            "final_video": str(subdirs["output"] / "final.mp4"),
        }

        return paths

    def get_audio_path(self, project_dir: str, index: int) -> str:
        """Get the path for an audio file in the project."""
        return str(Path(project_dir) / "audio" / f"line_{index}.wav")

    def get_infographic_path(self, project_dir: str, index: int) -> str:
        """Get the path for an infographic image in the project."""
        return str(Path(project_dir) / "assets" / f"info_{index}.png")
