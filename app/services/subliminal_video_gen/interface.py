import asyncio
from typing import Optional
from pathlib import Path

from ..shared_services.tts_service import generate_tts
from ..shared_services.llm_service import invoke_llm_with_prompt
from .project_manager import ProjectManager
from .video_service import generate_video
from .audio_service import generate_frequencies, fetch_background_music
from .models import SubliminalVideoConfig


async def generate_subliminal_video(
    duration_minutes: int,
    theme: str = "focus",
    language: str = "en",
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a subliminal video with affirmations, background music, and frequencies.
    Each request creates a new project directory with its own assets and output.

    Args:
        duration_minutes: Length of the video in minutes
        theme: Theme for affirmations and background (e.g., "focus", "relax", "confidence")
        language: Language for the affirmations
        output_path: Optional custom output path for the video

    Returns:
        str: Path to the generated video file
    """
    # Create project directory
    project_manager = ProjectManager()
    project_paths = project_manager.create_project(theme)
    print(f"Created new project directory: {project_paths['project_dir']}")

    # Generate configuration via LLM
    config = await invoke_llm_with_prompt(
        prompt=f"""Create a subliminal video configuration for a {duration_minutes} minute {theme} themed video.
        Include 10-15 relevant affirmations and appropriate frequency settings (binaural/isochronic).
        Background video should match the {theme} theme.""",
        response_model=SubliminalVideoConfig,
    )

    # Generate TTS for affirmations
    async def generate_all_audio():
        async def generate_single_audio(index: int, message: str):
            output_path = project_manager.get_audio_path(
                project_paths["project_dir"], index
            )
            audio_path = generate_tts(
                text=message,
                output_path=output_path,
                language=language,
            )
            return index, audio_path

        tasks = [
            generate_single_audio(i, msg) for i, msg in enumerate(config["messages"])
        ]
        results = await asyncio.gather(*tasks)
        return [path for _, path in sorted(results)]

    # Generate frequencies and fetch background music
    async def generate_audio_layers():
        frequency_path = project_manager.get_frequency_path(
            project_paths["project_dir"]
        )
        music_path = project_manager.get_music_path(project_paths["project_dir"])

        tasks = [
            generate_frequencies(config["audio"]["frequencies"], frequency_path),
            fetch_background_music(config["audio"]["background_music"], music_path),
        ]
        return await asyncio.gather(*tasks)

    # Run audio generation concurrently
    affirmation_paths, (frequency_path, music_path) = await asyncio.gather(
        generate_all_audio(), generate_audio_layers()
    )

    # Generate final video
    output_video_path = output_path or project_paths["final_video"]
    generate_video(
        config=config,
        affirmation_paths=affirmation_paths,
        frequency_path=frequency_path,
        music_path=music_path,
        output_path=output_video_path,
        duration_minutes=duration_minutes,
    )

    print(f"✅ Video generated at: {output_video_path}")
    print(f"Project assets stored in: {project_paths['project_dir']}")
    return output_video_path
