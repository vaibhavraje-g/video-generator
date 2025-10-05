import asyncio
from typing import Optional
import os

from .script_service import generate_script
from ..shared_services.tts_service import generate_tts
from .asset_service import (
    fetch_background_video,
    fetch_character_image,
    fetch_infographic,
)
from .project_manager import ProjectManager
from .video_service.video_service import generate_video


async def generate_family_guy_video(
    topic: str, output_path: Optional[str] = None
) -> str:
    """
    Generate a Family Guy style educational video for a given topic.
    Each request creates a new project directory with its own assets and output.

    Args:
        topic: The educational topic to create a video about
        output_path: Optional custom output path for the video. If not provided, uses a new project directory.

    Returns:
        str: Path to the generated video file
    """
    # Create a new project directory
    project_manager = ProjectManager()
    project_paths = project_manager.create_project(topic)
    print(f"Created new project directory: {project_paths['project_dir']}")

    # 1. Generate script
    script = await generate_script(topic)
    print(f"Generated script for topic: {topic}")

    # 2. Fetch static assets (character images and background video) - these are fast
    # Fetch all character images (these are cached/fast)
    unique_characters = {d.character for d in script.dialogues}
    character_image_map = {}
    for character in unique_characters:
        key = character.lower().strip()
        try:
            image_path = fetch_character_image(character)
            character_image_map[key] = image_path
        except Exception as e:
            print(f"⚠️ Character image missing for {character}: {e}")

    # Fetch background video (fast operation)
    background_video_path = fetch_background_video("gameplay.mp4")

    # 3. Run audio generation and infographic fetching in parallel
    async def generate_all_audio():
        async def generate_single_audio(index, dialogue):
            output_path = project_manager.get_audio_path(
                project_paths["project_dir"], index
            )
            audio_path = generate_tts(
                text=dialogue.text,
                output_path=output_path,
                character=dialogue.character.lower(),
            )
            return index, audio_path

        tasks = [generate_single_audio(i, d) for i, d in enumerate(script.dialogues)]
        results = await asyncio.gather(*tasks)
        return [path for _, path in sorted(results)]

    async def fetch_all_infographics():
        async def fetch_single_infographic(index, dialogue):
            infographic_hint = getattr(dialogue, "infographic", None)
            if not infographic_hint:
                return index, None

            infographic_path = project_manager.get_infographic_path(
                project_paths["project_dir"], index
            )
            path = fetch_infographic(
                topic=topic,
                dialogue_text=dialogue.text,
                output_filename=infographic_path,
                infographic_hint=infographic_hint,
            )
            return index, path

        info_tasks = [
            fetch_single_infographic(i, d) for i, d in enumerate(script.dialogues)
        ]
        info_results = await asyncio.gather(*info_tasks)
        return [path for _, path in sorted(info_results) if path is not None]

    # Run audio generation and infographic fetching simultaneously
    audio_paths, infographic_paths = await asyncio.gather(
        generate_all_audio(), fetch_all_infographics()
    )

    # Generate final video
    output_video_path = output_path or project_paths["final_video"]
    generate_video(
        script=script,
        tts_files=audio_paths,
        bg_video=background_video_path,
        output_path=output_video_path,
        char_images=character_image_map,
        infographic_images=infographic_paths,
    )

    print(f"✅ Video generated at: {output_video_path}")
    print(f"Project assets stored in: {project_paths['project_dir']}")
    return output_video_path
